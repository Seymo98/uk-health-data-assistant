"""
Visualizations for OpenPhenotypes.

Plotly-based charts inspired by Open Targets' evidence scoring approach,
the BHF DSC codelist comparison tool, and CALIBER phenotype dashboards.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from .models import EvidenceScore, Phenotype, CodingSystem, ValidationEvidence


# ---------------------------------------------------------------------------
# Colour palette (inspired by Open Targets)
# ---------------------------------------------------------------------------

PALETTE = {
    "primary": "#3489ca",
    "secondary": "#5C6BC0",
    "accent": "#26A69A",
    "warning": "#FFA726",
    "danger": "#EF5350",
    "success": "#66BB6A",
    "muted": "#90A4AE",
    "bg": "#FAFAFA",
    "text": "#263238",
}

EVIDENCE_COLOURS = {
    "Literature": "#3489ca",
    "Clinical review": "#5C6BC0",
    "Validation": "#26A69A",
    "Usage": "#FFA726",
    "Provenance": "#7E57C2",
}

THERAPEUTIC_AREA_COLOURS = {
    "Cardiovascular": "#E53935",
    "Respiratory": "#1E88E5",
    "Mental health": "#8E24AA",
    "Oncology": "#D81B60",
    "Diabetes & endocrine": "#FB8C00",
    "Musculoskeletal": "#43A047",
    "Neurology": "#5E35B1",
    "Infectious disease": "#00ACC1",
    "Renal": "#3949AB",
    "Gastrointestinal": "#7CB342",
    "Dermatology": "#F4511E",
    "Obstetrics & gynaecology": "#EC407A",
    "Paediatrics": "#26C6DA",
    "Multimorbidity": "#78909C",
    "Other": "#90A4AE",
}


def create_evidence_radar(score: EvidenceScore, title: str = "") -> go.Figure:
    """Create an Open Targets-style radar/spider chart for evidence scores."""
    categories = list(score.to_dict().keys())
    values = list(score.to_dict().values())
    colours = [EVIDENCE_COLOURS.get(c, PALETTE["primary"]) for c in categories]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(52, 137, 202, 0.15)",
        line=dict(color=PALETTE["primary"], width=2),
        marker=dict(size=8, color=colours + [colours[0]]),
        name="Evidence",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.25, 0.5, 0.75, 1.0],
                ticktext=["0.25", "0.50", "0.75", "1.00"],
                gridcolor="#E0E0E0",
            ),
            angularaxis=dict(gridcolor="#E0E0E0"),
            bgcolor="white",
        ),
        showlegend=False,
        title=dict(text=title, font=dict(size=14)),
        margin=dict(l=60, r=60, t=40, b=40),
        height=320,
    )

    return fig


def create_evidence_bars(score: EvidenceScore) -> go.Figure:
    """Horizontal bar chart of evidence dimensions (Open Targets style)."""
    data = score.to_dict()
    categories = list(data.keys())
    values = list(data.values())
    colours = [EVIDENCE_COLOURS.get(c, PALETTE["primary"]) for c in categories]

    fig = go.Figure(go.Bar(
        y=categories,
        x=values,
        orientation="h",
        marker_color=colours,
        text=[f"{v:.0%}" for v in values],
        textposition="outside",
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 1.15], title="Score", tickformat=".0%"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=120, r=40, t=10, b=30),
        height=220,
        plot_bgcolor="white",
    )

    return fig


def create_overall_score_gauge(score: float) -> go.Figure:
    """Gauge chart for overall evidence score."""
    colour = (
        PALETTE["success"] if score >= 0.75
        else PALETTE["warning"] if score >= 0.5
        else PALETTE["danger"]
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score * 100,
        number=dict(suffix="%", font=dict(size=28)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1),
            bar=dict(color=colour),
            bgcolor="white",
            steps=[
                dict(range=[0, 50], color="#FFEBEE"),
                dict(range=[50, 75], color="#FFF8E1"),
                dict(range=[75, 100], color="#E8F5E9"),
            ],
            threshold=dict(
                line=dict(color="black", width=2),
                thickness=0.75,
                value=score * 100,
            ),
        ),
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=10),
        height=180,
    )

    return fig


def create_coding_system_sunburst(phenotype: Phenotype) -> go.Figure:
    """Sunburst chart showing code distribution across coding systems."""
    labels = []
    parents = []
    values = []
    colours = []

    system_colours = {
        CodingSystem.SNOMED_CT: "#3489ca",
        CodingSystem.ICD10: "#E53935",
        CodingSystem.READ_V2: "#43A047",
        CodingSystem.CTV3: "#7CB342",
        CodingSystem.OPCS4: "#8E24AA",
        CodingSystem.BNF: "#FB8C00",
        CodingSystem.DMD: "#00ACC1",
        CodingSystem.CPRD_MEDCODE: "#5E35B1",
        CodingSystem.OMOP: "#D81B60",
    }

    # Root
    labels.append(phenotype.short_name)
    parents.append("")
    values.append(0)
    colours.append(PALETTE["primary"])

    for cl in phenotype.codelists:
        # Coding system level
        sys_label = cl.coding_system.value
        labels.append(sys_label)
        parents.append(phenotype.short_name)
        values.append(cl.code_count)
        colours.append(system_colours.get(cl.coding_system, PALETTE["muted"]))

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colours),
        branchvalues="total",
    ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
    )

    return fig


def create_therapeutic_area_chart(phenotypes: list[Phenotype]) -> go.Figure:
    """Bar chart of phenotypes by therapeutic area."""
    area_counts: dict[str, int] = {}
    for p in phenotypes:
        area = p.therapeutic_area.value
        area_counts[area] = area_counts.get(area, 0) + 1

    areas = sorted(area_counts.keys(), key=lambda a: area_counts[a], reverse=True)
    counts = [area_counts[a] for a in areas]
    colours = [THERAPEUTIC_AREA_COLOURS.get(a, PALETTE["muted"]) for a in areas]

    fig = go.Figure(go.Bar(
        x=counts,
        y=areas,
        orientation="h",
        marker_color=colours,
        text=counts,
        textposition="outside",
    ))

    fig.update_layout(
        xaxis=dict(title="Number of phenotypes"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=180, r=40, t=10, b=30),
        height=max(250, len(areas) * 35),
        plot_bgcolor="white",
    )

    return fig


def create_validation_status_pie(phenotypes: list[Phenotype]) -> go.Figure:
    """Donut chart of validation status distribution."""
    status_counts: dict[str, int] = {}
    for p in phenotypes:
        status = p.validation_status.value
        status_counts[status] = status_counts.get(status, 0) + 1

    status_colours = {
        "Draft": "#BDBDBD",
        "Under review": "#FFA726",
        "Peer reviewed": "#42A5F5",
        "Clinically validated": "#66BB6A",
        "Published in study": "#26A69A",
    }

    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colours = [status_colours.get(s, PALETTE["muted"]) for s in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colours),
        textinfo="label+value",
        textposition="outside",
    ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=280,
        showlegend=False,
        annotations=[dict(
            text=f"{sum(values)}<br>total",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False,
        )],
    )

    return fig


def create_coding_system_heatmap(phenotypes: list[Phenotype]) -> go.Figure:
    """Heatmap showing which phenotypes cover which coding systems."""
    systems = sorted(
        {cs for p in phenotypes for cs in p.coding_systems},
        key=lambda cs: cs.value,
    )
    system_labels = [cs.value for cs in systems]
    pheno_labels = [p.short_name for p in phenotypes]

    z = []
    hover_text = []
    for p in phenotypes:
        row = []
        hover_row = []
        for cs in systems:
            matching = [cl for cl in p.codelists if cl.coding_system == cs]
            if matching:
                count = matching[0].code_count
                row.append(count)
                hover_row.append(f"{p.short_name}: {count} {cs.value} codes")
            else:
                row.append(0)
                hover_row.append(f"{p.short_name}: No {cs.value} codes")
        z.append(row)
        hover_text.append(hover_row)

    fig = go.Figure(go.Heatmap(
        z=z,
        x=system_labels,
        y=pheno_labels,
        hovertext=hover_text,
        hoverinfo="text",
        colorscale=[
            [0, "#F5F5F5"],
            [0.01, "#E3F2FD"],
            [0.5, "#42A5F5"],
            [1, "#1565C0"],
        ],
        showscale=True,
        colorbar=dict(title="Code count"),
    ))

    fig.update_layout(
        xaxis=dict(title="Coding system", tickangle=45),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=120, r=20, t=10, b=80),
        height=max(300, len(phenotypes) * 30),
    )

    return fig


def create_comparison_overlap(
    codelist_a_codes: set[str],
    codelist_b_codes: set[str],
    name_a: str,
    name_b: str,
) -> go.Figure:
    """Visualize overlap between two codelists (simulated Venn diagram)."""
    only_a = len(codelist_a_codes - codelist_b_codes)
    only_b = len(codelist_b_codes - codelist_a_codes)
    overlap = len(codelist_a_codes & codelist_b_codes)
    total = only_a + only_b + overlap

    fig = go.Figure(go.Bar(
        x=[only_a, overlap, only_b],
        y=[f"Only in {name_a}", "Shared", f"Only in {name_b}"],
        orientation="h",
        marker_color=[PALETTE["primary"], PALETTE["success"], PALETTE["secondary"]],
        text=[only_a, overlap, only_b],
        textposition="outside",
    ))

    fig.update_layout(
        xaxis=dict(title="Number of codes"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=160, r=40, t=10, b=30),
        height=180,
        plot_bgcolor="white",
        title=dict(
            text=f"Total unique codes: {total}",
            font=dict(size=12, color=PALETTE["muted"]),
        ),
    )

    return fig


def create_source_repository_chart(phenotypes: list[Phenotype]) -> go.Figure:
    """Chart showing phenotype counts by source repository."""
    repo_counts: dict[str, int] = {}
    for p in phenotypes:
        repo = p.source_repository or "Unknown"
        repo_counts[repo] = repo_counts.get(repo, 0) + 1

    repos = sorted(repo_counts.keys(), key=lambda r: repo_counts[r], reverse=True)
    counts = [repo_counts[r] for r in repos]

    fig = go.Figure(go.Bar(
        x=repos,
        y=counts,
        marker_color=PALETTE["primary"],
        text=counts,
        textposition="outside",
    ))

    fig.update_layout(
        yaxis=dict(title="Phenotype count"),
        xaxis=dict(tickangle=30),
        margin=dict(l=40, r=20, t=10, b=100),
        height=280,
        plot_bgcolor="white",
    )

    return fig


def create_data_source_coverage(phenotypes: list[Phenotype]) -> go.Figure:
    """Heatmap of which phenotypes are compatible with which data sources."""
    all_sources = sorted({ds for p in phenotypes for ds in p.data_sources})
    pheno_labels = [p.short_name for p in phenotypes]

    z = []
    for p in phenotypes:
        row = [1 if ds in p.data_sources else 0 for ds in all_sources]
        z.append(row)

    fig = go.Figure(go.Heatmap(
        z=z,
        x=all_sources,
        y=pheno_labels,
        colorscale=[[0, "#F5F5F5"], [1, PALETTE["primary"]]],
        showscale=False,
    ))

    fig.update_layout(
        xaxis=dict(tickangle=45),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=120, r=20, t=10, b=100),
        height=max(300, len(phenotypes) * 30),
    )

    return fig


# ---------------------------------------------------------------------------
# New visualizations for FAIR-report fields
# ---------------------------------------------------------------------------

def create_validation_metrics_chart(validations: list[ValidationEvidence]) -> go.Figure:
    """Grouped bar chart of validation metrics (PPV, sensitivity, specificity, etc.)."""
    if not validations:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(text="No validation evidence", x=0.5, y=0.5,
                              showarrow=False, font=dict(size=14, color=PALETTE["muted"]))],
            height=200,
        )
        return fig

    labels = []
    ppvs = []
    sensitivities = []
    specificities = []
    npvs = []

    for v in validations:
        label = f"{v.method.value}\n({v.dataset})"
        labels.append(label)
        ppvs.append((v.ppv or 0) * 100)
        sensitivities.append((v.sensitivity or 0) * 100)
        specificities.append((v.specificity or 0) * 100)
        npvs.append((v.npv or 0) * 100)

    fig = go.Figure()

    metric_data = [
        ("PPV", ppvs, PALETTE["primary"]),
        ("Sensitivity", sensitivities, PALETTE["accent"]),
        ("Specificity", specificities, PALETTE["secondary"]),
        ("NPV", npvs, PALETTE["warning"]),
    ]

    for name, values, colour in metric_data:
        if any(v > 0 for v in values):
            fig.add_trace(go.Bar(
                name=name,
                x=labels,
                y=values,
                marker_color=colour,
                text=[f"{v:.0f}%" if v > 0 else "" for v in values],
                textposition="outside",
            ))

    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 110], title="Percentage", ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=20, t=40, b=80),
        height=300,
        plot_bgcolor="white",
    )

    return fig


def create_fair_completeness_chart(phenotype: Phenotype) -> go.Figure:
    """Show FAIR metadata completeness as a horizontal stacked bar."""
    checks = {
        "Accession ID": phenotype.accession.number > 0,
        "Ontology terms": len(phenotype.ontology_terms) > 0,
        "Population constraints": bool(phenotype.population.inclusion_criteria or phenotype.population.exclusion_criteria),
        "Primary publication": phenotype.primary_publication is not None,
        "Publication link": bool(
            phenotype.primary_publication
            and (phenotype.primary_publication.url or phenotype.primary_publication.doi)
        ),
        "Purpose": bool(phenotype.purpose),
        "Developed for": bool(phenotype.developed_for),
        "Limitations": bool(phenotype.limitations),
        "Source code link": bool(phenotype.source_code_url),
        "Validation evidence": len(phenotype.validations) > 0,
        "Implementation": len(phenotype.implementations) > 0,
        "Dummy data example": len(phenotype.dummy_data_examples) > 0,
        "QC rules": len(phenotype.qc_rules) > 0,
        "Clinical endorsement": len(phenotype.clinical_endorsements) > 0,
        "Dataset provenance": len(phenotype.dataset_provenance) > 0,
        "Logic description": bool(phenotype.logic_description),
    }

    labels = list(checks.keys())
    present = [1 if v else 0 for v in checks.values()]
    colours = [PALETTE["success"] if v else "#E0E0E0" for v in checks.values()]

    fig = go.Figure(go.Bar(
        y=labels,
        x=present,
        orientation="h",
        marker_color=colours,
        text=["Present" if v else "Missing" for v in checks.values()],
        textposition="inside",
        textfont=dict(color="white"),
    ))

    completeness = sum(checks.values()) / len(checks)

    fig.update_layout(
        xaxis=dict(range=[0, 1.2], showticklabels=False),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=160, r=40, t=30, b=10),
        height=max(300, len(checks) * 30),
        plot_bgcolor="white",
        title=dict(
            text=f"FAIR completeness: {completeness:.0%}",
            font=dict(size=13),
        ),
    )

    return fig
