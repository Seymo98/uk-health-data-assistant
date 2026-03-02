"""
Sample phenotype and codelist data for the OpenPhenotypes prototype.

Includes realistic phenotype definitions spanning multiple therapeutic areas,
coding systems, and validation statuses. Modelled on real-world codelists
from OpenCodelists, HDR UK Phenotype Library, ClinicalCodes, and Keele HCDR.
"""

from datetime import date

from .models import (
    AccessionID,
    Author,
    ClinicalEndorsement,
    Code,
    CodePosition,
    Codelist,
    CodingSystem,
    DatasetProvenance,
    DummyDataExample,
    EvidenceScore,
    Implementation,
    OntologyTerm,
    Phenotype,
    PhenotypeType,
    PopulationConstraints,
    Publication,
    QCRule,
    Sex,
    TherapeuticArea,
    ValidationEvidence,
    ValidationMethod,
    ValidationStatus,
)

# ---------------------------------------------------------------------------
# Shared authors
# ---------------------------------------------------------------------------

_AUTHORS = {
    "bennett": Author("Alex Walker", "Bennett Institute for Applied Data Science, Oxford", "0000-0002-1234-5678"),
    "hdruk": Author("Spiros Denaxas", "HDR UK / UCL", "0000-0001-9612-7791"),
    "keele": Author("Kelvin Jordan", "Keele University", "0000-0003-0001-1234"),
    "manchester": Author("Evangelos Kontopantelis", "University of Manchester", "0000-0001-6450-5815"),
    "cambridge": Author("Katherine Mansfield", "University of Cambridge"),
    "edinburgh": Author("Cathie Sudlow", "University of Edinburgh / HDR UK", "0000-0002-7524-3646"),
    "bristol": Author("Jonathan Sterne", "University of Bristol"),
    "caldicott": Author("Sarah Cadman", "NHS England"),
}

# ---------------------------------------------------------------------------
# 1. Type 2 Diabetes
# ---------------------------------------------------------------------------

