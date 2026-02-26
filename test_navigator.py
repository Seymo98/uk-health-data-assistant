"""Quick smoke test for the Data Access Navigator."""
import sys
sys.path.insert(0, ".")

from data_access.loader import load_all_custodians, load_governance_bodies
from data_access.navigator import rank_pathways
from data_access.models import ResearcherProfile

# --- Load data ---
custodians = load_all_custodians()
governance = load_governance_bodies()

print(f"Loaded {len(custodians)} custodians:")
for c in custodians:
    regions = ", ".join(c.regions)
    print(f"  - {c.short_name} ({c.id}): {len(c.data_types)} data types, regions=[{regions}], timeline={c.total_typical_weeks}wk")

print(f"\nLoaded {len(governance)} governance bodies:")
for g in governance:
    nations = ", ".join(g.nations)
    print(f"  - {g.short_name} ({g.id}): nations=[{nations}]")

# --- Test: England academic, GP + hospital data, no budget ---
print("\n=== Test 1: England academic, GP + hospital + mortality, free ===")
profile1 = ResearcherProfile(
    researcher_type="Academic researcher",
    institution_country="England",
    ethics_status="Not yet applied",
    funding_status="Funded (grant)",
    data_needs=["Primary care (GP records)", "Hospital episodes (HES/inpatient)", "Mortality/death registrations"],
    geographic_scope=["England"],
    population_size="100,000-1M",
    study_type="Observational/epidemiological",
    timeline_priority="Within 6 months",
    budget_range="Free/no budget",
    needs_data_extraction=False,
    needs_repeat_access=False,
    needs_section_251=False,
)

results1 = rank_pathways(profile1, custodians, governance)
for r in results1[:5]:
    gov_names = [g.short_name for g in r.required_governance]
    print(f"  {r.overall_score:.0f}% - {r.custodian.short_name} (~{r.estimated_total_weeks}wk, {r.estimated_cost_range}) Gov: {gov_names}")

# --- Test: Scottish data ---
print("\n=== Test 2: Scotland data, PBPP governance ===")
profile2 = ResearcherProfile(
    researcher_type="Academic researcher",
    institution_country="Scotland",
    ethics_status="Approved",
    funding_status="Funded (grant)",
    data_needs=["Primary care (GP records)", "Hospital episodes (HES/inpatient)"],
    geographic_scope=["Scotland"],
    population_size="Whole population",
    study_type="Record linkage study",
    timeline_priority="Within 12 months",
    budget_range="Free/no budget",
    needs_data_extraction=False,
    needs_repeat_access=False,
    needs_section_251=False,
)

results2 = rank_pathways(profile2, custodians, governance)
for r in results2[:5]:
    gov_names = [g.short_name for g in r.required_governance]
    print(f"  {r.overall_score:.0f}% - {r.custodian.short_name} (~{r.estimated_total_weeks}wk, {r.estimated_cost_range}) Gov: {gov_names}")

# --- Test: Genomics + Section 251 ---
print("\n=== Test 3: Genomic data + Section 251 (identifiable without consent) ===")
profile3 = ResearcherProfile(
    researcher_type="Academic researcher",
    institution_country="England",
    ethics_status="In progress",
    funding_status="Funded (grant)",
    data_needs=["Genomic/genetic data", "Primary care (GP records)"],
    geographic_scope=["England"],
    population_size="10,000-100,000",
    study_type="Genomic/biobank study",
    timeline_priority="Within 12 months",
    budget_range="GBP 5,000-25,000",
    needs_data_extraction=False,
    needs_repeat_access=False,
    needs_section_251=True,
)

results3 = rank_pathways(profile3, custodians, governance)
for r in results3[:5]:
    gov_names = [g.short_name for g in r.required_governance]
    print(f"  {r.overall_score:.0f}% - {r.custodian.short_name} (~{r.estimated_total_weeks}wk, {r.estimated_cost_range}) Gov: {gov_names}")

# --- Test: Industry researcher ---
print("\n=== Test 4: Industry pharma researcher ===")
profile4 = ResearcherProfile(
    researcher_type="Industry (pharma/biotech)",
    institution_country="England",
    ethics_status="Not yet applied",
    funding_status="Commercial budget",
    data_needs=["Primary care (GP records)", "Prescription data"],
    geographic_scope=["UK-wide"],
    population_size="1M+",
    study_type="Observational/epidemiological",
    timeline_priority="Within 6 months",
    budget_range="GBP 25,000-100,000",
    needs_data_extraction=True,
    needs_repeat_access=True,
    needs_section_251=False,
)

results4 = rank_pathways(profile4, custodians, governance)
for r in results4[:5]:
    gov_names = [g.short_name for g in r.required_governance]
    print(f"  {r.overall_score:.0f}% - {r.custodian.short_name} (~{r.estimated_total_weeks}wk, {r.estimated_cost_range}) Gov: {gov_names}")

print("\nAll tests passed!")
