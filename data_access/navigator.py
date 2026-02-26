"""Pathway recommendation engine — scores and ranks custodians against a researcher profile."""

from __future__ import annotations

from typing import Dict, List, Tuple

from data_access.models import (
    DataCustodian,
    GovernanceBody,
    PathwayRecommendation,
    ResearcherProfile,
)


# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------

WEIGHTS: Dict[str, float] = {
    "data_fit": 0.30,
    "geographic": 0.20,
    "eligibility": 0.15,
    "speed": 0.15,
    "cost": 0.10,
    "study_design": 0.10,
}

# ---------------------------------------------------------------------------
# Timeline urgency mapping (profile value → max acceptable typical weeks)
# ---------------------------------------------------------------------------

_URGENCY_MAP: Dict[str, int] = {
    "ASAP": 12,
    "Within 3 months": 13,
    "Within 6 months": 26,
    "Within 12 months": 52,
    "Not urgent": 200,
}

# ---------------------------------------------------------------------------
# Budget mapping (profile value → rough max GBP)
# ---------------------------------------------------------------------------

_BUDGET_MAP: Dict[str, int] = {
    "Free/no budget": 0,
    "Up to GBP 5,000": 5_000,
    "GBP 5,000-25,000": 25_000,
    "GBP 25,000-100,000": 100_000,
    "GBP 100,000+": 999_999,
}

# ---------------------------------------------------------------------------
# Access model compatibility with study types
# ---------------------------------------------------------------------------

_STUDY_MODEL_COMPAT: Dict[str, List[str]] = {
    "Observational/epidemiological": ["tre_only", "data_extract", "code_in_situ", "hybrid"],
    "Clinical trial (RCT)": ["data_extract", "hybrid"],
    "Health economics": ["tre_only", "data_extract", "code_in_situ", "hybrid"],
    "Machine learning/AI": ["tre_only", "code_in_situ", "hybrid"],
    "Public health surveillance": ["tre_only", "code_in_situ", "hybrid"],
    "Service evaluation": ["tre_only", "data_extract", "code_in_situ", "hybrid"],
    "Genomic/biobank study": ["tre_only", "hybrid"],
    "Record linkage study": ["tre_only", "hybrid"],
}


# ---------------------------------------------------------------------------
# Individual dimension scorers
# ---------------------------------------------------------------------------

def _score_data_fit(needs: List[str], custodian_types: List[str]) -> Tuple[float, List[str], List[str]]:
    """Return (score 0-100, reasons, concerns)."""
    if not needs:
        return 50.0, [], ["No data types specified"]

    needs_lower = {n.lower() for n in needs}
    cust_lower = {c.lower() for c in custodian_types}

    matched = needs_lower & cust_lower
    score = (len(matched) / len(needs_lower)) * 100

    reasons: List[str] = []
    concerns: List[str] = []

    if matched:
        reasons.append(f"Holds {len(matched)} of {len(needs_lower)} requested data types")
    missing = needs_lower - cust_lower
    if missing:
        # Shorten display names
        missing_display = [m.split("(")[0].strip().title() for m in list(missing)[:3]]
        concerns.append(f"Missing: {', '.join(missing_display)}")

    return score, reasons, concerns


def _score_geography(scope: List[str], custodian_regions: List[str]) -> Tuple[float, List[str], List[str]]:
    if not scope:
        return 50.0, [], []

    scope_set = set(scope)
    cust_set = set(custodian_regions)

    # UK-wide custodians match everything
    if "UK-wide" in cust_set:
        return 100.0, ["UK-wide coverage matches all geographic needs"], []

    # Check overlap
    overlap = scope_set & cust_set
    if not overlap:
        # If researcher wants UK-wide and custodian is regional, partial match
        if "UK-wide" in scope_set:
            return 40.0, [], [f"Only covers {', '.join(cust_set)} — not full UK"]
        return 0.0, [], [f"No geographic overlap — covers {', '.join(cust_set)}"]

    score = (len(overlap) / len(scope_set)) * 100
    reasons = [f"Covers {', '.join(overlap)}"]
    concerns = []
    uncovered = scope_set - cust_set - {"UK-wide"}
    if uncovered:
        concerns.append(f"Does not cover {', '.join(uncovered)}")
    return score, reasons, concerns


def _score_eligibility(researcher_type: str, eligible: List[str]) -> Tuple[float, List[str], List[str]]:
    if not eligible:
        return 70.0, ["Eligibility not specified — likely open"], []
    if researcher_type in eligible:
        return 100.0, [f"{researcher_type} is an eligible researcher type"], []
    # Partial match — some custodians accept similar types
    return 20.0, [], [f"{researcher_type} may not be eligible — check with custodian"]


def _score_speed(priority: str, custodian_timeline: list) -> Tuple[float, List[str], List[str]]:
    max_weeks = _URGENCY_MAP.get(priority, 200)
    typical = sum(t.typical_weeks for t in custodian_timeline) if custodian_timeline else 20

    if typical <= max_weeks * 0.5:
        score = 100.0
        reasons = [f"Estimated {typical} weeks — well within your timeframe"]
    elif typical <= max_weeks:
        score = 70.0
        reasons = [f"Estimated {typical} weeks — achievable within your timeframe"]
    elif typical <= max_weeks * 1.5:
        score = 40.0
        reasons = [f"Estimated {typical} weeks — may be tight for your timeline"]
    else:
        score = 10.0
        reasons = [f"Estimated {typical} weeks — likely exceeds your timeline"]

    return score, reasons, []