_t2dm_snomed = Codelist(
    id="cl-t2dm-snomed",
    name="Type 2 diabetes mellitus (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="2.1",
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
    description="SNOMED CT codes for type 2 diabetes mellitus including subtypes.",
    codes=[
        Code("44054006", "Diabetes mellitus type 2", CodingSystem.SNOMED_CT),
        Code("313436004", "Type 2 diabetes mellitus without complication", CodingSystem.SNOMED_CT),
        Code("314902007", "Type 2 diabetes mellitus with peripheral angiopathy", CodingSystem.SNOMED_CT),
        Code("314903002", "Type 2 diabetes mellitus with arthropathy", CodingSystem.SNOMED_CT),
        Code("314904008", "Type 2 diabetes mellitus with neuropathic arthropathy", CodingSystem.SNOMED_CT),
        Code("422034002", "Diabetic retinopathy associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("421847006", "Ketoacidotic coma in type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("421750000", "Ketoacidosis in type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("421631007", "Gangrene associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("420279001", "Renal disorder associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("420436000", "Mononeuropathy associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("421326000", "Disorder of nervous system associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("420715001", "Persistent microalbuminuria due to type 2 diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("420756003", "Cataract associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("427089005", "Diabetes mellitus due to cystic fibrosis", CodingSystem.SNOMED_CT, is_included=False),
    ],
)

_t2dm_icd10 = Codelist(
    id="cl-t2dm-icd10",
    name="Type 2 diabetes mellitus (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="2.1",
    coding_system_version="ICD-10 5th Edition 2019",
    description="ICD-10 codes for type 2 diabetes mellitus.",
    codes=[
        Code("E11", "Type 2 diabetes mellitus", CodingSystem.ICD10),
        Code("E11.0", "Type 2 DM with coma", CodingSystem.ICD10),
        Code("E11.1", "Type 2 DM with ketoacidosis", CodingSystem.ICD10),
        Code("E11.2", "Type 2 DM with kidney complications", CodingSystem.ICD10),
        Code("E11.3", "Type 2 DM with ophthalmic complications", CodingSystem.ICD10),
        Code("E11.4", "Type 2 DM with neurological complications", CodingSystem.ICD10),
        Code("E11.5", "Type 2 DM with peripheral circulatory complications", CodingSystem.ICD10),
        Code("E11.6", "Type 2 DM with other specified complications", CodingSystem.ICD10),
        Code("E11.7", "Type 2 DM with multiple complications", CodingSystem.ICD10),
        Code("E11.8", "Type 2 DM with unspecified complications", CodingSystem.ICD10),
        Code("E11.9", "Type 2 DM without complications", CodingSystem.ICD10),
    ],
)

_t2dm_read = Codelist(
    id="cl-t2dm-read",
    name="Type 2 diabetes mellitus (Read v2)",
    coding_system=CodingSystem.READ_V2,
    version="1.3",
    description="Read v2 codes for type 2 diabetes in primary care records.",
    codes=[
        Code("C10F.", "Type 2 diabetes mellitus", CodingSystem.READ_V2),
        Code("C10F0", "Type 2 DM with renal complications", CodingSystem.READ_V2),
        Code("C10F1", "Type 2 DM with ophthalmic complications", CodingSystem.READ_V2),
        Code("C10F2", "Type 2 DM with neurological complications", CodingSystem.READ_V2),
        Code("C10F3", "Type 2 DM with multiple complications", CodingSystem.READ_V2),
        Code("C10F4", "Type 2 DM with ulcer", CodingSystem.READ_V2),
        Code("C10F5", "Type 2 DM with gangrene", CodingSystem.READ_V2),
        Code("C10F6", "Type 2 DM with retinopathy", CodingSystem.READ_V2),
        Code("C10F7", "Type 2 DM - poor control", CodingSystem.READ_V2),
        Code("C10FJ", "Insulin treated type 2 DM", CodingSystem.READ_V2),
        Code("C10FK", "Hyperosmolar non-ketotic state in type 2 DM", CodingSystem.READ_V2),
    ],
)

t2dm = Phenotype(
    id="ph-t2dm-001",
    name="Type 2 Diabetes Mellitus",
    short_name="T2DM",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.DIABETES_ENDOCRINE,
    description=(
        "Phenotype definition for type 2 diabetes mellitus (T2DM) using primary care, "
        "secondary care and medication codes. Includes diagnostic codes, complication "
        "codes and excludes gestational and type 1 diabetes."
    ),
    accession=AccessionID(prefix="OP", number=1, version="2.1"),
    codelists=[_t2dm_snomed, _t2dm_icd10, _t2dm_read],
    ontology_terms=[
        OntologyTerm("SNOMED CT", "44054006", "Diabetes mellitus type 2"),
        OntologyTerm("ICD-10", "E11", "Type 2 diabetes mellitus", is_primary=False),
        OntologyTerm("MeSH", "D003924", "Diabetes Mellitus, Type 2", is_primary=False),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Registered in GP practice for >= 1 year with acceptable data quality",
        exclusion_criteria="Type 1 diabetes only, gestational diabetes only, secondary diabetes (e.g. cystic fibrosis-related)",
    ),
    authors=[_AUTHORS["hdruk"], _AUTHORS["bennett"]],
    publications=[
        Publication(
            "Defining type 2 diabetes phenotypes using electronic health records",
            doi="10.1136/bmjopen-2020-example",
            journal="BMJ Open",
            year=2023,
            is_primary=True,
        ),
    ],
    validation_status=ValidationStatus.VALIDATED,
    evidence_score=EvidenceScore(
        literature=0.95,
        clinical_review=0.90,
        validation=0.85,
        usage=0.92,
        provenance=0.88,
    ),
    validations=[
        ValidationEvidence(
            method=ValidationMethod.CHART_REVIEW,
            dataset="CPRD GOLD",
            comparator="GP-confirmed diagnosis from clinical notes",
            ppv=0.92,
            sensitivity=0.88,
            specificity=0.96,
            sample_size=500,
            publication_doi="10.1136/bmjopen-2020-example",
            notes="Random sample of 500 patients with T2DM codes reviewed by two GPs.",
        ),
        ValidationEvidence(
            method=ValidationMethod.CROSS_DATABASE,
            dataset="CPRD GOLD + HES APC",
            comparator="Concordance between primary and secondary care records",
            ppv=0.90,
            sensitivity=0.85,
            sample_size=2000,
        ),
    ],
    clinical_endorsements=[
        ClinicalEndorsement(
            reviewer_name="Dr James Peters",
            reviewer_role="Consultant Diabetologist",
            institution="King's College Hospital",
            date=date(2023, 6, 15),
            notes="Codes reviewed and approved. Recommended addition of HbA1c supporting evidence.",
        ),
    ],
    data_sources=["CPRD GOLD", "CPRD Aurum", "OpenSAFELY-TPP", "HES APC", "SAIL", "UK Biobank"],
    dataset_provenance=[
        DatasetProvenance(
            dataset_name="CPRD GOLD March 2023",
            dataset_identifier="cprd-gold-2023-03",
            date_range_start=date(2000, 1, 1),
            date_range_end=date(2023, 3, 31),
            population_size=18_000_000,
            notes="Used for initial code identification and chart review validation.",
        ),
    ],
    implementations=[
        Implementation(
            language="SQL",
            label="CPRD GOLD SQL query",
            code=(
                "-- Type 2 Diabetes identification in CPRD GOLD\n"
                "SELECT DISTINCT p.patid\n"
                "FROM patient p\n"
                "JOIN clinical c ON p.patid = c.patid\n"
                "JOIN medical m ON c.medcode = m.medcode\n"
                "WHERE m.readcode IN (\n"
                "  'C10F.', 'C10F0', 'C10F1', 'C10F2',\n"
                "  'C10F3', 'C10F4', 'C10F5', 'C10F6',\n"
                "  'C10F7', 'C10FJ', 'C10FK'\n"
                ")\n"
                "AND c.eventdate IS NOT NULL\n"
                "-- Exclude patients with ONLY Type 1 codes\n"
                "EXCEPT\n"
                "SELECT DISTINCT p.patid\n"
                "FROM patient p\n"
                "JOIN clinical c ON p.patid = c.patid\n"
                "JOIN medical m ON c.medcode = m.medcode\n"
                "WHERE m.readcode LIKE 'C10E%'\n"
                "AND p.patid NOT IN (\n"
                "  SELECT patid FROM clinical c2\n"
                "  JOIN medical m2 ON c2.medcode = m2.medcode\n"
                "  WHERE m2.readcode LIKE 'C10F%'\n"
                ");"
            ),
            dataset_target="CPRD GOLD",
            source_url="https://github.com/opensafely/example-t2dm",
        ),
        Implementation(
            language="Pseudocode",
            label="Algorithm pseudocode",
            code=(
                "1. Identify patients with T2DM diagnostic code (SNOMED/Read/ICD-10)\n"
                "2. Exclude patients with ONLY T1DM codes (no concurrent T2DM)\n"
                "3. Exclude gestational diabetes codes occurring without other T2DM codes\n"
                "4. For incident cases: use earliest T2DM code date as index\n"
                "5. For prevalent cases: any T2DM code before study start date\n"
                "6. Optional: require supporting evidence:\n"
                "   - HbA1c >= 48 mmol/mol, OR\n"
                "   - Oral hypoglycaemic prescription within 12 months"
            ),
        ),
    ],
    dummy_data_examples=[
        DummyDataExample(
            description="T2DM identification from primary care records",
            input_data=(
                "patid,eventdate,readcode,readterm\n"
                "1001,2020-03-15,C10F.,Type 2 diabetes mellitus\n"
                "1001,2020-06-01,C10F7,Type 2 DM - poor control\n"
                "1002,2019-11-20,C10E.,Type 1 diabetes mellitus\n"
                "1003,2021-01-10,C10F6,Type 2 DM with retinopathy"
            ),
            expected_output=(
                "patid,t2dm_date,t2dm_flag\n"
                "1001,2020-03-15,1\n"
                "1002,,0\n"
                "1003,2021-01-10,1"
            ),
            notes="Patient 1002 excluded because they only have T1DM codes.",
        ),
    ],
    qc_rules=[
        QCRule(
            rule_id="QC-T2DM-01",
            description="Patient should not have both T1DM and T2DM codes without resolution logic applied",
            severity="warning",
            applies_to="All codelists",
        ),
        QCRule(
            rule_id="QC-T2DM-02",
            description="T2DM diagnosis date should be after patient's 18th birthday",
            severity="error",
            applies_to="Date validation",
        ),
        QCRule(
            rule_id="QC-T2DM-03",
            description="ICD-10 codes in primary diagnosis position preferred for incident T2DM identification",
            severity="info",
            applies_to="ICD-10 codelist",
        ),
    ],
    methodology=(
        "Codes identified through literature review, clinical expert consensus, "
        "and cross-referencing with existing validated codelists (Cambridge, Exeter). "
        "Validated against clinical notes in CPRD with PPV 92%, sensitivity 88%."
    ),
    logic_description=(
        "Identify patients with at least one T2DM diagnostic code in primary or "
        "secondary care. Apply exclusion logic to remove patients with only T1DM "
        "or gestational diabetes codes. Optionally require supporting laboratory "
        "or prescribing evidence for higher specificity."
    ),
    data_preprocessing=(
        "CPRD GOLD: Use acceptable patients only (accept=1). Map medcodes to Read v2 "
        "via medical dictionary. For HES linkage: use primary diagnosis position (d_order=1) "
        "for ICD-10 codes. Handle ICD-10 trailing dots (e.g. 'E11.' should match 'E11')."
    ),
    source_code_url="https://github.com/opensafely/example-t2dm",
    created_date=date(2022, 3, 15),
    updated_date=date(2024, 11, 1),
    version="2.1",
    is_core_definition=True,
    child_use_ids=["ph-t2dm-002"],
    related_phenotype_ids=["ph-t1dm-001", "ph-hba1c-001", "ph-metformin-001"],
    source_repository="HDR UK Phenotype Library",
    tags=["diabetes", "endocrine", "metabolic", "primary care", "secondary care", "NCD"],
)

# ---------------------------------------------------------------------------
# 2. Hypertension
# ---------------------------------------------------------------------------

_htn_snomed = Codelist(
    id="cl-htn-snomed",
    name="Essential hypertension (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.5",
    description="SNOMED CT codes for essential (primary) hypertension.",
    codes=[
        Code("59621000", "Essential hypertension", CodingSystem.SNOMED_CT),
        Code("38341003", "Hypertensive disorder", CodingSystem.SNOMED_CT),
        Code("194783001", "Secondary hypertension NOS", CodingSystem.SNOMED_CT, is_included=False),
        Code("46113002", "Hypertensive renal failure", CodingSystem.SNOMED_CT),
        Code("194774006", "Hypertensive heart disease without CCF", CodingSystem.SNOMED_CT),
        Code("194775007", "Hypertensive heart disease with CCF", CodingSystem.SNOMED_CT),
        Code("78975002", "Malignant essential hypertension", CodingSystem.SNOMED_CT),
        Code("1201005", "Benign essential hypertension", CodingSystem.SNOMED_CT),
    ],
)

_htn_icd10 = Codelist(
    id="cl-htn-icd10",
    name="Hypertension (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="1.5",
    description="ICD-10 codes for hypertensive diseases.",
    codes=[
        Code("I10", "Essential (primary) hypertension", CodingSystem.ICD10),
        Code("I11", "Hypertensive heart disease", CodingSystem.ICD10),
        Code("I11.0", "Hypertensive heart disease with heart failure", CodingSystem.ICD10),
        Code("I11.9", "Hypertensive heart disease without heart failure", CodingSystem.ICD10),
        Code("I12", "Hypertensive renal disease", CodingSystem.ICD10),
        Code("I13", "Hypertensive heart and renal disease", CodingSystem.ICD10),
        Code("I15", "Secondary hypertension", CodingSystem.ICD10, is_included=False),
    ],
)

hypertension = Phenotype(
    id="ph-htn-001",
    name="Essential Hypertension",
    short_name="Hypertension",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.CARDIOVASCULAR,
    description=(
        "Phenotype for essential (primary) hypertension. Includes diagnostic codes "
        "from primary and secondary care. Excludes secondary and pregnancy-related "
        "hypertension."
    ),
    accession=AccessionID(prefix="OP", number=2, version="1.5"),
    codelists=[_htn_snomed, _htn_icd10],
    ontology_terms=[
        OntologyTerm("SNOMED CT", "59621000", "Essential hypertension"),
        OntologyTerm("ICD-10", "I10", "Essential (primary) hypertension", is_primary=False),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH, age_min=18,
        exclusion_criteria="Secondary hypertension, pregnancy-related hypertension",
    ),
    authors=[_AUTHORS["cambridge"], _AUTHORS["hdruk"]],
    publications=[
        Publication(
            "Hypertension phenotyping in UK primary care EHR",
            doi="10.1093/ije/example-htn",
            journal="International Journal of Epidemiology",
            year=2022,
            is_primary=True,
        ),
    ],
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.90,
        clinical_review=0.85,
        validation=0.80,
        usage=0.95,
        provenance=0.82,
    ),
    validations=[
        ValidationEvidence(
            method=ValidationMethod.CROSS_DATABASE,
            dataset="CPRD GOLD + HES APC",
            comparator="Blood pressure >= 140/90 on 2 occasions",
            ppv=0.89,
            sensitivity=0.91,
            sample_size=2000,
        ),
    ],
    clinical_endorsements=[
        ClinicalEndorsement(
            reviewer_name="Prof Mark Caulfield",
            reviewer_role="Professor of Clinical Pharmacology",
            institution="Queen Mary University of London",
            date=date(2022, 3, 1),
        ),
    ],
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "OpenSAFELY-TPP", "UK Biobank"],
    methodology=(
        "Codes curated from existing CALIBER phenotype algorithms with expert "
        "cardiology review. Validated using blood pressure measurements as gold "
        "standard. PPV 89%, sensitivity 91%."
    ),
    created_date=date(2021, 6, 10),
    updated_date=date(2024, 8, 20),
    version="1.5",
    related_phenotype_ids=["ph-chd-001", "ph-stroke-001", "ph-ckd-001"],
    source_repository="CALIBER / HDR UK",
    tags=["cardiovascular", "blood pressure", "NCD", "primary care", "CALIBER"],
)

# ---------------------------------------------------------------------------
# 3. Depression
# ---------------------------------------------------------------------------

_dep_snomed = Codelist(
    id="cl-dep-snomed",
    name="Depression (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="3.0",
    description="SNOMED CT codes for depressive disorders.",
    codes=[
        Code("35489007", "Depressive disorder", CodingSystem.SNOMED_CT),
        Code("386616008", "Major depressive disorder, single episode", CodingSystem.SNOMED_CT),
        Code("36923009", "Major depressive disorder, recurrent", CodingSystem.SNOMED_CT),
        Code("310495003", "Mild depression", CodingSystem.SNOMED_CT),
        Code("310496002", "Moderate depression", CodingSystem.SNOMED_CT),
        Code("310497006", "Severe depression", CodingSystem.SNOMED_CT),
        Code("40379007", "Mild recurrent major depression", CodingSystem.SNOMED_CT),
        Code("66344007", "Recurrent major depression", CodingSystem.SNOMED_CT),
        Code("191616006", "Recurrent brief depressive disorder", CodingSystem.SNOMED_CT),
        Code("78667006", "Dysthymia", CodingSystem.SNOMED_CT),
        Code("192080009", "Chronic depression", CodingSystem.SNOMED_CT),
        Code("87512008", "Mild major depression single episode", CodingSystem.SNOMED_CT),
        Code("370143000", "Major depressive disorder", CodingSystem.SNOMED_CT),
    ],
)

_dep_icd10 = Codelist(
    id="cl-dep-icd10",
    name="Depression (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="3.0",
    description="ICD-10 codes for depressive episodes and recurrent depression.",
    codes=[
        Code("F32", "Depressive episode", CodingSystem.ICD10),
        Code("F32.0", "Mild depressive episode", CodingSystem.ICD10),
        Code("F32.1", "Moderate depressive episode", CodingSystem.ICD10),
        Code("F32.2", "Severe depressive episode without psychotic symptoms", CodingSystem.ICD10),
        Code("F32.3", "Severe depressive episode with psychotic symptoms", CodingSystem.ICD10),
        Code("F32.8", "Other depressive episodes", CodingSystem.ICD10),
        Code("F32.9", "Depressive episode, unspecified", CodingSystem.ICD10),
        Code("F33", "Recurrent depressive disorder", CodingSystem.ICD10),
        Code("F33.0", "Recurrent depressive disorder, current episode mild", CodingSystem.ICD10),
        Code("F33.1", "Recurrent depressive disorder, current episode moderate", CodingSystem.ICD10),
        Code("F33.2", "Recurrent depressive disorder, severe without psychotic symptoms", CodingSystem.ICD10),
        Code("F33.3", "Recurrent depressive disorder, severe with psychotic symptoms", CodingSystem.ICD10),
        Code("F34.1", "Dysthymia", CodingSystem.ICD10),
    ],
)

depression = Phenotype(
    id="ph-dep-001",
    name="Depression",
    short_name="Depression",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.MENTAL_HEALTH,
    description=(
        "Broad phenotype for depressive disorders including major depressive "
        "disorder (single and recurrent episodes), dysthymia, and chronic "
        "depression. Excludes bipolar depression and adjustment disorders."
    ),
    accession=AccessionID(prefix="OP", number=3, version="3.0"),
    codelists=[_dep_snomed, _dep_icd10],
    ontology_terms=[
        OntologyTerm("SNOMED CT", "35489007", "Depressive disorder"),
        OntologyTerm("ICD-10", "F32", "Depressive episode", is_primary=False),
    ],
    population=PopulationConstraints(sex=Sex.BOTH, exclusion_criteria="Bipolar depression, adjustment disorders"),
    authors=[_AUTHORS["manchester"], _AUTHORS["edinburgh"]],
    publications=[
        Publication(
            "Defining depression in UK primary care: a clinical code validation study",
            doi="10.1016/j.jad.2023.example",
            journal="Journal of Affective Disorders",
            year=2023,
        ),
        Publication(
            "Common mental health disorders in electronic health records",
            journal="Psychological Medicine",
            year=2021,
        ),
    ],
    validation_status=ValidationStatus.PEER_REVIEWED,
    evidence_score=EvidenceScore(
        literature=0.88,
        clinical_review=0.82,
        validation=0.75,
        usage=0.90,
        provenance=0.80,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "SAIL", "Research Data Scotland"],
    methodology=(
        "Developed using systematic review of existing depression codelists "
        "(ClinicalCodes repository, CALIBER) and refined with psychiatrist input. "
        "Broad definition includes any recorded depressive episode."
    ),
    created_date=date(2021, 1, 20),
    updated_date=date(2024, 6, 15),
    version="3.0",
    related_phenotype_ids=["ph-anxiety-001", "ph-ssri-001"],
    source_repository="ClinicalCodes / University of Manchester",
    tags=["mental health", "depression", "mood disorder", "primary care", "common mental disorder"],
)

# ---------------------------------------------------------------------------
# 4. Asthma
# ---------------------------------------------------------------------------

_asthma_snomed = Codelist(
    id="cl-asthma-snomed",
    name="Asthma (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="2.0",
    description="SNOMED CT codes for asthma diagnosis.",
    codes=[
        Code("195967001", "Asthma", CodingSystem.SNOMED_CT),
        Code("31387002", "Exercise-induced asthma", CodingSystem.SNOMED_CT),
        Code("233678006", "Childhood asthma", CodingSystem.SNOMED_CT),
        Code("266361008", "Non-allergic asthma", CodingSystem.SNOMED_CT),
        Code("389145006", "Allergic asthma", CodingSystem.SNOMED_CT),
        Code("304527002", "Acute asthma", CodingSystem.SNOMED_CT),
        Code("370218001", "Mild asthma", CodingSystem.SNOMED_CT),
        Code("370219009", "Moderate asthma", CodingSystem.SNOMED_CT),
        Code("370221004", "Severe asthma", CodingSystem.SNOMED_CT),
        Code("707444001", "Uncomplicated asthma", CodingSystem.SNOMED_CT),
        Code("423889005", "Late onset asthma", CodingSystem.SNOMED_CT),
        Code("426656000", "Severe persistent asthma", CodingSystem.SNOMED_CT),
    ],
)

_asthma_icd10 = Codelist(
    id="cl-asthma-icd10",
    name="Asthma (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="2.0",
    description="ICD-10 codes for asthma.",
    codes=[
        Code("J45", "Asthma", CodingSystem.ICD10),
        Code("J45.0", "Predominantly allergic asthma", CodingSystem.ICD10),
        Code("J45.1", "Non-allergic asthma", CodingSystem.ICD10),
        Code("J45.8", "Mixed asthma", CodingSystem.ICD10),
        Code("J45.9", "Asthma, unspecified", CodingSystem.ICD10),
        Code("J46", "Status asthmaticus", CodingSystem.ICD10),
    ],
)

asthma = Phenotype(
    id="ph-asthma-001",
    name="Asthma",
    short_name="Asthma",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.RESPIRATORY,
    description=(
        "Phenotype for asthma diagnosis based on diagnostic codes from primary "
        "and secondary care. Includes allergic, non-allergic, exercise-induced, "
        "and severity subtypes. Excludes COPD overlap syndrome."
    ),
    accession=AccessionID(prefix="OP", number=4, version="2.0"),
    codelists=[_asthma_snomed, _asthma_icd10],
    ontology_terms=[OntologyTerm("SNOMED CT", "195967001", "Asthma")],
    population=PopulationConstraints(sex=Sex.BOTH, exclusion_criteria="COPD-asthma overlap syndrome"),
    authors=[_AUTHORS["bennett"], _AUTHORS["bristol"]],
    publications=[
        Publication(
            "Identifying asthma in UK electronic health records",
            doi="10.1136/thoraxjnl-2022-example",
            journal="Thorax",
            year=2022,
        ),
    ],
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.85,
        clinical_review=0.88,
        validation=0.82,
        usage=0.87,
        provenance=0.85,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "OpenSAFELY-TPP", "HES APC", "SAIL"],
    methodology=(
        "Based on OpenSAFELY asthma codelist with additional codes from BTS/SIGN "
        "guidelines review. Validated against GP-confirmed diagnosis."
    ),
    created_date=date(2020, 9, 1),
    updated_date=date(2024, 3, 10),
    version="2.0",
    related_phenotype_ids=["ph-copd-001", "ph-ics-001"],
    source_code_url="https://www.opencodelists.org/codelist/opensafely/asthma-diagnosis/",
    source_repository="OpenCodelists",
    tags=["respiratory", "asthma", "airways", "primary care", "OpenSAFELY"],
)

# ---------------------------------------------------------------------------
# 5. Chronic Kidney Disease
# ---------------------------------------------------------------------------

_ckd_snomed = Codelist(
    id="cl-ckd-snomed",
    name="Chronic kidney disease (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.2",
    description="SNOMED CT codes for CKD stages 1-5.",
    codes=[
        Code("709044004", "Chronic kidney disease", CodingSystem.SNOMED_CT),
        Code("431855005", "Chronic kidney disease stage 1", CodingSystem.SNOMED_CT),
        Code("431856006", "Chronic kidney disease stage 2", CodingSystem.SNOMED_CT),
        Code("433144002", "Chronic kidney disease stage 3", CodingSystem.SNOMED_CT),
        Code("431857002", "Chronic kidney disease stage 4", CodingSystem.SNOMED_CT),
        Code("433146000", "Chronic kidney disease stage 5", CodingSystem.SNOMED_CT),
        Code("46177005", "End-stage renal disease", CodingSystem.SNOMED_CT),
        Code("236578006", "Chronic glomerulonephritis", CodingSystem.SNOMED_CT),
        Code("90708001", "Kidney disease", CodingSystem.SNOMED_CT),
    ],
)

_ckd_icd10 = Codelist(
    id="cl-ckd-icd10",
    name="Chronic kidney disease (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="1.2",
    description="ICD-10 codes for CKD.",
    codes=[
        Code("N18", "Chronic kidney disease", CodingSystem.ICD10),
        Code("N18.1", "Chronic kidney disease, stage 1", CodingSystem.ICD10),
        Code("N18.2", "Chronic kidney disease, stage 2", CodingSystem.ICD10),
        Code("N18.3", "Chronic kidney disease, stage 3", CodingSystem.ICD10),
        Code("N18.4", "Chronic kidney disease, stage 4", CodingSystem.ICD10),
        Code("N18.5", "Chronic kidney disease, stage 5", CodingSystem.ICD10),
        Code("N18.9", "Chronic kidney disease, unspecified", CodingSystem.ICD10),
    ],
)

ckd = Phenotype(
    id="ph-ckd-001",
    name="Chronic Kidney Disease",
    short_name="CKD",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.RENAL,
    description=(
        "Phenotype for chronic kidney disease (CKD) stages 1-5 and end-stage "
        "renal disease. Based on diagnostic codes; can be combined with eGFR "
        "biomarker data for algorithmic phenotyping."
    ),
    accession=AccessionID(prefix="OP", number=5, version="1.2"),
    codelists=[_ckd_snomed, _ckd_icd10],
    ontology_terms=[OntologyTerm("SNOMED CT", "709044004", "Chronic kidney disease")],
    authors=[_AUTHORS["cambridge"]],
    publications=[
        Publication(
            "CKD phenotyping in UK electronic health records",
            journal="Kidney International",
            year=2023,
        ),
    ],
    validation_status=ValidationStatus.PEER_REVIEWED,
    evidence_score=EvidenceScore(
        literature=0.78,
        clinical_review=0.82,
        validation=0.70,
        usage=0.75,
        provenance=0.80,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "UK Biobank"],
    methodology=(
        "Diagnostic codes combined with eGFR threshold (< 60 mL/min/1.73m2 "
        "on two occasions > 90 days apart). Code-only version provided here."
    ),
    created_date=date(2022, 11, 5),
    updated_date=date(2024, 2, 28),
    version="1.2",
    related_phenotype_ids=["ph-t2dm-001", "ph-htn-001"],
    source_repository="CALIBER / HDR UK",
    tags=["renal", "kidney", "CKD", "eGFR", "CALIBER"],
)

# ---------------------------------------------------------------------------
# 6. COPD
# ---------------------------------------------------------------------------

_copd_snomed = Codelist(
    id="cl-copd-snomed",
    name="COPD (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.4",
    description="SNOMED CT codes for chronic obstructive pulmonary disease.",
    codes=[
        Code("13645005", "Chronic obstructive pulmonary disease", CodingSystem.SNOMED_CT),
        Code("185086009", "Chronic obstructive bronchitis", CodingSystem.SNOMED_CT),
        Code("87433001", "Pulmonary emphysema", CodingSystem.SNOMED_CT),
        Code("195951007", "Acute exacerbation of COPD", CodingSystem.SNOMED_CT),
        Code("313296004", "Mild chronic obstructive pulmonary disease", CodingSystem.SNOMED_CT),
        Code("313297008", "Moderate chronic obstructive pulmonary disease", CodingSystem.SNOMED_CT),
        Code("313299006", "Severe chronic obstructive pulmonary disease", CodingSystem.SNOMED_CT),
        Code("135836000", "End stage chronic obstructive airways disease", CodingSystem.SNOMED_CT),
    ],
)

copd = Phenotype(
    id="ph-copd-001",
    name="Chronic Obstructive Pulmonary Disease",
    short_name="COPD",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.RESPIRATORY,
    description=(
        "Phenotype for COPD including chronic obstructive bronchitis and "
        "emphysema. Includes severity staging and exacerbation codes."
    ),
    accession=AccessionID(prefix="OP", number=6, version="1.4"),
    codelists=[_copd_snomed],
    ontology_terms=[OntologyTerm("SNOMED CT", "13645005", "Chronic obstructive pulmonary disease")],
    authors=[_AUTHORS["bennett"]],
    publications=[
        Publication(
            "COPD codelists for OpenSAFELY studies",
            year=2021,
        ),
    ],
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.82,
        clinical_review=0.85,
        validation=0.78,
        usage=0.88,
        provenance=0.82,
    ),
    data_sources=["OpenSAFELY-TPP", "CPRD Aurum", "HES APC"],
    methodology="Developed by Bennett Institute for OpenSAFELY COVID-19 studies.",
    created_date=date(2020, 5, 1),
    updated_date=date(2023, 12, 1),
    version="1.4",
    related_phenotype_ids=["ph-asthma-001"],
    source_code_url="https://www.opencodelists.org/codelist/opensafely/copd/",
    source_repository="OpenCodelists",
    tags=["respiratory", "COPD", "emphysema", "OpenSAFELY"],
)

# ---------------------------------------------------------------------------
# 7. Atrial Fibrillation
# ---------------------------------------------------------------------------

_af_snomed = Codelist(
    id="cl-af-snomed",
    name="Atrial fibrillation (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="2.0",
    description="SNOMED CT codes for atrial fibrillation and flutter.",
    codes=[
        Code("49436004", "Atrial fibrillation", CodingSystem.SNOMED_CT),
        Code("5370000", "Atrial flutter", CodingSystem.SNOMED_CT),
        Code("312442005", "History of atrial fibrillation", CodingSystem.SNOMED_CT),
        Code("440028005", "Permanent atrial fibrillation", CodingSystem.SNOMED_CT),
        Code("440059007", "Persistent atrial fibrillation", CodingSystem.SNOMED_CT),
        Code("195080001", "Atrial fibrillation and flutter", CodingSystem.SNOMED_CT),
        Code("706923002", "Lone atrial fibrillation", CodingSystem.SNOMED_CT),
        Code("314208002", "Rapid atrial fibrillation", CodingSystem.SNOMED_CT),
    ],
)

_af_icd10 = Codelist(
    id="cl-af-icd10",
    name="Atrial fibrillation (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="2.0",
    description="ICD-10 codes for AF/flutter.",
    codes=[
        Code("I48", "Atrial fibrillation and flutter", CodingSystem.ICD10),
        Code("I48.0", "Paroxysmal atrial fibrillation", CodingSystem.ICD10),
        Code("I48.1", "Persistent atrial fibrillation", CodingSystem.ICD10),
        Code("I48.2", "Chronic atrial fibrillation", CodingSystem.ICD10),
        Code("I48.3", "Typical atrial flutter", CodingSystem.ICD10),
        Code("I48.4", "Atypical atrial flutter", CodingSystem.ICD10),
        Code("I48.9", "Atrial fibrillation and flutter, unspecified", CodingSystem.ICD10),
    ],
)

atrial_fibrillation = Phenotype(
    id="ph-af-001",
    name="Atrial Fibrillation",
    short_name="AF",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.CARDIOVASCULAR,
    description=(
        "Phenotype for atrial fibrillation and atrial flutter. Includes "
        "paroxysmal, persistent and permanent AF subtypes."
    ),
    accession=AccessionID(prefix="OP", number=7, version="2.0"),
    codelists=[_af_snomed, _af_icd10],
    ontology_terms=[OntologyTerm("SNOMED CT", "49436004", "Atrial fibrillation")],
    authors=[_AUTHORS["hdruk"], _AUTHORS["cambridge"]],
    publications=[
        Publication(
            "Atrial fibrillation in electronic health records: the CALIBER approach",
            doi="10.1136/heartjnl-2021-example",
            journal="Heart",
            year=2021,
        ),
    ],
    validation_status=ValidationStatus.VALIDATED,
    evidence_score=EvidenceScore(
        literature=0.92,
        clinical_review=0.88,
        validation=0.85,
        usage=0.90,
        provenance=0.86,
    ),
    validations=[
        ValidationEvidence(
            method=ValidationMethod.REGISTRY_COMPARISON,
            dataset="CPRD GOLD",
            comparator="ECG-confirmed AF",
            ppv=0.95,
            sensitivity=0.87,
            sample_size=800,
        ),
    ],
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "OpenSAFELY-TPP", "UK Biobank"],
    methodology=(
        "CALIBER phenotype algorithm using primary care Read/SNOMED codes plus "
        "HES ICD-10 codes. Validated against ECG-confirmed AF. PPV 95%."
    ),
    created_date=date(2019, 8, 1),
    updated_date=date(2024, 5, 15),
    version="2.0",
    related_phenotype_ids=["ph-stroke-001", "ph-htn-001"],
    source_repository="CALIBER / HDR UK",
    tags=["cardiovascular", "arrhythmia", "AF", "stroke risk", "CALIBER"],
)

