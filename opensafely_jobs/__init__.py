"""
OpenSAFELY Jobs Client Library.

A Python client for accessing public data from jobs.opensafely.org,
OpenSAFELY's transparent job execution platform.
"""

from .client import OpenSAFELYJobsClient
from .models import (
    Organization,
    Project,
    Workspace,
    JobRequest,
    Job,
    Backend,
    JobStatus,
    ProjectStatus,
)

__all__ = [
    "OpenSAFELYJobsClient",
    "Organization",
    "Project",
    "Workspace",
    "JobRequest",
    "Job",
    "Backend",
    "JobStatus",
    "ProjectStatus",
]

__version__ = "1.0.0"
