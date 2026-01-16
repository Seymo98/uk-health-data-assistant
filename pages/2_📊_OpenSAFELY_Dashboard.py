"""
OpenSAFELY Jobs Dashboard.

A transparency dashboard for visualizing OpenSAFELY's public job execution data.
OpenSAFELY publishes machine-readable logs of every query run against NHS data,
making this the gold standard for research transparency.

Data source: https://jobs.opensafely.org
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from opensafely_jobs import (
        OpenSAFELYJobsClient,
        Organization,
        Project,
        JobRequest,
        JobStatus,
    )
    OPENSAFELY_AVAILABLE = True
except ImportError as e:
    OPENSAFELY_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Page configuration
st.set_page_config(
    page_title="OpenSAFELY Dashboard - UK Health Data",
    page_icon="📊",
    layout="wide",
)

# Custom CSS for dashboard styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a5276;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #566573;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .org-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #3498db;
        transition: transform 0.2s;
    }
    .org-card:hover {
        transform: translateX(5px);
    }
    .org-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .org-stats {
        font-size: 0.85rem;
        color: #7f8c8d;
    }
    .job-row {
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #95a5a6;
    }
    .job-succeeded {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .job-failed {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .job-running {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .job-pending {
        background-color: #e2e3e5;
        border-left-color: #6c757d;
    }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .status-succeeded { background-color: #28a745; color: white; }
    .status-failed { background-color: #dc3545; color: white; }
    .status-running { background-color: #ffc107; color: black; }
    .status-pending { background-color: #6c757d; color: white; }
    .info-box {
        background-color: #e8f4f8;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #17a2b8;
    }
    .transparency-badge {
        background: linear-gradient(90deg, #00b894, #00cec9);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a5276;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def get_status_badge(status: JobStatus) -> str:
    """Generate HTML for a status badge."""
    status_classes = {
        JobStatus.SUCCEEDED: "status-succeeded",
        JobStatus.FAILED: "status-failed",
        JobStatus.RUNNING: "status-running",
        JobStatus.PENDING: "status-pending",
        JobStatus.UNKNOWN: "status-pending",
    }
    css_class = status_classes.get(status, "status-pending")
    return f'<span class="status-badge {css_class}">{status.value}</span>'


def get_job_row_class(status: JobStatus) -> str:
    """Get CSS class for job row based on status."""
    return {
        JobStatus.SUCCEEDED: "job-succeeded",
        JobStatus.FAILED: "job-failed",
        JobStatus.RUNNING: "job-running",
        JobStatus.PENDING: "job-pending",
    }.get(status, "")


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    if not dt:
        return "Unknown"
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt

    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            mins = diff.seconds // 60
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%d %b %Y")


# Initialize session state
if "opensafely_data" not in st.session_state:
    st.session_state.opensafely_data = None
if "selected_org" not in st.session_state:
    st.session_state.selected_org = None
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False


# Header
st.markdown('<div class="main-header">OpenSAFELY Jobs Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-header">
Real-time transparency dashboard for OpenSAFELY's secure analytics platform.
Every query against NHS patient data is logged and publicly accessible.
</div>
""", unsafe_allow_html=True)

# Transparency badge
st.markdown('<span class="transparency-badge">The Gold Standard for Research Transparency</span>', unsafe_allow_html=True)

if not OPENSAFELY_AVAILABLE:
    st.error(f"""
    **OpenSAFELY client not available.**

    Import error: {IMPORT_ERROR if 'IMPORT_ERROR' in dir() else 'Unknown'}

    Please ensure all dependencies are installed:
    ```bash
    pip install requests beautifulsoup4 lxml pandas
    ```
    """)
    st.stop()

# Information box about OpenSAFELY
with st.expander("About OpenSAFELY", expanded=False):
    st.markdown("""
    **OpenSAFELY** is a secure analytics platform for NHS electronic health records,
    developed by the Bennett Institute for Applied Data Science at the University of Oxford.

    **Key Features:**
    - Access to ~60 million patient records from TPP and EMIS systems
    - Code runs inside the secure environment (data never leaves)
    - Complete audit trail of all queries
    - All analysis code is published on GitHub
    - Machine-readable logs available at jobs.opensafely.org

    **Why is this important?**
    OpenSAFELY represents the gold standard for transparent, reproducible health research.
    Unlike traditional data access models, OpenSAFELY provides complete visibility into
    what research is being conducted and how patient data is being used.

    [Learn more at opensafely.org](https://www.opensafely.org)
    """)