# ---------------------------------------------------------------------------
# 8. Stroke
# ---------------------------------------------------------------------------

_stroke_snomed = Codelist(
    id="cl-stroke-snomed",
    name="Stroke (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.8",
    description="SNOMED CT codes for ischaemic and haemorrhagic stroke.",
    codes=[
        Code("230690007", "Cerebrovascular accident", CodingSystem.SNOMED_CT),
        Code("422504002", "Ischaemic stroke", CodingSystem.SNOMED_CT),
        Code("274100004", "Cerebral haemorrhage", CodingSystem.SNOMED_CT),
        Code("230691006", "Cerebrovascular accident due to cerebral haemorrhage", CodingSystem.SNOMED_CT),
        Code("432504007", "Cerebral infarction", CodingSystem.SNOMED_CT),
        Code("195185009", "Cerebral infarction due to thrombosis", CodingSystem.SNOMED_CT),
        Code("195186005", "Cerebral infarction due to embolism", CodingSystem.SNOMED_CT),
        Code("266253001", "Transient ischaemic attack", CodingSystem.SNOMED_CT, is_included=False),
    ],
)

_stroke_icd10 = Codelist(
    id="cl-stroke-icd10",
    name="Stroke (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="1.8",
    description="ICD-10 codes for stroke (ischaemic and haemorrhagic).",
    codes=[
        Code("I60", "Subarachnoid haemorrhage", CodingSystem.ICD10),
        Code("I61", "Intracerebral haemorrhage", CodingSystem.ICD10),
        Code("I62", "Other nontraumatic intracranial haemorrhage", CodingSystem.ICD10),
        Code("I63", "Cerebral infarction", CodingSystem.ICD10),
        Code("I63.0", "Cerebral infarction due to thrombosis of precerebral arteries", CodingSystem.ICD10),
        Code("I63.1", "Cerebral infarction due to embolism of precerebral arteries", CodingSystem.ICD10),
        Code("I63.9", "Cerebral infarction, unspecified", CodingSystem.ICD10),
        Code("I64", "Stroke, not specified as haemorrhage or infarction", CodingSystem.ICD10),
        Code("G45", "Transient ischaemic attack", CodingSystem.ICD10, is_included=False),
    ],
)

