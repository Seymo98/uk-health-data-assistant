"""
Data models for HDR UK Gateway API.

Based on TypeScript interfaces from gateway-web/src/interfaces/
Converted to Python dataclasses with Pydantic validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class ResourceType(str, Enum):
    """Resource types available in the Gateway."""
    DATASET = "dataset"
    DATA_USE_REGISTER = "dataUseRegister"
    PUBLICATION = "publication"
    TOOL = "tool"
    COLLECTION = "collection"
    DATA_PROVIDER = "dataProvider"


class DatasetStatus(str, Enum):
    """Dataset publication status."""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class AccessType(str, Enum):
    """Data access types."""
    OPEN = "open"
    SAFEGUARDED = "safeguarded"
    CONTROLLED = "controlled"


class OrganisationSector(str, Enum):
    """Organisation sector types."""
    NHS = "NHS"
    ACADEMIA = "Academia"
    GOVERNMENT = "Government"
    CHARITY = "Charity"
    COMMERCIAL = "Commercial"
    OTHER = "Other"


@dataclass
class Publisher:
    """Data publisher/custodian information."""
    id: Optional[str] = None
    name: str = ""
    logo: Optional[str] = None
    description: Optional[str] = None
    contact_point: Optional[str] = None
    member_of: Optional[str] = None  # Parent organisation


@dataclass
class DatasetMetadata:
    """
    Dataset metadata following HDR UK schema.

    Based on latest_metadata.metadata.metadata structure from Gateway.
    """
    # Core identifiers
    identifier: Optional[str] = None
    version: Optional[str] = None
    issued: Optional[str] = None
    modified: Optional[str] = None

    # Summary
    title: str = ""
    abstract: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    # Publisher
    publisher: Optional[Publisher] = None

    # Coverage
    spatial: Optional[str] = None  # Geographic coverage
    temporal_coverage_start: Optional[str] = None
    temporal_coverage_end: Optional[str] = None
    population_size: Optional[int] = None

    # Access
    access_rights: Optional[str] = None
    access_request_cost: Optional[str] = None
    delivery_lead_time: Optional[str] = None
    access_environment: Optional[str] = None  # TRE details

    # Technical
    conformsTo: Optional[str] = None  # Schema standard
    language: Optional[str] = None
    format: List[str] = field(default_factory=list)

    # Linkages
    linked_datasets: List[str] = field(default_factory=list)
    derivations: List[str] = field(default_factory=list)


@dataclass
class Dataset:
    """
    Dataset resource from HDR UK Gateway.

    Mirrors the Dataset interface from gateway-web.
    """
    id: str
    pid: Optional[str] = None  # Persistent identifier

    # Status
    status: DatasetStatus = DatasetStatus.ACTIVE

    # Metadata (nested structure like Gateway)
    metadata: Optional[DatasetMetadata] = None

    # Relationships
    team_id: Optional[str] = None
    team: Optional['Team'] = None
    user_id: Optional[str] = None

    # Counts
    durs_count: int = 0
    publications_count: int = 0
    tools_count: int = 0
    collections_count: int = 0

    # Related resources
    publications: List['Publication'] = field(default_factory=list)

    # Flags
    is_cohort_discovery: bool = False

    # Versions
    versions: List[str] = field(default_factory=list)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Raw data for extension
    _raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def title(self) -> str:
        """Extract title from nested metadata."""
        if self.metadata and self.metadata.title:
            return self.metadata.title
        return self._raw.get("name", "Untitled")

    @property
    def publisher_name(self) -> str:
        """Extract publisher name."""
        if self.metadata and self.metadata.publisher:
            return self.metadata.publisher.name
        if self.team:
            return self.team.name
        return "Unknown"

    @property
    def abstract(self) -> str:
        """Extract abstract/description."""
        if self.metadata:
            return self.metadata.abstract or self.metadata.description or ""
        return ""

    @property
    def gateway_url(self) -> str:
        """Generate Gateway URL for this dataset."""
        return f"https://www.healthdatagateway.org/dataset/{self.id}"


@dataclass
class DataUseRegister:
    """
    Data Use Register entry (approved research project).

    Mirrors the DataUse interface from gateway-web.
    """
    id: str

    # Project identification
    project_id_text: Optional[str] = None
    project_title: str = ""

    # Organisation
    organisation_id: Optional[str] = None
    organisation_name: Optional[str] = None
    organisation_sector: Optional[OrganisationSector] = None

    # Dates
    project_start_date: Optional[str] = None
    project_end_date: Optional[str] = None
    access_date: Optional[str] = None
    latest_approval_date: Optional[str] = None

    # Descriptions
    lay_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    public_benefit_statement: Optional[str] = None

    # Data specifics
    datasets: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    data_sensitivity_level: Optional[str] = None

    # Legal basis
    legal_basis_for_data_article6: Optional[str] = None
    legal_basis_for_data_article9: Optional[str] = None
    duty_of_confidentiality: Optional[str] = None
    national_data_optout: Optional[str] = None

    # Access details
    access_type: Optional[AccessType] = None
    request_category_type: Optional[str] = None
    request_frequency: Optional[str] = None
    accredited_researcher_status: Optional[str] = None
    sublicence_arrangements: Optional[str] = None

    # Relationships
    team: Optional['Team'] = None
    user_id: Optional[str] = None
    status: Optional[str] = None

    # Raw data
    _raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def gateway_url(self) -> str:
        """Generate Gateway URL for this data use."""
        return f"https://www.healthdatagateway.org/datause/{self.id}"


@dataclass
class Publication:
    """
    Publication linked to datasets.

    Mirrors the Publication interface from gateway-web.
    """
    id: str

    # Citation info
    paper_title: str = ""
    authors: Optional[str] = None
    year_of_publication: Optional[int] = None
    journal_name: Optional[str] = None
    paper_doi: Optional[str] = None

    # Details
    publication_type: Optional[str] = None
    abstract: Optional[str] = None
    full_text_url: Optional[str] = None
    url: Optional[str] = None

    # Status
    status: Optional[str] = None

    # Relationships
    dataset_versions: List[str] = field(default_factory=list)

    _raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def gateway_url(self) -> str:
        """Generate Gateway URL for this publication."""
        return f"https://www.healthdatagateway.org/publication/{self.id}"


@dataclass
class Tool:
    """
    Tool/software linked to datasets.

    Mirrors the Tool interface from gateway-web.
    """
    id: str
    name: str = ""

    # Details
    description: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None
    tech_stack: Optional[str] = None

    # Categorization
    category_id: Optional[str] = None
    programming_languages: List[str] = field(default_factory=list)
    type_category: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Relationships
    team_id: Optional[str] = None
    team: Optional['Team'] = None
    user_id: Optional[str] = None
    associated_authors: Optional[str] = None

    # Related
    publications: List[Publication] = field(default_factory=list)
    collections: List['Collection'] = field(default_factory=list)
    dataset_versions: List[str] = field(default_factory=list)

    # Status
    enabled: bool = True

    _raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def gateway_url(self) -> str:
        """Generate Gateway URL for this tool."""
        return f"https://www.healthdatagateway.org/tool/{self.id}"


@dataclass
class Collection:
    """
    Curated collection of resources.

    Mirrors the Collection interface from gateway-web.
    """
    id: str
    name: str = ""

    # Details
    description: Optional[str] = None
    image_link: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    # Status
    enabled: bool = True
    status: Optional[str] = None
    public: bool = True

    # Relationships
    team_id: Optional[str] = None
    team: Optional['Team'] = None
    user_id: Optional[str] = None
    users: List[Dict] = field(default_factory=list)
    collaborators: List[Dict] = field(default_factory=list)

    # Contained resources
    datasets: List[Dataset] = field(default_factory=list)
    dataset_versions: List[str] = field(default_factory=list)
    publications: List[Publication] = field(default_factory=list)
    tools: List[Tool] = field(default_factory=list)
    dur: List[DataUseRegister] = field(default_factory=list)
    applications: List[Dict] = field(default_factory=list)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    _raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def gateway_url(self) -> str:
        """Generate Gateway URL for this collection."""
        return f"https://www.healthdatagateway.org/collection/{self.id}"


@dataclass
class Team:
    """
    Team/organisation in the Gateway.

    Mirrors the Team interface from gateway-web.
    """
    id: str
    pid: Optional[str] = None
    name: str = ""

    # Details
    introduction: Optional[str] = None
    contact_point: Optional[str] = None
    team_logo: Optional[str] = None
    url: Optional[str] = None
    service: Optional[str] = None

    # Hierarchy
    member_of: Optional[str] = None  # Parent team

    # Capabilities
    enabled: bool = True
    allows_messaging: bool = False
    workflow_enabled: bool = False
    access_requests_management: bool = False
    uses_5_safes: bool = False
    is_question_bank: bool = False
    is_dar: bool = False
    is_admin: bool = False
    has_published_dar_template: bool = False

    # DAR customization
    dar_modal_header: Optional[str] = None
    dar_modal_content: Optional[str] = None
    dar_modal_footer: Optional[str] = None

    # Relationships
    users: List[Dict] = field(default_factory=list)
    notifications: List[Dict] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    # Timestamps
    updated_at: Optional[datetime] = None

    _raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def gateway_url(self) -> str:
        """Generate Gateway URL for this team."""
        return f"https://www.healthdatagateway.org/data-custodian/{self.id}"


@dataclass
class SearchFilters:
    """
    Search filters for Gateway queries.

    Based on SearchQueryParams interface from gateway-web.
    Supports 42+ filter categories.
    """
    # Text search
    query: str = ""

    # Resource type
    resource_type: Optional[ResourceType] = None

    # Geographic
    geographic_coverage: List[str] = field(default_factory=list)

    # Publisher/custodian
    publisher: List[str] = field(default_factory=list)

    # Data characteristics
    data_use_limitation: List[str] = field(default_factory=list)
    data_use_requirements: List[str] = field(default_factory=list)

    # Access
    access_service: List[str] = field(default_factory=list)

    # Temporal
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None

    # Sector (for data use registers)
    organisation_sector: List[OrganisationSector] = field(default_factory=list)

    # Keywords/tags
    keywords: List[str] = field(default_factory=list)

    # Pagination
    page: int = 1
    per_page: int = 25

    # Sorting
    sort_by: str = "relevance"
    sort_order: str = "desc"

    # Additional filters (raw)
    extra_filters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API query parameters."""
        params = {}

        if self.query:
            params["search"] = self.query

        if self.resource_type:
            params["type"] = self.resource_type.value

        if self.geographic_coverage:
            params["geographicCoverage"] = self.geographic_coverage

        if self.publisher:
            params["publisher"] = self.publisher

        if self.organisation_sector:
            params["organisationSector"] = [s.value for s in self.organisation_sector]

        if self.keywords:
            params["keywords"] = self.keywords

        # Pagination
        params["page"] = self.page
        params["perPage"] = self.per_page

        # Sorting
        params["sortBy"] = self.sort_by
        params["sortOrder"] = self.sort_order

        # Merge extra filters
        params.update(self.extra_filters)

        return params


