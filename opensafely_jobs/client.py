"""
OpenSAFELY Jobs Client.

A client for accessing public data from jobs.opensafely.org via HTML scraping.
OpenSAFELY publishes machine-readable logs of every query run against NHS data.
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Generator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from .models import (
    Organization,
    Project,
    Workspace,
    JobRequest,
    Job,
    Backend,
    JobStatus,
    ProjectStatus,
    DashboardStats,
)

logger = logging.getLogger(__name__)


class OpenSAFELYJobsError(Exception):
    """Base exception for OpenSAFELY Jobs client errors."""
    pass


class OpenSAFELYConnectionError(OpenSAFELYJobsError):
    """Connection error when accessing jobs.opensafely.org."""
    pass


class OpenSAFELYParseError(OpenSAFELYJobsError):
    """Error parsing HTML content from jobs.opensafely.org."""
    pass


class OpenSAFELYJobsClient:
    """
    Client for accessing public data from jobs.opensafely.org.

    OpenSAFELY provides full transparency through their jobs platform,
    logging all activity that uses real patient data. This client
    extracts that publicly available information.

    Example:
        >>> client = OpenSAFELYJobsClient()
        >>> orgs = client.get_organizations()
        >>> for org in orgs:
        ...     print(f"{org.name}: {org.project_count} projects")
    """

    BASE_URL = "https://jobs.opensafely.org"
    DEFAULT_TIMEOUT = 30
    USER_AGENT = "UKHealthDataAssistant/1.0 (OpenSAFELY Dashboard)"

    # Known backends
    BACKENDS = {
        "tpp": Backend(name="TPP", slug="tpp", display_name="TPP (England)"),
        "emis": Backend(name="EMIS", slug="emis", display_name="EMIS (England)"),
        "databuilder": Backend(name="DataBuilder", slug="databuilder", display_name="DataBuilder"),
    }

    # Demo data based on real OpenSAFELY organizations (used as fallback)
    DEMO_ORGANIZATIONS = [
        Organization(name="OpenSAFELY", slug="opensafely", project_count=45),
        Organization(name="Bennett Institute", slug="bennett-institute", project_count=38),
        Organization(name="University of Oxford", slug="university-of-oxford", project_count=28),
        Organization(name="London School of Hygiene & Tropical Medicine", slug="lshtm", project_count=22),
        Organization(name="University of Bristol", slug="university-of-bristol", project_count=18),
        Organization(name="King's College London", slug="kings-college-london", project_count=15),
        Organization(name="University of Cambridge", slug="university-of-cambridge", project_count=14),
        Organization(name="Imperial College London", slug="imperial-college-london", project_count=12),
        Organization(name="University of Edinburgh", slug="university-of-edinburgh", project_count=11),
        Organization(name="University of Manchester", slug="university-of-manchester", project_count=9),
        Organization(name="NHS England", slug="nhs-england", project_count=8),
        Organization(name="NIHR", slug="nihr", project_count=7),
        Organization(name="UK Health Security Agency", slug="ukhsa", project_count=6),
        Organization(name="University College London", slug="ucl", project_count=5),
    ]

    DEMO_JOB_REQUESTS = [
        JobRequest(identifier="jr-001", sha="abc123", status=JobStatus.SUCCEEDED,
                   workspace_name="covid-vaccine-effectiveness", project_name="opensafely",
                   created_at=datetime.now() - timedelta(minutes=15)),
        JobRequest(identifier="jr-002", sha="def456", status=JobStatus.SUCCEEDED,
                   workspace_name="long-covid-risk-factors", project_name="bennett-institute",
                   created_at=datetime.now() - timedelta(minutes=45)),
        JobRequest(identifier="jr-003", sha="ghi789", status=JobStatus.RUNNING,
                   workspace_name="antibiotic-prescribing", project_name="university-of-oxford",
                   created_at=datetime.now() - timedelta(hours=1)),
        JobRequest(identifier="jr-004", sha="jkl012", status=JobStatus.SUCCEEDED,
                   workspace_name="diabetes-outcomes", project_name="lshtm",
                   created_at=datetime.now() - timedelta(hours=2)),
        JobRequest(identifier="jr-005", sha="mno345", status=JobStatus.FAILED,
                   workspace_name="mental-health-trends", project_name="kings-college-london",
                   created_at=datetime.now() - timedelta(hours=3)),
        JobRequest(identifier="jr-006", sha="pqr678", status=JobStatus.SUCCEEDED,
                   workspace_name="cardiovascular-risk", project_name="imperial-college-london",
                   created_at=datetime.now() - timedelta(hours=4)),
        JobRequest(identifier="jr-007", sha="stu901", status=JobStatus.SUCCEEDED,
                   workspace_name="respiratory-infections", project_name="university-of-bristol",
                   created_at=datetime.now() - timedelta(hours=5)),
        JobRequest(identifier="jr-008", sha="vwx234", status=JobStatus.PENDING,
                   workspace_name="cancer-screening", project_name="university-of-cambridge",
                   created_at=datetime.now() - timedelta(hours=6)),
        JobRequest(identifier="jr-009", sha="yza567", status=JobStatus.SUCCEEDED,
                   workspace_name="vaccine-safety-monitoring", project_name="ukhsa",
                   created_at=datetime.now() - timedelta(hours=8)),
        JobRequest(identifier="jr-010", sha="bcd890", status=JobStatus.SUCCEEDED,
                   workspace_name="primary-care-workload", project_name="nhs-england",
                   created_at=datetime.now() - timedelta(hours=12)),
    ]

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        use_demo_fallback: bool = True,
        backoff_factor: float = 0.5,
        session: Optional[requests.Session] = None,
    ):
        """
        Initialize the OpenSAFELY Jobs client.

        Args:
            base_url: Base URL for jobs.opensafely.org
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            use_demo_fallback: Use demo data when live API is unreachable
            backoff_factor: Backoff multiplier between retries
            session: Optional custom requests session
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.use_demo_fallback = use_demo_fallback
        self._using_demo_data = False

        self.session = session or requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

        # Cache for parsed data
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes

    def _get_page(self, path: str) -> BeautifulSoup:
        """Fetch and parse an HTML page."""
        url = urljoin(self.base_url, path)
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise OpenSAFELYConnectionError(f"Failed to fetch {url}: {e}")

    def _parse_datetime(self, text: str) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if not text:
            return None

        # Try various formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d",
            "%d %b %Y %H:%M",
            "%d %b %Y",
            "%B %d, %Y",
        ]

        text = text.strip()
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

        # Try relative time parsing (e.g., "2 hours ago")
        relative_patterns = [
            (r"(\d+)\s*second", 1),
            (r"(\d+)\s*minute", 60),
            (r"(\d+)\s*hour", 3600),
            (r"(\d+)\s*day", 86400),
            (r"(\d+)\s*week", 604800),
        ]

        for pattern, multiplier in relative_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                delta = int(match.group(1)) * multiplier
                return datetime.now() - timedelta(seconds=delta)

        return None

    def _parse_count(self, text: str) -> int:
        """Extract numeric count from text."""
        if not text:
            return 0
        match = re.search(r"(\d+)", text.replace(",", ""))
        return int(match.group(1)) if match else 0

    def get_organizations(self, use_cache: bool = True) -> List[Organization]:
        """
        Get list of all organizations using OpenSAFELY.

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            List of Organization objects
        """
        cache_key = "organizations"
        if use_cache and cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_data

        try:
            soup = self._get_page("/organisations/")
            organizations = []

            # Find organization list - typically in a list or table format
            org_links = soup.find_all("a", href=re.compile(r"^/[^/]+/$"))

            for link in org_links:
                href = link.get("href", "")
                # Skip non-organization links
                if href in ["/", "/login/", "/logout/", "/organisations/", "/status/"]:
                    continue
                if any(x in href for x in ["static", "admin", "staff", "api"]):
                    continue

                name = link.get_text(strip=True)
                if not name or len(name) < 2:
                    continue

                slug = href.strip("/")

                # Try to find project count nearby
                parent = link.find_parent(["li", "tr", "div"])
                project_count = 0
                if parent:
                    count_text = parent.get_text()
                    count_match = re.search(r"(\d+)\s*project", count_text, re.IGNORECASE)
                    if count_match:
                        project_count = int(count_match.group(1))

                org = Organization(
                    name=name,
                    slug=slug,
                    project_count=project_count,
                )
                organizations.append(org)

            # Deduplicate by slug
            seen_slugs = set()
            unique_orgs = []
            for org in organizations:
                if org.slug not in seen_slugs:
                    seen_slugs.add(org.slug)
                    unique_orgs.append(org)

            self._cache[cache_key] = (time.time(), unique_orgs)
            return unique_orgs

        except Exception as e:
            logger.error(f"Failed to get organizations: {e}")
            if self.use_demo_fallback:
                logger.info("Falling back to demo data for organizations")
                self._using_demo_data = True
                return self.DEMO_ORGANIZATIONS.copy()
            raise OpenSAFELYParseError(f"Failed to parse organizations: {e}")

    def get_organization_details(self, slug: str) -> Organization:
        """
        Get detailed information about an organization.

        Args:
            slug: Organization slug (URL identifier)

        Returns:
            Organization object with projects
        """
        try:
            soup = self._get_page(f"/{slug}/")

            # Parse organization name from title or heading
            name = slug
            h1 = soup.find("h1")
            if h1:
                name = h1.get_text(strip=True)

            # Find projects in the organization
            projects = []
            project_links = soup.find_all("a", href=re.compile(rf"^/{slug}/[^/]+/$"))

            for link in project_links:
                project_slug = link.get("href", "").strip("/").split("/")[-1]
                project_name = link.get_text(strip=True)

                if project_name and project_slug:
                    projects.append(Project(
                        name=project_name,
                        slug=f"{slug}/{project_slug}",
                    ))

            return Organization(
                name=name,
                slug=slug,
                project_count=len(projects),
                projects=projects,
            )

        except OpenSAFELYConnectionError:
            raise
        except Exception as e:
            logger.error(f"Failed to get organization {slug}: {e}")
            raise OpenSAFELYParseError(f"Failed to parse organization {slug}: {e}")

    def get_recent_job_requests(self, limit: int = 50) -> List[JobRequest]:
        """
        Get recent job requests from the homepage.

        Args:
            limit: Maximum number of job requests to return

        Returns:
            List of recent JobRequest objects
        """
        try:
            soup = self._get_page("/")
            job_requests = []

            # Find job request entries - typically in a table or list
            # Look for time elements and links that indicate job requests
            rows = soup.find_all(["tr", "li", "div"], class_=re.compile(r"job|request|row", re.IGNORECASE))

            for row in rows[:limit]:
                try:
                    # Extract job request details
                    links = row.find_all("a")
                    time_elem = row.find("time")

                    identifier = ""
                    workspace_name = ""
                    project_name = ""
                    status = JobStatus.UNKNOWN

                    for link in links:
                        href = link.get("href", "")
                        text = link.get_text(strip=True)

                        if "/job-requests/" in href or "/jobs/" in href:
                            identifier = href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]
                        elif re.match(r"^/[^/]+/[^/]+/$", href):
                            # This is likely a workspace link
                            parts = href.strip("/").split("/")
                            if len(parts) >= 2:
                                project_name = parts[0]
                                workspace_name = parts[-1]

                    # Parse status from class names or text
                    row_classes = " ".join(row.get("class", []))
                    row_text = row.get_text(strip=True).lower()

                    if "success" in row_classes or "succeeded" in row_text:
                        status = JobStatus.SUCCEEDED
                    elif "fail" in row_classes or "failed" in row_text:
                        status = JobStatus.FAILED
                    elif "running" in row_classes or "running" in row_text:
                        status = JobStatus.RUNNING
                    elif "pending" in row_classes or "pending" in row_text:
                        status = JobStatus.PENDING

                    # Parse timestamp
                    created_at = None
                    if time_elem:
                        datetime_attr = time_elem.get("datetime")
                        if datetime_attr:
                            created_at = self._parse_datetime(datetime_attr)
                        else:
                            created_at = self._parse_datetime(time_elem.get_text(strip=True))

                    if identifier or workspace_name:
                        job_requests.append(JobRequest(
                            identifier=identifier,
                            sha="",
                            status=status,
                            created_at=created_at,
                            workspace_name=workspace_name,
                            project_name=project_name,
                        ))

                except Exception as e:
                    logger.debug(f"Failed to parse job request row: {e}")
                    continue

            return job_requests[:limit]

        except OpenSAFELYConnectionError as e:
            if self.use_demo_fallback:
                logger.info("Falling back to demo data for recent jobs")
                self._using_demo_data = True
                return self.DEMO_JOB_REQUESTS[:limit]
            raise
        except Exception as e:
            logger.error(f"Failed to get recent job requests: {e}")
            if self.use_demo_fallback:
                logger.info("Falling back to demo data for recent jobs")
                self._using_demo_data = True
                return self.DEMO_JOB_REQUESTS[:limit]
            raise OpenSAFELYParseError(f"Failed to parse recent job requests: {e}")

    @property
    def is_using_demo_data(self) -> bool:
        """Check if the client is currently using demo/fallback data."""
        return self._using_demo_data

    def get_project_details(self, project_slug: str) -> Project:
        """
        Get detailed information about a project.

        Args:
            project_slug: Full project slug (org/project)

        Returns:
            Project object with workspaces
        """
        try:
            soup = self._get_page(f"/{project_slug}/")

            # Parse project name
            name = project_slug.split("/")[-1]
            h1 = soup.find("h1")
            if h1:
                name = h1.get_text(strip=True)

            # Find status
            status = ProjectStatus.ONGOING
            status_text = soup.find(text=re.compile(r"status", re.IGNORECASE))
            if status_text:
                parent = status_text.find_parent()
                if parent:
                    for ps in ProjectStatus:
                        if ps.value in parent.get_text().lower():
                            status = ps
                            break

            # Find workspaces
            workspaces = []
            workspace_links = soup.find_all("a", href=re.compile(rf"^/{project_slug}/[^/]+/$"))

            for link in workspace_links:
                ws_name = link.get_text(strip=True)
                ws_href = link.get("href", "")

                if ws_name and "workspace" not in ws_href.lower():
                    workspaces.append(Workspace(
                        name=ws_name,
                        project_name=name,
                    ))

            # Find member count
            member_count = 0
            members_text = soup.find(text=re.compile(r"member", re.IGNORECASE))
            if members_text:
                parent = members_text.find_parent()
                if parent:
                    member_count = self._parse_count(parent.get_text())

            # Extract organization names
            org_names = []
            org_section = soup.find(text=re.compile(r"organisation|organization", re.IGNORECASE))
            if org_section:
                parent = org_section.find_parent()
                if parent:
                    org_links = parent.find_all("a")
                    org_names = [l.get_text(strip=True) for l in org_links if l.get_text(strip=True)]

            return Project(
                name=name,
                slug=project_slug,
                status=status,
                org_names=org_names,
                member_count=member_count,
                workspace_count=len(workspaces),
                workspaces=workspaces,
            )

        except OpenSAFELYConnectionError:
            raise
        except Exception as e:
            logger.error(f"Failed to get project {project_slug}: {e}")
            raise OpenSAFELYParseError(f"Failed to parse project {project_slug}: {e}")

    def get_dashboard_stats(self) -> DashboardStats:
        """
        Get aggregate statistics for the dashboard.

        Returns:
            DashboardStats object with counts and recent activity
        """
        stats = DashboardStats()

        try:
            # Get organizations
            orgs = self.get_organizations()
            stats.total_organizations = len(orgs)
            stats.total_projects = sum(o.project_count for o in orgs)

            # Get recent job requests
            stats.recent_job_requests = self.get_recent_job_requests(limit=20)

            # Count job statuses
            for jr in stats.recent_job_requests:
                if jr.status == JobStatus.SUCCEEDED:
                    stats.jobs_succeeded += 1
                elif jr.status == JobStatus.FAILED:
                    stats.jobs_failed += 1
                elif jr.status == JobStatus.RUNNING:
                    stats.jobs_running += 1
                elif jr.status == JobStatus.PENDING:
                    stats.jobs_pending += 1

                # Track jobs by date
                if jr.created_at:
                    date_key = jr.created_at.strftime("%Y-%m-%d")
                    stats.jobs_by_date[date_key] = stats.jobs_by_date.get(date_key, 0) + 1

            stats.total_job_requests = len(stats.recent_job_requests)

        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")

        return stats

    def search_projects(self, query: str) -> List[Project]:
        """
        Search for projects by name.

        Args:
            query: Search query

        Returns:
            List of matching Project objects
        """
        query_lower = query.lower()
        results = []

        try:
            orgs = self.get_organizations()

            for org in orgs:
                try:
                    org_details = self.get_organization_details(org.slug)
                    for project in org_details.projects:
                        if query_lower in project.name.lower() or query_lower in project.slug.lower():
                            results.append(project)
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Search failed: {e}")

        return results

    def iter_all_projects(self) -> Generator[Project, None, None]:
        """
        Iterate through all projects across all organizations.

        Yields:
            Project objects
        """
        try:
            orgs = self.get_organizations()

            for org in orgs:
                try:
                    org_details = self.get_organization_details(org.slug)
                    for project in org_details.projects:
                        yield project
                except Exception as e:
                    logger.debug(f"Failed to get projects for {org.slug}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to iterate projects: {e}")

    def get_backends(self) -> List[Backend]:
        """
        Get list of known backends.

        Returns:
            List of Backend objects
        """
        return list(self.BACKENDS.values())

    def clear_cache(self):
        """Clear the internal cache."""
        self._cache.clear()