stroke = Phenotype(
    id="ph-stroke-001",
    name="Stroke (Ischaemic and Haemorrhagic)",
    short_name="Stroke",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.CARDIOVASCULAR,
    description=(
        "Phenotype for stroke including ischaemic stroke, intracerebral "
        "haemorrhage and subarachnoid haemorrhage. TIA explicitly excluded."
    ),
    accession=AccessionID(prefix="OP", number=8, version="1.8"),
    codelists=[_stroke_snomed, _stroke_icd10],
    ontology_terms=[OntologyTerm("SNOMED CT", "230690007", "Cerebrovascular accident")],
    population=PopulationConstraints(sex=Sex.BOTH, exclusion_criteria="Transient ischaemic attack (TIA)"),
    authors=[_AUTHORS["hdruk"], _AUTHORS["edinburgh"]],
    publications=[
        Publication(
            "Stroke phenotyping in linked primary and secondary care records",
            doi="10.1136/jnnp-2022-example",
            journal="Journal of Neurology, Neurosurgery & Psychiatry",
            year=2022,
        ),
    ],
    validation_status=ValidationStatus.VALIDATED,
    evidence_score=EvidenceScore(
        literature=0.90,
        clinical_review=0.92,
        validation=0.88,
        usage=0.85,
        provenance=0.90,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "SAIL", "Scottish Safe Haven"],
    methodology=(
        "CALIBER stroke phenotype using hospital episode codes (primary position) "
        "plus GP diagnostic codes. Excludes TIA. Validated against SSNAP registry."
    ),
    created_date=date(2020, 2, 1),
    updated_date=date(2024, 9, 1),
    version="1.8",
    related_phenotype_ids=["ph-af-001", "ph-htn-001"],
    source_repository="CALIBER / HDR UK",
    tags=["cardiovascular", "stroke", "cerebrovascular", "neurology", "CALIBER"],
)