# Initialize client
@st.cache_resource
def get_client():
    """Get cached OpenSAFELY client instance."""
    return OpenSAFELYJobsClient(use_demo_fallback=True)


@st.cache_data(ttl=300)
def load_organizations():
    """Load organizations with caching."""
    client = get_client()
    orgs = client.get_organizations()
    return orgs, client.is_using_demo_data


@st.cache_data(ttl=300)
def load_recent_jobs():
    """Load recent job requests with caching."""
    client = get_client()
    jobs = client.get_recent_job_requests(limit=50)
    return jobs, client.is_using_demo_data


def check_if_demo_data():
    """Check if we're using demo data."""
    client = get_client()
    return client.is_using_demo_data


@st.cache_data(ttl=300)
def load_dashboard_stats():
    """Load dashboard statistics with caching."""
    client = get_client()
    return client.get_dashboard_stats()


@st.cache_data(ttl=600)
def load_org_details(slug: str):
    """Load organization details with caching."""
    client = get_client()
    try:
        return client.get_organization_details(slug)
    except Exception:
        return None


# Check if using demo data and show banner
organizations_data = load_organizations()
if isinstance(organizations_data, tuple):
    organizations_initial, using_demo = organizations_data
else:
    organizations_initial = organizations_data
    using_demo = check_if_demo_data()

if using_demo:
    st.warning("""
    **Demo Mode**: Showing representative data based on real OpenSAFELY organizations.
    Live data will be available when deployed to Streamlit Cloud or run locally.

    [View live data at jobs.opensafely.org](https://jobs.opensafely.org)
    """)

# Sidebar
with st.sidebar:
    st.header("Dashboard Controls")

    # Refresh button
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Quick stats
    st.subheader("Quick Links")
    st.link_button(
        "jobs.opensafely.org",
        "https://jobs.opensafely.org",
        use_container_width=True
    )
    st.link_button(
        "OpenSAFELY Documentation",
        "https://docs.opensafely.org",
        use_container_width=True
    )
    st.link_button(
        "GitHub Repositories",
        "https://github.com/opensafely",
        use_container_width=True
    )

    st.divider()

    # Data source info
    st.info("""
    **Data Source:** jobs.opensafely.org

    Data is refreshed every 5 minutes.
    All information shown is publicly available.
    """)


# Main content with tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Organizations",
    "Recent Activity",
    "Analytics"
])


