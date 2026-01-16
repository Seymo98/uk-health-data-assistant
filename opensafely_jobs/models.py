"""
Data models for OpenSAFELY Jobs.

These models represent the public data structures exposed by jobs.opensafely.org.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class JobStatus(str, Enum):
    """Status of a job execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str) -> "JobStatus":
        """Convert string to JobStatus, defaulting to UNKNOWN."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.UNKNOWN


class ProjectStatus(str, Enum):
    """Status of a project."""
    ONGOING = "ongoing"
    POSTPONED = "postponed"
    COMPLETED = "completed"
    RETIRED = "retired"

    @classmethod
    def from_string(cls, value: str) -> "ProjectStatus":
        """Convert string to ProjectStatus."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.ONGOING


@dataclass
class Backend:
    """Represents a secure backend environment where jobs run."""
    name: str
    slug: str
    display_name: Optional[str] = None
    level_4_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Backend":
        return cls(
            name=data.get("name", ""),
            slug=data.get("slug", data.get("name", "").lower()),
            display_name=data.get("display_name"),
            level_4_url=data.get("level_4_url"),
        )


@dataclass
class Job:
    """Represents a single job execution."""
    identifier: str
    action: str
    status: JobStatus
    status_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    runtime_seconds: Optional[float] = None

    @property
    def is_completed(self) -> bool:
        return self.status in (JobStatus.SUCCEEDED, JobStatus.FAILED)

    @property
    def runtime_formatted(self) -> str:
        """Format runtime as human-readable string."""
        if self.runtime_seconds is None:
            return "N/A"

        hours = int(self.runtime_seconds // 3600)
        minutes = int((self.runtime_seconds % 3600) // 60)
        seconds = int(self.runtime_seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        created_at = None
        started_at = None
        completed_at = None

        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        if data.get("started_at"):
            try:
                started_at = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        if data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        runtime_seconds = None
        if started_at and completed_at:
            runtime_seconds = (completed_at - started_at).total_seconds()

        return cls(
            identifier=data.get("identifier", ""),
            action=data.get("action", ""),
            status=JobStatus.from_string(data.get("status", "unknown")),
            status_message=data.get("status_message"),
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            runtime_seconds=runtime_seconds,
        )


@dataclass
class JobRequest:
    """Represents a job request containing one or more jobs."""
    identifier: str
    sha: str
    status: JobStatus
    status_message: Optional[str] = None
    requested_actions: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    workspace_name: Optional[str] = None
    project_name: Optional[str] = None
    backend_name: Optional[str] = None
    jobs: List[Job] = field(default_factory=list)
    repo_url: Optional[str] = None

    @property
    def job_count(self) -> int:
        return len(self.jobs) if self.jobs else len(self.requested_actions)

    @property
    def success_rate(self) -> Optional[float]:
        """Calculate success rate of jobs in this request."""
        if not self.jobs:
            return None
        completed = [j for j in self.jobs if j.is_completed]
        if not completed:
            return None
        succeeded = sum(1 for j in completed if j.status == JobStatus.SUCCEEDED)
        return succeeded / len(completed) * 100

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobRequest":
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        jobs = []
        if data.get("jobs"):
            jobs = [Job.from_dict(j) for j in data["jobs"]]

        return cls(
            identifier=data.get("identifier", ""),
            sha=data.get("sha", ""),
            status=JobStatus.from_string(data.get("status", "unknown")),
            status_message=data.get("status_message"),
            requested_actions=data.get("requested_actions", []),
            created_at=created_at,
            created_by=data.get("created_by", {}).get("username") if isinstance(data.get("created_by"), dict) else data.get("created_by"),
            workspace_name=data.get("workspace", {}).get("name") if isinstance(data.get("workspace"), dict) else data.get("workspace_name"),
            project_name=data.get("project_name"),
            backend_name=data.get("backend", {}).get("name") if isinstance(data.get("backend"), dict) else data.get("backend_name"),
            jobs=jobs,
            repo_url=data.get("repo_url"),
        )


@dataclass
class Workspace:
    """Represents a workspace containing related jobs."""
    name: str
    project_name: Optional[str] = None
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    branch: Optional[str] = None
    is_archived: bool = False
    created_at: Optional[datetime] = None
    job_request_count: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            name=data.get("name", ""),
            project_name=data.get("project", {}).get("name") if isinstance(data.get("project"), dict) else data.get("project_name"),
            repo_name=data.get("repo", {}).get("name") if isinstance(data.get("repo"), dict) else data.get("repo_name"),
            repo_url=data.get("repo", {}).get("url") if isinstance(data.get("repo"), dict) else data.get("repo_url"),
            branch=data.get("branch"),
            is_archived=data.get("is_archived", False),
            created_at=created_at,
            job_request_count=data.get("job_request_count", 0),
        )


@dataclass
class Project:
    """Represents a research project on OpenSAFELY."""
    name: str
    slug: str
    status: ProjectStatus = ProjectStatus.ONGOING
    status_description: Optional[str] = None
    number: Optional[int] = None
    org_names: List[str] = field(default_factory=list)
    member_count: int = 0
    workspace_count: int = 0
    workspaces: List[Workspace] = field(default_factory=list)
    first_job_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @property
    def url(self) -> str:
        return f"https://jobs.opensafely.org/{self.slug}/"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        created_at = None
        first_job_at = None

        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        if data.get("first_job_at"):
            try:
                first_job_at = datetime.fromisoformat(data["first_job_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        workspaces = []
        if data.get("workspaces"):
            workspaces = [Workspace.from_dict(w) for w in data["workspaces"]]

        org_names = data.get("org_names", [])
        if data.get("orgs"):
            org_names = [o.get("name", "") for o in data["orgs"] if isinstance(o, dict)]

        return cls(
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            status=ProjectStatus.from_string(data.get("status", "ongoing")),
            status_description=data.get("status_description"),
            number=data.get("number"),
            org_names=org_names,
            member_count=data.get("member_count", 0),
            workspace_count=data.get("workspace_count", len(workspaces)),
            workspaces=workspaces,
            first_job_at=first_job_at,
            created_at=created_at,
        )


@dataclass
class Organization:
    """Represents an organization using OpenSAFELY."""
    name: str
    slug: str
    project_count: int = 0
    projects: List[Project] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"https://jobs.opensafely.org/{self.slug}/"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Organization":
        projects = []
        if data.get("projects"):
            projects = [Project.from_dict(p) for p in data["projects"]]

        return cls(
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            project_count=data.get("project_count", len(projects)),
            projects=projects,
        )


@dataclass
class DashboardStats:
    """Aggregate statistics for the dashboard."""
    total_organizations: int = 0
    total_projects: int = 0
    total_workspaces: int = 0
    total_job_requests: int = 0
    total_jobs: int = 0
    jobs_succeeded: int = 0
    jobs_failed: int = 0
    jobs_running: int = 0
    jobs_pending: int = 0
    recent_job_requests: List[JobRequest] = field(default_factory=list)
    projects_by_status: Dict[str, int] = field(default_factory=dict)
    jobs_by_backend: Dict[str, int] = field(default_factory=dict)
    jobs_by_date: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        completed = self.jobs_succeeded + self.jobs_failed
        if completed == 0:
            return 0.0
        return self.jobs_succeeded / completed * 100

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DashboardStats":
        recent = []
        if data.get("recent_job_requests"):
            recent = [JobRequest.from_dict(jr) for jr in data["recent_job_requests"]]

        return cls(
            total_organizations=data.get("total_organizations", 0),
            total_projects=data.get("total_projects", 0),
            total_workspaces=data.get("total_workspaces", 0),
            total_job_requests=data.get("total_job_requests", 0),
            total_jobs=data.get("total_jobs", 0),
            jobs_succeeded=data.get("jobs_succeeded", 0),
            jobs_failed=data.get("jobs_failed", 0),
            jobs_running=data.get("jobs_running", 0),
            jobs_pending=data.get("jobs_pending", 0),
            recent_job_requests=recent,
            projects_by_status=data.get("projects_by_status", {}),
            jobs_by_backend=data.get("jobs_by_backend", {}),
            jobs_by_date=data.get("jobs_by_date", {}),
        )