# ---------------------------------------------------------------------------
# 9. Osteoarthritis (Keele-style)
# ---------------------------------------------------------------------------

_oa_read = Codelist(
    id="cl-oa-read",
    name="Osteoarthritis (Read v2)",
    coding_system=CodingSystem.READ_V2,
    version="1.0",
    description="Read v2 codes for osteoarthritis used in Keele primary care studies.",
    codes=[
        Code("N05..", "Osteoarthritis and allied disorders", CodingSystem.READ_V2),
        Code("N050.", "Generalised osteoarthritis", CodingSystem.READ_V2),
        Code("N051.", "Osteoarthritis of hip", CodingSystem.READ_V2),
        Code("N052.", "Osteoarthritis of knee", CodingSystem.READ_V2),
        Code("N053.", "Osteoarthritis of shoulder", CodingSystem.READ_V2),
        Code("N054.", "Osteoarthritis of hand", CodingSystem.READ_V2),
        Code("N055.", "Osteoarthritis of spine", CodingSystem.READ_V2),
        Code("N056.", "Osteoarthritis of ankle and foot", CodingSystem.READ_V2),
    ],
)

_oa_snomed = Codelist(
    id="cl-oa-snomed",
    name="Osteoarthritis (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.0",
    description="SNOMED CT codes for osteoarthritis.",
    codes=[
        Code("396275006", "Osteoarthritis", CodingSystem.SNOMED_CT),
        Code("239872002", "Osteoarthritis of hip", CodingSystem.SNOMED_CT),
        Code("239873007", "Osteoarthritis of knee", CodingSystem.SNOMED_CT),
        Code("67315001", "Generalised osteoarthritis", CodingSystem.SNOMED_CT),
        Code("201834006", "Localised, primary osteoarthritis of the hand", CodingSystem.SNOMED_CT),
        Code("48461003", "Osteoarthritis of shoulder region", CodingSystem.SNOMED_CT),
    ],
)