# Tab 1: Overview Dashboard
with tab1:
    st.subheader("Platform Overview")

    # Load data
    with st.spinner("Loading dashboard data..."):
        org_result = load_organizations()
        job_result = load_recent_jobs()
        stats = load_dashboard_stats()

        # Handle tuple returns (data, is_demo)
        organizations = org_result[0] if isinstance(org_result, tuple) else org_result
        recent_jobs = job_result[0] if isinstance(job_result, tuple) else job_result

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Organizations",
            value=len(organizations),
            help="Number of organizations using OpenSAFELY"
        )

    with col2:
        total_projects = sum(o.project_count for o in organizations)
        st.metric(
            label="Total Projects",
            value=total_projects,
            help="Total research projects across all organizations"
        )

    with col3:
        st.metric(
            label="Recent Jobs",
            value=len(recent_jobs),
            help="Job requests in the recent activity feed"
        )

    with col4:
        if stats:
            success_rate = stats.success_rate
            st.metric(
                label="Success Rate",
                value=f"{success_rate:.1f}%",
                help="Success rate of recent jobs"
            )
        else:
            st.metric(label="Success Rate", value="N/A")

    st.divider()

    # Two-column layout for overview
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Top Organizations")

        if organizations:
            # Sort by project count
            sorted_orgs = sorted(organizations, key=lambda x: x.project_count, reverse=True)[:10]

            for org in sorted_orgs:
                st.markdown(f"""
                <div class="org-card">
                    <div class="org-name">{org.name}</div>
                    <div class="org-stats">{org.project_count} project{'s' if org.project_count != 1 else ''}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No organizations loaded yet.")

    with right_col:
        st.subheader("Recent Job Activity")

        if recent_jobs:
            for job in recent_jobs[:10]:
                status_badge = get_status_badge(job.status)
                row_class = get_job_row_class(job.status)
                time_str = format_datetime(job.created_at) if job.created_at else "Unknown time"

                workspace = job.workspace_name or "Unknown workspace"
                project = job.project_name or ""

                st.markdown(f"""
                <div class="job-row {row_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{workspace}</strong>
                            {f'<span style="color: #7f8c8d; font-size: 0.85rem;"> / {project}</span>' if project else ''}
                        </div>
                        {status_badge}
                    </div>
                    <div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.3rem;">
                        {time_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent jobs loaded yet.")


# Tab 2: Organizations
with tab2:
    st.subheader("Organizations Using OpenSAFELY")

    org_result = load_organizations()
    organizations = org_result[0] if isinstance(org_result, tuple) else org_result

    if organizations:
        # Search/filter
        search_query = st.text_input(
            "Search organizations",
            placeholder="Type to filter...",
            key="org_search"
        )

        filtered_orgs = organizations
        if search_query:
            filtered_orgs = [
                o for o in organizations
                if search_query.lower() in o.name.lower() or search_query.lower() in o.slug.lower()
            ]

        st.write(f"Showing {len(filtered_orgs)} of {len(organizations)} organizations")

        # Display organizations
        for i in range(0, len(filtered_orgs), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(filtered_orgs):
                    org = filtered_orgs[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"**{org.name}**")
                            st.caption(f"{org.project_count} projects")
                            st.link_button(
                                "View on OpenSAFELY",
                                f"https://jobs.opensafely.org/{org.slug}/",
                                use_container_width=True
                            )

        # Organization details expander
        st.divider()
        st.subheader("Organization Details")

        org_names = [o.name for o in organizations]
        selected_org_name = st.selectbox("Select an organization", options=org_names)

        if selected_org_name:
            selected_org = next((o for o in organizations if o.name == selected_org_name), None)
            if selected_org:
                with st.spinner(f"Loading details for {selected_org.name}..."):
                    org_details = load_org_details(selected_org.slug)

                if org_details:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Projects", org_details.project_count)
                    with col2:
                        st.link_button(
                            "Open in OpenSAFELY",
                            org_details.url,
                            use_container_width=True
                        )

                    if org_details.projects:
                        st.subheader("Projects")
                        for project in org_details.projects[:20]:
                            st.markdown(f"- [{project.name}](https://jobs.opensafely.org/{project.slug}/)")
                else:
                    st.warning("Could not load organization details.")
    else:
        st.info("Loading organizations...")


# Tab 3: Recent Activity
with tab3:
    st.subheader("Recent Job Requests")

    job_result = load_recent_jobs()
    recent_jobs = job_result[0] if isinstance(job_result, tuple) else job_result

    if recent_jobs:
        # Status filter
        status_filter = st.multiselect(
            "Filter by status",
            options=["Succeeded", "Failed", "Running", "Pending", "Unknown"],
            default=["Succeeded", "Failed", "Running", "Pending"]
        )

        # Convert filter to JobStatus
        status_map = {
            "Succeeded": JobStatus.SUCCEEDED,
            "Failed": JobStatus.FAILED,
            "Running": JobStatus.RUNNING,
            "Pending": JobStatus.PENDING,
            "Unknown": JobStatus.UNKNOWN,
        }
        selected_statuses = [status_map[s] for s in status_filter]

        filtered_jobs = [j for j in recent_jobs if j.status in selected_statuses]

        st.write(f"Showing {len(filtered_jobs)} of {len(recent_jobs)} job requests")

        # Create DataFrame for display
        job_data = []
        for job in filtered_jobs:
            job_data.append({
                "Status": job.status.value.title(),
                "Workspace": job.workspace_name or "Unknown",
                "Project": job.project_name or "Unknown",
                "Created": format_datetime(job.created_at) if job.created_at else "Unknown",
                "ID": job.identifier[:8] + "..." if job.identifier and len(job.identifier) > 8 else job.identifier,
            })

        if job_data:
            df = pd.DataFrame(job_data)

            # Display with custom styling
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Workspace": st.column_config.TextColumn("Workspace", width="medium"),
                    "Project": st.column_config.TextColumn("Project", width="medium"),
                    "Created": st.column_config.TextColumn("Created", width="small"),
                    "ID": st.column_config.TextColumn("ID", width="small"),
                }
            )

            # Summary stats
            st.divider()
            cols = st.columns(4)

            succeeded = sum(1 for j in filtered_jobs if j.status == JobStatus.SUCCEEDED)
            failed = sum(1 for j in filtered_jobs if j.status == JobStatus.FAILED)
            running = sum(1 for j in filtered_jobs if j.status == JobStatus.RUNNING)
            pending = sum(1 for j in filtered_jobs if j.status == JobStatus.PENDING)

            with cols[0]:
                st.metric("Succeeded", succeeded, delta=None)
            with cols[1]:
                st.metric("Failed", failed, delta=None)
            with cols[2]:
                st.metric("Running", running, delta=None)
            with cols[3]:
                st.metric("Pending", pending, delta=None)
    else:
        st.info("No recent job requests available.")


# Tab 4: Analytics
with tab4:
    st.subheader("Platform Analytics")

    org_result = load_organizations()
    job_result = load_recent_jobs()
    organizations = org_result[0] if isinstance(org_result, tuple) else org_result
    recent_jobs = job_result[0] if isinstance(job_result, tuple) else job_result

    if organizations:
        # Organization distribution chart
        st.subheader("Projects by Organization")

        org_data = pd.DataFrame([
            {"Organization": o.name, "Projects": o.project_count}
            for o in sorted(organizations, key=lambda x: x.project_count, reverse=True)[:15]
        ])

        if not org_data.empty:
            st.bar_chart(org_data.set_index("Organization"))

    if recent_jobs:
        st.divider()

        # Job status distribution
        st.subheader("Job Status Distribution")

        status_counts = {}
        for job in recent_jobs:
            status = job.status.value.title()
            status_counts[status] = status_counts.get(status, 0) + 1

        status_df = pd.DataFrame([
            {"Status": k, "Count": v}
            for k, v in status_counts.items()
        ])

        if not status_df.empty:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.bar_chart(status_df.set_index("Status"))

            with col2:
                for status, count in status_counts.items():
                    pct = count / len(recent_jobs) * 100
                    st.write(f"**{status}:** {count} ({pct:.1f}%)")

        # Jobs by time
        st.divider()
        st.subheader("Activity Timeline")

        jobs_with_time = [j for j in recent_jobs if j.created_at]
        if jobs_with_time:
            # Group by date
            date_counts = {}
            for job in jobs_with_time:
                date_key = job.created_at.strftime("%Y-%m-%d")
                date_counts[date_key] = date_counts.get(date_key, 0) + 1

            timeline_df = pd.DataFrame([
                {"Date": k, "Jobs": v}
                for k, v in sorted(date_counts.items())
            ])

            if not timeline_df.empty:
                st.line_chart(timeline_df.set_index("Date"))

    # Data quality notice
    st.divider()
    st.markdown("""
    <div class="info-box">
        <strong>Data Quality Note</strong><br>
        This dashboard displays publicly available data from jobs.opensafely.org.
        The data shown represents a snapshot of recent activity and may not reflect
        the complete history of all jobs run on the platform.
    </div>
    """, unsafe_allow_html=True)


# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.85rem;">
    Data sourced from <a href="https://jobs.opensafely.org" target="_blank">jobs.opensafely.org</a> |
    OpenSAFELY is developed by the <a href="https://www.bennett.ox.ac.uk" target="_blank">Bennett Institute for Applied Data Science</a>
</div>
""", unsafe_allow_html=True)