def _score_cost(budget: str, custodian_costs) -> Tuple[float, List[str], List[str]]:
    max_budget = _BUDGET_MAP.get(budget, 999_999)

    if custodian_costs is None:
        return 50.0, ["Costs not fully specified"], ["Check costs with custodian"]

    # Check if free
    fee_str = (custodian_costs.application_fee or "").lower()
    if "free" in fee_str or fee_str == "":
        return 100.0, ["Free access"], []

    # Try to parse a rough numeric from the fee string
    import re
    numbers = re.findall(r"[\d,]+", fee_str.replace(",", ""))
    if numbers:
        min_fee = int(numbers[0])
        if min_fee <= max_budget:
            return 80.0, [f"Costs ({custodian_costs.application_fee}) within budget"], []
        else:
            return 20.0, [], [f"Costs ({custodian_costs.application_fee}) may exceed budget of {budget}"]

    return 50.0, ["Cost details require verification"], []


def _score_study_design(study_type: str, access_model: str) -> Tuple[float, List[str], List[str]]:
    compatible = _STUDY_MODEL_COMPAT.get(study_type, [])
    if access_model in compatible:
        return 100.0, [f"Access model ({access_model.replace('_', ' ')}) supports {study_type}"], []
    return 30.0, [], [f"Access model ({access_model.replace('_', ' ')}) may not suit {study_type}"]


# ---------------------------------------------------------------------------
# Governance resolution
# ---------------------------------------------------------------------------

def _resolve_governance(
    profile: ResearcherProfile,
    custodian: DataCustodian,
    all_bodies: List[GovernanceBody],
) -> List[GovernanceBody]:
    """Determine which governance bodies are needed for this combination.

    For PBPP (Scotland), selects the appropriate tier based on the researcher
    profile rather than including both tiers.
    """
    body_map = {b.id: b for b in all_bodies}
    needed: List[GovernanceBody] = []
    needed_ids: set = set()

    # Determine which PBPP tier is appropriate for Scottish custodians
    pbpp_preferred = "pbpp_tier2" if profile.needs_section_251 else "pbpp_tier1"
    pbpp_excluded = "pbpp_tier1" if profile.needs_section_251 else "pbpp_tier2"

    # Include bodies listed by custodian, but filter PBPP to appropriate tier
    for gid in custodian.related_governance_bodies:
        if gid == pbpp_excluded:
            continue  # skip the non-applicable PBPP tier
        if gid in body_map and gid not in needed_ids:
            needed.append(body_map[gid])
            needed_ids.add(gid)

    # Section 251 / CAG trigger
    if profile.needs_section_251:
        cag = body_map.get("cag")
        if cag and "cag" not in needed_ids:
            cust_nations = set(custodian.regions)
            cag_nations = {"England", "Wales"}
            if cust_nations & cag_nations:
                needed.append(cag)
                needed_ids.add("cag")

    # Scotland PBPP auto-inclusion (if not already added via custodian)
    if "Scotland" in custodian.regions and pbpp_preferred not in needed_ids:
        tier = body_map.get(pbpp_preferred)
        if tier:
            needed.append(tier)
            needed_ids.add(pbpp_preferred)

    return needed


# ---------------------------------------------------------------------------
# Main ranking function
# ---------------------------------------------------------------------------

def rank_pathways(
    profile: ResearcherProfile,
    custodians: List[DataCustodian],
    governance_bodies: List[GovernanceBody],
) -> List[PathwayRecommendation]:
    """Score and rank all custodians against the researcher's profile.

    Returns a descending-sorted list of ``PathwayRecommendation`` objects.
    """
    recommendations: List[PathwayRecommendation] = []

    for custodian in custodians:
        all_reasons: List[str] = []
        all_concerns: List[str] = []
        dim_scores: Dict[str, float] = {}

        # --- score each dimension ---
        for dim, scorer in [
            ("data_fit", lambda: _score_data_fit(profile.data_needs, custodian.data_types)),
            ("geographic", lambda: _score_geography(profile.geographic_scope, custodian.regions)),
            ("eligibility", lambda: _score_eligibility(profile.researcher_type, custodian.eligible_researchers)),
            ("speed", lambda: _score_speed(profile.timeline_priority, custodian.timeline)),
            ("cost", lambda: _score_cost(profile.budget_range, custodian.costs)),
            ("study_design", lambda: _score_study_design(profile.study_type, custodian.access_model)),
        ]:
            score, reasons, concerns = scorer()
            dim_scores[dim] = score
            all_reasons.extend(reasons)
            all_concerns.extend(concerns)

        # --- weighted overall ---
        overall = sum(dim_scores[k] * WEIGHTS[k] for k in WEIGHTS)

        # --- data extraction check ---
        if profile.needs_data_extraction and custodian.access_model == "tre_only":
            all_concerns.append("TRE-only — no data extraction available")
            overall *= 0.85  # penalty

        # --- resolve governance ---
        gov = _resolve_governance(profile, custodian, governance_bodies)
        if gov:
            gov_names = [g.short_name for g in gov]
            all_reasons.append(f"Governance route: {', '.join(gov_names)}")

        # --- timeline & cost summaries ---
        typical_weeks = custodian.total_typical_weeks
        # Add governance body time
        for g in gov:
            if g.tiers:
                typical_weeks += g.tiers[0].typical_weeks

        cost_range = custodian.cost_summary

        recommendations.append(
            PathwayRecommendation(
                custodian=custodian,
                overall_score=round(overall, 1),
                dimension_scores=dim_scores,
                match_reasons=all_reasons,
                concerns=all_concerns,
                estimated_total_weeks=typical_weeks,
                estimated_cost_range=cost_range,
                required_governance=gov,
            )
        )

    recommendations.sort(key=lambda r: r.overall_score, reverse=True)
    return recommendations