osteoarthritis = Phenotype(
    id="ph-oa-001",
    name="Osteoarthritis",
    short_name="OA",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.MUSCULOSKELETAL,
    description=(
        "Phenotype for osteoarthritis including site-specific subtypes "
        "(hip, knee, hand, shoulder, spine). Developed from Keele University "
        "primary care musculoskeletal research programme."
    ),
    accession=AccessionID(prefix="OP", number=9, version="1.0"),
    codelists=[_oa_read, _oa_snomed],
    ontology_terms=[OntologyTerm("SNOMED CT", "396275006", "Osteoarthritis")],
    authors=[_AUTHORS["keele"]],
    publications=[
        Publication(
            "Consultation incidence of osteoarthritis in UK primary care",
            journal="Osteoarthritis and Cartilage",
            year=2020,
        ),
    ],
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.80,
        clinical_review=0.85,
        validation=0.72,
        usage=0.78,
        provenance=0.80,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "Keele CiPCA"],
    methodology=(
        "Developed by Keele Primary Care Centre Versus Arthritis using Read v2 "
        "mapped to SNOMED CT. Based on 20+ years of musculoskeletal primary care research."
    ),
    created_date=date(2018, 4, 1),
    updated_date=date(2023, 9, 1),
    version="1.0",
    related_phenotype_ids=[],
    source_repository="Keele HCDR Codelists",
    tags=["musculoskeletal", "osteoarthritis", "joint", "primary care", "Keele"],
)

# ---------------------------------------------------------------------------
# 10. COVID-19
# ---------------------------------------------------------------------------

_covid_snomed = Codelist(
    id="cl-covid-snomed",
    name="COVID-19 (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="4.0",
    description="SNOMED CT codes for COVID-19 diagnosis and related conditions.",
    codes=[
        Code("840539006", "Disease caused by SARS-CoV-2", CodingSystem.SNOMED_CT),
        Code("840544004", "Suspected disease caused by SARS-CoV-2", CodingSystem.SNOMED_CT),
        Code("1240751000000100", "COVID-19", CodingSystem.SNOMED_CT),
        Code("1325161000000102", "COVID-19 confirmed by laboratory test", CodingSystem.SNOMED_CT),
        Code("1325171000000109", "COVID-19 confirmed using clinical diagnostic criteria", CodingSystem.SNOMED_CT),
        Code("1325181000000106", "Post-COVID-19 syndrome", CodingSystem.SNOMED_CT),
        Code("1119302008", "Acute disease caused by SARS-CoV-2", CodingSystem.SNOMED_CT),
        Code("138389411000119105", "Pneumonia caused by SARS-CoV-2", CodingSystem.SNOMED_CT),
    ],
)

_covid_icd10 = Codelist(
    id="cl-covid-icd10",
    name="COVID-19 (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="4.0",
    description="ICD-10 codes for COVID-19.",
    codes=[
        Code("U07.1", "COVID-19, virus identified", CodingSystem.ICD10),
        Code("U07.2", "COVID-19, virus not identified", CodingSystem.ICD10),
        Code("U09.9", "Post-COVID-19 condition, unspecified", CodingSystem.ICD10),
        Code("U10.9", "Multisystem inflammatory syndrome associated with COVID-19", CodingSystem.ICD10),
    ],
)

covid19 = Phenotype(
    id="ph-covid-001",
    name="COVID-19",
    short_name="COVID-19",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.INFECTIOUS_DISEASE,
    description=(
        "Phenotype for COVID-19 (disease caused by SARS-CoV-2) including "
        "confirmed, suspected, and post-COVID syndrome. Developed for "
        "OpenSAFELY pandemic research programme."
    ),
    accession=AccessionID(prefix="OP", number=10, version="4.0"),
    codelists=[_covid_snomed, _covid_icd10],
    ontology_terms=[
        OntologyTerm("SNOMED CT", "840539006", "Disease caused by SARS-CoV-2"),
        OntologyTerm("ICD-10", "U07.1", "COVID-19, virus identified", is_primary=False),
    ],
    population=PopulationConstraints(sex=Sex.BOTH),
    authors=[_AUTHORS["bennett"], _AUTHORS["hdruk"]],
    publications=[
        Publication(
            "Factors associated with COVID-19-related death using OpenSAFELY",
            doi="10.1038/s41586-020-2521-4",
            journal="Nature",
            year=2020,
            pubmed_id="32640463",
            is_primary=True,
        ),
    ],
    validation_status=ValidationStatus.VALIDATED,
    evidence_score=EvidenceScore(
        literature=0.98,
        clinical_review=0.95,
        validation=0.92,
        usage=0.98,
        provenance=0.95,
    ),
    validations=[
        ValidationEvidence(
            method=ValidationMethod.LAB_CONFIRMATION,
            dataset="OpenSAFELY-TPP",
            comparator="SGSS positive PCR test result",
            ppv=0.95,
            sensitivity=0.91,
            specificity=0.99,
            sample_size=10000,
        ),
    ],
    data_sources=["OpenSAFELY-TPP", "OpenSAFELY-EMIS", "HES APC", "CPRD Aurum", "ONS"],
    dataset_provenance=[
        DatasetProvenance(
            dataset_name="OpenSAFELY-TPP",
            dataset_identifier="opensafely-tpp-2023",
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2023, 12, 31),
            population_size=24_000_000,
        ),
    ],
    implementations=[
        Implementation(
            language="Pseudocode",
            label="COVID-19 case identification",
            code=(
                "1. Identify patients with COVID-19 diagnostic SNOMED code\n"
                "   OR positive SGSS test result linked via NHS number\n"
                "   OR COVID-19 ICD-10 code (U07.1, U07.2) in hospital episode\n"
                "2. Index date = earliest of: diagnostic code, positive test, admission\n"
                "3. For post-COVID: require U09.9 or SNOMED post-COVID code >= 12 weeks after index"
            ),
            source_url="https://github.com/opensafely/covid-vaccine-effectiveness-research",
        ),
    ],
    methodology=(
        "Developed iteratively during the pandemic using SGSS positive test results "
        "as reference standard. Refined through multiple OpenSAFELY studies."
    ),
    logic_description=(
        "Case identification combining GP diagnostic codes, SGSS laboratory test "
        "results, and hospital episode ICD-10 codes. Index date is the earliest "
        "recorded evidence of COVID-19."
    ),
    source_code_url="https://www.opencodelists.org/codelist/opensafely/covid-identification/",
    created_date=date(2020, 3, 15),
    updated_date=date(2024, 1, 10),
    version="4.0",
    valid_date_start=date(2020, 1, 1),
    related_phenotype_ids=[],
    source_repository="OpenCodelists",
    tags=["infectious disease", "COVID-19", "pandemic", "respiratory", "OpenSAFELY"],
)

# ---------------------------------------------------------------------------
# 11. Breast Cancer
# ---------------------------------------------------------------------------

_brca_snomed = Codelist(
    id="cl-brca-snomed",
    name="Breast cancer (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.3",
    description="SNOMED CT codes for breast cancer diagnosis.",
    codes=[
        Code("254837009", "Malignant neoplasm of breast", CodingSystem.SNOMED_CT),
        Code("188166003", "Carcinoma in situ of breast", CodingSystem.SNOMED_CT),
        Code("372064008", "Malignant neoplasm of female breast", CodingSystem.SNOMED_CT),
        Code("408643008", "Infiltrating duct carcinoma of breast", CodingSystem.SNOMED_CT),
        Code("82711006", "Infiltrating lobular carcinoma", CodingSystem.SNOMED_CT),
        Code("3898006", "Inflammatory carcinoma of breast", CodingSystem.SNOMED_CT),
    ],
)

_brca_icd10 = Codelist(
    id="cl-brca-icd10",
    name="Breast cancer (ICD-10)",
    coding_system=CodingSystem.ICD10,
    version="1.3",
    description="ICD-10 codes for breast cancer.",
    codes=[
        Code("C50", "Malignant neoplasm of breast", CodingSystem.ICD10),
        Code("C50.0", "Nipple and areola", CodingSystem.ICD10),
        Code("C50.1", "Central portion of breast", CodingSystem.ICD10),
        Code("C50.2", "Upper-inner quadrant of breast", CodingSystem.ICD10),
        Code("C50.3", "Lower-inner quadrant of breast", CodingSystem.ICD10),
        Code("C50.4", "Upper-outer quadrant of breast", CodingSystem.ICD10),
        Code("C50.5", "Lower-outer quadrant of breast", CodingSystem.ICD10),
        Code("C50.8", "Overlapping lesion of breast", CodingSystem.ICD10),
        Code("C50.9", "Breast, unspecified", CodingSystem.ICD10),
        Code("D05", "Carcinoma in situ of breast", CodingSystem.ICD10),
    ],
)

