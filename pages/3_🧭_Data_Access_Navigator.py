"""
UK Health Data Access Navigator
================================
Flagship page: personalised pathway recommendations for accessing UK health data.
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime

# Ensure project root is on sys.path so `data_access` is importable.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from data_access.loader import load_all_custodians, load_governance_bodies
from data_access.navigator import rank_pathways
from data_access.models import ResearcherProfile, PathwayRecommendation
from data_access.visualizations import (
    create_pathway_sankey,
    create_comparison_radar,
    create_timeline_gantt,
    create_cost_comparison,
    create_score_overview,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Data Access Navigator | UK Health Data",
    page_icon=":compass:",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Load data (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def cached_load_custodians():
    return load_all_custodians()

@st.cache_data
def cached_load_governance():
    return load_governance_bodies()

custodians = cached_load_custodians()
governance_bodies = cached_load_governance()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("Data Access Navigator")
st.markdown(
    f"**Personalised pathway recommendations across {len(custodians)} data custodians "
    f"covering all 4 UK nations**"
)
st.markdown(
    "Tell us about your research and we'll recommend the best routes to access "
    "the health data you need — with estimated timelines, costs, and governance requirements."
)

st.divider()

# ---------------------------------------------------------------------------
# Form options
# ---------------------------------------------------------------------------

RESEARCHER_TYPES = [
    "Academic researcher",
    "NHS analyst",
    "Industry (pharma/biotech)",
    "Government/policy",
    "Charity/third sector",
    "Student/trainee",
]

INSTITUTION_COUNTRIES = [
    "England", "Wales", "Scotland", "Northern Ireland", "Outside UK",
]

ETHICS_OPTIONS = [
    "Not yet applied",
    "In progress",
    "Approved",
    "Not sure what I need",
]

FUNDING_OPTIONS = [
    "Funded (grant)",
    "Funded (institutional)",
    "Seeking funding",
    "No funding needed",
    "Commercial budget",
]

DATA_TYPES = [
    "Primary care (GP records)",
    "Hospital episodes (HES/inpatient)",
    "Mortality/death registrations",
    "Cancer registry",
    "Genomic/genetic data",
    "Imaging (MRI, CT, X-ray)",
    "Mental health records",
    "Maternity records",
    "Prescription data",
    "COVID-19 specific",
    "Linked social/education data",
    "Biomarker/blood samples",
    "Patient-reported outcomes",
    "Administrative/billing",
]

GEOGRAPHIC_OPTIONS = [
    "England", "Wales", "Scotland", "Northern Ireland", "UK-wide",
]

POPULATION_OPTIONS = [
    "<1,000", "1,000-10,000", "10,000-100,000",
    "100,000-1M", "1M+", "Whole population",
]

STUDY_TYPES = [
    "Observational/epidemiological",
    "Clinical trial (RCT)",
    "Health economics",
    "Machine learning/AI",
    "Public health surveillance",
    "Service evaluation",
    "Genomic/biobank study",
    "Record linkage study",
]

TIMELINE_OPTIONS = [
    "Not urgent", "Within 12 months", "Within 6 months",
    "Within 3 months", "ASAP",
]

BUDGET_OPTIONS = [
    "Free/no budget",
    "Up to GBP 5,000",
    "GBP 5,000-25,000",
    "GBP 25,000-100,000",
    "GBP 100,000+",
]


# ---------------------------------------------------------------------------
# Research profile form
# ---------------------------------------------------------------------------

with st.form("research_profile", border=True):
    st.subheader("Tell us about your research")

    # --- About you ---
    st.markdown("##### About You")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        researcher_type = st.selectbox("I am a...", RESEARCHER_TYPES)
        institution_country = st.selectbox("Institution based in...", INSTITUTION_COUNTRIES)
    with col_a2:
        ethics_status = st.selectbox("Ethics approval status", ETHICS_OPTIONS)
        funding_status = st.selectbox("Funding status", FUNDING_OPTIONS)

    st.markdown("---")

    # --- Data requirements ---
    st.markdown("##### Data Requirements")
    data_needs = st.multiselect(
        "What type of data do you need?",
        DATA_TYPES,
        help="Select all data types relevant to your study",
    )
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        geographic_scope = st.multiselect(
            "Geographic coverage needed",
            GEOGRAPHIC_OPTIONS,
            default=["England"],
        )
    with col_d2:
        population_size = st.select_slider(
            "Approximate population size needed",
            options=POPULATION_OPTIONS,
            value="10,000-100,000",
        )
    study_type = st.selectbox("Study design", STUDY_TYPES)

    st.markdown("---")

    # --- Preferences ---
    st.markdown("##### Preferences & Constraints")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        timeline_priority = st.select_slider(
            "Timeline priority",
            options=TIMELINE_OPTIONS,
            value="Within 12 months",
        )
        budget_range = st.selectbox("Budget for data access", BUDGET_OPTIONS)
    with col_p2:
        needs_extraction = st.checkbox(
            "I need data extracted/exported (not just TRE access)",
            help="Most custodians require analysis within a Trusted Research Environment. "
                 "Tick this if you specifically need data extracts.",
        )
        needs_repeat = st.checkbox("I need ongoing/repeat access")
        needs_s251 = st.checkbox(
            "Involves identifiable data without explicit patient consent",
            help="If ticked, we'll include Section 251 / CAG in the governance requirements (England & Wales) "
                 "or PBPP Tier 2 (Scotland).",
        )

    submitted = st.form_submit_button("Find My Pathways", type="primary", use_container_width=True)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

if submitted:
    if not data_needs:
        st.warning("Please select at least one data type to get recommendations.")
        st.stop()

    profile = ResearcherProfile(
        researcher_type=researcher_type,
        institution_country=institution_country,
        ethics_status=ethics_status,
        funding_status=funding_status,
        data_needs=data_needs,
        geographic_scope=geographic_scope,
        population_size=population_size,
        study_type=study_type,
        timeline_priority=timeline_priority,
        budget_range=budget_range,
        needs_data_extraction=needs_extraction,
        needs_repeat_access=needs_repeat,
        needs_section_251=needs_s251,
    )

    # --- Run the scoring engine ---
    recommendations = rank_pathways(profile, custodians, governance_bodies)

    # Store in session for AI advisory and cross-page use
    st.session_state["navigator_results"] = recommendations
    st.session_state["navigator_profile"] = profile

    # --- Metrics ---
    st.divider()
    top = recommendations[0] if recommendations else None
    fastest = min(recommendations, key=lambda r: r.estimated_total_weeks) if recommendations else None

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Pathways Analysed", len(recommendations))
    col_m2.metric("Top Match", f"{top.overall_score:.0f}%" if top else "N/A")
    col_m3.metric("Fastest Route", f"~{fastest.estimated_total_weeks}wk" if fastest else "N/A")
    col_m4.metric("Custodians Loaded", len(custodians))

    st.divider()

    # === Hero recommendation ===
    if top and top.overall_score > 0:
        st.subheader(f"Top Recommendation: {top.custodian.name}")
        hero_col1, hero_col2 = st.columns([3, 1])
        with hero_col1:
            st.markdown(f"**{top.custodian.description}**")
            if top.match_reasons:
                for reason in top.match_reasons[:4]:
                    st.markdown(f"- {reason}")
            if top.concerns:
                st.markdown("**Considerations:**")
                for concern in top.concerns[:3]:
                    st.markdown(f"- :orange[{concern}]")
        with hero_col2:
            st.metric("Match Score", f"{top.overall_score:.0f}%")
            st.metric("Est. Timeline", f"~{top.estimated_total_weeks} weeks")
            st.metric("Est. Cost", top.estimated_cost_range)
            st.link_button("Visit Website", top.custodian.url)

        st.divider()

    # === Tabbed results ===
    tab_recs, tab_visual, tab_timeline, tab_costs, tab_governance = st.tabs([
        "All Recommendations",
        "Visual Comparison",
        "Timeline",
        "Costs",
        "Governance Requirements",
    ])

    # --- Tab: All Recommendations ---
    with tab_recs:
        # Score overview chart
        st.plotly_chart(create_score_overview(recommendations), use_container_width=True)

        for idx, rec in enumerate(recommendations):
            score_emoji = "🟢" if rec.overall_score > 70 else ("🟡" if rec.overall_score > 40 else "🔴")
            with st.expander(
                f"{score_emoji} {rec.custodian.short_name} — {rec.overall_score:.0f}% match "
                f"| ~{rec.estimated_total_weeks} weeks | {rec.estimated_cost_range}",
                expanded=(idx == 0),
            ):
                exp_col1, exp_col2 = st.columns([2, 1])
                with exp_col1:
                    st.markdown(f"**{rec.custodian.name}**")
                    st.markdown(rec.custodian.description)

                    st.markdown("**Why this pathway:**")
                    for r in rec.match_reasons:
                        st.markdown(f"- {r}")

                    if rec.concerns:
                        st.markdown("**Considerations:**")
                        for c in rec.concerns:
                            st.markdown(f"- :orange[{c}]")

                    if rec.custodian.strengths:
                        st.markdown("**Strengths:**")
                        for s in rec.custodian.strengths:
                            st.markdown(f"- {s}")

                    if rec.custodian.limitations:
                        st.markdown("**Limitations:**")
                        for l in rec.custodian.limitations:
                            st.markdown(f"- {l}")

                with exp_col2:
                    st.markdown("**Dimension Scores:**")
                    for dim_name, dim_key in [
                        ("Data Fit", "data_fit"),
                        ("Geography", "geographic"),
                        ("Eligibility", "eligibility"),
                        ("Speed", "speed"),
                        ("Cost", "cost"),
                        ("Study Design", "study_design"),
                    ]:
                        val = rec.dimension_scores.get(dim_key, 0)
                        st.progress(val / 100, text=f"{dim_name}: {val:.0f}%")

                    st.markdown("---")
                    st.markdown(f"**Access Model:** {rec.custodian.access_model.replace('_', ' ').title()}")
                    st.markdown(f"**Regions:** {', '.join(rec.custodian.regions)}")
                    if rec.custodian.patient_count:
                        st.markdown(f"**Population:** {rec.custodian.patient_count}")
                    st.link_button("Visit Website", rec.custodian.url)

                # Access steps
                if rec.custodian.access_steps:
                    st.markdown("---")
                    st.markdown("**Access Process Steps:**")
                    step_cols = st.columns(min(len(rec.custodian.access_steps), 5))
                    for i, step in enumerate(rec.custodian.access_steps[:5]):
                        with step_cols[i]:
                            gov_badge = ""
                            if step.governance_body_id:
                                gov_badge = f" ({step.governance_body_id.upper()})"
                            st.markdown(
                                f"""<div style="text-align:center; padding: 8px;">
                                <div style="background:#0066CC; color:white; border-radius:50%;
                                            width:36px; height:36px; line-height:36px;
                                            margin:0 auto; font-weight:bold; font-size:14px;">
                                    {step.order}
                                </div>
                                <p style="font-weight:bold; margin-top:6px; font-size:0.85rem;">
                                    {step.name}{gov_badge}
                                </p>
                                <p style="font-size:0.75rem; color:#666;">
                                    ~{step.estimated_weeks} weeks
                                </p>
                                </div>""",
                                unsafe_allow_html=True,
                            )

    # --- Tab: Visual Comparison ---
    with tab_visual:
        st.markdown("#### Pathway Flow")
        st.plotly_chart(
            create_pathway_sankey(recommendations, data_needs),
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("#### Compare Custodians")
        compare_options = [rec.custodian.short_name for rec in recommendations]
        selected = st.multiselect(
            "Select 2-4 custodians to compare",
            compare_options,
            default=compare_options[:min(3, len(compare_options))],
            max_selections=4,
        )
        if len(selected) >= 2:
            compare_recs = [r for r in recommendations if r.custodian.short_name in selected]
            st.plotly_chart(create_comparison_radar(compare_recs), use_container_width=True)

            # Comparison table
            st.markdown("#### Side-by-Side Comparison")
            import pandas as pd
            comp_data = {
                "Dimension": [
                    "Coverage", "Data Types", "Access Model", "Typical Timeline",
                    "Cost", "Regions", "TRE Platform",
                ],
            }
            for rec in compare_recs:
                c = rec.custodian
                comp_data[c.short_name] = [
                    c.patient_count or "Not specified",
                    f"{len(c.data_types)} types",
                    c.access_model.replace("_", " ").title(),
                    f"~{rec.estimated_total_weeks} weeks",
                    rec.estimated_cost_range,
                    ", ".join(c.regions),
                    c.tre_platform or "Not specified",
                ]
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
        elif selected:
            st.info("Select at least 2 custodians to compare.")

    # --- Tab: Timeline ---
    with tab_timeline:
        st.plotly_chart(create_timeline_gantt(recommendations), use_container_width=True)

        st.markdown("#### Detailed Timeline Breakdown")
        for rec in recommendations[:5]:
            with st.expander(f"{rec.custodian.short_name} — ~{rec.estimated_total_weeks} weeks total"):
                for phase in rec.custodian.timeline:
                    st.markdown(
                        f"**{phase.phase}**: {phase.typical_weeks} weeks "
                        f"(range: {phase.min_weeks}-{phase.max_weeks})"
                    )
                    if phase.notes:
                        st.caption(phase.notes)
                for gov in rec.required_governance:
                    if gov.tiers:
                        weeks = gov.tiers[0].typical_weeks
                        st.markdown(f"**{gov.short_name}**: ~{weeks} weeks")

    # --- Tab: Costs ---
    with tab_costs:
        st.plotly_chart(create_cost_comparison(recommendations), use_container_width=True)

        st.markdown("#### Cost Details")
        for rec in recommendations[:5]:
            if rec.custodian.costs:
                costs = rec.custodian.costs
                with st.expander(f"{rec.custodian.short_name} — {rec.estimated_cost_range}"):
                    if costs.application_fee:
                        st.markdown(f"**Application Fee:** {costs.application_fee}")
                    if costs.annual_access_fee:
                        st.markdown(f"**Annual Access Fee:** {costs.annual_access_fee}")
                    if costs.per_dataset_fee:
                        st.markdown(f"**Per-Dataset Fee:** {costs.per_dataset_fee}")
                    if costs.tre_fee:
                        st.markdown(f"**TRE Fee:** {costs.tre_fee}")
                    if costs.free_for:
                        st.markdown(f"**Free for:** {', '.join(costs.free_for)}")
                    if costs.notes:
                        st.caption(costs.notes)

    # --- Tab: Governance ---
    with tab_governance:
        st.markdown(
            "The governance bodies below are relevant to your research based on "
            "your profile, the data you need, and the nations you're working across."
        )

        # Collect unique governance bodies
        all_gov: dict = {}
        for rec in recommendations:
            for g in rec.required_governance:
                if g.id not in all_gov:
                    all_gov[g.id] = {"body": g, "custodians": []}
                all_gov[g.id]["custodians"].append(rec.custodian.short_name)

        if not all_gov:
            st.info("No specific governance bodies identified for your profile. Check individual custodian requirements.")
        else:
            for gid, info in all_gov.items():
                gov = info["body"]
                with st.expander(f"{gov.name} ({gov.short_name})", expanded=True):
                    st.markdown(gov.description)
                    st.markdown(f"**Nations:** {', '.join(gov.nations)}")
                    if gov.role:
                        st.markdown(f"**Role:** {gov.role}")
                    if gov.url:
                        st.link_button(f"Visit {gov.short_name}", gov.url)
                    st.markdown(f"**Relevant to:** {', '.join(info['custodians'])}")
                    if gov.tiers:
                        st.markdown("**Tiers:**")
                        for tier in gov.tiers:
                            st.markdown(f"- **{tier.tier_name}** (~{tier.typical_weeks} weeks): {tier.description}")

        # Section 251 / CAG note
        if profile.needs_section_251:
            st.warning(
                "You indicated your study involves identifiable data without explicit patient consent. "
                "In England and Wales, this typically requires a Section 251 application to the "
                "Confidentiality Advisory Group (CAG). In Scotland, this may route through PBPP Tier 2."
            )

    # === AI Advisory Panel ===
    st.divider()
    st.subheader("AI Advisory Panel")
    st.markdown(
        "Get a narrative analysis of your recommendations from the AI advisor. "
        "Requires an OpenAI API key (set in the main chat page sidebar)."
    )

    api_key = st.session_state.get("api_key", os.environ.get("OPENAI_API_KEY", ""))

    if st.button("Generate AI Analysis", type="secondary"):
        if not api_key:
            st.warning("Please set your OpenAI API key in the main chat page sidebar first.")
        else:
            # Build context for the LLM
            recs_summary = []
            for rec in recommendations[:6]:
                gov_names = [g.short_name for g in rec.required_governance]
                recs_summary.append(
                    f"- {rec.custodian.short_name} ({rec.overall_score:.0f}% match, "
                    f"~{rec.estimated_total_weeks} weeks, {rec.estimated_cost_range}): "
                    f"Reasons: {'; '.join(rec.match_reasons[:3])}. "
                    f"Concerns: {'; '.join(rec.concerns[:3]) if rec.concerns else 'None'}. "
                    f"Governance: {', '.join(gov_names) if gov_names else 'Standard'}."
                )

            context = (
                f"Researcher profile: {researcher_type} based in {institution_country}, "
                f"studying {study_type}, needs {', '.join(data_needs)}, "
                f"scope: {', '.join(geographic_scope)}, timeline: {timeline_priority}, "
                f"budget: {budget_range}.\n\n"
                f"Ranked pathway recommendations:\n" + "\n".join(recs_summary)
            )

            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)

                system_msg = (
                    "You are the UK Health Data Access Navigator — an expert advisor helping "
                    "researchers find the best route to access UK health data. Based on the "
                    "structured recommendations below, provide a concise narrative analysis:\n"
                    "1. Why the top recommendation is the best fit\n"
                    "2. Key trade-offs between the top 2-3 options\n"
                    "3. Important governance steps to be aware of\n"
                    "4. Practical next steps the researcher should take\n\n"
                    "Be direct, specific, and practical. Use concrete timelines and costs. "
                    "Always caveat that estimates should be verified with custodians."
                )

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    stream = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": context},
                        ],
                        temperature=0.3,
                        stream=True,
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

            except Exception as e:
                st.error(f"AI analysis failed: {e}")

    # === Export ===
    st.divider()
    export_lines = [
        "# UK Health Data Access Navigator — Recommendations Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\n## Research Profile",
        f"- **Researcher type:** {researcher_type}",
        f"- **Institution country:** {institution_country}",
        f"- **Study design:** {study_type}",
        f"- **Data needs:** {', '.join(data_needs)}",
        f"- **Geographic scope:** {', '.join(geographic_scope)}",
        f"- **Timeline priority:** {timeline_priority}",
        f"- **Budget:** {budget_range}",
        f"\n## Ranked Recommendations\n",
    ]
    for idx, rec in enumerate(recommendations, 1):
        export_lines.append(f"### {idx}. {rec.custodian.name} — {rec.overall_score:.0f}% match")
        export_lines.append(f"- **Timeline:** ~{rec.estimated_total_weeks} weeks")
        export_lines.append(f"- **Cost:** {rec.estimated_cost_range}")
        export_lines.append(f"- **Access model:** {rec.custodian.access_model}")
        export_lines.append(f"- **Website:** {rec.custodian.url}")
        if rec.match_reasons:
            export_lines.append("- **Why recommended:** " + "; ".join(rec.match_reasons[:3]))
        if rec.concerns:
            export_lines.append("- **Considerations:** " + "; ".join(rec.concerns[:3]))
        export_lines.append("")

    export_md = "\n".join(export_lines)
    st.download_button(
        "Download Recommendations Report",
        data=export_md,
        file_name=f"data_access_recommendations_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown",
    )

# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------
elif not st.session_state.get("navigator_results"):
    st.info(
        "Fill out the research profile form above and click **Find My Pathways** "
        "to get personalised recommendations."
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    "<div style='text-align: center; font-size: 0.85rem; color: grey;'>"
    "<p>This is a prototype. Timeline and cost estimates are indicative and based on "
    "publicly available information. Always verify current processes with data custodians directly.</p>"
    "<p>Custodian data loaded from JSON configuration files — "
    f"{len(custodians)} pathways across {len(set(r for c in custodians for r in c.regions))} nations.</p>"
    "</div>",
    unsafe_allow_html=True,
)
