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
    create_overall_score_gauge,
    create_source_repository_chart,
    create_therapeutic_area_chart,
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

                st.markdown(f"""
                <div class="op-card">
                    <div class="op-card-title">{p.name}</div>
                    <div class="op-card-meta" style="margin-bottom:0.4rem;">
                        {p.description[:150]}{'...' if len(p.description) > 150 else ''}
                    </div>
                    <div style="margin-bottom:0.3rem;">
                        <span class="op-badge {area_badge}">{p.therapeutic_area.value}</span>
                        <span class="op-badge {status_badge}">{p.validation_status.value}</span>
                        <span class="op-badge op-badge-grey">{p.phenotype_type.value}</span>
                        <span class="op-badge op-badge-grey">v{p.version}</span>
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

    st.markdown(f"""
    <div style="border-bottom:3px solid #0d47a1;padding-bottom:1rem;margin-bottom:1.5rem;">
        <h1 style="margin-bottom:0.2rem;color:#0d47a1;">{phenotype.name}</h1>
        <div style="margin-bottom:0.5rem;">
            <span class="op-badge {area_badge}">{phenotype.therapeutic_area.value}</span>
            <span class="op-badge {status_badge}">{phenotype.validation_status.value}</span>
            <span class="op-badge op-badge-grey">{phenotype.phenotype_type.value}</span>
            <span class="op-badge op-badge-grey">v{phenotype.version}</span>
            <span class="op-badge op-badge-blue">{phenotype.source_repository}</span>
        </div>
        <p style="color:#546e7a;margin:0;">{phenotype.description}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------- Summary widget bar (Open Targets-inspired) ----------
    widgets_data = [
        ("Codes", phenotype.total_codes > 0),
        ("Evidence", phenotype.evidence_score.overall > 0),
        ("Pubs", len(phenotype.publications) > 0),
        ("Sources", len(phenotype.data_sources) > 0),
        ("Method", bool(phenotype.methodology)),
        ("Related", len(phenotype.related_phenotype_ids) > 0),
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
        tab_metadata,
        tab_sources,
        tab_download,
    ) = st.tabs([
        "Codelists & Codes",
        "Evidence & Validation",
        "Metadata & Provenance",
        "Data Sources",
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
            with st.expander(
                f"{cl.coding_system.value} — {cl.name} "
                f"({cl.code_count} codes, v{cl.version})",
                expanded=True,
            ):
                if cl.description:
                    st.caption(cl.description)

                # Code table
                code_data = []
                for code in cl.codes:
                    code_data.append({
                        "Code": code.code,
                        "Term": code.term,
                        "Status": "Included" if code.is_included else "Excluded",
                    })
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

        # Publications
        if phenotype.publications:
            st.subheader("Publications")
            for pub in phenotype.publications:
                pub_text = f"**{pub.title}**"
                if pub.journal:
                    pub_text += f" — *{pub.journal}*"
                if pub.year:
                    pub_text += f" ({pub.year})"
                st.markdown(pub_text)
                if pub.doi:
                    st.caption(f"DOI: {pub.doi}")
                if pub.pubmed_id:
                    st.caption(f"PubMed: {pub.pubmed_id}")

    # ----- Metadata & Provenance -----
    with tab_metadata:
        mcol1, mcol2 = st.columns(2)

        with mcol1:
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
            | Phenotype ID | `{phenotype.id}` |
            """)

        with mcol2:
            st.subheader("Tags")
            tags_html = " ".join(
                f'<span class="op-badge op-badge-blue">{tag}</span>'
                for tag in phenotype.tags
            )
            st.markdown(tags_html, unsafe_allow_html=True)

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

        # Full phenotype metadata download
        st.divider()
        st.subheader("Download phenotype metadata")
        meta = {
            "id": phenotype.id,
            "name": phenotype.name,
            "short_name": phenotype.short_name,
            "type": phenotype.phenotype_type.value,
            "therapeutic_area": phenotype.therapeutic_area.value,
            "description": phenotype.description,
            "validation_status": phenotype.validation_status.value,
            "version": phenotype.version,
            "evidence_score": phenotype.evidence_score.overall,
            "total_codes": phenotype.total_codes,
            "coding_systems": [cs.value for cs in phenotype.coding_systems],
            "data_sources": phenotype.data_sources,
            "authors": [
                {"name": a.name, "institution": a.institution, "orcid": a.orcid}
                for a in phenotype.authors
            ],
            "publications": [
                {"title": pub.title, "doi": pub.doi, "journal": pub.journal, "year": pub.year}
                for pub in phenotype.publications
            ],
            "methodology": phenotype.methodology,
            "created_date": phenotype.created_date.isoformat(),
            "updated_date": phenotype.updated_date.isoformat(),
            "source_repository": phenotype.source_repository,
            "tags": phenotype.tags,
        }
        import json
        st.download_button(
            label="Download full metadata (JSON)",
            data=json.dumps(meta, indent=2),
            file_name=f"{phenotype.id}_metadata.json",
            mime="application/json",
            key="dl_meta",
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