breast_cancer = Phenotype(
    id="ph-brca-001",
    name="Breast Cancer",
    short_name="Breast Ca",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.ONCOLOGY,
    description=(
        "Phenotype for breast cancer including invasive carcinoma and carcinoma "
        "in situ. Covers ductal, lobular and inflammatory subtypes."
    ),
    accession=AccessionID(prefix="OP", number=11, version="1.3"),
    codelists=[_brca_snomed, _brca_icd10],
    ontology_terms=[OntologyTerm("SNOMED CT", "254837009", "Malignant neoplasm of breast")],
    population=PopulationConstraints(sex=Sex.FEMALE),
    authors=[_AUTHORS["edinburgh"]],
    publications=[
        Publication(
            "Cancer registration phenotypes for UK Biobank studies",
            journal="British Journal of Cancer",
            year=2023,
        ),
    ],
    validation_status=ValidationStatus.PEER_REVIEWED,
    evidence_score=EvidenceScore(
        literature=0.85,
        clinical_review=0.80,
        validation=0.82,
        usage=0.78,
        provenance=0.80,
    ),
    data_sources=["HES APC", "National Cancer Registry", "CPRD GOLD", "UK Biobank"],
    methodology=(
        "Based on cancer registry linkage codes with secondary care HES codes. "
        "Cross-validated against NCRAS cancer registrations."
    ),
    created_date=date(2021, 7, 1),
    updated_date=date(2024, 4, 1),
    version="1.3",
    related_phenotype_ids=[],
    source_repository="HDR UK Phenotype Library",
    tags=["oncology", "breast cancer", "cancer", "screening"],
)

# ---------------------------------------------------------------------------
# 12. Metformin (medication phenotype)
# ---------------------------------------------------------------------------

_metformin_dmd = Codelist(
    id="cl-metformin-dmd",
    name="Metformin (dm+d)",
    coding_system=CodingSystem.DMD,
    version="1.1",
    description="Dictionary of medicines and devices codes for metformin preparations.",
    codes=[
        Code("325278007", "Metformin hydrochloride 500mg tablets", CodingSystem.DMD),
        Code("325279004", "Metformin hydrochloride 850mg tablets", CodingSystem.DMD),
        Code("376689003", "Metformin hydrochloride 1g tablets", CodingSystem.DMD),
        Code("134531000001109", "Metformin 500mg/5ml oral solution", CodingSystem.DMD),
        Code("325280001", "Metformin hydrochloride 500mg modified-release tablets", CodingSystem.DMD),
        Code("411530001", "Metformin 500mg / Sitagliptin 50mg tablets", CodingSystem.DMD),
    ],
)

_metformin_bnf = Codelist(
    id="cl-metformin-bnf",
    name="Metformin (BNF)",
    coding_system=CodingSystem.BNF,
    version="1.1",
    description="BNF paragraph codes for metformin.",
    codes=[
        Code("0601022B0", "Metformin hydrochloride", CodingSystem.BNF),
        Code("0601022B0AAABAB", "Metformin 500mg tablets", CodingSystem.BNF),
        Code("0601022B0AAACAC", "Metformin 850mg tablets", CodingSystem.BNF),
        Code("0601022B0AAADAD", "Metformin 1g tablets", CodingSystem.BNF),
    ],
)

metformin = Phenotype(
    id="ph-metformin-001",
    name="Metformin Prescribing",
    short_name="Metformin",
    phenotype_type=PhenotypeType.MEDICATION,
    therapeutic_area=TherapeuticArea.DIABETES_ENDOCRINE,
    description=(
        "Medication phenotype for metformin prescribing in primary care. "
        "Includes all formulations (standard, modified-release, oral solution) "
        "and combination products."
    ),
    accession=AccessionID(prefix="OP", number=12, version="1.1"),
    codelists=[_metformin_dmd, _metformin_bnf],
    ontology_terms=[OntologyTerm("SNOMED CT", "325278007", "Metformin hydrochloride")],
    authors=[_AUTHORS["bennett"]],
    publications=[],
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.70,
        clinical_review=0.90,
        validation=0.80,
        usage=0.92,
        provenance=0.85,
    ),
    data_sources=["OpenSAFELY-TPP", "CPRD GOLD", "CPRD Aurum"],
    methodology="Based on dm+d mapping from OpenSAFELY medication codelists.",
    created_date=date(2020, 6, 1),
    updated_date=date(2024, 7, 1),
    version="1.1",
    related_phenotype_ids=["ph-t2dm-001"],
    source_code_url="https://www.opencodelists.org/codelist/opensafely/metformin/",
    source_repository="OpenCodelists",
    tags=["medication", "diabetes", "metformin", "prescribing", "OpenSAFELY"],
)

# ---------------------------------------------------------------------------
# 13. HbA1c (biomarker phenotype)
# ---------------------------------------------------------------------------

_hba1c_snomed = Codelist(
    id="cl-hba1c-snomed",
    name="HbA1c measurement (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.0",
    description="SNOMED CT codes for HbA1c laboratory measurements.",
    codes=[
        Code("43396009", "Haemoglobin A1c measurement", CodingSystem.SNOMED_CT),
        Code("313835008", "HbA1c level", CodingSystem.SNOMED_CT),
        Code("999791000000106", "HbA1c level (DCCT aligned)", CodingSystem.SNOMED_CT),
        Code("1049471000000109", "HbA1c level (IFCC standardised)", CodingSystem.SNOMED_CT),
    ],
)

hba1c = Phenotype(
    id="ph-hba1c-001",
    name="HbA1c Measurement",
    short_name="HbA1c",
    phenotype_type=PhenotypeType.BIOMARKER,
    therapeutic_area=TherapeuticArea.DIABETES_ENDOCRINE,
    description=(
        "Biomarker phenotype for glycated haemoglobin (HbA1c) measurements. "
        "Captures both DCCT-aligned and IFCC-standardised values."
    ),
    accession=AccessionID(prefix="OP", number=13, version="1.0"),
    codelists=[_hba1c_snomed],
    ontology_terms=[OntologyTerm("SNOMED CT", "43396009", "Haemoglobin A1c measurement")],
    authors=[_AUTHORS["hdruk"]],
    publications=[],
    validation_status=ValidationStatus.UNDER_REVIEW,
    evidence_score=EvidenceScore(
        literature=0.65,
        clinical_review=0.75,
        validation=0.60,
        usage=0.70,
        provenance=0.70,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "OpenSAFELY-TPP"],
    methodology="Code identification from SNOMED CT term search and clinical review.",
    created_date=date(2023, 5, 1),
    updated_date=date(2024, 1, 1),
    version="1.0",
    related_phenotype_ids=["ph-t2dm-001", "ph-metformin-001"],
    source_repository="HDR UK Phenotype Library",
    tags=["biomarker", "diabetes", "HbA1c", "laboratory", "glycaemic control"],
)

# ---------------------------------------------------------------------------
# 14. Dementia
# ---------------------------------------------------------------------------

_dementia_snomed = Codelist(
    id="cl-dementia-snomed",
    name="Dementia (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="2.2",
    description="SNOMED CT codes for all-cause dementia including subtypes.",
    codes=[
        Code("52448006", "Dementia", CodingSystem.SNOMED_CT),
        Code("26929004", "Alzheimer's disease", CodingSystem.SNOMED_CT),
        Code("429998004", "Vascular dementia", CodingSystem.SNOMED_CT),
        Code("312991009", "Senile dementia of the Lewy body type", CodingSystem.SNOMED_CT),
        Code("230270009", "Frontotemporal dementia", CodingSystem.SNOMED_CT),
        Code("56267009", "Multi-infarct dementia", CodingSystem.SNOMED_CT),
        Code("191463002", "Uncomplicated presenile dementia", CodingSystem.SNOMED_CT),
        Code("191461000", "Uncomplicated senile dementia", CodingSystem.SNOMED_CT),
        Code("416975007", "Dementia associated with Parkinson's disease", CodingSystem.SNOMED_CT),
    ],
)

