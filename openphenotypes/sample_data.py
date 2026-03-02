"""
Sample phenotype and codelist data for the OpenPhenotypes prototype.

Includes realistic phenotype definitions spanning multiple therapeutic areas,
coding systems, and validation statuses. Modelled on real-world codelists
from OpenCodelists, HDR UK Phenotype Library, ClinicalCodes, and Keele HCDR.

Updated to include full BHF DSC FAIR Table 1 metadata fields: accession IDs,
ontology terms, population constraints, validation evidence, implementation
artefacts, dummy data examples, QC rules, dataset provenance, and clinical
endorsements.
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
# 1. Type 2 Diabetes (FLAGSHIP — full FAIR compliance)
# ---------------------------------------------------------------------------

_t2dm_snomed = Codelist(
    id="cl-t2dm-snomed",
    name="Type 2 diabetes mellitus (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="2.1",
    description="SNOMED CT codes for type 2 diabetes mellitus including subtypes.",
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
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
    description="ICD-10 codes for type 2 diabetes mellitus.",
    coding_system_version="ICD-10 5th Edition 2016",
    coding_system_release=date(2016, 1, 1),
    codes=[
        Code("E11", "Type 2 diabetes mellitus", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.0", "Type 2 DM with coma", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.1", "Type 2 DM with ketoacidosis", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.2", "Type 2 DM with kidney complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.3", "Type 2 DM with ophthalmic complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.4", "Type 2 DM with neurological complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.5", "Type 2 DM with peripheral circulatory complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.6", "Type 2 DM with other specified complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.7", "Type 2 DM with multiple complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.8", "Type 2 DM with unspecified complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("E11.9", "Type 2 DM without complications", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
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
        OntologyTerm(system="SNOMED CT", code="44054006", label="Diabetes mellitus type 2", is_primary=True),
        OntologyTerm(system="ICD-10", code="E11", label="Type 2 diabetes mellitus"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults aged 18+ registered with a GP practice in England",
        exclusion_criteria="Type 1 diabetes, gestational diabetes, secondary diabetes, MODY",
        notes="Paediatric T2DM rare; separate phenotype recommended for under-18s",
    ),
    authors=[_AUTHORS["hdruk"], _AUTHORS["bennett"]],
    publications=[
        Publication(
            "Defining type 2 diabetes phenotypes using electronic health records",
            doi="10.1136/bmjopen-2020-example",
            journal="BMJ Open",
            year=2023,
            url="https://bmjopen.bmj.com/content/example-t2dm",
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
            specificity=0.97,
            sample_size=500,
            publication_doi="10.1136/bmjopen-2020-example",
            notes="Random sample of 500 patients; reviewed by two clinicians",
        ),
        ValidationEvidence(
            method=ValidationMethod.CROSS_DATABASE,
            dataset="UK Biobank",
            comparator="Self-reported diabetes + HbA1c >= 48 mmol/mol",
            ppv=0.89,
            sensitivity=0.91,
            sample_size=5000,
            notes="Cross-validated against UK Biobank adjudicated outcomes",
        ),
    ],
    clinical_endorsements=[
        ClinicalEndorsement(
            reviewer_name="Prof. Naveed Sattar",
            reviewer_role="Professor of Metabolic Medicine",
            institution="University of Glasgow",
            date=date(2024, 6, 15),
            notes="Reviewed codelist completeness; endorsed for use in CVD outcome studies",
        ),
    ],
    data_sources=["CPRD GOLD", "CPRD Aurum", "OpenSAFELY-TPP", "HES APC", "SAIL", "UK Biobank"],
    dataset_provenance=[
        DatasetProvenance(
            dataset_name="CPRD GOLD March 2023",
            dataset_identifier="doi:10.1234/cprd-gold-2023-03",
            date_range_start=date(2000, 1, 1),
            date_range_end=date(2023, 3, 31),
            population_size=18000000,
            notes="Used for primary validation study",
        ),
        DatasetProvenance(
            dataset_name="OpenSAFELY-TPP February 2024",
            dataset_identifier="opensafely-tpp-2024-02",
            date_range_start=date(2019, 1, 1),
            date_range_end=date(2024, 2, 29),
            population_size=24000000,
            notes="Used for prevalence estimation and code frequency analysis",
        ),
    ],
    implementations=[
        Implementation(
            language="SQL",
            label="CPRD GOLD T2DM case identification query",
            code=(
                "SELECT DISTINCT patid\n"
                "FROM clinical c\n"
                "JOIN medical m ON c.medcode = m.medcode\n"
                "WHERE m.snomedctconceptid IN (\n"
                "  '44054006', '313436004', '314902007',\n"
                "  '314903002', '314904008'  -- etc.\n"
                ")\n"
                "AND c.eventdate IS NOT NULL;"
            ),
            dataset_target="CPRD GOLD",
            notes="Simplified example; production query includes date windows and exclusion logic",
        ),
        Implementation(
            language="OpenSAFELY ehrQL",
            label="OpenSAFELY ehrQL study definition (pseudocode)",
            code=(
                "from ehrql import create_dataset\n"
                "from ehrql.tables.tpp import clinical_events\n"
                "\n"
                "t2dm_codes = codelist_from_csv('codelists/cl-t2dm-snomed.csv')\n"
                "dataset = create_dataset()\n"
                "dataset.define_population(\n"
                "    clinical_events.where(\n"
                "        clinical_events.snomedct_code.is_in(t2dm_codes)\n"
                "    ).exists_for_patient()\n"
                ")"
            ),
            source_url="https://github.com/opensafely/example-t2dm",
            dataset_target="OpenSAFELY-TPP",
            notes="Pseudocode; actual study definitions use ehrQL v1",
        ),
    ],
    dummy_data_examples=[
        DummyDataExample(
            description="Correctly identified T2DM patient with primary care diagnosis",
            input_data=(
                "patient_id,event_date,snomedct_code,term\n"
                "1001,2018-03-14,44054006,Diabetes mellitus type 2\n"
                "1001,2018-06-01,313835008,HbA1c level\n"
                "1001,2019-01-10,325278007,Metformin 500mg tablets"
            ),
            expected_output=(
                "patient_id,t2dm_case,first_diagnosis_date\n"
                "1001,True,2018-03-14"
            ),
            notes="Patient has a T2DM SNOMED code -> classified as case with earliest date",
        ),
    ],
    qc_rules=[
        QCRule(
            rule_id="T2DM-QC-01",
            description="Exclude patients with concurrent Type 1 diabetes codes recorded on the same date",
            severity="warning",
            applies_to="all",
            automated=True,
        ),
        QCRule(
            rule_id="T2DM-QC-02",
            description="Flag patients aged under 18 at first T2DM code for manual review",
            severity="warning",
            applies_to="all",
            automated=True,
        ),
        QCRule(
            rule_id="T2DM-QC-03",
            description="ICD-10 codes should appear in primary diagnosis position for incident identification",
            severity="info",
            applies_to="ICD-10 codelist",
            automated=True,
        ),
    ],
    purpose=(
        "To identify patients with type 2 diabetes mellitus in UK electronic health "
        "records for epidemiological research, outcome studies, and population health monitoring."
    ),
    developed_for=(
        "Originally developed for the CALIBER programme to enable cardiovascular disease "
        "research in linked primary-secondary care datasets (CPRD GOLD + HES)."
    ),
    used_for=(
        "Reused in OpenSAFELY COVID-19 risk factor studies, UK Biobank diabetes "
        "sub-studies, and HDR UK national phenotype library. Basis for derived "
        "study-specific codelists (e.g. OP-0016)."
    ),
    limitations=(
        "Code-based identification may under-ascertain T2DM in populations with low "
        "primary care engagement. Does not distinguish well-controlled from poorly "
        "controlled diabetes without supplementary HbA1c data. Read v2 codes are "
        "legacy and may not be available in newer TPP/EMIS extracts."
    ),
    methodology=(
        "Codes identified through literature review, clinical expert consensus, "
        "and cross-referencing with existing validated codelists (Cambridge, Exeter). "
        "Validated against clinical notes in CPRD with PPV 92%, sensitivity 88%."
    ),
    logic_description=(
        "A patient is classified as having T2DM if they have at least one diagnostic "
        "code from the SNOMED CT or Read v2 codelist recorded in primary care, OR an "
        "ICD-10 E11.x code in the primary diagnosis position in HES APC. Patients with "
        "a prior Type 1 diabetes code (E10.x / 46635009) are excluded unless the T2DM "
        "code is recorded after age 35 and there is no insulin prescription within "
        "6 months of the T1DM code."
    ),
    created_date=date(2022, 3, 15),
    updated_date=date(2024, 11, 1),
    version="2.1",
    source_code_url="https://www.opencodelists.org/codelist/opensafely/type-2-diabetes/2024-04-01/",
    is_core_definition=True,
    child_use_ids=["ph-t2dm-opensafely-use-001"],
    related_phenotype_ids=["ph-t1dm-001", "ph-hba1c-001", "ph-metformin-001"],
    source_repository="HDR UK Phenotype Library",
    tags=["diabetes", "endocrine", "metabolic", "primary care", "secondary care", "NCD"],
)

# ---------------------------------------------------------------------------
# 2. Hypertension (second-tier FAIR completeness)
# ---------------------------------------------------------------------------

_htn_snomed = Codelist(
    id="cl-htn-snomed",
    name="Essential hypertension (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.5",
    description="SNOMED CT codes for essential (primary) hypertension.",
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
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
    coding_system_version="ICD-10 5th Edition 2016",
    coding_system_release=date(2016, 1, 1),
    codes=[
        Code("I10", "Essential (primary) hypertension", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I11", "Hypertensive heart disease", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I11.0", "Hypertensive heart disease with heart failure", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I11.9", "Hypertensive heart disease without heart failure", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I12", "Hypertensive renal disease", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I13", "Hypertensive heart and renal disease", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
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
        OntologyTerm(system="SNOMED CT", code="59621000", label="Essential hypertension", is_primary=True),
        OntologyTerm(system="ICD-10", code="I10", label="Essential (primary) hypertension"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults aged 18+ with GP registration",
        exclusion_criteria="Pregnancy-related hypertension (O10-O16), secondary hypertension (I15)",
    ),
    authors=[_AUTHORS["cambridge"], _AUTHORS["hdruk"]],
    publications=[
        Publication(
            "Hypertension phenotyping in UK primary care EHR",
            doi="10.1093/ije/example-htn",
            journal="International Journal of Epidemiology",
            year=2022,
            url="https://academic.oup.com/ije/example-htn",
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
            method=ValidationMethod.CHART_REVIEW,
            dataset="CPRD GOLD",
            comparator="Blood pressure readings >= 140/90 mmHg on two occasions",
            ppv=0.89,
            sensitivity=0.91,
            sample_size=400,
            publication_doi="10.1093/ije/example-htn",
            notes="Validated using BP measurement gold standard",
        ),
    ],
    clinical_endorsements=[
        ClinicalEndorsement(
            reviewer_name="Prof. Bryan Williams",
            reviewer_role="Professor of Medicine / NICE Hypertension Guideline Chair",
            institution="University College London",
            date=date(2023, 11, 1),
            notes="Codelist aligned with NICE NG136 hypertension guidelines",
        ),
    ],
    data_sources=["CPRD GOLD", "CPRD Aurum", "HES APC", "OpenSAFELY-TPP", "UK Biobank"],
    purpose="To identify patients with essential hypertension for cardiovascular risk studies.",
    developed_for="CALIBER programme cardiovascular disease research in linked GP and hospital data.",
    used_for="CVD outcome studies, multimorbidity analyses, blood pressure treatment pathway research.",
    limitations=(
        "Relies on diagnostic codes; patients managed on BP-lowering drugs without a "
        "coded hypertension diagnosis may be missed. Secondary hypertension explicitly excluded."
    ),
    methodology=(
        "Codes curated from existing CALIBER phenotype algorithms with expert "
        "cardiology review. Validated using blood pressure measurements as gold "
        "standard. PPV 89%, sensitivity 91%."
    ),
    created_date=date(2021, 6, 10),
    updated_date=date(2024, 8, 20),
    version="1.5",
    source_code_url="https://www.caliberresearch.org/portal/phenotypes/hypertension",
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
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
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
    coding_system_version="ICD-10 5th Edition 2016",
    coding_system_release=date(2016, 1, 1),
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
        OntologyTerm(system="SNOMED CT", code="35489007", label="Depressive disorder", is_primary=True),
        OntologyTerm(system="ICD-10", code="F32", label="Depressive episode"),
        OntologyTerm(system="ICD-10", code="F33", label="Recurrent depressive disorder"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=16,
        inclusion_criteria="Individuals aged 16+ with GP registration",
        exclusion_criteria="Bipolar affective disorder (F31), adjustment disorders (F43.2)",
    ),
    authors=[_AUTHORS["manchester"], _AUTHORS["edinburgh"]],
    publications=[
        Publication(
            "Defining depression in UK primary care: a clinical code validation study",
            doi="10.1016/j.jad.2023.example",
            journal="Journal of Affective Disorders",
            year=2023,
            url="https://www.sciencedirect.com/journal/journal-of-affective-disorders",
            is_primary=True,
        ),
        Publication(
            "Common mental health disorders in electronic health records",
            journal="Psychological Medicine",
            year=2021,
        ),
    ],
    purpose="To identify patients with depressive disorders for mental health research and service planning.",
    developed_for="ClinicalCodes / University of Manchester common mental disorder studies in CPRD and SAIL.",
    used_for="Prevalence studies, antidepressant prescribing research, multimorbidity analyses, NHS service evaluation.",
    limitations=(
        "Broad definition may include mild/transient episodes. Depression recording "
        "varies by GP practice and over time. Does not distinguish severity without "
        "additional clinical information."
    ),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="195967001", label="Asthma", is_primary=True),
        OntologyTerm(system="ICD-10", code="J45", label="Asthma"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        inclusion_criteria="All ages; includes childhood and adult-onset asthma",
        exclusion_criteria="COPD-asthma overlap (ACO) should use separate composite phenotype",
    ),
    authors=[_AUTHORS["bennett"], _AUTHORS["bristol"]],
    publications=[
        Publication(
            "Identifying asthma in UK electronic health records",
            doi="10.1136/thoraxjnl-2022-example",
            journal="Thorax",
            year=2022,
            url="https://thorax.bmj.com/content/example-asthma",
            is_primary=True,
        ),
    ],
    purpose="To identify asthma patients for respiratory disease epidemiology and medication safety studies.",
    developed_for="OpenSAFELY respiratory disease research and BTS/SIGN guideline compliance studies.",
    used_for="Asthma prevalence estimation, inhaler prescribing analyses, COVID-19 risk group identification.",
    limitations=(
        "Code-based definition cannot distinguish active from historical asthma. "
        "Overlap with COPD in older adults requires additional exclusion logic. "
        "Severity classification requires medication data (not codes alone)."
    ),
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
    source_code_url="https://www.opencodelists.org/codelist/opensafely/asthma-diagnosis/",
    related_phenotype_ids=["ph-copd-001", "ph-ics-001"],
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="709044004", label="Chronic kidney disease", is_primary=True),
        OntologyTerm(system="ICD-10", code="N18", label="Chronic kidney disease"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults aged 18+ with GP registration",
        exclusion_criteria="Acute kidney injury without chronicity markers",
    ),
    authors=[_AUTHORS["cambridge"]],
    publications=[
        Publication(
            "CKD phenotyping in UK electronic health records",
            journal="Kidney International",
            year=2023,
            url="https://www.kidney-international.org/example-ckd",
            is_primary=True,
        ),
    ],
    purpose="To identify CKD patients by stage for renal disease epidemiology and cardiovascular risk studies.",
    developed_for="CALIBER / HDR UK cardiorenal disease linkage studies.",
    used_for="CKD prevalence estimation, cardiovascular comorbidity analyses, medication safety studies.",
    limitations=(
        "Code-only version does not incorporate eGFR values; combining with biomarker "
        "data recommended for accurate staging. CKD stage 1-2 underrecorded in primary care."
    ),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="13645005", label="Chronic obstructive pulmonary disease", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=35,
        inclusion_criteria="Adults aged 35+ (COPD rare below this age)",
        exclusion_criteria="Asthma-only diagnoses without COPD code",
    ),
    authors=[_AUTHORS["bennett"]],
    publications=[
        Publication(
            "COPD codelists for OpenSAFELY studies",
            year=2021,
            url="https://www.opencodelists.org/codelist/opensafely/copd/",
            is_primary=True,
        ),
    ],
    purpose="To identify COPD patients for respiratory disease research and shielding list studies.",
    developed_for="OpenSAFELY COVID-19 shielding and respiratory vulnerability studies.",
    used_for="COPD prevalence, COVID-19 risk group identification, exacerbation outcome studies.",
    limitations=(
        "Single coding system (SNOMED CT only); may miss cases recorded only in ICD-10 "
        "secondary care data. Severity staging depends on spirometry, which is not "
        "captured in code-based definitions alone."
    ),
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
    source_code_url="https://www.opencodelists.org/codelist/opensafely/copd/",
    related_phenotype_ids=["ph-asthma-001"],
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
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
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
    coding_system_version="ICD-10 5th Edition 2016",
    coding_system_release=date(2016, 1, 1),
    codes=[
        Code("I48", "Atrial fibrillation and flutter", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I48.0", "Paroxysmal atrial fibrillation", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I48.1", "Persistent atrial fibrillation", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I48.2", "Chronic atrial fibrillation", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I48.3", "Typical atrial flutter", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I48.4", "Atypical atrial flutter", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I48.9", "Atrial fibrillation and flutter, unspecified", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="49436004", label="Atrial fibrillation", is_primary=True),
        OntologyTerm(system="ICD-10", code="I48", label="Atrial fibrillation and flutter"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults aged 18+ with GP registration",
    ),
    authors=[_AUTHORS["hdruk"], _AUTHORS["cambridge"]],
    publications=[
        Publication(
            "Atrial fibrillation in electronic health records: the CALIBER approach",
            doi="10.1136/heartjnl-2021-example",
            journal="Heart",
            year=2021,
            url="https://heart.bmj.com/content/example-af",
            is_primary=True,
        ),
    ],
    purpose="To identify AF patients for stroke risk prediction and anticoagulation research.",
    developed_for="CALIBER programme cardiovascular disease phenotyping in linked GP and hospital data.",
    used_for="Stroke risk stratification (CHA2DS2-VASc), anticoagulation prescribing studies, heart failure comorbidity analyses.",
    limitations=(
        "Cannot distinguish paroxysmal from persistent AF without ECG data. "
        "PPV may be lower in younger populations where AF is rare. "
        "Atrial flutter included — may need separation for some studies."
    ),
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
            dataset="CPRD GOLD linked to HES",
            comparator="ECG-confirmed AF in hospital records",
            ppv=0.95,
            sensitivity=0.82,
            sample_size=350,
            publication_doi="10.1136/heartjnl-2021-example",
            notes="Validated against ECG-confirmed AF diagnoses in linked HES data",
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
    source_code_url="https://www.caliberresearch.org/portal/phenotypes/af",
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
        Code("I60", "Subarachnoid haemorrhage", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I61", "Intracerebral haemorrhage", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I62", "Other nontraumatic intracranial haemorrhage", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I63", "Cerebral infarction", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I63.0", "Cerebral infarction due to thrombosis of precerebral arteries", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I63.1", "Cerebral infarction due to embolism of precerebral arteries", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I63.9", "Cerebral infarction, unspecified", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("I64", "Stroke, not specified as haemorrhage or infarction", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="230690007", label="Cerebrovascular accident", is_primary=True),
        OntologyTerm(system="ICD-10", code="I63", label="Cerebral infarction"),
        OntologyTerm(system="ICD-10", code="I61", label="Intracerebral haemorrhage"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults aged 18+ with GP registration",
        exclusion_criteria="TIA (transient ischaemic attack) — separate phenotype",
    ),
    authors=[_AUTHORS["hdruk"], _AUTHORS["edinburgh"]],
    publications=[
        Publication(
            "Stroke phenotyping in linked primary and secondary care records",
            doi="10.1136/jnnp-2022-example",
            journal="Journal of Neurology, Neurosurgery & Psychiatry",
            year=2022,
            url="https://jnnp.bmj.com/content/example-stroke",
            is_primary=True,
        ),
    ],
    purpose="To identify ischaemic and haemorrhagic stroke events for cerebrovascular disease research.",
    developed_for="CALIBER cerebrovascular phenotyping in linked primary and secondary care data.",
    used_for="Stroke incidence/outcome studies, AF-stroke association analyses, anticoagulation effectiveness research.",
    limitations=(
        "TIA explicitly excluded — requires separate phenotype. Primary position ICD-10 "
        "codes may miss strokes recorded as secondary diagnoses. Stroke subtype classification "
        "(ischaemic vs haemorrhagic) depends on imaging, which is not captured in codes."
    ),
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
    source_code_url="https://www.caliberresearch.org/portal/phenotypes/stroke",
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="396275006", label="Osteoarthritis", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=40,
        inclusion_criteria="Adults aged 40+ consulting in primary care",
        notes="OA incidence increases steeply after age 40",
    ),
    authors=[_AUTHORS["keele"]],
    publications=[
        Publication(
            "Consultation incidence of osteoarthritis in UK primary care",
            journal="Osteoarthritis and Cartilage",
            year=2020,
            url="https://www.oarsijournal.com/example-oa",
            is_primary=True,
        ),
    ],
    purpose="To identify OA consultations in primary care for musculoskeletal disease epidemiology.",
    developed_for="Keele Primary Care Centre Versus Arthritis musculoskeletal research programme.",
    used_for="OA prevalence estimation, joint replacement pathway studies, pain management research.",
    limitations=(
        "Read v2 codes are legacy (pre-2018 GP systems). SNOMED CT mapping provided "
        "but may not be complete for all subtypes. Does not capture radiographic severity."
    ),
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
# 10. COVID-19 (second-tier FAIR completeness)
# ---------------------------------------------------------------------------

_covid_snomed = Codelist(
    id="cl-covid-snomed",
    name="COVID-19 (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="4.0",
    description="SNOMED CT codes for COVID-19 diagnosis and related conditions.",
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
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
    coding_system_version="ICD-10 5th Edition 2016 + WHO COVID-19 emergency codes",
    coding_system_release=date(2020, 3, 25),
    codes=[
        Code("U07.1", "COVID-19, virus identified", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("U07.2", "COVID-19, virus not identified", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("U09.9", "Post-COVID-19 condition, unspecified", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("U10.9", "Multisystem inflammatory syndrome associated with COVID-19", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
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
        OntologyTerm(system="SNOMED CT", code="840539006", label="Disease caused by SARS-CoV-2", is_primary=True),
        OntologyTerm(system="ICD-10", code="U07.1", label="COVID-19, virus identified"),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        inclusion_criteria="All ages; applicable to any individual with suspected or confirmed SARS-CoV-2 infection",
        notes="Phenotype only applicable from March 2020 onwards (see valid_date_start)",
    ),
    authors=[_AUTHORS["bennett"], _AUTHORS["hdruk"]],
    publications=[
        Publication(
            "Factors associated with COVID-19-related death using OpenSAFELY",
            doi="10.1038/s41586-020-2521-4",
            journal="Nature",
            year=2020,
            pubmed_id="32640463",
            url="https://www.nature.com/articles/s41586-020-2521-4",
            is_primary=True,
        ),
    ],
    purpose="To identify COVID-19 cases for pandemic research including mortality, vaccine effectiveness, and long COVID studies.",
    developed_for="OpenSAFELY pandemic research programme; used in >100 studies during 2020-2024.",
    used_for="COVID-19 mortality analyses, vaccine effectiveness studies, long COVID identification, shielding patient research.",
    limitations=(
        "Dependent on testing availability (limited early pandemic). Suspected cases "
        "(U07.2) have lower specificity. Post-COVID syndrome codes only available from "
        "late 2020. Lateral flow test results not consistently captured."
    ),
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
            dataset="OpenSAFELY-TPP linked to SGSS",
            comparator="SGSS PCR-positive test result",
            ppv=0.97,
            sensitivity=0.85,
            specificity=0.99,
            sample_size=10000,
            publication_doi="10.1038/s41586-020-2521-4",
            notes="Validated against SGSS positive test results during first wave",
        ),
    ],
    data_sources=["OpenSAFELY-TPP", "OpenSAFELY-EMIS", "HES APC", "CPRD Aurum", "ONS"],
    dataset_provenance=[
        DatasetProvenance(
            dataset_name="OpenSAFELY-TPP March 2020 - December 2023",
            dataset_identifier="opensafely-tpp-covid-cohort",
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2023, 12, 31),
            population_size=24000000,
            notes="Primary dataset for all OpenSAFELY COVID-19 studies",
        ),
    ],
    implementations=[
        Implementation(
            language="OpenSAFELY ehrQL",
            label="OpenSAFELY COVID-19 case identification",
            code=(
                "from ehrql import create_dataset\n"
                "from ehrql.tables.tpp import clinical_events, sgss_covid_all_tests\n"
                "\n"
                "covid_codes = codelist_from_csv('codelists/cl-covid-snomed.csv')\n"
                "dataset = create_dataset()\n"
                "dataset.define_population(\n"
                "    clinical_events.where(\n"
                "        clinical_events.snomedct_code.is_in(covid_codes)\n"
                "    ).exists_for_patient()\n"
                "    | sgss_covid_all_tests.where(\n"
                "        sgss_covid_all_tests.is_positive\n"
                "    ).exists_for_patient()\n"
                ")"
            ),
            source_url="https://github.com/opensafely/covid-vaccine-effectiveness",
            dataset_target="OpenSAFELY-TPP",
            notes="Combines SNOMED codes with SGSS test results",
        ),
    ],
    methodology=(
        "Developed iteratively during the pandemic using SGSS positive test results "
        "as reference standard. Refined through multiple OpenSAFELY studies."
    ),
    logic_description=(
        "A patient is classified as having COVID-19 if they have: (1) a SNOMED CT "
        "code for confirmed/suspected COVID-19 in primary care, OR (2) a positive "
        "SARS-CoV-2 PCR or lateral flow test in SGSS, OR (3) an ICD-10 U07.1/U07.2 "
        "code in HES APC. Post-COVID syndrome (U09.9 / 1325181000000106) is captured "
        "as a separate flag. Date of onset is the earliest of clinical code or positive test."
    ),
    created_date=date(2020, 3, 15),
    updated_date=date(2024, 1, 10),
    version="4.0",
    source_code_url="https://www.opencodelists.org/codelist/opensafely/covid-identification/",
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
        Code("C50", "Malignant neoplasm of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.0", "Nipple and areola", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.1", "Central portion of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.2", "Upper-inner quadrant of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.3", "Lower-inner quadrant of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.4", "Upper-outer quadrant of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.5", "Lower-outer quadrant of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.8", "Overlapping lesion of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("C50.9", "Breast, unspecified", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
        Code("D05", "Carcinoma in situ of breast", CodingSystem.ICD10, code_position=CodePosition.PRIMARY),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="254837009", label="Malignant neoplasm of breast", is_primary=True),
        OntologyTerm(system="ICD-10", code="C50", label="Malignant neoplasm of breast"),
    ],
    population=PopulationConstraints(
        sex=Sex.FEMALE,
        age_min=18,
        inclusion_criteria="Females aged 18+; male breast cancer uses a separate phenotype",
        exclusion_criteria="Benign breast neoplasms, phyllodes tumours",
        notes="Male breast cancer (<1% of cases) excluded for population specificity",
    ),
    authors=[_AUTHORS["edinburgh"]],
    publications=[
        Publication(
            "Cancer registration phenotypes for UK Biobank studies",
            journal="British Journal of Cancer",
            year=2023,
            url="https://www.nature.com/bjc/example-brca",
            is_primary=True,
        ),
    ],
    purpose="To identify breast cancer cases for cancer epidemiology and outcomes research.",
    developed_for="UK Biobank cancer phenotyping linked to national cancer registry data.",
    used_for="Cancer incidence studies, screening effectiveness analyses, survival outcome research.",
    limitations=(
        "Excludes male breast cancer (<1% of cases). Carcinoma in situ included — may need "
        "separation for invasive-only analyses. Histological subtype requires registry linkage."
    ),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="109081006", label="Metformin", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults with active GP prescriptions",
    ),
    authors=[_AUTHORS["bennett"]],
    publications=[],
    purpose="To identify metformin prescribing for diabetes medication utilisation and safety research.",
    developed_for="OpenSAFELY medication codelist programme for pharmacoepidemiological studies.",
    used_for="Prescribing prevalence studies, medication adherence research, T2DM treatment pathway analyses.",
    limitations=(
        "Captures prescriptions issued, not dispensed or taken. Combination products may "
        "lead to double-counting if not handled. Hospital prescribing not captured in primary care data."
    ),
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
    source_code_url="https://www.opencodelists.org/codelist/opensafely/metformin/",
    related_phenotype_ids=["ph-t2dm-001"],
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="43396009", label="Haemoglobin A1c measurement", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        inclusion_criteria="Any patient with HbA1c test recorded",
    ),
    authors=[_AUTHORS["hdruk"]],
    publications=[],
    purpose="To capture HbA1c laboratory measurements for glycaemic control monitoring in diabetes research.",
    developed_for="HDR UK Phenotype Library biomarker phenotyping programme.",
    used_for="Diabetes control assessment, treatment effectiveness studies, risk stratification research.",
    limitations=(
        "Captures test ordering/results, not clinical interpretation. DCCT and IFCC units "
        "must be standardised before analysis. Missing values common in early EHR data."
    ),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="52448006", label="Dementia", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=40,
        inclusion_criteria="Adults aged 40+; early-onset dementia included",
        notes="95% of dementia cases are aged 65+; younger cases should be flagged for review",
    ),
    authors=[_AUTHORS["edinburgh"], _AUTHORS["manchester"]],
    publications=[
        Publication(
            "Dementia diagnosis in UK electronic health records",
            journal="Alzheimer's & Dementia",
            year=2024,
            url="https://alz-journals.onlinelibrary.wiley.com/example-dementia",
            is_primary=True,
        ),
    ],
    purpose="To identify all-cause dementia for neurodegenerative disease epidemiology and care pathway research.",
    developed_for="ClinicalCodes / University of Manchester dementia research programme.",
    used_for="Dementia prevalence estimation, comorbidity analyses, care home research, drug safety studies.",
    limitations=(
        "Broad definition includes all subtypes — subtype-specific analyses require "
        "related phenotypes. Dementia underrecorded in primary care (estimated 30-40% "
        "undiagnosed). Onset date difficult to determine from diagnostic codes alone."
    ),
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
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="77386006", label="Pregnant", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.FEMALE,
        age_min=12,
        age_max=55,
        inclusion_criteria="Females of reproductive age (12-55)",
        notes="Age range covers the biologically plausible fertility window",
    ),
    authors=[_AUTHORS["cambridge"]],
    publications=[],
    purpose="To identify pregnancy episodes for maternal health research and drug safety studies.",
    developed_for="Initial development for maternal medication safety studies in CPRD.",
    used_for="Pregnancy identification for covariate adjustment, medication safety in pregnancy, birth outcome studies.",
    limitations=(
        "Draft status — awaiting clinical review. Pregnancy episode boundaries "
        "(start/end dates) require additional algorithm logic beyond diagnosis codes. "
        "Early pregnancy losses may not be captured."
    ),
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
# 16. T2DM OpenSAFELY Study-Use (child of T2DM core definition)
# ---------------------------------------------------------------------------

_t2dm_opensafely_snomed = Codelist(
    id="cl-t2dm-opensafely-snomed",
    name="Type 2 diabetes mellitus — OpenSAFELY simplified (SNOMED CT)",
    coding_system=CodingSystem.SNOMED_CT,
    version="1.0",
    description=(
        "Simplified SNOMED CT codelist for T2DM used in OpenSAFELY CVD outcome "
        "studies. Subset of the core T2DM phenotype focusing on high-specificity "
        "diagnostic codes only (excludes complication-only codes)."
    ),
    coding_system_version="SNOMED CT UK Edition 2024-04-01",
    coding_system_release=date(2024, 4, 1),
    codes=[
        Code("44054006", "Diabetes mellitus type 2", CodingSystem.SNOMED_CT),
        Code("313436004", "Type 2 diabetes mellitus without complication", CodingSystem.SNOMED_CT),
        Code("421750000", "Ketoacidosis in type II diabetes mellitus", CodingSystem.SNOMED_CT),
    ],
)

t2dm_opensafely_use = Phenotype(
    id="ph-t2dm-opensafely-use-001",
    name="Type 2 Diabetes Mellitus — OpenSAFELY CVD Study Use",
    short_name="T2DM (OpenSAFELY)",
    phenotype_type=PhenotypeType.DISEASE,
    therapeutic_area=TherapeuticArea.DIABETES_ENDOCRINE,
    description=(
        "Study-specific adaptation of the core T2DM phenotype (OP-0001) for "
        "use in OpenSAFELY cardiovascular outcome studies. Uses a simplified "
        "SNOMED CT codelist focusing on high-specificity diagnostic codes to "
        "minimise misclassification in the context of CVD risk analysis."
    ),
    accession=AccessionID(prefix="OP", number=16, version="1.0"),
    codelists=[_t2dm_opensafely_snomed],
    ontology_terms=[
        OntologyTerm(system="SNOMED CT", code="44054006", label="Diabetes mellitus type 2", is_primary=True),
    ],
    population=PopulationConstraints(
        sex=Sex.BOTH,
        age_min=18,
        inclusion_criteria="Adults aged 18+ registered with an OpenSAFELY-TPP practice",
        exclusion_criteria="Type 1 diabetes, gestational diabetes, secondary diabetes",
        notes="Narrower codelist than core; prioritises specificity for CVD outcome studies",
    ),
    authors=[_AUTHORS["bennett"]],
    publications=[
        Publication(
            "Cardiovascular outcomes in type 2 diabetes: an OpenSAFELY cohort study",
            doi="10.1016/j.landig-2024-example",
            journal="The Lancet Digital Health",
            year=2024,
            url="https://www.thelancet.com/journals/landig/example-t2dm-cvd",
            is_primary=True,
        ),
    ],
    purpose="To identify T2DM patients with high specificity for CVD outcome analyses in OpenSAFELY.",
    developed_for="OpenSAFELY cardiovascular outcomes in type 2 diabetes cohort study.",
    used_for="CVD risk analysis in T2DM, medication effectiveness studies within OpenSAFELY-TPP.",
    limitations=(
        "Narrower codelist than core T2DM definition — trades sensitivity for specificity. "
        "Only validated in OpenSAFELY-TPP population; transferability to other datasets "
        "not yet assessed. Does not capture T2DM complications."
    ),
    validation_status=ValidationStatus.PUBLISHED,
    evidence_score=EvidenceScore(
        literature=0.80,
        clinical_review=0.75,
        validation=0.70,
        usage=0.85,
        provenance=0.80,
    ),
    data_sources=["OpenSAFELY-TPP"],
    methodology=(
        "Derived from core T2DM phenotype (OP-0001) by selecting high-specificity "
        "SNOMED CT codes only. Complication codes excluded to reduce false positives "
        "in CVD outcome analyses. Validated within the OpenSAFELY-TPP population."
    ),
    created_date=date(2024, 6, 1),
    updated_date=date(2024, 11, 1),
    version="1.0",
    source_code_url="https://github.com/opensafely/t2dm-cvd-outcomes",
    is_core_definition=False,
    parent_phenotype_id="ph-t2dm-001",
    related_phenotype_ids=["ph-t2dm-001", "ph-metformin-001"],
    source_repository="OpenCodelists / OpenSAFELY",
    tags=["diabetes", "endocrine", "OpenSAFELY", "CVD", "study-specific"],
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
    """Text search across phenotype metadata, codelist contents, and ontology terms.

    Searches phenotype names, descriptions, tags, therapeutic areas, types,
    source repositories, author names/institutions, AND (product fix #1):
    - All code values and term descriptions inside codelists
    - Ontology term labels and codes
    """
    query_lower = query.lower().strip()
    if not query_lower:
        return ALL_PHENOTYPES

    results = []
    for p in ALL_PHENOTYPES:
        # Core phenotype metadata
        searchable_parts = [
            p.name,
            p.short_name,
            p.description,
            " ".join(p.tags),
            p.therapeutic_area.value,
            p.phenotype_type.value,
            p.source_repository,
            " ".join(a.name for a in p.authors),
            " ".join(a.institution for a in p.authors),
        ]

        # Product fix #1: search code values and terms inside codelists
        for cl in p.codelists:
            for code in cl.codes:
                searchable_parts.append(code.code)
                searchable_parts.append(code.term)

        # Product fix #1: search ontology term labels and codes
        for ot in p.ontology_terms:
            searchable_parts.append(ot.code)
            searchable_parts.append(ot.label)

        searchable = " ".join(searchable_parts).lower()

        if query_lower in searchable:
            results.append(p)

    return results
