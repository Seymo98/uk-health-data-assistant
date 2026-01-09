"""
HDR UK Gateway Client

A Python client for the HDR UK Innovation Gateway API.
Based on patterns from the official gateway-web repository.

Usage:
    from hdruk_gateway import GatewayClient

    client = GatewayClient()
    datasets = client.search_datasets("diabetes")

    for dataset in datasets:
        print(f"{dataset.title} - {dataset.publisher}")
"""

from .client import GatewayClient
from .models import (
    Dataset,
    DatasetMetadata,
    DataUseRegister,
    Publication,
    Tool,
    Collection,
    Team,
    SearchResult,
    SearchFilters,
    PaginatedResponse,
)
from .search import DatasetSearcher
from .exceptions import GatewayAPIError, GatewayAuthError, GatewayNotFoundError

__version__ = "1.0.0"
__all__ = [
    "GatewayClient",
    "Dataset",
    "DatasetMetadata",
    "DataUseRegister",
    "Publication",
    "Tool",
    "Collection",
    "Team",
    "SearchResult",
    "SearchFilters",
    "PaginatedResponse",
    "DatasetSearcher",
    "GatewayAPIError",
    "GatewayAuthError",
    "GatewayNotFoundError",
]
