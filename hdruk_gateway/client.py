"""
HDR UK Gateway API Client.

A Python client for interacting with the Health Data Research UK Innovation Gateway.
Based on patterns from the official gateway-web Next.js application.
"""

import logging
import time
from typing import Optional, Dict, Any, List, Union, Generator
from urllib.parse import urljoin, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import (
    Dataset,
    DatasetMetadata,
    DataUseRegister,
    Publication,
    Tool,
    Collection,
    Team,
    Publisher,
    SearchResult,
    SearchFilters,
    PaginatedResponse,
    ResourceType,
    DatasetStatus,
    AccessType,
    OrganisationSector,
)
from .exceptions import (
    GatewayAPIError,
    GatewayAuthError,
    GatewayNotFoundError,
    GatewayRateLimitError,
    GatewayServerError,
    GatewayTimeoutError,
    GatewayConnectionError,
)

logger = logging.getLogger(__name__)


class GatewayClient:
    """
    Client for the HDR UK Innovation Gateway API.

    Provides methods to search and retrieve datasets, data use registers,
    publications, tools, collections, and teams.

    Example:
        >>> client = GatewayClient()
        >>> datasets = client.search_datasets("diabetes")
        >>> for ds in datasets:
        ...     print(f"{ds.title} - {ds.publisher_name}")
    """

    # API endpoints
    DEFAULT_BASE_URL = "https://api.www.healthdatagateway.org/api/v1"
    WEB_BASE_URL = "https://www.healthdatagateway.org"

    # Request settings
    DEFAULT_TIMEOUT = 30
    DEFAULT_PER_PAGE = 25
    MIN_SEARCH_LENGTH = 3  # Minimum query length (from gateway-web)

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        session: Optional[requests.Session] = None,
    ):
        """
        Initialize the Gateway client.

        Args:
            base_url: API base URL (defaults to production Gateway API)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff multiplier for retries
            session: Optional custom requests session
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries

        # Setup session with retry logic
        self.session = session or requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Set default headers
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "uk-health-data-assistant/1.0",
        })

    def _build_url(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Build full URL with query parameters."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        if params:
            # Filter out None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                url = f"{url}?{urlencode(filtered_params, doseq=True)}"
        return url

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Gateway API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body for POST/PUT requests

        Returns:
            Parsed JSON response

        Raises:
            GatewayAPIError: On API errors
        """
        url = self._build_url(endpoint, params if method == "GET" else None)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params if method != "GET" else None,
                json=json_data,
                timeout=self.timeout,
                **kwargs,
            )

            # Handle different status codes
            if response.status_code == 401:
                raise GatewayAuthError(request_url=url)
            elif response.status_code == 404:
                raise GatewayNotFoundError("Resource", endpoint, request_url=url)
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise GatewayRateLimitError(
                    retry_after=int(retry_after) if retry_after else None,
                    request_url=url,
                )
            elif response.status_code >= 500:
                raise GatewayServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                    request_url=url,
                )
            elif response.status_code >= 400:
                raise GatewayAPIError(
                    f"Request failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.text else {},
                    request_url=url,
                )

            # Parse response based on content type
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            elif "text/csv" in content_type:
                return {"csv_data": response.text, "content_type": "csv"}
            else:
                return {"data": response.text, "content_type": content_type}

        except requests.exceptions.Timeout:
            raise GatewayTimeoutError(self.timeout, request_url=url)
        except requests.exceptions.ConnectionError as e:
            raise GatewayConnectionError(str(e), request_url=url)
        except requests.exceptions.RequestException as e:
            raise GatewayAPIError(str(e), request_url=url)

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)

    def _post(
        self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, params=params, json_data=data)

    # =========================================================================
    # Dataset Methods
    # =========================================================================

    def _parse_dataset(self, data: Dict[str, Any]) -> Dataset:
        """Parse raw dataset data into Dataset model."""
        # Extract nested metadata
        metadata = None
        raw_metadata = data.get("latest_metadata", {}).get("metadata", {}).get("metadata", {})
        if not raw_metadata:
            raw_metadata = data.get("metadata", {})

        if raw_metadata:
            publisher_data = raw_metadata.get("publisher", {})
            publisher = Publisher(
                id=publisher_data.get("id"),
                name=publisher_data.get("name", ""),
                logo=publisher_data.get("logo"),
                description=publisher_data.get("description"),
                contact_point=publisher_data.get("contactPoint"),
            ) if publisher_data else None

            metadata = DatasetMetadata(
                identifier=raw_metadata.get("identifier"),
                version=raw_metadata.get("version"),
                issued=raw_metadata.get("issued"),
                modified=raw_metadata.get("modified"),
                title=raw_metadata.get("title", data.get("name", "")),
                abstract=raw_metadata.get("abstract"),
                description=raw_metadata.get("description"),
                keywords=raw_metadata.get("keywords", []),
                publisher=publisher,
                spatial=raw_metadata.get("spatial"),
                access_rights=raw_metadata.get("accessRights"),
            )

        # Parse team if present
        team = None
        team_data = data.get("team")
        if team_data:
            team = Team(
                id=team_data.get("id", ""),
                name=team_data.get("name", ""),
                pid=team_data.get("pid"),
            )

        return Dataset(
            id=data.get("id", ""),
            pid=data.get("pid"),
            status=DatasetStatus(data.get("status", "active")),
            metadata=metadata,
            team_id=data.get("team_id"),
            team=team,
            user_id=data.get("user_id"),
            durs_count=data.get("durs_count", 0),
            publications_count=data.get("publications_count", 0),
            tools_count=data.get("tools_count", 0),
            collections_count=data.get("collections_count", 0),
            is_cohort_discovery=data.get("is_cohort_discovery", False),
            versions=data.get("versions", []),
            _raw=data,
        )

    def get_dataset(self, dataset_id: str) -> Dataset:
        """
        Get a single dataset by ID.

        Args:
            dataset_id: Dataset ID or PID

        Returns:
            Dataset object
        """
        response = self._get(f"/datasets/{dataset_id}")
        data = response.get("data", response)
        return self._parse_dataset(data)

    def search_datasets(
        self,
        query: str = "",
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> List[Dataset]:
        """
        Search for datasets.

        Args:
            query: Search query string
            filters: Optional search filters
            page: Page number
            per_page: Results per page

        Returns:
            List of Dataset objects
        """
        # Enforce minimum search length
        if query and len(query) < self.MIN_SEARCH_LENGTH:
            logger.warning(f"Query too short (min {self.MIN_SEARCH_LENGTH} chars): {query}")
            return []

        params = {
            "search": query,
            "type": "dataset",
            "page": page,
            "perPage": per_page,
        }

        if filters:
            params.update(filters.to_dict())

        try:
            response = self._post("/search", data=params)
            data = response.get("data", [])
            return [self._parse_dataset(d) for d in data if d]
        except GatewayAPIError as e:
            logger.error(f"Dataset search failed: {e}")
            return []

    def list_datasets(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PaginatedResponse:
        """
        List all datasets with pagination.

        Args:
            page: Page number
            per_page: Results per page

        Returns:
            Paginated response with Dataset objects
        """
        response = self._get("/datasets", params={"page": page, "perPage": per_page})
        paginated = PaginatedResponse.from_api_response(response)
        paginated.data = [self._parse_dataset(d) for d in paginated.data]
        return paginated

    def iter_datasets(self, per_page: int = 100) -> Generator[Dataset, None, None]:
        """
        Iterate over all datasets.

        Yields datasets one by one, handling pagination automatically.

        Args:
            per_page: Number of results per API call

        Yields:
            Dataset objects
        """
        page = 1
        while True:
            response = self.list_datasets(page=page, per_page=per_page)
            for dataset in response.data:
                yield dataset

            if not response.has_more:
                break
            page += 1

    # =========================================================================
    # Data Use Register Methods
    # =========================================================================

    def _parse_data_use(self, data: Dict[str, Any]) -> DataUseRegister:
        """Parse raw data use data into DataUseRegister model."""
        sector = data.get("organisation_sector")
        if sector:
            try:
                sector = OrganisationSector(sector)
            except ValueError:
                sector = OrganisationSector.OTHER

        access_type = data.get("access_type")
        if access_type:
            try:
                access_type = AccessType(access_type)
            except ValueError:
                access_type = None

        team = None
        team_data = data.get("team")
        if team_data:
            team = Team(
                id=team_data.get("id", ""),
                name=team_data.get("name", ""),
            )

        return DataUseRegister(
            id=data.get("id", ""),
            project_id_text=data.get("project_id_text"),
            project_title=data.get("project_title", data.get("projectTitle", "")),
            organisation_id=data.get("organisation_id"),
            organisation_name=data.get("organisation_name", data.get("organisationName")),
            organisation_sector=sector,
            project_start_date=data.get("project_start_date", data.get("projectStartDate")),
            project_end_date=data.get("project_end_date", data.get("projectEndDate")),
            access_date=data.get("access_date", data.get("accessDate")),
            latest_approval_date=data.get("latest_approval_date", data.get("latestApprovalDate")),
            lay_summary=data.get("lay_summary", data.get("laySummary")),
            technical_summary=data.get("technical_summary", data.get("technicalSummary")),
            public_benefit_statement=data.get("public_benefit_statement", data.get("publicBenefitStatement")),
            datasets=data.get("datasets", data.get("datasetTitles", [])),
            keywords=data.get("keywords", []),
            access_type=access_type,
            team=team,
            status=data.get("status"),
            _raw=data,
        )

    def get_data_use(self, dur_id: str) -> DataUseRegister:
        """Get a single data use register entry by ID."""
        response = self._get(f"/dur/{dur_id}")
        data = response.get("data", response)
        return self._parse_data_use(data)

    def search_data_uses(
        self,
        query: str = "",
        publisher: Optional[str] = None,
        organisation_sector: Optional[List[OrganisationSector]] = None,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> List[DataUseRegister]:
        """
        Search for data use register entries.

        Args:
            query: Search query string
            publisher: Filter by data publisher/custodian
            organisation_sector: Filter by organisation sector
            page: Page number
            per_page: Results per page

        Returns:
            List of DataUseRegister objects
        """
        params = {
            "search": query,
            "type": "dataUseRegister",
            "page": page,
            "perPage": per_page,
        }

        if publisher:
            params["publisher"] = publisher

        if organisation_sector:
            params["organisationSector"] = [s.value for s in organisation_sector]

        try:
            response = self._post("/search", data=params)
            data = response.get("data", [])
            return [self._parse_data_use(d) for d in data if d]
        except GatewayAPIError as e:
            logger.error(f"Data use search failed: {e}")
            return []

    def export_data_uses(self) -> List[DataUseRegister]:
        """
        Export all data use register entries.

        Returns:
            List of all DataUseRegister objects
        """
        try:
            response = self._get("/dur/export")
            data = response.get("data", [])
            if isinstance(data, list):
                return [self._parse_data_use(d) for d in data if d]
            return []
        except GatewayAPIError as e:
            logger.error(f"Data use export failed: {e}")
            return []

    # =========================================================================
    # Publication Methods
    # =========================================================================

    def _parse_publication(self, data: Dict[str, Any]) -> Publication:
        """Parse raw publication data into Publication model."""
        return Publication(
            id=data.get("id", ""),
            paper_title=data.get("paper_title", data.get("paperTitle", "")),
            authors=data.get("authors"),
            year_of_publication=data.get("year_of_publication", data.get("yearOfPublication")),
            journal_name=data.get("journal_name", data.get("journalName")),
            paper_doi=data.get("paper_doi", data.get("paperDoi")),
            publication_type=data.get("publication_type", data.get("publicationType")),
            abstract=data.get("abstract"),
            full_text_url=data.get("full_text_url"),
            url=data.get("url"),
            status=data.get("status"),
            _raw=data,
        )

    def get_publication(self, pub_id: str) -> Publication:
        """Get a single publication by ID."""
        response = self._get(f"/publications/{pub_id}")
        data = response.get("data", response)
        return self._parse_publication(data)

    def search_publications(
        self,
        query: str = "",
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> List[Publication]:
        """Search for publications."""
        params = {
            "search": query,
            "type": "publication",
            "page": page,
            "perPage": per_page,
        }

        try:
            response = self._post("/search", data=params)
            data = response.get("data", [])
            return [self._parse_publication(p) for p in data if p]
        except GatewayAPIError as e:
            logger.error(f"Publication search failed: {e}")
            return []

    # =========================================================================
    # Tool Methods
    # =========================================================================

    def _parse_tool(self, data: Dict[str, Any]) -> Tool:
        """Parse raw tool data into Tool model."""
        team = None
        team_data = data.get("team")
        if team_data:
            team = Team(id=team_data.get("id", ""), name=team_data.get("name", ""))

        return Tool(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            url=data.get("url"),
            license=data.get("license"),
            tech_stack=data.get("tech_stack"),
            programming_languages=data.get("programming_languages", []),
            tags=data.get("tags", []),
            team=team,
            enabled=data.get("enabled", True),
            _raw=data,
        )

    def get_tool(self, tool_id: str) -> Tool:
        """Get a single tool by ID."""
        response = self._get(f"/tools/{tool_id}")
        data = response.get("data", response)
        return self._parse_tool(data)

    def search_tools(
        self,
        query: str = "",
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> List[Tool]:
        """Search for tools."""
        params = {
            "search": query,
            "type": "tool",
            "page": page,
            "perPage": per_page,
        }

        try:
            response = self._post("/search", data=params)
            data = response.get("data", [])
            return [self._parse_tool(t) for t in data if t]
        except GatewayAPIError as e:
            logger.error(f"Tool search failed: {e}")
            return []

    # =========================================================================
    # Collection Methods
    # =========================================================================

    def _parse_collection(self, data: Dict[str, Any]) -> Collection:
        """Parse raw collection data into Collection model."""
        team = None
        team_data = data.get("team")
        if team_data:
            team = Team(id=team_data.get("id", ""), name=team_data.get("name", ""))

        return Collection(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            keywords=data.get("keywords", []),
            enabled=data.get("enabled", True),
            status=data.get("status"),
            public=data.get("public", True),
            team=team,
            _raw=data,
        )

    def get_collection(self, collection_id: str) -> Collection:
        """Get a single collection by ID."""
        response = self._get(f"/collections/{collection_id}")
        data = response.get("data", response)
        return self._parse_collection(data)

    def search_collections(
        self,
        query: str = "",
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> List[Collection]:
        """Search for collections."""
        params = {
            "search": query,
            "type": "collection",
            "page": page,
            "perPage": per_page,
        }

        try:
            response = self._post("/search", data=params)
            data = response.get("data", [])
            return [self._parse_collection(c) for c in data if c]
        except GatewayAPIError as e:
            logger.error(f"Collection search failed: {e}")
            return []

    # =========================================================================
    # Team/Publisher Methods
    # =========================================================================

    def _parse_team(self, data: Dict[str, Any]) -> Team:
        """Parse raw team data into Team model."""
        return Team(
            id=data.get("id", ""),
            pid=data.get("pid"),
            name=data.get("name", ""),
            introduction=data.get("introduction"),
            contact_point=data.get("contact_point"),
            team_logo=data.get("team_logo"),
            url=data.get("url"),
            member_of=data.get("member_of"),
            enabled=data.get("enabled", True),
            allows_messaging=data.get("allows_messaging", False),
            is_dar=data.get("is_dar", False),
            _raw=data,
        )

    def get_team(self, team_id: str) -> Team:
        """Get a team/publisher by ID."""
        response = self._get(f"/teams/{team_id}")
        data = response.get("data", response)
        return self._parse_team(data)

    def list_publishers(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> List[Team]:
        """List all data publishers/custodians."""
        try:
            response = self._get("/publishers", params={"page": page, "perPage": per_page})
            data = response.get("data", [])
            return [self._parse_team(t) for t in data if t]
        except GatewayAPIError as e:
            logger.error(f"Publisher list failed: {e}")
            return []

    # =========================================================================
    # Unified Search
    # =========================================================================

    def search(
        self,
        query: str = "",
        resource_types: Optional[List[ResourceType]] = None,
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> SearchResult:
        """
        Unified search across all resource types.

        Args:
            query: Search query string
            resource_types: List of resource types to search (default: all)
            filters: Optional search filters
            page: Page number
            per_page: Results per page

        Returns:
            SearchResult containing all matching resources
        """
        if resource_types is None:
            resource_types = [
                ResourceType.DATASET,
                ResourceType.DATA_USE_REGISTER,
                ResourceType.PUBLICATION,
                ResourceType.TOOL,
                ResourceType.COLLECTION,
            ]

        result = SearchResult()

        for resource_type in resource_types:
            try:
                if resource_type == ResourceType.DATASET:
                    result.datasets = self.search_datasets(query, filters, page, per_page)
                elif resource_type == ResourceType.DATA_USE_REGISTER:
                    result.data_uses = self.search_data_uses(query, page=page, per_page=per_page)
                elif resource_type == ResourceType.PUBLICATION:
                    result.publications = self.search_publications(query, page, per_page)
                elif resource_type == ResourceType.TOOL:
                    result.tools = self.search_tools(query, page, per_page)
                elif resource_type == ResourceType.COLLECTION:
                    result.collections = self.search_collections(query, page, per_page)
            except GatewayAPIError as e:
                logger.warning(f"Search failed for {resource_type.value}: {e}")

        return result

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def get_web_url(self, resource_type: str, resource_id: str) -> str:
        """Generate a web URL for a resource."""
        type_map = {
            "dataset": "dataset",
            "datause": "datause",
            "dur": "datause",
            "publication": "publication",
            "tool": "tool",
            "collection": "collection",
            "team": "data-custodian",
            "publisher": "data-custodian",
        }
        path = type_map.get(resource_type.lower(), resource_type)
        return f"{self.WEB_BASE_URL}/{path}/{resource_id}"

    def health_check(self) -> bool:
        """Check if the Gateway API is accessible."""
        try:
            self._get("/health")
            return True
        except GatewayAPIError:
            # Try a simple search as fallback
            try:
                self.search_datasets("test", per_page=1)
                return True
            except GatewayAPIError:
                return False
