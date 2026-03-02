"""
Data models for OpenPhenotypes.

Defines the core domain objects aligned with the BHF DSC FAIR Phenotyping
report Table 1 metadata requirements. Supports:

- Full Table 1 mandatory/recommended fields (population constraints,
  ontology terms, dataset provenance, implementation artefacts, etc.)
- Citation-grade accession IDs with stable URL conventions
- Structured validation evidence (method + dataset + metrics)
- Executable logic artefacts (pseudocode, reference implementations, QC rules)
- Core definition vs. study-use hierarchy
- Semantic validation rules for quality-gating submissions

Design unifies the best metadata from OpenCodelists, HDR UK Phenotype
Library, OHDSI Phenotype Library, ClinicalCodes, Keele HCDR, BHF DSC
Codelist Comparison Tool, and Open Targets.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
import re


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CodingSystem(Enum):
    SNOMED_CT = "SNOMED CT"
    ICD10 = "ICD-10"
    ICD11 = "ICD-11"
    READ_V2 = "Read v2"
    CTV3 = "CTV3 (Read v3)"
    OPCS4 = "OPCS-4"
    BNF = "BNF"
    DMD = "dm+d"
    CPRD_MEDCODE = "CPRD Medcode"
    CPRD_PRODCODE = "CPRD Prodcode"
    HES_APC = "HES APC"
    OMOP = "OMOP CDM"


class PhenotypeType(Enum):
    DISEASE = "Disease or syndrome"
    MEDICATION = "Medication"
    BIOMARKER = "Biomarker"
    PROCEDURE = "Procedure"
    LIFESTYLE = "Lifestyle risk factor"
    DEMOGRAPHIC = "Demographic"
    COMPOSITE = "Composite endpoint"


class ValidationStatus(Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under review"
    PEER_REVIEWED = "Peer reviewed"
    VALIDATED = "Clinically validated"
    PUBLISHED = "Published in study"


class TherapeuticArea(Enum):
    CARDIOVASCULAR = "Cardiovascular"
    RESPIRATORY = "Respiratory"
    MENTAL_HEALTH = "Mental health"
    ONCOLOGY = "Oncology"
    DIABETES_ENDOCRINE = "Diabetes & endocrine"
    MUSCULOSKELETAL = "Musculoskeletal"
    NEUROLOGY = "Neurology"
    INFECTIOUS_DISEASE = "Infectious disease"
    RENAL = "Renal"
    GASTROINTESTINAL = "Gastrointestinal"
    DERMATOLOGY = "Dermatology"
    OBSTETRICS_GYNAECOLOGY = "Obstetrics & gynaecology"
    PAEDIATRICS = "Paediatrics"
    MULTIMORBIDITY = "Multimorbidity"
    OTHER = "Other"


class Sex(Enum):
    MALE = "Male"
    FEMALE = "Female"
    BOTH = "Both"


class CodePosition(Enum):
    """Position of a diagnosis code within a hospital episode (Table 1)."""
    PRIMARY = "Primary diagnosis"
    SECONDARY = "Secondary diagnosis"
    ANY = "Any position"


class ValidationMethod(Enum):
    CHART_REVIEW = "Chart review"
    CASE_NOTE_REVIEW = "Case note review"
    REGISTRY_COMPARISON = "Registry comparison"
    CROSS_DATABASE = "Cross-database replication"
    EXPERT_PANEL = "Expert clinical panel"
    SENSITIVITY_ANALYSIS = "Sensitivity analysis"
    QUESTIONNAIRE = "Patient questionnaire"
    LAB_CONFIRMATION = "Laboratory confirmation"


# ---------------------------------------------------------------------------
# Table 1 — Code-level attributes
# ---------------------------------------------------------------------------

@dataclass
class Code:
    """A single clinical code within a codelist."""
    code: str
    term: str
    coding_system: CodingSystem
    is_included: bool = True  # False = explicitly excluded code
    # Table 1: code position and flags
    code_position: CodePosition = CodePosition.ANY
    prevalent_only: bool = False  # True = only count if pre-existing
    incident_only: bool = False   # True = only count new occurrences
    notes: str = ""               # Free-text annotation on this code


# ---------------------------------------------------------------------------
# Table 1 — Ontology term (for ontology-supported search)
# ---------------------------------------------------------------------------

@dataclass
class OntologyTerm:
    """Overarching ontology/vocabulary term representing the phenotype (Table 1).

    Used for ontology-supported searching: users can find phenotypes by
    navigating a hierarchy, and the system can expand queries to include
    child/parent terms.
    """
    system: str          # e.g. "SNOMED CT", "ICD-10", "MeSH", "HPO"
    code: str
    label: str
    is_primary: bool = True  # Primary vs. secondary mapping


# ---------------------------------------------------------------------------
# Authors and publications
# ---------------------------------------------------------------------------

@dataclass
class Author:
    name: str
    institution: str
    orcid: Optional[str] = None


@dataclass
class Publication:
    title: str
    doi: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    pubmed_id: Optional[str] = None
    is_primary: bool = False  # True = the primary/defining publication


# ---------------------------------------------------------------------------
# Table 1 — Dataset provenance
# ---------------------------------------------------------------------------

@dataclass
class DatasetProvenance:
    """Records the specific dataset version used to create/validate a phenotype (Table 1)."""
    dataset_name: str                     # e.g. "CPRD GOLD March 2023"
    dataset_identifier: str = ""          # e.g. DOI or accession
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    population_size: Optional[int] = None
    notes: str = ""


# ---------------------------------------------------------------------------
# Table 1 — Validation evidence (structured)
# ---------------------------------------------------------------------------

@dataclass
class ValidationEvidence:
    """Structured validation result with method, dataset, and metrics (Table 1)."""
    method: ValidationMethod
    dataset: str
    comparator: str = ""   # Gold standard used
    ppv: Optional[float] = None          # Positive predictive value (0-1)
    npv: Optional[float] = None          # Negative predictive value (0-1)
    sensitivity: Optional[float] = None  # (0-1)
    specificity: Optional[float] = None  # (0-1)
    f1_score: Optional[float] = None     # (0-1)
    sample_size: Optional[int] = None
    publication_doi: Optional[str] = None
    notes: str = ""

    @property
    def has_metrics(self) -> bool:
        return any(v is not None for v in [
            self.ppv, self.npv, self.sensitivity, self.specificity, self.f1_score
        ])


# ---------------------------------------------------------------------------
# Table 1 — Implementation artefacts (executable logic)
# ---------------------------------------------------------------------------

@dataclass
class Implementation:
    """Machine-readable or human-readable implementation of phenotyping logic (Table 1)."""
    language: str             # e.g. "SQL", "Python", "OpenSAFELY ehrQL", "OMOP Concept Set JSON", "Pseudocode"
    label: str                # Human-readable name, e.g. "OpenSAFELY ehrQL study definition"
    code: str                 # The actual logic / pseudocode
    source_url: str = ""      # Link to source repository
    dataset_target: str = ""  # Which dataset this is written for
    notes: str = ""


@dataclass
class DummyDataExample:
    """Small worked example with dummy data (Table 1 recommended)."""
    description: str
    input_data: str   # CSV-like or markdown table
    expected_output: str
    notes: str = ""


@dataclass
class QCRule:
    """Quality-control / data-preprocessing rule (Table 1 recommended)."""
    rule_id: str
    description: str
    severity: str = "warning"  # "error" | "warning" | "info"
    applies_to: str = ""       # e.g. "ICD-10 codelist" or "all"
    automated: bool = True     # Can this be checked automatically?


# ---------------------------------------------------------------------------
# Clinical endorsement
# ---------------------------------------------------------------------------

@dataclass
class ClinicalEndorsement:
    """Record of clinical expert review/endorsement."""
    reviewer_name: str
    reviewer_role: str         # e.g. "Consultant Cardiologist"
    institution: str
    date: Optional[date] = None
    notes: str = ""


# ---------------------------------------------------------------------------
# Evidence score (Open Targets-inspired)
# ---------------------------------------------------------------------------

@dataclass
class EvidenceScore:
    """OpenTargets-inspired scoring for phenotype quality/confidence."""
    literature: float = 0.0        # 0-1: Evidence from publications
    clinical_review: float = 0.0   # 0-1: Expert clinical review
    validation: float = 0.0        # 0-1: Formal validation studies
    usage: float = 0.0             # 0-1: Adoption in research studies
    provenance: float = 0.0        # 0-1: Methodology documentation quality

    @property
    def overall(self) -> float:
        weights = {
            "literature": 0.25,
            "clinical_review": 0.25,
            "validation": 0.20,
            "usage": 0.15,
            "provenance": 0.15,
        }
        return sum(
            getattr(self, k) * w for k, w in weights.items()
        )

    def to_dict(self) -> dict:
        return {
            "Literature": self.literature,
            "Clinical review": self.clinical_review,
            "Validation": self.validation,
            "Usage": self.usage,
            "Provenance": self.provenance,
        }


# ---------------------------------------------------------------------------
# Codelist (expanded with Table 1 fields)
# ---------------------------------------------------------------------------

@dataclass
class Codelist:
    id: str
    name: str
    coding_system: CodingSystem
    codes: list[Code] = field(default_factory=list)
    version: str = "1.0"
    description: str = ""
    # Table 1: coding system version/release date
    coding_system_version: str = ""       # e.g. "SNOMED CT UK Edition 2024-04-01"
    coding_system_release: Optional[date] = None

    @property
    def code_count(self) -> int:
        return len([c for c in self.codes if c.is_included])

    @property
    def excluded_count(self) -> int:
        return len([c for c in self.codes if not c.is_included])


# ---------------------------------------------------------------------------
# Population constraints (Table 1)
# ---------------------------------------------------------------------------

@dataclass
class PopulationConstraints:
    """Table 1: Who is the phenotype intended for?"""
    sex: Sex = Sex.BOTH
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    inclusion_criteria: str = ""
    exclusion_criteria: str = ""
    notes: str = ""


# ---------------------------------------------------------------------------
# Accession ID and URL conventions (citation-grade)
# ---------------------------------------------------------------------------

# Base URL for stable phenotype references (configurable per deployment)
OPENPHENOTYPES_BASE_URL = "https://openphenotypes.org"


@dataclass
class AccessionID:
    """Citation-grade persistent identifier for a phenotype version.

    Pattern: OP-<nnnn>.<version>  e.g. OP-0001.v2.1
    Stable URL: {base}/phenotypes/OP-0001/v2.1
    """
    prefix: str = "OP"
    number: int = 0
    version: str = "1.0"

    @property
    def accession(self) -> str:
        return f"{self.prefix}-{self.number:04d}.v{self.version}"

    @property
    def stable_url(self) -> str:
        return f"{OPENPHENOTYPES_BASE_URL}/phenotypes/{self.prefix}-{self.number:04d}/v{self.version}"

    @property
    def latest_url(self) -> str:
        return f"{OPENPHENOTYPES_BASE_URL}/phenotypes/{self.prefix}-{self.number:04d}/latest"


# ---------------------------------------------------------------------------
# Phenotype (full FAIR-compliant model)
# ---------------------------------------------------------------------------

@dataclass
class Phenotype:
    id: str
    name: str
    short_name: str
    phenotype_type: PhenotypeType
    therapeutic_area: TherapeuticArea
    description: str

    # --- Citation-grade identifier (B) ---
    accession: AccessionID = field(default_factory=AccessionID)

    # --- Codelists (may span multiple coding systems) ---
    codelists: list[Codelist] = field(default_factory=list)

    # --- Ontology terms for semantic search (C / Table 1) ---
    ontology_terms: list[OntologyTerm] = field(default_factory=list)

    # --- Population constraints (Table 1) ---
    population: PopulationConstraints = field(default_factory=PopulationConstraints)

    # --- Authors and publications ---
    authors: list[Author] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)

    # --- Validation lifecycle ---
    validation_status: ValidationStatus = ValidationStatus.DRAFT
    evidence_score: EvidenceScore = field(default_factory=EvidenceScore)

    # --- Structured validation evidence (E / Table 1) ---
    validations: list[ValidationEvidence] = field(default_factory=list)

    # --- Clinical endorsements ---
    clinical_endorsements: list[ClinicalEndorsement] = field(default_factory=list)

    # --- Data source compatibility ---
    data_sources: list[str] = field(default_factory=list)

    # --- Dataset provenance (Table 1) ---
    dataset_provenance: list[DatasetProvenance] = field(default_factory=list)

    # --- Implementation artefacts (D / Table 1) ---
    implementations: list[Implementation] = field(default_factory=list)
    dummy_data_examples: list[DummyDataExample] = field(default_factory=list)
    qc_rules: list[QCRule] = field(default_factory=list)
    data_preprocessing: str = ""  # Dataset-specific guidance

    # --- Provenance ---
    methodology: str = ""
    logic_description: str = ""  # Plain-English algorithm description
    created_date: date = field(default_factory=date.today)
    updated_date: date = field(default_factory=date.today)
    version: str = "1.0"
    source_code_url: str = ""  # Table 1: mandatory source code link

    # --- Core/use hierarchy (G) ---
    is_core_definition: bool = True  # False = study-specific use/derivation
    parent_phenotype_id: Optional[str] = None
    child_use_ids: list[str] = field(default_factory=list)  # Study uses derived from this core
    related_phenotype_ids: list[str] = field(default_factory=list)
    source_repository: str = ""

    # --- Tags for search ---
    tags: list[str] = field(default_factory=list)

    # --- Valid event date range (Table 1) ---
    valid_date_start: Optional[date] = None  # Phenotype only applicable after this date
    valid_date_end: Optional[date] = None    # Phenotype only applicable before this date

    @property
    def coding_systems(self) -> list[CodingSystem]:
        return list({cl.coding_system for cl in self.codelists})

    @property
    def total_codes(self) -> int:
        return sum(cl.code_count for cl in self.codelists)

    @property
    def primary_publication(self) -> Optional[Publication]:
        for pub in self.publications:
            if pub.is_primary:
                return pub
        return self.publications[0] if self.publications else None

    @property
    def primary_ontology_term(self) -> Optional[OntologyTerm]:
        for term in self.ontology_terms:
            if term.is_primary:
                return term
        return self.ontology_terms[0] if self.ontology_terms else None


# ---------------------------------------------------------------------------
# Semantic validation pipeline (F)
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    """A single issue found by the semantic validation pipeline."""
    severity: str   # "error", "warning", "info"
    field: str
    message: str
    suggestion: str = ""


def validate_phenotype(p: Phenotype) -> list[ValidationIssue]:
    """Semantic validation pipeline for phenotype submissions (F).

    Checks mandatory field presence, code format consistency, duplicate
    detection, and minimum metadata completeness. Returns a list of
    issues; an empty list means the phenotype passes validation.
    """
    issues: list[ValidationIssue] = []

    # --- Mandatory field checks ---
    if not p.name.strip():
        issues.append(ValidationIssue("error", "name", "Phenotype name is required."))
    if not p.description.strip():
        issues.append(ValidationIssue("error", "description", "Description is required."))
    if not p.authors:
        issues.append(ValidationIssue("error", "authors", "At least one author is required."))
    if not p.codelists:
        issues.append(ValidationIssue("error", "codelists", "At least one codelist is required."))
    if not p.ontology_terms:
        issues.append(ValidationIssue("warning", "ontology_terms",
                                       "No ontology terms provided. Ontology terms improve discoverability.",
                                       "Add at least one SNOMED CT or ICD-10 ontology term."))
    if not p.methodology.strip():
        issues.append(ValidationIssue("warning", "methodology",
                                       "No methodology description provided.",
                                       "Describe how codes were identified and reviewed."))
    if not p.source_code_url:
        issues.append(ValidationIssue("warning", "source_code_url",
                                       "No source code link provided (Table 1 mandatory field).",
                                       "Provide a link to the source repository."))

    # --- Code format validation ---
    _CODE_PATTERNS: dict[CodingSystem, str] = {
        CodingSystem.ICD10: r"^[A-Z]\d{2}(\.\d{1,4})?$",
        CodingSystem.SNOMED_CT: r"^\d{6,18}$",
        CodingSystem.BNF: r"^\d{4,15}[A-Z0-9]*$",
    }
    for cl in p.codelists:
        seen_codes: set[str] = set()
        pattern = _CODE_PATTERNS.get(cl.coding_system)
        for code in cl.codes:
            # Duplicate check
            if code.code in seen_codes:
                issues.append(ValidationIssue(
                    "error", f"codelists.{cl.id}",
                    f"Duplicate code '{code.code}' in codelist '{cl.name}'.",
                ))
            seen_codes.add(code.code)

            # Format check (if we have a pattern for this system)
            if pattern and not re.match(pattern, code.code):
                issues.append(ValidationIssue(
                    "warning", f"codelists.{cl.id}.codes",
                    f"Code '{code.code}' may not match expected {cl.coding_system.value} format.",
                    f"Expected pattern: {pattern}",
                ))

        # Coding system version recommended
        if not cl.coding_system_version:
            issues.append(ValidationIssue(
                "info", f"codelists.{cl.id}.coding_system_version",
                f"Coding system version not specified for '{cl.name}'.",
                "Specify the coding system edition/release used.",
            ))

    # --- Publication checks ---
    primary_pubs = [pub for pub in p.publications if pub.is_primary]
    if p.publications and not primary_pubs:
        issues.append(ValidationIssue(
            "info", "publications",
            "No primary publication flagged.",
            "Mark the defining publication with is_primary=True.",
        ))

    # --- Validation evidence completeness ---
    if not p.validations:
        issues.append(ValidationIssue(
            "info", "validations",
            "No structured validation evidence provided.",
            "Add validation results with method, dataset, and metrics.",
        ))

    # --- Population constraints ---
    if not p.population.inclusion_criteria and not p.population.exclusion_criteria:
        issues.append(ValidationIssue(
            "info", "population",
            "No inclusion/exclusion criteria specified.",
            "Document the target population for this phenotype.",
        ))

    return issues


def validation_summary(issues: list[ValidationIssue]) -> dict:
    """Summarise validation issues by severity."""
    counts = {"error": 0, "warning": 0, "info": 0}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return {
        "passed": counts["error"] == 0,
        "errors": counts["error"],
        "warnings": counts["warning"],
        "info": counts["info"],
        "total_issues": sum(counts.values()),
    }
