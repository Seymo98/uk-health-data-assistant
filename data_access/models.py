"""Data models for the UK Health Data Access Navigator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AccessModel(str, Enum):
    TRE_ONLY = "tre_only"
    DATA_EXTRACT = "data_extract"
    CODE_IN_SITU = "code_in_situ"
    HYBRID = "hybrid"


class Region(str, Enum):
    ENGLAND = "England"
    WALES = "Wales"
    SCOTLAND = "Scotland"
    NORTHERN_IRELAND = "Northern Ireland"
    UK_WIDE = "UK-wide"


class EntityType(str, Enum):
    DATA_CUSTODIAN = "data_custodian"
    GOVERNANCE_BODY = "governance_body"
    INFRASTRUCTURE_PROVIDER = "infrastructure_provider"


# ---------------------------------------------------------------------------
# Building-block dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TimelineEstimate:
    """One phase of the access process with duration range in weeks."""
    phase: str
    min_weeks: int
    typical_weeks: int
    max_weeks: int
    notes: Optional[str] = None


@dataclass
class CostEstimate:
    """Estimated costs for accessing data from a custodian."""
    application_fee: Optional[str] = None
    annual_access_fee: Optional[str] = None
    per_dataset_fee: Optional[str] = None
    tre_fee: Optional[str] = None
    notes: Optional[str] = None
    free_for: List[str] = field(default_factory=list)


@dataclass
class AccessRequirement:
    """A prerequisite the researcher must meet."""
    name: str
    description: str
    mandatory: bool = True
    applies_to: List[str] = field(default_factory=list)
    url: Optional[str] = None


@dataclass
class AccessStep:
    """A discrete step in the access journey."""
    order: int
    name: str
    description: str
    estimated_weeks: int
    url: Optional[str] = None
    governance_body_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Governance bodies
# ---------------------------------------------------------------------------

@dataclass
class GovernanceTier:
    """One tier of a multi-tier governance body (e.g. PBPP Tier 1 / Tier 2)."""
    tier_name: str
    description: str
    typical_weeks: int
    criteria: Optional[str] = None


@dataclass
class GovernanceBody:
    """A governance / approval body that sits across custodian pathways."""
    id: str
    name: str
    short_name: str
    description: str
    url: Optional[str] = None
    nations: List[str] = field(default_factory=list)
    role: Optional[str] = None
    tiers: List[GovernanceTier] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core entities
# ---------------------------------------------------------------------------

@dataclass
class DataCustodian:
    """Complete profile of a UK health data custodian / pathway."""
    id: str
    name: str
    short_name: str
    description: str
    url: str

    entity_type: str = EntityType.DATA_CUSTODIAN.value
    regions: List[str] = field(default_factory=list)
    access_model: str = AccessModel.TRE_ONLY.value

    population_coverage: Optional[str] = None
    patient_count: Optional[str] = None

    data_types: List[str] = field(default_factory=list)
    key_datasets: List[str] = field(default_factory=list)
    linkages: List[str] = field(default_factory=list)

    tre_platform: Optional[str] = None
    eligible_researchers: List[str] = field(default_factory=list)

    requirements: List[AccessRequirement] = field(default_factory=list)
    access_steps: List[AccessStep] = field(default_factory=list)
    timeline: List[TimelineEstimate] = field(default_factory=list)
    costs: Optional[CostEstimate] = None

    strengths: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    recent_changes: List[str] = field(default_factory=list)

    related_governance_bodies: List[str] = field(default_factory=list)
    gateway_search_term: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    contact_email: Optional[str] = None
    last_updated: Optional[str] = None

    # -- derived helpers --
    @property
    def total_typical_weeks(self) -> int:
        return sum(t.typical_weeks for t in self.timeline)

    @property
    def total_min_weeks(self) -> int:
        return sum(t.min_weeks for t in self.timeline)

    @property
    def total_max_weeks(self) -> int:
        return sum(t.max_weeks for t in self.timeline)

    @property
    def cost_summary(self) -> str:
        if self.costs is None:
            return "Not specified"
        parts = []
        if self.costs.application_fee:
            parts.append(self.costs.application_fee)
        if self.costs.annual_access_fee:
            parts.append(f"{self.costs.annual_access_fee}/yr")
        if self.costs.tre_fee:
            parts.append(f"TRE: {self.costs.tre_fee}")
        if self.costs.free_for:
            parts.append(f"Free for: {', '.join(self.costs.free_for)}")
        return " | ".join(parts) if parts else "Contact custodian"


# ---------------------------------------------------------------------------
# Researcher profile (form input)
# ---------------------------------------------------------------------------

@dataclass
class ResearcherProfile:
    """Captures what the researcher needs - maps to the Navigator form."""
    researcher_type: str
    institution_country: str
    ethics_status: str
    funding_status: str
    data_needs: List[str]
    geographic_scope: List[str]
    population_size: str
    study_type: str
    timeline_priority: str
    budget_range: str
    needs_data_extraction: bool = False
    needs_repeat_access: bool = False
    needs_section_251: bool = False


# ---------------------------------------------------------------------------
# Recommendation output
# ---------------------------------------------------------------------------

@dataclass
class PathwayRecommendation:
    """A scored recommendation for a single custodian pathway."""
    custodian: DataCustodian
    overall_score: float
    dimension_scores: Dict[str, float]
    match_reasons: List[str]
    concerns: List[str]
    estimated_total_weeks: int
    estimated_cost_range: str
    required_governance: List[GovernanceBody] = field(default_factory=list)