dementia = Phenotype(
    id="ph-dementia-001",
    name="Dementia (All-Cause)",
    short_name="Dementia",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.NEUROLOGY,
    description=(
        "Broad phenotype for all-cause dementia including Alzheimer's disease, "
        "vascular dementia, Lewy body dementia, frontotemporal dementia, and "
        "mixed/unspecified subtypes."
    ),
    accession=AccessionID(prefix="OP", number=14, version="2.2"),
    codelists=[_dementia_snomed],
    ontology_terms=[OntologyTerm("SNOMED CT", "52448006", "Dementia")],
    population=PopulationConstraints(sex=Sex.BOTH, age_min=40),
    authors=[_AUTHORS["edinburgh"], _AUTHORS["manchester"]],
    publications=[
        Publication(
            "Dementia diagnosis in UK electronic health records",
            journal="Alzheimer's & Dementia",
            year=2024,
        ),
    ],
    validation_status=ValidationStatus.PEER_REVIEWED,
    evidence_score=EvidenceScore(
        literature=0.88,
        clinical_review=0.82,
        validation=0.75,
        usage=0.80,
        provenance=0.78,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "SAIL", "UK Biobank"],
    methodology=(
        "Broad definition capturing any recorded dementia diagnosis. "
        "Subtype-specific definitions available as related phenotypes."
    ),
    created_date=date(2022, 3, 1),
    updated_date=date(2024, 10, 1),
    version="2.2",
    related_phenotype_ids=[],
    source_repository="ClinicalCodes / University of Manchester",
    tags=["neurology", "dementia", "Alzheimer's", "cognitive", "ageing"],
)

# ---------------------------------------------------------------------------
# 15. Pregnancy
# ---------------------------------------------------------------------------

_pregnancy_snomed = Codelist(
    id="cl-pregnancy-snomed",
    name="Pregnancy (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.0",
    description="SNOMED CT codes for pregnancy identification.",
    codes=[
        Code("77386006", "Pregnant", CodingSystem.SNOMED_CT),
        Code("72892002", "Normal pregnancy", CodingSystem.SNOMED_CT),
        Code("237238006", "Pregnancy with complications", CodingSystem.SNOMED_CT),
        Code("16356006", "Multiple pregnancy", CodingSystem.SNOMED_CT),
        Code("47200007", "High risk pregnancy", CodingSystem.SNOMED_CT),
        Code("169826009", "Single live birth", CodingSystem.SNOMED_CT),
    ],
)

pregnancy = Phenotype(
    id="ph-preg-001",
    name="Pregnancy",
    short_name="Pregnancy",
    phenotype_type=PhenotypeType.DEMOGRAPHIC,
    therapeutic_area=TherapeuticArea.OBSTETRICS_GYNAECOLOGY,
    description=(
        "Phenotype for identifying pregnancy episodes in electronic health "
        "records. Used as a covariate and for defining pregnancy-related "
        "study populations."
    ),
    accession=AccessionID(prefix="OP", number=15, version="1.0"),
    codelists=[_pregnancy_snomed],
    ontology_terms=[OntologyTerm("SNOMED CT", "77386006", "Pregnant")],
    population=PopulationConstraints(sex=Sex.FEMALE, age_min=12, age_max=55),
    authors=[_AUTHORS["cambridge"]],
    publications=[],
    validation_status=ValidationStatus.DRAFT,
    evidence_score=EvidenceScore(
        literature=0.60,
        clinical_review=0.65,
        validation=0.50,
        usage=0.55,
        provenance=0.60,
    ),
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "SAIL"],
    methodology="Initial code identification from term search. Awaiting clinical review.",
    created_date=date(2024, 8, 1),
    updated_date=date(2024, 8, 1),
    version="1.0",
    related_phenotype_ids=[],
    source_repository="OpenPhenotypes (new)",
    tags=["obstetrics", "pregnancy", "maternal", "reproductive"],
)


# ---------------------------------------------------------------------------
# 16. T2DM — OpenSAFELY COVID study use (study-specific derivation)
# ---------------------------------------------------------------------------

_t2dm_opensafely_snomed = Codelist(
    id="cl-t2dm-os-snomed",
    name="T2DM for OpenSAFELY COVID (SNOMED CT subset)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.0",
    coding_system_version="SNOMED CT UK Edition 2020-09-01",
    description="Simplified SNOMED CT codelist for T2DM used in OpenSAFELY COVID-19 risk factor studies.",
    codes=[
        Code("44054006", "Diabetes mellitus type 2", CodingSystem.SNOMED_CT),
        Code("313436004", "Type 2 diabetes mellitus without complication", CodingSystem.SNOMED_CT),
        Code("421750000", "Ketoacidosis in type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("422034002", "Diabetic retinopathy associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
        Code("420279001", "Renal disorder associated with type II diabetes mellitus", CodingSystem.SNOMED_CT),
    ],
)

t2dm_opensafely_use = Phenotype(
    id="ph-t2dm-002",
    name="T2DM (OpenSAFELY COVID-19 study use)",
    short_name="T2DM-OS",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.DIABETES_ENDOCRINE,
    description=(
        "Study-specific derivation of the T2DM core phenotype, used as a "
        "covariate in the OpenSAFELY COVID-19 risk factor analysis (Williamson "
        "et al., Nature 2020). Uses a simplified SNOMED CT-only codelist."
    ),
    accession=AccessionID(prefix="OP", number=16, version="1.0"),
    codelists=[_t2dm_opensafely_snomed],
    ontology_terms=[OntologyTerm("SNOMED CT", "44054006", "Diabetes mellitus type 2")],
    population=PopulationConstraints(
        sex=Sex.BOTH, age_min=18,
        inclusion_criteria="Registered in TPP practice on 1 Feb 2020",
    ),
    authors=[_AUTHORS["bennett"]],
    publications=[
        Publication(
            "Factors associated with COVID-19-related death using OpenSAFELY",
            doi="10.1038/s41586-020-2521-4",
            journal="Nature",
            year=2020,
            pubmed_id="32640463",
            is_primary=True,
        ),
    ],
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.95,
        clinical_review=0.75,
        validation=0.70,
        usage=0.98,
        provenance=0.80,
    ),
    data_sources=["OpenSAFELY-TPP"],
    methodology="Subset of HDR UK T2DM phenotype adapted for OpenSAFELY TPP backend.",
    source_code_url="https://github.com/opensafely/risk-factors-research",
    created_date=date(2020, 4, 1),
    updated_date=date(2020, 7, 1),
    version="1.0",
    is_core_definition=False,
    parent_phenotype_id="ph-t2dm-001",
    related_phenotype_ids=["ph-covid-001"],
    source_repository="OpenCodelists",
    tags=["diabetes", "COVID-19", "OpenSAFELY", "risk factor", "study use"],
)


# ---------------------------------------------------------------------------
# Registry of all sample phenotypes
# ---------------------------------------------------------------------------

ALL_PHENOTYPES: list[Phenotype] = [
    t2dm,
    hypertension,
    depression,
    asthma,
    ckd,
    copd,
    atrial_fibrillation,
    stroke,
    osteoarthritis,
    covid19,
    breast_cancer,
    metformin,
    hba1c,
    dementia,
    pregnancy,
    t2dm_opensafely_use,
]


def get_phenotype_by_id(phenotype_id: str) -> Phenotype | None:
    for p in ALL_PHENOTYPES:
        if p.id == phenotype_id:
            return p
    return None


def search_phenotypes(query: str) -> list[Phenotype]:
    """Full-text search across names, descriptions, tags, authors, codes, and ontology terms."""
    query_lower = query.lower().strip()
    if not query_lower:
        return ALL_PHENOTYPES

    results = []
    for p in ALL_PHENOTYPES:
        # Text fields
        searchable = " ".join([
            p.name,
            p.short_name,
            p.description,
            " ".join(p.tags),
            p.therapeutic_area.value,
            p.phenotype_type.value,
            p.source_repository,
            " ".join(a.name for a in p.authors),
            " ".join(a.institution for a in p.authors),
        ]).lower()

        # Code values and terms (product fix #1 — search inside codelists)
        code_searchable = " ".join(
            f"{code.code} {code.term}"
            for cl in p.codelists for code in cl.codes
        ).lower()

        # Ontology terms (ontology-supported search)
        ontology_searchable = " ".join(
            f"{t.system} {t.code} {t.label}"
            for t in p.ontology_terms
        ).lower()

        full_searchable = f"{searchable} {code_searchable} {ontology_searchable}"

        if query_lower in full_searchable:
            results.append(p)

    return results
