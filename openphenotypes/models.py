"""
Data models for OpenPhenotypes.

Defines the core domain objects: Phenotype, Codelist, Code, and supporting
metadata types. Designed to unify the best metadata from OpenCodelists,
HDR UK Phenotype Library, OHDSI, ClinicalCodes, and Keele.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


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


@dataclass
class Code:
    code: str
    term: str
    coding_system: CodingSystem
    is_included: bool = True  # False = excluded code


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


@dataclass
class Codelist:
    id: str
    name: str
    coding_system: CodingSystem
    codes: list[Code] = field(default_factory=list)
    version: str = "1.0"
    description: str = ""

    @property
    def code_count(self) -> int:
        return len([c for c in self.codes if c.is_included])


@dataclass
class Phenotype:
    id: str
    name: str
    short_name: str
    phenotype_type: PhenotypeType
    therapeutic_area: TherapeuticArea
    description: str

    # Codelists (may span multiple coding systems)
    codelists: list[Codelist] = field(default_factory=list)

    # Metadata
    authors: list[Author] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.DRAFT
    evidence_score: EvidenceScore = field(default_factory=EvidenceScore)

    # Data source compatibility
    data_sources: list[str] = field(default_factory=list)

    # Provenance
    methodology: str = ""
    created_date: date = field(default_factory=date.today)
    updated_date: date = field(default_factory=date.today)
    version: str = "1.0"

    # Relationships
    parent_phenotype_id: Optional[str] = None
    related_phenotype_ids: list[str] = field(default_factory=list)
    source_repository: str = ""  # e.g. "OpenCodelists", "HDR UK", etc.

    # Tags for search
    tags: list[str] = field(default_factory=list)

    @property
    def coding_systems(self) -> list[CodingSystem]:
        return list({cl.coding_system for cl in self.codelists})

    @property
    def total_codes(self) -> int:
        return sum(cl.code_count for cl in self.codelists)
