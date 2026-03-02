"""
OpenPhenotypes — A best-of-class phenotype and codelist library.

Prototype combining the best features from:
- OpenCodelists (hierarchy-aware code browsing, versioning)
- HDR UK Phenotype Library (rich metadata, data source compatibility)
- OHDSI Phenotype Library (evidence scoring, peer review lifecycle)
- ClinicalCodes (publication linkage, coding-system coverage)
- Keele HCDR (clinical validation, musculoskeletal expertise)
- BHF DSC Codelist Comparison Tool (overlap analysis, GDPPR alignment)
- Open Targets (evidence scoring radar, therapeutic area browsing, search UX)
- Aslam et al. 2024 (automation, FAIR principles, cross-ontology mapping)
"""

import streamlit as st
import pandas as pd
import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from openphenotypes.models import (
    CodingSystem,
    PhenotypeType,
    TherapeuticArea,
    ValidationStatus,
    validate_phenotype,
    validation_summary,
)
from openphenotypes.sample_data import (
    ALL_PHENOTYPES,
    get_phenotype_by_id,
    search_phenotypes,
)
from openphenotypes.visualizations import (
    create_coding_system_heatmap,
    create_coding_system_sunburst,
    create_comparison_overlap,
    create_data_source_coverage,
    create_evidence_bars,
    create_evidence_radar,
    create_fair_completeness_chart,
    create_overall_score_gauge,
    create_source_repository_chart,
    create_therapeutic_area_chart,
    create_validation_metrics_chart,
    create_validation_status_pie,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="OpenPhenotypes | Phenotype & Codelist Library",
    page_icon=":dna:",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS — inspired by Open Targets' clean, data-rich aesthetic
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Global */
    .block-container { max-width: 1200px; }

    /* Hero header */
    .op-hero {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 40%, #0277bd 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .op-hero h1 {
        color: white;
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
    }
    .op-hero p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin-top: 0;
    }

    /* Stat cards */
    .op-stat-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .op-stat-card {
        flex: 1;
        min-width: 120px;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        border-top: 3px solid #0d47a1;
    }
    .op-stat-card .number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0d47a1;
    }
    .op-stat-card .label {
        font-size: 0.82rem;
        color: #546e7a;
        margin-top: 0.2rem;
    }

    /* Phenotype cards */
    .op-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: box-shadow 0.2s;
        border-left: 4px solid #0d47a1;
    }
    .op-card:hover {
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .op-card-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0d47a1;
        margin-bottom: 0.3rem;
    }
    .op-card-meta {
        font-size: 0.82rem;
        color: #78909c;
    }

    /* Badges */
    .op-badge {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }
    .op-badge-blue { background: #e3f2fd; color: #1565c0; }
    .op-badge-green { background: #e8f5e9; color: #2e7d32; }
    .op-badge-orange { background: #fff3e0; color: #e65100; }
    .op-badge-purple { background: #f3e5f5; color: #6a1b9a; }
    .op-badge-red { background: #fce4ec; color: #c62828; }
    .op-badge-grey { background: #eceff1; color: #455a64; }
    .op-badge-teal { background: #e0f2f1; color: #00695c; }

    /* Score bar */
    .op-score-bar {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .op-score-fill {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #e53935, #ffa726, #66bb6a);
    }
    .op-score-track {
        flex: 1;
        height: 8px;
        border-radius: 4px;
        background: #e0e0e0;
        overflow: hidden;
    }

    /* Evidence widget bar (Open Targets-inspired) */
    .op-widget-bar {
        display: flex;
        gap: 0.5rem;
        margin: 0.5rem 0;
        flex-wrap: wrap;
    }
    .op-widget {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
        color: white;
    }
    .op-widget-active { background: #0d47a1; }
    .op-widget-empty { background: #cfd8dc; }

    /* Code table */
    .op-code-row {
        display: flex;
        padding: 0.4rem 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 0.88rem;
    }
    .op-code-val {
        font-family: monospace;
        font-weight: 600;
        color: #0d47a1;
        width: 140px;
        flex-shrink: 0;
    }
    .op-code-term { color: #37474f; flex: 1; }
    .op-code-excluded {
        text-decoration: line-through;
        color: #b0bec5;
    }

    /* Source indicator dots (Open Targets-inspired) */
    .op-source-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 3px;
    }
    .op-source-active { background: #0d47a1; }
    .op-source-inactive { background: #e0e0e0; }

    /* Tab styling */
    div[data-testid="stTabs"] > div > div > div > button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "op_view" not in st.session_state:
    st.session_state.op_view = "browse"  # browse | detail | compare
if "op_selected_id" not in st.session_state:
    st.session_state.op_selected_id = None
if "op_compare_ids" not in st.session_state:
    st.session_state.op_compare_ids = []


def switch_to_detail(phenotype_id: str):
    st.session_state.op_view = "detail"
    st.session_state.op_selected_id = phenotype_id


def switch_to_browse():
    st.session_state.op_view = "browse"
    st.session_state.op_selected_id = None


def switch_to_compare():
    st.session_state.op_view = "compare"


# ---------------------------------------------------------------------------
# Helper renderers
# ---------------------------------------------------------------------------

VALIDATION_BADGE_CLASS = {
    ValidationStatus.DRAFT: "op-badge-grey",
    ValidationStatus.UNDER_REVIEW: "op-badge-orange",
    ValidationStatus.PEER_REVIEWED: "op-badge-blue",
    ValidationStatus.VALIDATED: "op-badge-green",
    ValidationStatus.PUBLISHED: "op-badge-teal",
}

THERAPEUTIC_AREA_BADGE_CLASS = {
    TherapeuticArea.CARDIOVASCULAR: "op-badge-red",
    TherapeuticArea.RESPIRATORY: "op-badge-blue",
    TherapeuticArea.MENTAL_HEALTH: "op-badge-purple",
    TherapeuticArea.ONCOLOGY: "op-badge-red",
    TherapeuticArea.DIABETES_ENDOCRINE: "op-badge-orange",
    TherapeuticArea.MUSCULOSKELETAL: "op-badge-green",
    TherapeuticArea.NEUROLOGY: "op-badge-purple",
    TherapeuticArea.INFECTIOUS_DISEASE: "op-badge-teal",
    TherapeuticArea.RENAL: "op-badge-blue",
    TherapeuticArea.GASTROINTESTINAL: "op-badge-green",
    TherapeuticArea.OBSTETRICS_GYNAECOLOGY: "op-badge-red",
    TherapeuticArea.OTHER: "op-badge-grey",
}


def render_score_bar(score: float) -> str:
    pct = int(score * 100)
    colour = "#66bb6a" if score >= 0.75 else "#ffa726" if score >= 0.5 else "#e53935"
    return (
        f'<div class="op-score-bar">'
        f'<div class="op-score-track"><div style="width:{pct}%;height:100%;'
        f'background:{colour};border-radius:4px;"></div></div>'
        f'<span style="font-size:0.85rem;font-weight:600;color:{colour};">{pct}%</span>'
        f'</div>'
    )


def render_data_source_dots(phenotype) -> str:
    """Open Targets-inspired availability dots for data sources."""
    all_sources = [
        "CPRD GOLD", "CPRD Aurum", "OpenSAFELY-TPP", "HES APC",
        "SAIL", "UK Biobank", "Research Data Scotland", "Scottish Safe Haven",
        "ONS", "National Cancer Registry", "Keele CiPCA", "OpenSAFELY-EMIS",
    ]
    dots = ""
    for src in all_sources:
        cls = "op-source-active" if src in phenotype.data_sources else "op-source-inactive"
        dots += f'<span class="op-source-dot {cls}" title="{src}"></span>'
    return dots


# ===========================================================================
# VIEW: BROWSE & SEARCH (main landing page)
# ===========================================================================

def render_browse_view():
    # Hero header
    st.markdown("""
    <div class="op-hero">
        <h1>OpenPhenotypes</h1>
        <p>A unified, open-access library of phenotype definitions and clinical codelists
        for UK health data research. Search, compare, and reuse validated phenotypes
        across SNOMED CT, ICD-10, Read, BNF, dm+d and more.</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary statistics
    total_phenotypes = len(ALL_PHENOTYPES)
    total_codes = sum(p.total_codes for p in ALL_PHENOTYPES)
    total_codelists = sum(len(p.codelists) for p in ALL_PHENOTYPES)
    coding_systems = len({cs for p in ALL_PHENOTYPES for cs in p.coding_systems})
    data_sources = len({ds for p in ALL_PHENOTYPES for ds in p.data_sources})
    validated = len([p for p in ALL_PHENOTYPES if p.validation_status in (
        ValidationStatus.VALIDATED, ValidationStatus.PUBLISHED
    )])

    st.markdown(f"""
    <div class="op-stat-row">
        <div class="op-stat-card">
            <div class="number">{total_phenotypes}</div>
            <div class="label">Phenotypes</div>
        </div>
        <div class="op-stat-card">
            <div class="number">{total_codelists}</div>
            <div class="label">Codelists</div>
        </div>
        <div class="op-stat-card">
            <div class="number">{total_codes:,}</div>
            <div class="label">Clinical codes</div>
        </div>
        <div class="op-stat-card">
            <div class="number">{coding_systems}</div>
            <div class="label">Coding systems</div>
        </div>
        <div class="op-stat-card">
            <div class="number">{data_sources}</div>
            <div class="label">Data sources</div>
        </div>
        <div class="op-stat-card">
            <div class="number">{validated}</div>
            <div class="label">Validated</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search bar (Open Targets-inspired: unified, prominent)
    col_search, col_compare = st.columns([4, 1])
    with col_search:
        query = st.text_input(
            "Search phenotypes, conditions, codes, or authors",
            placeholder="e.g. diabetes, SNOMED, cardiovascular, Bennett Institute...",
            label_visibility="collapsed",
        )
    with col_compare:
        if st.button("Compare codelists", use_container_width=True, type="secondary"):
            switch_to_compare()
            st.rerun()

    # Filters
    with st.expander("Filters", expanded=False):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            filter_area = st.multiselect(
                "Therapeutic area",
                options=[ta.value for ta in TherapeuticArea],
            )
        with fcol2:
            filter_type = st.multiselect(
                "Phenotype type",
                options=[pt.value for pt in PhenotypeType],
            )
        with fcol3:
            filter_status = st.multiselect(
                "Validation status",
                options=[vs.value for vs in ValidationStatus],
            )
        with fcol4:
            filter_system = st.multiselect(
                "Coding system",
                options=[cs.value for cs in CodingSystem],
            )

    # Apply search and filters
    results = search_phenotypes(query) if query else ALL_PHENOTYPES

    if filter_area:
        results = [p for p in results if p.therapeutic_area.value in filter_area]
    if filter_type:
        results = [p for p in results if p.phenotype_type.value in filter_type]
    if filter_status:
        results = [p for p in results if p.validation_status.value in filter_status]
    if filter_system:
        results = [
            p for p in results
            if any(cs.value in filter_system for cs in p.coding_systems)
        ]

    # Tabs for different views
    tab_list, tab_dashboard, tab_coverage = st.tabs([
        "Phenotype Library",
        "Dashboard",
        "Coverage Matrix",
    ])

    # ----- TAB 1: Phenotype list -----
    with tab_list:
        if not results:
            st.info("No phenotypes match your search criteria.")
        else:
            st.caption(f"Showing {len(results)} phenotype{'s' if len(results) != 1 else ''}")

            for p in results:
                area_badge = THERAPEUTIC_AREA_BADGE_CLASS.get(
                    p.therapeutic_area, "op-badge-grey"
                )
                status_badge = VALIDATION_BADGE_CLASS.get(
                    p.validation_status, "op-badge-grey"
                )
                score_pct = int(p.evidence_score.overall * 100)
                coding_badges = " ".join(
                    f'<span class="op-badge op-badge-blue">{cs.value}</span>'
                    for cs in p.coding_systems
                )
                # Accession ID badge
                accession_html = ""
                if p.accession.number > 0:
                    accession_html = f'<span class="op-badge op-badge-purple">{p.accession.accession}</span>'
                # Core vs use indicator
                hierarchy_badge = ""
                if not p.is_core_definition:
                    hierarchy_badge = '<span class="op-badge op-badge-orange">Study use</span>'
                # Ontology term
                ontology_html = ""
                if p.primary_ontology_term:
                    t = p.primary_ontology_term
                    ontology_html = f'<span class="op-badge op-badge-teal">{t.system}: {t.label}</span>'

                st.markdown(f"""
                <div class="op-card">
                    <div style="display:flex;align-items:baseline;gap:0.5rem;">
                        <div class="op-card-title">{p.name}</div>
                        {accession_html} {hierarchy_badge}
                    </div>
                    <div class="op-card-meta" style="margin-bottom:0.4rem;">
                        {p.description[:150]}{'...' if len(p.description) > 150 else ''}
                    </div>
                    <div style="margin-bottom:0.3rem;">
                        <span class="op-badge {area_badge}">{p.therapeutic_area.value}</span>
                        <span class="op-badge {status_badge}">{p.validation_status.value}</span>
                        <span class="op-badge op-badge-grey">{p.phenotype_type.value}</span>
                        <span class="op-badge op-badge-grey">v{p.version}</span>
                        {ontology_html}
                    </div>
                    <div style="margin-bottom:0.3rem;">{coding_badges}</div>
                    <div style="display:flex;align-items:center;gap:1rem;font-size:0.82rem;color:#546e7a;">
                        <span>Evidence: {render_score_bar(p.evidence_score.overall)}</span>
                        <span>{p.total_codes} codes</span>
                        <span>{len(p.codelists)} codelists</span>
                        <span>{len(p.data_sources)} data sources</span>
                        <span>Source: {p.source_repository}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(
                    f"View {p.short_name} details",
                    key=f"view_{p.id}",
                    use_container_width=False,
                ):
                    switch_to_detail(p.id)
                    st.rerun()

    # ----- TAB 2: Dashboard -----
    with tab_dashboard:
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.subheader("Phenotypes by therapeutic area")
            st.plotly_chart(
                create_therapeutic_area_chart(ALL_PHENOTYPES),
                use_container_width=True,
            )
        with dcol2:
            st.subheader("Validation status")
            st.plotly_chart(
                create_validation_status_pie(ALL_PHENOTYPES),
                use_container_width=True,
            )

        st.subheader("Source repositories")
        st.plotly_chart(
            create_source_repository_chart(ALL_PHENOTYPES),
            use_container_width=True,
        )

    # ----- TAB 3: Coverage matrix -----
    with tab_coverage:
        st.subheader("Coding system coverage")
        st.caption(
            "Which phenotypes have codelists in which coding systems. "
            "Colour intensity indicates number of codes."
        )
        st.plotly_chart(
            create_coding_system_heatmap(ALL_PHENOTYPES),
            use_container_width=True,
        )

        st.subheader("Data source compatibility")
        st.caption(
            "Which phenotypes have been validated or used in which UK data sources."
        )
        st.plotly_chart(
            create_data_source_coverage(ALL_PHENOTYPES),
            use_container_width=True,
        )


# ===========================================================================
# VIEW: PHENOTYPE DETAIL (entity profile page — Open Targets-inspired)
# ===========================================================================

def render_detail_view():
    phenotype = get_phenotype_by_id(st.session_state.op_selected_id)
    if not phenotype:
        st.error("Phenotype not found.")
        if st.button("Back to library"):
            switch_to_browse()
            st.rerun()
        return

    # Back button
    if st.button("Back to library", type="secondary"):
        switch_to_browse()
        st.rerun()

    # ---------- Header ----------
    area_badge = THERAPEUTIC_AREA_BADGE_CLASS.get(
        phenotype.therapeutic_area, "op-badge-grey"
    )
    status_badge = VALIDATION_BADGE_CLASS.get(
        phenotype.validation_status, "op-badge-grey"
    )

    # Accession and ontology info for header
    accession_html = ""
    if phenotype.accession.number > 0:
        accession_html = (
            f'<span class="op-badge op-badge-purple">{phenotype.accession.accession}</span>'
        )
    ontology_html = ""
    for term in phenotype.ontology_terms:
        ontology_html += f'<span class="op-badge op-badge-teal">{term.system}: {term.code} ({term.label})</span> '
    hierarchy_html = ""
    if not phenotype.is_core_definition:
        hierarchy_html = '<span class="op-badge op-badge-orange">Study-specific use</span>'

    st.markdown(f"""
    <div style="border-bottom:3px solid #0d47a1;padding-bottom:1rem;margin-bottom:1.5rem;">
        <h1 style="margin-bottom:0.2rem;color:#0d47a1;">{phenotype.name}</h1>
        <div style="margin-bottom:0.3rem;">
            {accession_html}
            <span class="op-badge {area_badge}">{phenotype.therapeutic_area.value}</span>
            <span class="op-badge {status_badge}">{phenotype.validation_status.value}</span>
            <span class="op-badge op-badge-grey">{phenotype.phenotype_type.value}</span>
            <span class="op-badge op-badge-grey">v{phenotype.version}</span>
            <span class="op-badge op-badge-blue">{phenotype.source_repository}</span>
            {hierarchy_html}
        </div>
        <div style="margin-bottom:0.3rem;">{ontology_html}</div>
        <p style="color:#546e7a;margin:0;">{phenotype.description}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------- Summary widget bar (Open Targets-inspired) ----------
    widgets_data = [
        ("Codes", phenotype.total_codes > 0),
        ("Evidence", phenotype.evidence_score.overall > 0),
        ("Valid", len(phenotype.validations) > 0),
        ("Impl", len(phenotype.implementations) > 0),
        ("Pubs", len(phenotype.publications) > 0),
        ("Sources", len(phenotype.data_sources) > 0),
        ("Method", bool(phenotype.methodology)),
        ("QC", len(phenotype.qc_rules) > 0),
        ("Related", len(phenotype.related_phenotype_ids) > 0 or len(phenotype.child_use_ids) > 0),
    ]
    widget_html = ""
    for label, active in widgets_data:
        cls = "op-widget-active" if active else "op-widget-empty"
        widget_html += f'<div class="op-widget {cls}" title="{label}">{label[:2]}</div>'

    st.markdown(f'<div class="op-widget-bar">{widget_html}</div>', unsafe_allow_html=True)

    # ---------- Key metrics row ----------
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    mcol1.metric("Total codes", phenotype.total_codes)
    mcol2.metric("Codelists", len(phenotype.codelists))
    mcol3.metric("Coding systems", len(phenotype.coding_systems))
    mcol4.metric("Data sources", len(phenotype.data_sources))
    mcol5.metric("Evidence score", f"{phenotype.evidence_score.overall:.0%}")

    st.divider()

    # ---------- Tabbed detail sections ----------
    (
        tab_codes,
        tab_evidence,
        tab_implementation,
        tab_metadata,
        tab_sources,
        tab_fair,
        tab_download,
    ) = st.tabs([
        "Codelists & Codes",
        "Evidence & Validation",
        "Implementation",
        "Metadata & Provenance",
        "Data Sources",
        "FAIR Compliance",
        "Download",
    ])

    # ----- Codelists & Codes -----
    with tab_codes:
        # Code distribution sunburst
        if len(phenotype.codelists) > 1:
            st.subheader("Code distribution by coding system")
            st.plotly_chart(
                create_coding_system_sunburst(phenotype),
                use_container_width=True,
            )

        # Individual codelists
        for cl in phenotype.codelists:
            version_info = f"v{cl.version}"
            if cl.coding_system_version:
                version_info += f" | {cl.coding_system_version}"

            with st.expander(
                f"{cl.coding_system.value} — {cl.name} "
                f"({cl.code_count} codes, {version_info})",
                expanded=True,
            ):
                if cl.description:
                    st.caption(cl.description)

                # Code table with expanded attributes
                code_data = []
                for code in cl.codes:
                    row = {
                        "Code": code.code,
                        "Term": code.term,
                        "Status": "Included" if code.is_included else "Excluded",
                        "Position": code.code_position.value,
                    }
                    if code.notes:
                        row["Notes"] = code.notes
                    code_data.append(row)
                df = pd.DataFrame(code_data)

                # Style excluded codes
                def highlight_excluded(row):
                    if row["Status"] == "Excluded":
                        return ["color: #b0bec5; text-decoration: line-through"] * len(row)
                    return [""] * len(row)

                st.dataframe(
                    df.style.apply(highlight_excluded, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    height=min(400, len(code_data) * 38 + 40),
                )

    # ----- Evidence & Validation -----
    with tab_evidence:
        ecol1, ecol2 = st.columns([1, 1])

        with ecol1:
            st.subheader("Overall evidence score")
            st.plotly_chart(
                create_overall_score_gauge(phenotype.evidence_score.overall),
                use_container_width=True,
            )

            st.subheader("Evidence dimensions")
            st.plotly_chart(
                create_evidence_bars(phenotype.evidence_score),
                use_container_width=True,
            )

        with ecol2:
            st.subheader("Evidence radar")
            st.plotly_chart(
                create_evidence_radar(phenotype.evidence_score, phenotype.short_name),
                use_container_width=True,
            )

            st.subheader("Validation methodology")
            if phenotype.methodology:
                st.markdown(phenotype.methodology)
            else:
                st.info("No methodology documentation available.")

        # Structured validation evidence (E)
        if phenotype.validations:
            st.subheader("Validation studies")
            st.plotly_chart(
                create_validation_metrics_chart(phenotype.validations),
                use_container_width=True,
            )
            for i, val in enumerate(phenotype.validations):
                with st.expander(f"Validation {i+1}: {val.method.value} — {val.dataset}"):
                    vcol1, vcol2 = st.columns(2)
                    with vcol1:
                        if val.ppv is not None:
                            st.metric("PPV", f"{val.ppv:.0%}")
                        if val.sensitivity is not None:
                            st.metric("Sensitivity", f"{val.sensitivity:.0%}")
                        if val.sample_size is not None:
                            st.metric("Sample size", f"{val.sample_size:,}")
                    with vcol2:
                        if val.specificity is not None:
                            st.metric("Specificity", f"{val.specificity:.0%}")
                        if val.npv is not None:
                            st.metric("NPV", f"{val.npv:.0%}")
                        if val.comparator:
                            st.caption(f"**Comparator:** {val.comparator}")
                    if val.notes:
                        st.markdown(val.notes)
                    if val.publication_doi:
                        st.caption(f"DOI: {val.publication_doi}")

        # Clinical endorsements
        if phenotype.clinical_endorsements:
            st.subheader("Clinical endorsements")
            for ce in phenotype.clinical_endorsements:
                ce_text = f"**{ce.reviewer_name}** — {ce.reviewer_role}, {ce.institution}"
                if ce.date:
                    ce_text += f" ({ce.date.isoformat()})"
                st.markdown(ce_text)
                if ce.notes:
                    st.caption(ce.notes)

        # Publications
        if phenotype.publications:
            st.subheader("Publications")
            for pub in phenotype.publications:
                primary_marker = " **[Primary]**" if pub.is_primary else ""
                pub_text = f"**{pub.title}**{primary_marker}"
                if pub.journal:
                    pub_text += f" — *{pub.journal}*"
                if pub.year:
                    pub_text += f" ({pub.year})"
                st.markdown(pub_text)
                if pub.doi:
                    st.caption(f"DOI: {pub.doi}")
                if pub.pubmed_id:
                    st.caption(f"PubMed: {pub.pubmed_id}")

    # ----- Implementation (D) -----
    with tab_implementation:
        if phenotype.logic_description:
            st.subheader("Algorithm description")
            st.markdown(phenotype.logic_description)

        if phenotype.implementations:
            st.subheader("Reference implementations")
            for impl in phenotype.implementations:
                with st.expander(f"{impl.label} ({impl.language})"):
                    if impl.dataset_target:
                        st.caption(f"Target dataset: {impl.dataset_target}")
                    st.code(impl.code, language=impl.language.lower() if impl.language.lower() in ("sql", "python") else None)
                    if impl.source_url:
                        st.caption(f"Source: {impl.source_url}")
                    if impl.notes:
                        st.caption(impl.notes)
        else:
            st.info("No reference implementations available yet.")

        if phenotype.dummy_data_examples:
            st.subheader("Worked examples (dummy data)")
            for ex in phenotype.dummy_data_examples:
                with st.expander(ex.description):
                    st.markdown("**Input data:**")
                    st.code(ex.input_data)
                    st.markdown("**Expected output:**")
                    st.code(ex.expected_output)
                    if ex.notes:
                        st.caption(ex.notes)

        if phenotype.qc_rules:
            st.subheader("Quality control rules")
            for rule in phenotype.qc_rules:
                severity_icon = {"error": "!!!", "warning": "!!", "info": "i"}.get(rule.severity, "?")
                st.markdown(
                    f"**[{rule.rule_id}]** ({rule.severity}) {rule.description}"
                )
                if rule.applies_to:
                    st.caption(f"Applies to: {rule.applies_to}")

        if phenotype.data_preprocessing:
            st.subheader("Dataset-specific preprocessing")
            st.markdown(phenotype.data_preprocessing)

        if not any([phenotype.implementations, phenotype.dummy_data_examples,
                     phenotype.qc_rules, phenotype.logic_description]):
            st.info(
                "No implementation artefacts available. "
                "Consider contributing pseudocode, SQL, or Python implementations."
            )

    # ----- Metadata & Provenance -----
    with tab_metadata:
        mcol1, mcol2 = st.columns(2)

        with mcol1:
            st.subheader("Identifiers")
            id_rows = [
                ("Phenotype ID", f"`{phenotype.id}`"),
                ("Version", phenotype.version),
            ]
            if phenotype.accession.number > 0:
                id_rows.append(("Accession", f"`{phenotype.accession.accession}`"))
                id_rows.append(("Stable URL", f"`{phenotype.accession.stable_url}`"))
                id_rows.append(("Latest URL", f"`{phenotype.accession.latest_url}`"))
            if phenotype.source_code_url:
                id_rows.append(("Source code", phenotype.source_code_url))
            id_table = "| Field | Value |\n|-------|-------|\n"
            for field_name, value in id_rows:
                id_table += f"| {field_name} | {value} |\n"
            st.markdown(id_table)

            st.subheader("Authors")
            for author in phenotype.authors:
                author_text = f"**{author.name}** — {author.institution}"
                if author.orcid:
                    author_text += f" (ORCID: {author.orcid})"
                st.markdown(author_text)

            st.subheader("Version history")
            st.markdown(f"""
            | Field | Value |
            |-------|-------|
            | Current version | {phenotype.version} |
            | Created | {phenotype.created_date.isoformat()} |
            | Last updated | {phenotype.updated_date.isoformat()} |
            | Source repository | {phenotype.source_repository} |
            """)

            # Population constraints (Table 1)
            st.subheader("Population constraints")
            pop = phenotype.population
            pop_rows = [("Sex", pop.sex.value)]
            if pop.age_min is not None or pop.age_max is not None:
                age_range = f"{pop.age_min or 'any'} – {pop.age_max or 'any'}"
                pop_rows.append(("Age range", age_range))
            if pop.inclusion_criteria:
                pop_rows.append(("Inclusion criteria", pop.inclusion_criteria))
            if pop.exclusion_criteria:
                pop_rows.append(("Exclusion criteria", pop.exclusion_criteria))
            if pop.notes:
                pop_rows.append(("Notes", pop.notes))
            if phenotype.valid_date_start or phenotype.valid_date_end:
                date_range = f"{phenotype.valid_date_start or 'any'} – {phenotype.valid_date_end or 'ongoing'}"
                pop_rows.append(("Valid date range", date_range))
            pop_table = "| Field | Value |\n|-------|-------|\n"
            for field_name, value in pop_rows:
                pop_table += f"| {field_name} | {value} |\n"
            st.markdown(pop_table)

        with mcol2:
            # Ontology terms
            if phenotype.ontology_terms:
                st.subheader("Ontology terms")
                for term in phenotype.ontology_terms:
                    primary_marker = " (primary)" if term.is_primary else ""
                    st.markdown(f"- **{term.system}**: `{term.code}` — {term.label}{primary_marker}")

            st.subheader("Tags")
            tags_html = " ".join(
                f'<span class="op-badge op-badge-blue">{tag}</span>'
                for tag in phenotype.tags
            )
            st.markdown(tags_html, unsafe_allow_html=True)

            # Core/use hierarchy (G)
            if phenotype.is_core_definition and phenotype.child_use_ids:
                st.subheader("Study-specific uses (derived)")
                st.caption("Phenotypes derived from this core definition for specific studies.")
                for child_id in phenotype.child_use_ids:
                    child_p = get_phenotype_by_id(child_id)
                    if child_p:
                        if st.button(
                            f"{child_p.name} ({child_p.short_name})",
                            key=f"child_{child_id}",
                        ):
                            switch_to_detail(child_id)
                            st.rerun()
            elif not phenotype.is_core_definition and phenotype.parent_phenotype_id:
                st.subheader("Parent core definition")
                parent_p = get_phenotype_by_id(phenotype.parent_phenotype_id)
                if parent_p:
                    if st.button(
                        f"{parent_p.name} ({parent_p.short_name})",
                        key=f"parent_{phenotype.parent_phenotype_id}",
                    ):
                        switch_to_detail(phenotype.parent_phenotype_id)
                        st.rerun()

            st.subheader("Related phenotypes")
            if phenotype.related_phenotype_ids:
                for rel_id in phenotype.related_phenotype_ids:
                    rel_p = get_phenotype_by_id(rel_id)
                    if rel_p:
                        if st.button(
                            f"{rel_p.name} ({rel_p.short_name})",
                            key=f"rel_{rel_id}",
                        ):
                            switch_to_detail(rel_id)
                            st.rerun()
                    else:
                        st.caption(f"`{rel_id}` (not in library)")
            else:
                st.caption("No related phenotypes linked.")

            # Dataset provenance (Table 1)
            if phenotype.dataset_provenance:
                st.subheader("Dataset provenance")
                for dp in phenotype.dataset_provenance:
                    dp_text = f"**{dp.dataset_name}**"
                    if dp.dataset_identifier:
                        dp_text += f" ({dp.dataset_identifier})"
                    if dp.date_range_start and dp.date_range_end:
                        dp_text += f" | {dp.date_range_start} – {dp.date_range_end}"
                    if dp.population_size:
                        dp_text += f" | N={dp.population_size:,}"
                    st.markdown(dp_text)
                    if dp.notes:
                        st.caption(dp.notes)

    # ----- Data Sources -----
    with tab_sources:
        st.subheader("Compatible data sources")
        st.caption(
            "Data sources where this phenotype has been used or validated."
        )

        source_cols = st.columns(3)
        for i, src in enumerate(phenotype.data_sources):
            with source_cols[i % 3]:
                st.markdown(f"""
                <div style="background:#e3f2fd;border-radius:8px;padding:0.6rem 1rem;
                margin-bottom:0.5rem;font-weight:600;color:#0d47a1;">
                    {src}
                </div>
                """, unsafe_allow_html=True)

        st.subheader("Coding systems available")
        for cl in phenotype.codelists:
            st.markdown(
                f"- **{cl.coding_system.value}** — {cl.code_count} codes (v{cl.version})"
            )

    # ----- FAIR Compliance -----
    with tab_fair:
        st.subheader("FAIR metadata completeness")
        st.caption(
            "Assessment of metadata completeness against the BHF DSC FAIR "
            "Phenotyping report Table 1 requirements."
        )

        st.plotly_chart(
            create_fair_completeness_chart(phenotype),
            use_container_width=True,
        )

        # Semantic validation results
        st.subheader("Semantic validation")
        issues = validate_phenotype(phenotype)
        summary = validation_summary(issues)

        if summary["passed"]:
            st.success(
                f"Phenotype passes validation. "
                f"{summary['warnings']} warning(s), {summary['info']} info message(s)."
            )
        else:
            st.error(
                f"Phenotype has {summary['errors']} error(s) that must be resolved."
            )

        if issues:
            for issue in issues:
                icon = {"error": "!!!", "warning": "!", "info": "i"}.get(issue.severity, "?")
                if issue.severity == "error":
                    st.markdown(f"**[ERROR]** `{issue.field}`: {issue.message}")
                elif issue.severity == "warning":
                    st.markdown(f"**[WARNING]** `{issue.field}`: {issue.message}")
                else:
                    st.markdown(f"**[INFO]** `{issue.field}`: {issue.message}")
                if issue.suggestion:
                    st.caption(f"Suggestion: {issue.suggestion}")

    # ----- Download -----
    with tab_download:
        st.subheader("Download codelists")
        st.caption(
            "Download individual codelists as CSV files for use in your research pipeline."
        )

        for cl in phenotype.codelists:
            code_data = []
            for code in cl.codes:
                code_data.append({
                    "code": code.code,
                    "term": code.term,
                    "coding_system": code.coding_system.value,
                    "included": code.is_included,
                })
            df = pd.DataFrame(code_data)

            csv = df.to_csv(index=False)
            st.download_button(
                label=f"Download {cl.coding_system.value} codelist ({cl.code_count} codes)",
                data=csv,
                file_name=f"{phenotype.id}_{cl.id}.csv",
                mime="text/csv",
                key=f"dl_{cl.id}",
            )

        # Full phenotype metadata download (FAIR-complete)
        st.divider()
        st.subheader("Download phenotype metadata (FAIR-complete)")
        import json
        meta = {
            "id": phenotype.id,
            "accession": phenotype.accession.accession if phenotype.accession.number > 0 else None,
            "stable_url": phenotype.accession.stable_url if phenotype.accession.number > 0 else None,
            "name": phenotype.name,
            "short_name": phenotype.short_name,
            "type": phenotype.phenotype_type.value,
            "therapeutic_area": phenotype.therapeutic_area.value,
            "description": phenotype.description,
            "validation_status": phenotype.validation_status.value,
            "version": phenotype.version,
            "evidence_score": phenotype.evidence_score.overall,
            "evidence_dimensions": phenotype.evidence_score.to_dict(),
            "total_codes": phenotype.total_codes,
            "coding_systems": [cs.value for cs in phenotype.coding_systems],
            "ontology_terms": [
                {"system": t.system, "code": t.code, "label": t.label, "is_primary": t.is_primary}
                for t in phenotype.ontology_terms
            ],
            "population": {
                "sex": phenotype.population.sex.value,
                "age_min": phenotype.population.age_min,
                "age_max": phenotype.population.age_max,
                "inclusion_criteria": phenotype.population.inclusion_criteria,
                "exclusion_criteria": phenotype.population.exclusion_criteria,
            },
            "data_sources": phenotype.data_sources,
            "dataset_provenance": [
                {"name": dp.dataset_name, "identifier": dp.dataset_identifier,
                 "date_range_start": dp.date_range_start.isoformat() if dp.date_range_start else None,
                 "date_range_end": dp.date_range_end.isoformat() if dp.date_range_end else None,
                 "population_size": dp.population_size}
                for dp in phenotype.dataset_provenance
            ],
            "authors": [
                {"name": a.name, "institution": a.institution, "orcid": a.orcid}
                for a in phenotype.authors
            ],
            "publications": [
                {"title": pub.title, "doi": pub.doi, "journal": pub.journal,
                 "year": pub.year, "is_primary": pub.is_primary}
                for pub in phenotype.publications
            ],
            "validations": [
                {"method": v.method.value, "dataset": v.dataset,
                 "ppv": v.ppv, "sensitivity": v.sensitivity,
                 "specificity": v.specificity, "npv": v.npv,
                 "sample_size": v.sample_size, "comparator": v.comparator}
                for v in phenotype.validations
            ],
            "methodology": phenotype.methodology,
            "logic_description": phenotype.logic_description,
            "source_code_url": phenotype.source_code_url,
            "created_date": phenotype.created_date.isoformat(),
            "updated_date": phenotype.updated_date.isoformat(),
            "source_repository": phenotype.source_repository,
            "is_core_definition": phenotype.is_core_definition,
            "parent_phenotype_id": phenotype.parent_phenotype_id,
            "child_use_ids": phenotype.child_use_ids,
            "related_phenotype_ids": phenotype.related_phenotype_ids,
            "tags": phenotype.tags,
        }
        st.download_button(
            label="Download full metadata (JSON)",
            data=json.dumps(meta, indent=2),
            file_name=f"{phenotype.id}_metadata.json",
            mime="application/json",
            key="dl_meta",
        )

        # Algorithm bundle (zip of metadata + codelists + implementations)
        st.divider()
        st.subheader("Phenotype algorithm bundle")
        st.caption(
            "Download a complete bundle containing metadata JSON, all codelists "
            "as CSV, and any reference implementations. Suitable for reproducible research."
        )
        import io
        import zipfile
        bundle_buf = io.BytesIO()
        with zipfile.ZipFile(bundle_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # Metadata
            zf.writestr("metadata.json", json.dumps(meta, indent=2))
            # Codelists
            for cl in phenotype.codelists:
                rows = []
                for code in cl.codes:
                    rows.append({
                        "code": code.code,
                        "term": code.term,
                        "coding_system": code.coding_system.value,
                        "included": code.is_included,
                        "code_position": code.code_position.value,
                    })
                csv_df = pd.DataFrame(rows)
                zf.writestr(f"codelists/{cl.id}.csv", csv_df.to_csv(index=False))
            # Implementations
            for i, impl in enumerate(phenotype.implementations):
                ext = {"sql": "sql", "python": "py", "pseudocode": "txt"}.get(
                    impl.language.lower(), "txt"
                )
                zf.writestr(f"implementations/{i+1}_{impl.language.lower()}.{ext}", impl.code)
        bundle_buf.seek(0)
        st.download_button(
            label="Download algorithm bundle (.zip)",
            data=bundle_buf.getvalue(),
            file_name=f"{phenotype.id}_bundle.zip",
            mime="application/zip",
            key="dl_bundle",
        )

        # OMOP concept set export (if OMOP codelist exists)
        omop_codelists = [cl for cl in phenotype.codelists if cl.coding_system == CodingSystem.OMOP]
        if omop_codelists:
            st.divider()
            st.subheader("OMOP concept set export")
            for cl in omop_codelists:
                concept_set = {
                    "name": phenotype.name,
                    "id": phenotype.id,
                    "expression": {
                        "items": [
                            {
                                "concept": {"CONCEPT_ID": code.code, "CONCEPT_NAME": code.term},
                                "isExcluded": not code.is_included,
                                "includeDescendants": True,
                            }
                            for code in cl.codes
                        ]
                    }
                }
                st.download_button(
                    label="Download OMOP concept set (JSON)",
                    data=json.dumps(concept_set, indent=2),
                    file_name=f"{phenotype.id}_omop_concept_set.json",
                    mime="application/json",
                    key=f"dl_omop_{cl.id}",
                )


# ===========================================================================
# VIEW: CODELIST COMPARISON (inspired by BHF DSC tool)
# ===========================================================================

def render_compare_view():
    if st.button("Back to library", type="secondary"):
        switch_to_browse()
        st.rerun()

    st.markdown("""
    <div style="border-bottom:3px solid #0d47a1;padding-bottom:1rem;margin-bottom:1.5rem;">
        <h1 style="color:#0d47a1;">Codelist Comparison Tool</h1>
        <p style="color:#546e7a;">
            Compare codelists across phenotype definitions to identify overlap,
            unique codes, and gaps. Inspired by the
            <a href="https://bhfdsc.github.io/documentation/docs/resources/codelist_comparison_tool">BHF DSC Codelist Comparison Tool</a>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Select phenotypes to compare
    pheno_options = {p.id: f"{p.name} ({p.short_name})" for p in ALL_PHENOTYPES}

    ccol1, ccol2 = st.columns(2)
    with ccol1:
        pheno_a_id = st.selectbox(
            "Phenotype A",
            options=list(pheno_options.keys()),
            format_func=lambda x: pheno_options[x],
            index=0,
        )
    with ccol2:
        pheno_b_id = st.selectbox(
            "Phenotype B",
            options=list(pheno_options.keys()),
            format_func=lambda x: pheno_options[x],
            index=min(1, len(pheno_options) - 1),
        )

    pheno_a = get_phenotype_by_id(pheno_a_id)
    pheno_b = get_phenotype_by_id(pheno_b_id)

    if not pheno_a or not pheno_b:
        st.error("Please select two valid phenotypes.")
        return

    if pheno_a_id == pheno_b_id:
        st.warning("Please select two different phenotypes to compare.")
        return

    st.divider()

    # ---------- Side-by-side overview ----------
    st.subheader("Overview comparison")
    overview_df = pd.DataFrame({
        "Attribute": [
            "Name",
            "Type",
            "Therapeutic area",
            "Validation status",
            "Version",
            "Evidence score",
            "Total codes",
            "Coding systems",
            "Data sources",
            "Source repository",
        ],
        pheno_a.short_name: [
            pheno_a.name,
            pheno_a.phenotype_type.value,
            pheno_a.therapeutic_area.value,
            pheno_a.validation_status.value,
            pheno_a.version,
            f"{pheno_a.evidence_score.overall:.0%}",
            str(pheno_a.total_codes),
            ", ".join(cs.value for cs in pheno_a.coding_systems),
            str(len(pheno_a.data_sources)),
            pheno_a.source_repository,
        ],
        pheno_b.short_name: [
            pheno_b.name,
            pheno_b.phenotype_type.value,
            pheno_b.therapeutic_area.value,
            pheno_b.validation_status.value,
            pheno_b.version,
            f"{pheno_b.evidence_score.overall:.0%}",
            str(pheno_b.total_codes),
            ", ".join(cs.value for cs in pheno_b.coding_systems),
            str(len(pheno_b.data_sources)),
            pheno_b.source_repository,
        ],
    })
    st.dataframe(overview_df, use_container_width=True, hide_index=True)

    # ---------- Evidence comparison ----------
    st.subheader("Evidence score comparison")
    evcol1, evcol2 = st.columns(2)
    with evcol1:
        st.plotly_chart(
            create_evidence_radar(pheno_a.evidence_score, pheno_a.short_name),
            use_container_width=True,
        )
    with evcol2:
        st.plotly_chart(
            create_evidence_radar(pheno_b.evidence_score, pheno_b.short_name),
            use_container_width=True,
        )

    # ---------- Code overlap analysis ----------
    # Find shared coding systems
    shared_systems = set(pheno_a.coding_systems) & set(pheno_b.coding_systems)

    if shared_systems:
        st.subheader("Code overlap analysis")
        st.caption("Comparing codes in shared coding systems.")

        for system in sorted(shared_systems, key=lambda s: s.value):
            cl_a = next(
                (cl for cl in pheno_a.codelists if cl.coding_system == system), None
            )
            cl_b = next(
                (cl for cl in pheno_b.codelists if cl.coding_system == system), None
            )
            if not cl_a or not cl_b:
                continue

            codes_a = {c.code for c in cl_a.codes if c.is_included}
            codes_b = {c.code for c in cl_b.codes if c.is_included}

            st.markdown(f"**{system.value}**")
            st.plotly_chart(
                create_comparison_overlap(
                    codes_a, codes_b, pheno_a.short_name, pheno_b.short_name
                ),
                use_container_width=True,
            )

            # Show shared codes
            shared = codes_a & codes_b
            if shared:
                with st.expander(f"Shared {system.value} codes ({len(shared)})"):
                    shared_data = []
                    for code_val in sorted(shared):
                        term_a = next(
                            (c.term for c in cl_a.codes if c.code == code_val), ""
                        )
                        shared_data.append({"Code": code_val, "Term": term_a})
                    st.dataframe(
                        pd.DataFrame(shared_data),
                        use_container_width=True,
                        hide_index=True,
                    )

            # Show codes only in A
            only_a = codes_a - codes_b
            if only_a:
                with st.expander(
                    f"Only in {pheno_a.short_name} ({len(only_a)} codes)"
                ):
                    only_a_data = []
                    for code_val in sorted(only_a):
                        term = next(
                            (c.term for c in cl_a.codes if c.code == code_val), ""
                        )
                        only_a_data.append({"Code": code_val, "Term": term})
                    st.dataframe(
                        pd.DataFrame(only_a_data),
                        use_container_width=True,
                        hide_index=True,
                    )

            # Show codes only in B
            only_b = codes_b - codes_a
            if only_b:
                with st.expander(
                    f"Only in {pheno_b.short_name} ({len(only_b)} codes)"
                ):
                    only_b_data = []
                    for code_val in sorted(only_b):
                        term = next(
                            (c.term for c in cl_b.codes if c.code == code_val), ""
                        )
                        only_b_data.append({"Code": code_val, "Term": term})
                    st.dataframe(
                        pd.DataFrame(only_b_data),
                        use_container_width=True,
                        hide_index=True,
                    )
    else:
        st.info(
            "These phenotypes do not share any coding systems, so code-level "
            "comparison is not possible."
        )

    # ---------- Data source overlap ----------
    st.subheader("Data source compatibility")
    sources_a = set(pheno_a.data_sources)
    sources_b = set(pheno_b.data_sources)
    shared_sources = sources_a & sources_b

    source_comparison = []
    all_sources = sorted(sources_a | sources_b)
    for src in all_sources:
        source_comparison.append({
            "Data source": src,
            pheno_a.short_name: "Yes" if src in sources_a else "",
            pheno_b.short_name: "Yes" if src in sources_b else "",
            "Shared": "Yes" if src in shared_sources else "",
        })

    st.dataframe(
        pd.DataFrame(source_comparison),
        use_container_width=True,
        hide_index=True,
    )


# ===========================================================================
# Router
# ===========================================================================

if st.session_state.op_view == "detail":
    render_detail_view()
elif st.session_state.op_view == "compare":
    render_compare_view()
else:
    render_browse_view()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.markdown("""
<div style='text-align: center; font-size: 0.85rem; color: #90a4ae; padding: 1rem 0;'>
    <strong>OpenPhenotypes</strong> — Prototype v0.1<br>
    Combining the best of
    <a href="https://www.opencodelists.org/">OpenCodelists</a>,
    <a href="https://phenotypes.healthdatagateway.org/">HDR UK Phenotype Library</a>,
    <a href="https://ohdsi.github.io/PhenotypeLibrary/">OHDSI Phenotype Library</a>,
    <a href="https://clinicalcodes.rss.mhs.man.ac.uk/">ClinicalCodes</a>,
    <a href="https://www.keele.ac.uk/hcdr/codelists/">Keele HCDR</a>, and
    <a href="https://www.opentargets.org/">Open Targets</a> design patterns.<br>
    Sample data for demonstration purposes only.
</div>
""", unsafe_allow_html=True)
