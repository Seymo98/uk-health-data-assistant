"""Load custodian and governance body data from JSON configuration files."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from data_access.models import (
    AccessRequirement,
    AccessStep,
    CostEstimate,
    DataCustodian,
    GovernanceBody,
    GovernanceTier,
    TimelineEstimate,
)

# Resolve paths relative to the project root (one level up from this file's package).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CUSTODIANS_DIR = _PROJECT_ROOT / "data" / "custodians"
_GOVERNANCE_FILE = _PROJECT_ROOT / "data" / "governance_bodies.json"
_SCHEMA_FILE = _PROJECT_ROOT / "data" / "custodian_schema.json"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_timeline(raw: list) -> List[TimelineEstimate]:
    return [
        TimelineEstimate(
            phase=t["phase"],
            min_weeks=t["min_weeks"],
            typical_weeks=t["typical_weeks"],
            max_weeks=t["max_weeks"],
            notes=t.get("notes"),
        )
        for t in raw
    ]


def _parse_costs(raw: Optional[dict]) -> Optional[CostEstimate]:
    if raw is None:
        return None
    return CostEstimate(
        application_fee=raw.get("application_fee"),
        annual_access_fee=raw.get("annual_access_fee"),
        per_dataset_fee=raw.get("per_dataset_fee"),
        tre_fee=raw.get("tre_fee"),
        notes=raw.get("notes"),
        free_for=raw.get("free_for", []),
    )


def _parse_requirements(raw: list) -> List[AccessRequirement]:
    return [
        AccessRequirement(
            name=r["name"],
            description=r["description"],
            mandatory=r.get("mandatory", True),
            applies_to=r.get("applies_to", []),
            url=r.get("url"),
        )
        for r in raw
    ]


def _parse_steps(raw: list) -> List[AccessStep]:
    return [
        AccessStep(
            order=s["order"],
            name=s["name"],
            description=s["description"],
            estimated_weeks=s["estimated_weeks"],
            url=s.get("url"),
            governance_body_id=s.get("governance_body_id"),
        )
        for s in raw
    ]


def _parse_custodian(data: dict) -> DataCustodian:
    return DataCustodian(
        id=data["id"],
        name=data["name"],
        short_name=data["short_name"],
        description=data["description"],
        url=data["url"],
        entity_type=data.get("entity_type", "data_custodian"),
        regions=data.get("regions", []),
        access_model=data.get("access_model", "tre_only"),
        population_coverage=data.get("population_coverage"),
        patient_count=data.get("patient_count"),
        data_types=data.get("data_types", []),
        key_datasets=data.get("key_datasets", []),
        linkages=data.get("linkages", []),
        tre_platform=data.get("tre_platform"),
        eligible_researchers=data.get("eligible_researchers", []),
        requirements=_parse_requirements(data.get("requirements", [])),
        access_steps=_parse_steps(data.get("access_steps", [])),
        timeline=_parse_timeline(data.get("timeline", [])),
        costs=_parse_costs(data.get("costs")),
        strengths=data.get("strengths", []),
        limitations=data.get("limitations", []),
        recent_changes=data.get("recent_changes", []),
        related_governance_bodies=data.get("related_governance_bodies", []),
        gateway_search_term=data.get("gateway_search_term"),
        tags=data.get("tags", []),
        contact_email=data.get("contact_email"),
        last_updated=data.get("last_updated"),
    )


def _parse_governance_body(data: dict) -> GovernanceBody:
    tiers = [
        GovernanceTier(
            tier_name=t["tier_name"],
            description=t["description"],
            typical_weeks=t["typical_weeks"],
            criteria=t.get("criteria"),
        )
        for t in data.get("tiers", [])
    ]
    return GovernanceBody(
        id=data["id"],
        name=data["name"],
        short_name=data["short_name"],
        description=data["description"],
        url=data.get("url"),
        nations=data.get("nations", []),
        role=data.get("role"),
        tiers=tiers,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_all_custodians() -> List[DataCustodian]:
    """Load every ``*.json`` file from ``data/custodians/`` and return parsed objects."""
    custodians: List[DataCustodian] = []
    if not _CUSTODIANS_DIR.is_dir():
        return custodians
    for fp in sorted(_CUSTODIANS_DIR.glob("*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            custodians.append(_parse_custodian(data))
        except Exception as exc:
            # Log but don't crash — partial data is better than nothing.
            print(f"[loader] Warning: failed to load {fp.name}: {exc}")
    return custodians


def load_governance_bodies() -> List[GovernanceBody]:
    """Load governance bodies from ``data/governance_bodies.json``."""
    if not _GOVERNANCE_FILE.is_file():
        return []
    try:
        with open(_GOVERNANCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [_parse_governance_body(g) for g in data]
    except Exception as exc:
        print(f"[loader] Warning: failed to load governance bodies: {exc}")
        return []


def get_custodian(custodian_id: str, custodians: Optional[List[DataCustodian]] = None) -> Optional[DataCustodian]:
    """Look up a single custodian by ID."""
    if custodians is None:
        custodians = load_all_custodians()
    for c in custodians:
        if c.id == custodian_id:
            return c
    return None


def get_governance_body(body_id: str, bodies: Optional[List[GovernanceBody]] = None) -> Optional[GovernanceBody]:
    """Look up a single governance body by ID."""
    if bodies is None:
        bodies = load_governance_bodies()
    for b in bodies:
        if b.id == body_id:
            return b
    return None