@dataclass
class PaginatedResponse:
    """
    Paginated API response.

    Follows Laravel pagination format used by Gateway.
    """
    data: List[Any] = field(default_factory=list)

    # Pagination info (converted from snake_case)
    current_page: int = 1
    per_page: int = 25
    total: int = 0
    last_page: int = 1

    # Links
    first_page_url: Optional[str] = None
    last_page_url: Optional[str] = None
    next_page_url: Optional[str] = None
    prev_page_url: Optional[str] = None

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.current_page < self.last_page

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'PaginatedResponse':
        """Create from raw API response with snake_case to camelCase conversion."""
        return cls(
            data=response.get("data", []),
            current_page=response.get("current_page", response.get("currentPage", 1)),
            per_page=response.get("per_page", response.get("perPage", 25)),
            total=response.get("total", 0),
            last_page=response.get("last_page", response.get("lastPage", 1)),
            first_page_url=response.get("first_page_url"),
            last_page_url=response.get("last_page_url"),
            next_page_url=response.get("next_page_url"),
            prev_page_url=response.get("prev_page_url"),
        )


@dataclass
class SearchResult:
    """
    Search result combining multiple resource types.
    """
    datasets: List[Dataset] = field(default_factory=list)
    data_uses: List[DataUseRegister] = field(default_factory=list)
    publications: List[Publication] = field(default_factory=list)
    tools: List[Tool] = field(default_factory=list)
    collections: List[Collection] = field(default_factory=list)

    # Aggregations/facets
    filters: Dict[str, List[Dict]] = field(default_factory=dict)

    # Pagination
    pagination: Optional[PaginatedResponse] = None

    @property
    def total_results(self) -> int:
        """Total number of results across all types."""
        return (
            len(self.datasets) +
            len(self.data_uses) +
            len(self.publications) +
            len(self.tools) +
            len(self.collections)
        )
