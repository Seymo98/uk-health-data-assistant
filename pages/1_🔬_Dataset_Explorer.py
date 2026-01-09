"""
Interactive Dataset Explorer for HDR UK Gateway.

This Streamlit page provides a visual interface for searching and exploring
UK health datasets from the HDR UK Innovation Gateway.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hdruk_gateway import GatewayClient, DatasetSearcher
    from hdruk_gateway.models import ResourceType, OrganisationSector
    GATEWAY_AVAILABLE = True
except ImportError:
    GATEWAY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Dataset Explorer - UK Health Data",
    page_icon="🔬",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .dataset-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #0066cc;
    }
    .dataset-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #0066cc;
    }
    .publisher-badge {
        background-color: #e9ecef;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .metric-box {
        text-align: center;
        padding: 0.5rem;
        background-color: #f0f7ff;
        border-radius: 8px;
    }
    .facet-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🔬 UK Health Dataset Explorer")
st.markdown("""
Search and explore health datasets from the [HDR UK Innovation Gateway](https://www.healthdatagateway.org/).
Find datasets, research projects, and related publications across the UK health data ecosystem.
""")

if not GATEWAY_AVAILABLE:
    st.error("""
    **Gateway client not available.**

    Please install the required dependencies:
    ```bash
    pip install requests
    ```
    """)
    st.stop()

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_dataset" not in st.session_state:
    st.session_state.selected_dataset = None

# Sidebar filters
with st.sidebar:
    st.header("🔧 Search Filters")

    # Resource type selection
    resource_types = st.multiselect(
        "Resource Types",
        options=["Datasets", "Data Use Register", "Publications", "Tools"],
        default=["Datasets", "Data Use Register"],
        help="Select which types of resources to search"
    )

    st.divider()

    # Geographic filter
    geographic_filter = st.multiselect(
        "Geographic Coverage",
        options=["England", "Wales", "Scotland", "Northern Ireland", "UK-wide"],
        help="Filter by geographic coverage"
    )

    # Publisher filter
    publisher_filter = st.text_input(
        "Publisher/Custodian",
        placeholder="e.g., CPRD, NHS England",
        help="Filter by data publisher"
    )

    st.divider()

    # Results settings
    per_page = st.slider("Results per page", 5, 50, 25)

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        parse_query = st.checkbox("Smart query parsing", value=True,
                                  help="Automatically extract filters from natural language queries")
        show_facets = st.checkbox("Show facets", value=True)
        show_suggestions = st.checkbox("Show suggestions", value=True)

    st.divider()

    # Quick links
    st.subheader("🔗 Quick Links")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("HDR UK Gateway", "https://www.healthdatagateway.org/", use_container_width=True)
    with col2:
        st.link_button("CPRD", "https://cprd.com/", use_container_width=True)

# Main content area
col_search, col_actions = st.columns([4, 1])

with col_search:
    search_query = st.text_input(
        "🔍 Search health datasets",
        placeholder="e.g., diabetes data in Wales, cardiovascular research, genomics",
        value=st.session_state.search_query,
        key="search_input",
    )

with col_actions:
    st.write("")  # Spacer
    search_clicked = st.button("Search", type="primary", use_container_width=True)

# Example queries
if not st.session_state.search_results:
    st.markdown("### 💡 Try these example searches:")
    example_queries = [
        "diabetes datasets",
        "cancer data in Wales",
        "cardiovascular research CPRD",
        "mental health primary care",
        "COVID-19 OpenSAFELY",
        "genomics UK Biobank",
    ]

    cols = st.columns(3)
    for i, query in enumerate(example_queries):
        with cols[i % 3]:
            if st.button(query, key=f"example_{i}", use_container_width=True):
                st.session_state.search_query = query
                search_clicked = True
                st.rerun()

# Perform search
if search_clicked and search_query:
    st.session_state.search_query = search_query

    with st.spinner("🔍 Searching HDR UK Gateway..."):
        try:
            searcher = DatasetSearcher()

            # Map UI selections to resource types
            include_data_uses = "Data Use Register" in resource_types
            include_publications = "Publications" in resource_types

            result = searcher.search(
                query=search_query,
                parse_query=parse_query,
                include_data_uses=include_data_uses,
                include_publications=include_publications,
                per_page=per_page,
            )

            st.session_state.search_results = result

        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            st.session_state.search_results = None

# Display results
if st.session_state.search_results:
    result = st.session_state.search_results

    # Results summary
    st.divider()
    cols = st.columns(5)

    with cols[0]:
        st.metric("Total Results", result.total_count)
    with cols[1]:
        st.metric("Datasets", len(result.results.datasets))
    with cols[2]:
        st.metric("Data Uses", len(result.results.data_uses))
    with cols[3]:
        st.metric("Publications", len(result.results.publications))
    with cols[4]:
        st.metric("Search Time", f"{result.search_time_ms:.0f}ms")

    # Query interpretation
    if result.query_interpretation:
        st.info(f"📝 {result.query_interpretation}")

    # Main content area with facets sidebar
    if show_facets and result.facets:
        col_results, col_facets = st.columns([3, 1])
    else:
        col_results = st.container()
        col_facets = None

    with col_results:
        # Tabs for different resource types
        tabs = st.tabs(["📊 Datasets", "📋 Data Use Register", "📄 Publications"])

        # Datasets tab
        with tabs[0]:
            if result.results.datasets:
                for ds in result.results.datasets:
                    with st.container():
                        st.markdown(f"""
                        <div class="dataset-card">
                            <div class="dataset-title">{ds.title}</div>
                            <span class="publisher-badge">📍 {ds.publisher_name}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        # Abstract
                        if ds.abstract:
                            abstract = ds.abstract[:300] + "..." if len(ds.abstract) > 300 else ds.abstract
                            st.markdown(abstract)

                        # Metrics row
                        m1, m2, m3, m4 = st.columns(4)
                        with m1:
                            st.caption(f"📄 {ds.publications_count} publications")
                        with m2:
                            st.caption(f"📋 {ds.durs_count} data uses")
                        with m3:
                            if ds.is_cohort_discovery:
                                st.caption("🔬 Cohort Discovery")
                        with m4:
                            st.link_button("View on Gateway →", ds.gateway_url, use_container_width=True)

                        st.divider()
            else:
                st.info("No datasets found. Try adjusting your search terms.")

        # Data Use Register tab
        with tabs[1]:
            if result.results.data_uses:
                for dur in result.results.data_uses:
                    with st.container():
                        st.markdown(f"### {dur.project_title}")

                        col1, col2 = st.columns([2, 1])
                        with col1:
                            if dur.organisation_name:
                                st.markdown(f"**Organisation:** {dur.organisation_name}")
                            if dur.organisation_sector:
                                st.markdown(f"**Sector:** {dur.organisation_sector.value}")

                        with col2:
                            if dur.latest_approval_date:
                                st.markdown(f"**Approved:** {dur.latest_approval_date}")

                        if dur.lay_summary:
                            summary = dur.lay_summary[:400] + "..." if len(dur.lay_summary) > 400 else dur.lay_summary
                            with st.expander("📖 Lay Summary"):
                                st.markdown(summary)

                        if dur.public_benefit_statement:
                            with st.expander("🎯 Public Benefit"):
                                benefit = dur.public_benefit_statement[:400] + "..." if len(dur.public_benefit_statement) > 400 else dur.public_benefit_statement
                                st.markdown(benefit)

                        st.link_button("View Details →", dur.gateway_url)
                        st.divider()
            else:
                st.info("No data use register entries found.")

        # Publications tab
        with tabs[2]:
            if result.results.publications:
                for pub in result.results.publications:
                    with st.container():
                        st.markdown(f"### {pub.paper_title}")

                        if pub.authors:
                            st.markdown(f"*{pub.authors}*")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if pub.year_of_publication:
                                st.markdown(f"**Year:** {pub.year_of_publication}")
                        with col2:
                            if pub.journal_name:
                                st.markdown(f"**Journal:** {pub.journal_name}")
                        with col3:
                            if pub.paper_doi:
                                st.link_button("DOI", f"https://doi.org/{pub.paper_doi}")

                        st.link_button("View on Gateway →", pub.gateway_url)
                        st.divider()
            else:
                st.info("No publications found. Enable publications in search filters.")

    # Facets sidebar
    if col_facets and result.facets:
        with col_facets:
            st.markdown("### 📊 Facets")

            for facet in result.facets:
                with st.expander(facet.name, expanded=True):
                    for bucket in facet.buckets[:8]:
                        st.markdown(f"- {bucket['key']} ({bucket['count']})")

    # Suggestions
    if show_suggestions and result.suggestions:
        st.markdown("### 💡 Related Searches")
        cols = st.columns(min(len(result.suggestions), 4))
        for i, suggestion in enumerate(result.suggestions[:4]):
            with cols[i]:
                if st.button(suggestion.text, key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.search_query = suggestion.text
                    st.rerun()

    # Export options
    st.divider()
    st.markdown("### 📥 Export Results")

    col_csv, col_json = st.columns(2)

    with col_csv:
        searcher = DatasetSearcher()
        csv_data = searcher.export_results_csv(result.results)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_json:
        json_data = searcher.export_results_json(result.results)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: grey; font-size: 0.9rem;'>
    Data from <a href="https://www.healthdatagateway.org/">HDR UK Innovation Gateway</a>.
    This is a discovery tool - always verify dataset details with official custodians.
</div>
""", unsafe_allow_html=True)
