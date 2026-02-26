"""Plotly-based visualisations for the Data Access Navigator."""

from __future__ import annotations

from typing import List

import plotly.graph_objects as go

from data_access.models import DataCustodian, PathwayRecommendation


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

_SCORE_COLOURS = {
    "high": "#27ae60",    # green  (>70)
    "medium": "#f39c12",  # amber  (40-70)
    "low": "#e74c3c",     # red    (<40)
}

_PHASE_COLOURS = {
    "Preparation": "#3498db",
    "Development": "#9b59b6",
    "Review": "#e74c3c",
    "Contracting": "#e67e22",
    "Provisioning": "#2ecc71",
    "Analysis": "#1abc9c",
}

_CUSTODIAN_COLOURS = [
    "#0066CC", "#E63946", "#2A9D8F", "#E9C46A",
    "#264653", "#F4A261", "#606C38", "#BF0603",
    "#6D6875", "#3D405B", "#81B29A", "#F2CC8F",
]


def _score_colour(score: float) -> str:
    if score > 70:
        return _SCORE_COLOURS["high"]
    if score > 40:
        return _SCORE_COLOURS["medium"]
    return _SCORE_COLOURS["low"]


# ---------------------------------------------------------------------------
# 1. Pathway Sankey diagram
# ---------------------------------------------------------------------------

