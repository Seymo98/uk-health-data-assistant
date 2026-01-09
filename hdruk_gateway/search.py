"""
Advanced dataset search functionality for HDR UK Gateway.

Provides high-level search capabilities including:
- Natural language query parsing
- Faceted search with aggregations
- Result ranking and scoring
- Export to various formats
"""

import re
import csv
import json
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from io import StringIO

from .client import GatewayClient
from .models import (
    Dataset,
    DataUseRegister,
    Publication,
    SearchResult,
    SearchFilters,
    ResourceType,
    OrganisationSector,
)

logger = logging.getLogger(__name__)


@dataclass
class SearchSuggestion:
    """A search suggestion or autocomplete result."""
    text: str
    type: str  # 'dataset', 'publisher', 'keyword', etc.
    score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchFacet:
    """A search facet/filter with counts."""
    name: str
    field: str
    buckets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EnhancedSearchResult:
    """Enhanced search result with facets and suggestions."""
    results: SearchResult
    facets: List[SearchFacet] = field(default_factory=list)
    suggestions: List[SearchSuggestion] = field(default_factory=list)
    query_interpretation: Optional[str] = None
    total_count: int = 0
    search_time_ms: float = 0


class DatasetSearcher:
    """
    Advanced dataset search with natural language understanding.

    Features:
    - Query parsing to extract entities (diseases, regions, data types)
    - Automatic filter suggestion
    - Result ranking by relevance
    - Export capabilities

    Example:
        >>> searcher = DatasetSearcher()
        >>> results = searcher.search("diabetes data in Wales")
        >>> print(f"Found {len(results.datasets)} datasets")
    """

    # Common UK health-related terms and their mappings
    CONDITION_KEYWORDS = {
        "diabetes": ["diabetes", "diabetic", "glucose", "hba1c", "insulin"],
        "cardiovascular": ["heart", "cardiac", "cardiovascular", "cvd", "stroke", "hypertension"],
        "cancer": ["cancer", "oncology", "tumour", "tumor", "malignant", "neoplasm"],
        "mental health": ["mental", "psychiatric", "depression", "anxiety", "psychosis"],
        "respiratory": ["respiratory", "lung", "pulmonary", "asthma", "copd"],
        "maternal": ["maternal", "pregnancy", "prenatal", "postnatal", "obstetric"],
        "covid": ["covid", "coronavirus", "sars-cov-2", "pandemic"],
        "genomics": ["genomic", "genetic", "dna", "wgs", "genome", "sequencing"],
    }

    REGION_KEYWORDS = {
        "england": ["england", "english", "nhs england"],
        "wales": ["wales", "welsh", "sail"],
        "scotland": ["scotland", "scottish", "rds", "research data scotland"],
        "northern ireland": ["northern ireland", "ni"],
        "uk": ["uk", "united kingdom", "british", "national"],
    }

    DATA_TYPE_KEYWORDS = {
        "primary care": ["primary care", "gp", "general practice", "cprd"],
        "hospital": ["hospital", "hes", "secondary care", "inpatient", "outpatient"],
        "registry": ["registry", "register", "cancer registry"],
        "cohort": ["cohort", "biobank", "longitudinal"],
        "imaging": ["imaging", "mri", "ct", "x-ray", "radiology"],
        "genomic": ["genomic", "genetic", "wgs", "exome"],
    }

    PUBLISHER_ALIASES = {
        "cprd": ["CPRD", "Clinical Practice Research Datalink"],
        "opensafely": ["OpenSAFELY"],
        "uk biobank": ["UK Biobank"],
        "sail": ["SAIL Databank", "SAIL"],
        "nhs england": ["NHS England", "NHS Digital"],
        "genomics england": ["Genomics England"],
        "rds": ["Research Data Scotland"],
    }

    def __init__(self, client: Optional[GatewayClient] = None):
        """
        Initialize the searcher.

        Args:
            client: Optional GatewayClient instance (creates new if not provided)
        """
        self.client = client or GatewayClient()

    def parse_query(self, query: str) -> Tuple[str, SearchFilters]:
        """
        Parse a natural language query into search terms and filters.

        Args:
            query: Natural language search query

        Returns:
            Tuple of (cleaned query string, SearchFilters)
        """
        query_lower = query.lower()
        filters = SearchFilters()
        terms_to_remove = []

        # Extract conditions
        for condition, keywords in self.CONDITION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    filters.keywords.append(condition)
                    break

        # Extract regions
        for region, keywords in self.REGION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    filters.geographic_coverage.append(region.title())
                    terms_to_remove.append(keyword)
                    break

        # Extract data types
        for data_type, keywords in self.DATA_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    filters.keywords.append(data_type)
                    break

        # Extract publishers
        for alias, names in self.PUBLISHER_ALIASES.items():
            if alias in query_lower:
                filters.publisher.extend(names)
                terms_to_remove.append(alias)

        # Clean query by removing identified terms
        cleaned_query = query
        for term in terms_to_remove:
            cleaned_query = re.sub(rf'\b{re.escape(term)}\b', '', cleaned_query, flags=re.IGNORECASE)

        # Remove common filler words
        filler_words = ["data", "dataset", "datasets", "in", "for", "about", "the", "with", "from"]
        for word in filler_words:
            cleaned_query = re.sub(rf'\b{word}\b', '', cleaned_query, flags=re.IGNORECASE)

        cleaned_query = ' '.join(cleaned_query.split()).strip()

        return cleaned_query, filters

    def search(
        self,
        query: str,
        parse_query: bool = True,
        include_data_uses: bool = True,
        include_publications: bool = False,
        page: int = 1,
        per_page: int = 25,
    ) -> EnhancedSearchResult:
        """
        Perform an enhanced search with query parsing.

        Args:
            query: Natural language search query
            parse_query: Whether to parse and extract filters from query
            include_data_uses: Include data use register results
            include_publications: Include publication results
            page: Page number
            per_page: Results per page

        Returns:
            EnhancedSearchResult with datasets and metadata
        """
        import time
        start_time = time.time()

        # Parse query if enabled
        if parse_query:
            search_term, filters = self.parse_query(query)
            query_interpretation = self._generate_interpretation(query, filters)
        else:
            search_term = query
            filters = SearchFilters()
            query_interpretation = None

        # Determine resource types to search
        resource_types = [ResourceType.DATASET]
        if include_data_uses:
            resource_types.append(ResourceType.DATA_USE_REGISTER)
        if include_publications:
            resource_types.append(ResourceType.PUBLICATION)

        # Perform search
        filters.page = page
        filters.per_page = per_page
        results = self.client.search(
            query=search_term or query,
            resource_types=resource_types,
            filters=filters if parse_query else None,
            page=page,
            per_page=per_page,
        )

        # Calculate search time
        search_time_ms = (time.time() - start_time) * 1000

        # Generate facets from results
        facets = self._generate_facets(results)

        # Generate suggestions
        suggestions = self._generate_suggestions(query, results)

        return EnhancedSearchResult(
            results=results,
            facets=facets,
            suggestions=suggestions,
            query_interpretation=query_interpretation,
            total_count=results.total_results,
            search_time_ms=search_time_ms,
        )

    def _generate_interpretation(self, query: str, filters: SearchFilters) -> str:
        """Generate a human-readable interpretation of the parsed query."""
        parts = []

        if filters.keywords:
            parts.append(f"topics: {', '.join(filters.keywords)}")

        if filters.geographic_coverage:
            parts.append(f"region: {', '.join(filters.geographic_coverage)}")

        if filters.publisher:
            parts.append(f"publishers: {', '.join(filters.publisher)}")

        if parts:
            return f"Searching for: {' | '.join(parts)}"
        return f"Searching for: {query}"

    def _generate_facets(self, results: SearchResult) -> List[SearchFacet]:
        """Generate facets/aggregations from search results."""
        facets = []

        # Publisher facet
        publisher_counts: Dict[str, int] = {}
        for dataset in results.datasets:
            publisher = dataset.publisher_name
            publisher_counts[publisher] = publisher_counts.get(publisher, 0) + 1

        if publisher_counts:
            facets.append(SearchFacet(
                name="Publisher",
                field="publisher",
                buckets=[
                    {"key": k, "count": v}
                    for k, v in sorted(publisher_counts.items(), key=lambda x: -x[1])[:10]
                ]
            ))

        # Organisation sector facet (from data uses)
        sector_counts: Dict[str, int] = {}
        for dur in results.data_uses:
            if dur.organisation_sector:
                sector = dur.organisation_sector.value
                sector_counts[sector] = sector_counts.get(sector, 0) + 1

        if sector_counts:
            facets.append(SearchFacet(
                name="Organisation Sector",
                field="organisation_sector",
                buckets=[
                    {"key": k, "count": v}
                    for k, v in sorted(sector_counts.items(), key=lambda x: -x[1])
                ]
            ))

        return facets

    def _generate_suggestions(self, query: str, results: SearchResult) -> List[SearchSuggestion]:
        """Generate search suggestions based on results."""
        suggestions = []

        # Suggest related publishers if few results
        if len(results.datasets) < 5:
            for alias, names in self.PUBLISHER_ALIASES.items():
                if alias not in query.lower():
                    suggestions.append(SearchSuggestion(
                        text=f"{query} {names[0]}",
                        type="publisher",
                        score=0.8,
                        metadata={"publisher": names[0]}
                    ))

        # Suggest related conditions
        query_lower = query.lower()
        for condition, keywords in self.CONDITION_KEYWORDS.items():
            if condition not in query_lower and not any(k in query_lower for k in keywords):
                if results.datasets:  # Only suggest if we have some results
                    suggestions.append(SearchSuggestion(
                        text=f"{query} {condition}",
                        type="condition",
                        score=0.6,
                    ))

        return suggestions[:5]  # Limit suggestions

    def find_similar_datasets(self, dataset_id: str, limit: int = 5) -> List[Dataset]:
        """
        Find datasets similar to a given dataset.

        Args:
            dataset_id: ID of the reference dataset
            limit: Maximum number of similar datasets to return

        Returns:
            List of similar Dataset objects
        """
        try:
            dataset = self.client.get_dataset(dataset_id)
        except Exception:
            return []

        # Search using keywords from the dataset
        keywords = []
        if dataset.metadata:
            keywords = dataset.metadata.keywords[:3]  # Use top 3 keywords

        if not keywords and dataset.metadata and dataset.metadata.abstract:
            # Extract keywords from abstract
            words = dataset.metadata.abstract.lower().split()
            # Simple keyword extraction (could be improved with NLP)
            keywords = [w for w in words if len(w) > 5][:3]

        if not keywords:
            return []

        results = self.client.search_datasets(
            " ".join(keywords),
            per_page=limit + 1  # Get one extra to exclude the original
        )

        # Filter out the original dataset
        return [ds for ds in results if ds.id != dataset_id][:limit]

    def get_publisher_datasets(
        self,
        publisher_name: str,
        page: int = 1,
        per_page: int = 25,
    ) -> List[Dataset]:
        """
        Get all datasets from a specific publisher.

        Args:
            publisher_name: Name of the data publisher/custodian
            page: Page number
            per_page: Results per page

        Returns:
            List of Dataset objects from that publisher
        """
        filters = SearchFilters(publisher=[publisher_name])
        return self.client.search_datasets("", filters=filters, page=page, per_page=per_page)

    def export_results_csv(self, results: SearchResult) -> str:
        """
        Export search results to CSV format.

        Args:
            results: SearchResult to export

        Returns:
            CSV string
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write datasets
        if results.datasets:
            writer.writerow([
                "Type", "ID", "Title", "Publisher", "Abstract",
                "Publications", "Data Uses", "Gateway URL"
            ])
            for ds in results.datasets:
                writer.writerow([
                    "Dataset",
                    ds.id,
                    ds.title,
                    ds.publisher_name,
                    ds.abstract[:200] + "..." if ds.abstract and len(ds.abstract) > 200 else ds.abstract,
                    ds.publications_count,
                    ds.durs_count,
                    ds.gateway_url,
                ])

        # Write data uses
        if results.data_uses:
            writer.writerow([])  # Empty row separator
            writer.writerow([
                "Type", "ID", "Project Title", "Organisation", "Sector",
                "Lay Summary", "Approval Date", "Gateway URL"
            ])
            for dur in results.data_uses:
                writer.writerow([
                    "Data Use",
                    dur.id,
                    dur.project_title,
                    dur.organisation_name,
                    dur.organisation_sector.value if dur.organisation_sector else "",
                    dur.lay_summary[:200] + "..." if dur.lay_summary and len(dur.lay_summary) > 200 else dur.lay_summary,
                    dur.latest_approval_date,
                    dur.gateway_url,
                ])

        return output.getvalue()

    def export_results_json(self, results: SearchResult) -> str:
        """
        Export search results to JSON format.

        Args:
            results: SearchResult to export

        Returns:
            JSON string
        """
        data = {
            "datasets": [
                {
                    "id": ds.id,
                    "title": ds.title,
                    "publisher": ds.publisher_name,
                    "abstract": ds.abstract,
                    "publications_count": ds.publications_count,
                    "data_uses_count": ds.durs_count,
                    "gateway_url": ds.gateway_url,
                }
                for ds in results.datasets
            ],
            "data_uses": [
                {
                    "id": dur.id,
                    "project_title": dur.project_title,
                    "organisation": dur.organisation_name,
                    "sector": dur.organisation_sector.value if dur.organisation_sector else None,
                    "lay_summary": dur.lay_summary,
                    "approval_date": dur.latest_approval_date,
                    "gateway_url": dur.gateway_url,
                }
                for dur in results.data_uses
            ],
            "publications": [
                {
                    "id": pub.id,
                    "title": pub.paper_title,
                    "authors": pub.authors,
                    "year": pub.year_of_publication,
                    "doi": pub.paper_doi,
                    "gateway_url": pub.gateway_url,
                }
                for pub in results.publications
            ],
            "total_count": results.total_results,
        }
        return json.dumps(data, indent=2)


def quick_search(query: str, limit: int = 10) -> List[Dataset]:
    """
    Convenience function for quick dataset searches.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        List of Dataset objects
    """
    searcher = DatasetSearcher()
    result = searcher.search(query, per_page=limit)
    return result.results.datasets