def create_pathway_sankey(
    recommendations: List[PathwayRecommendation],
    data_needs: List[str],
) -> go.Figure:
    """Sankey: data needs → custodians → access models."""

    # Deduplicate access models
    access_models_set = sorted({r.custodian.access_model for r in recommendations})

    # Build label lists
    labels: List[str] = []
    colours: List[str] = []

    # Left column: data needs
    for dn in data_needs:
        short = dn.split("(")[0].strip()
        labels.append(short)
        colours.append("#3498db")
    data_need_offset = 0

    # Middle column: custodians
    custodian_offset = len(labels)
    for rec in recommendations:
        labels.append(rec.custodian.short_name)
        colours.append(_score_colour(rec.overall_score))

    # Right column: access models
    model_offset = len(labels)
    model_display = {
        "tre_only": "TRE Only",
        "data_extract": "Data Extract",
        "code_in_situ": "Code-in-Situ",
        "hybrid": "Hybrid",
    }
    for am in access_models_set:
        labels.append(model_display.get(am, am))
        colours.append("#95a5a6")

    sources: List[int] = []
    targets: List[int] = []
    values: List[float] = []
    link_colours: List[str] = []

    # Links: data_need → custodian
    for i, dn in enumerate(data_needs):
        dn_lower = dn.lower()
        for j, rec in enumerate(recommendations):
            cust_types_lower = {dt.lower() for dt in rec.custodian.data_types}
            if dn_lower in cust_types_lower:
                sources.append(data_need_offset + i)
                targets.append(custodian_offset + j)
                values.append(max(rec.overall_score / 10, 1))
                link_colours.append(_score_colour(rec.overall_score).replace(")", ", 0.4)").replace("rgb", "rgba") if "rgb" in _score_colour(rec.overall_score) else f"rgba(100,100,100,0.3)")

    # Links: custodian → access model
    for j, rec in enumerate(recommendations):
        am = rec.custodian.access_model
        if am in access_models_set:
            am_idx = model_offset + access_models_set.index(am)
            sources.append(custodian_offset + j)
            targets.append(am_idx)
            values.append(max(rec.overall_score / 10, 1))
            link_colours.append(f"rgba(150,150,150,0.3)")

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            label=labels,
            color=colours,
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colours,
        ),
    )])

    fig.update_layout(
        title_text="Data Access Pathway Flow",
        font_size=12,
        height=max(400, len(recommendations) * 60 + 200),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Comparison radar chart
# ---------------------------------------------------------------------------

_RADAR_DIMENSIONS = [
    "Data Fit", "Geographic Match", "Eligibility",
    "Speed", "Cost", "Study Design Fit",
]

_RADAR_DIM_KEYS = [
    "data_fit", "geographic", "eligibility",
    "speed", "cost", "study_design",
]


def create_comparison_radar(recommendations: List[PathwayRecommendation]) -> go.Figure:
    """Spider chart comparing custodians across scoring dimensions."""
    fig = go.Figure()

    for idx, rec in enumerate(recommendations):
        values = [rec.dimension_scores.get(k, 0) / 10 for k in _RADAR_DIM_KEYS]
        values.append(values[0])  # close the polygon

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=_RADAR_DIMENSIONS + [_RADAR_DIMENSIONS[0]],
            fill="toself",
            name=rec.custodian.short_name,
            line_color=_CUSTODIAN_COLOURS[idx % len(_CUSTODIAN_COLOURS)],
            opacity=0.7,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title_text="Pathway Comparison",
        height=500,
        margin=dict(l=60, r=60, t=60, b=40),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Timeline Gantt chart
# ---------------------------------------------------------------------------

def create_timeline_gantt(recommendations: List[PathwayRecommendation]) -> go.Figure:
    """Horizontal stacked bars showing estimated phases per custodian."""
    fig = go.Figure()

    phase_names_seen: set = set()

    for idx, rec in enumerate(recommendations):
        offset = 0
        for phase in rec.custodian.timeline:
            show_legend = phase.phase not in phase_names_seen
            phase_names_seen.add(phase.phase)

            colour = _PHASE_COLOURS.get(phase.phase, "#95a5a6")

            fig.add_trace(go.Bar(
                y=[rec.custodian.short_name],
                x=[phase.typical_weeks],
                base=offset,
                orientation="h",
                name=phase.phase,
                marker_color=colour,
                showlegend=show_legend,
                legendgroup=phase.phase,
                hovertemplate=(
                    f"<b>{rec.custodian.short_name}</b><br>"
                    f"{phase.phase}: {phase.typical_weeks} weeks<br>"
                    f"(Range: {phase.min_weeks}-{phase.max_weeks} weeks)"
                    "<extra></extra>"
                ),
            ))
            offset += phase.typical_weeks

        # Add governance body time as a separate bar
        for gov in rec.required_governance:
            if gov.tiers:
                gov_weeks = gov.tiers[0].typical_weeks
            else:
                gov_weeks = 0
            if gov_weeks > 0:
                show_legend = "Governance" not in phase_names_seen
                phase_names_seen.add("Governance")
                fig.add_trace(go.Bar(
                    y=[rec.custodian.short_name],
                    x=[gov_weeks],
                    base=offset,
                    orientation="h",
                    name="Governance",
                    marker_color="#8e44ad",
                    showlegend=show_legend,
                    legendgroup="Governance",
                    hovertemplate=(
                        f"<b>{rec.custodian.short_name}</b><br>"
                        f"{gov.short_name}: ~{gov_weeks} weeks"
                        "<extra></extra>"
                    ),
                ))
                offset += gov_weeks

    fig.update_layout(
        barmode="stack",
        xaxis_title="Weeks",
        title_text="Estimated Timeline Comparison",
        height=max(300, len(recommendations) * 50 + 150),
        margin=dict(l=10, r=10, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ---------------------------------------------------------------------------
# 4. Cost breakdown chart
# ---------------------------------------------------------------------------

def create_cost_comparison(recommendations: List[PathwayRecommendation]) -> go.Figure:
    """Bar chart showing cost categories per custodian."""
    import re

    custodian_names: List[str] = []
    app_fees: List[float] = []
    annual_fees: List[float] = []
    tre_fees: List[float] = []

    def _parse_fee(fee_str: str | None) -> float:
        if not fee_str:
            return 0
        if "free" in fee_str.lower():
            return 0
        numbers = re.findall(r"[\d,]+", fee_str.replace(",", ""))
        if numbers:
            return float(numbers[0])
        return 0

    for rec in recommendations:
        custodian_names.append(rec.custodian.short_name)
        costs = rec.custodian.costs
        if costs:
            app_fees.append(_parse_fee(costs.application_fee))
            annual_fees.append(_parse_fee(costs.annual_access_fee))
            tre_fees.append(_parse_fee(costs.tre_fee))
        else:
            app_fees.append(0)
            annual_fees.append(0)
            tre_fees.append(0)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Application Fee", x=custodian_names, y=app_fees, marker_color="#3498db"))
    fig.add_trace(go.Bar(name="Annual Fee", x=custodian_names, y=annual_fees, marker_color="#e74c3c"))
    fig.add_trace(go.Bar(name="TRE Fee", x=custodian_names, y=tre_fees, marker_color="#2ecc71"))

    fig.update_layout(
        barmode="group",
        yaxis_title="Estimated Cost (GBP)",
        title_text="Cost Comparison",
        height=400,
        margin=dict(l=10, r=10, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ---------------------------------------------------------------------------
# 5. Score bar chart (simple overview)
# ---------------------------------------------------------------------------

def create_score_overview(recommendations: List[PathwayRecommendation]) -> go.Figure:
    """Horizontal bar chart of overall match scores."""
    names = [r.custodian.short_name for r in reversed(recommendations)]
    scores = [r.overall_score for r in reversed(recommendations)]
    bar_colours = [_score_colour(s) for s in scores]

    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation="h",
        marker_color=bar_colours,
        text=[f"{s:.0f}%" for s in scores],
        textposition="auto",
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Match Score (%)"),
        title_text="Pathway Match Scores",
        height=max(300, len(recommendations) * 40 + 100),
        margin=dict(l=10, r=10, t=40, b=20),
    )
    return fig
