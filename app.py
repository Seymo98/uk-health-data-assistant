
import streamlit as st
from openai import OpenAI
import os
import re
import hashlib
from datetime import datetime
from collections import Counter
import requests
import json
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="UK Health Data Assistant", page_icon=":microscope:", layout="centered")

# --- LOAD SYSTEM PROMPT FROM FILE ---
@st.cache_data
def load_system_prompt():
    """Load the system prompt from external file"""
    try:
        with open("system_prompt_v3_structured.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback to hardcoded prompt if file not found
        return """You are the UK Health Data Assistant — a professional and trusted assistant supporting industry and academic researchers, innovators, and public sector analysts in exploring and accessing UK health datasets.

---

🎓 ROLE & PURPOSE:
- Help users identify relevant datasets, understand access routes, and compare sources across a federated UK health data ecosystem.
- You are not a search engine. You are a discovery companion.
- Your value lies in clarifying user intent, connecting them to relevant data sources, and dramatically reducing the time researchers spend trying to find the right data.

---

💬 TONE & COMMUNICATION:
- Speak in a professional but accessible tone.
- Avoid jargon; explain terms clearly and simply.
- Clarify vague questions by asking follow-ups.
- Summarise clearly and concisely, with context or next steps.

---

🌐 BROWSING GUIDANCE:
- While you can't browse directly, simulate reasoning as if you could.
- Reference trusted public sources: HDR UK, NHS England, ADR UK, CLOSER, UK Biobank, ONS, GOV.UK, Research Data Scotland, SAIL, Our Future Health, Genomics England, CPRD, OpenSAFELY, BHF Data Science Centre.
- If an answer isn't definitive, advise checking directly with the data custodian or platform.

---

📘 LANDSCAPE CONTEXT (as of May 2025):
- NHS Digital has merged into NHS England — always refer to NHS England.
- OpenSAFELY only operates on TPP and supports COVID-related research (not general purpose).
- The terms TRE and SDE are interchangeable; Scotland uses "Data Safe Haven"; "Secure Processing Environment" appears in Digital Economy Act.
- Gateway metadata is incomplete — verification with custodians is often necessary.

---

🚫 DO NOT:
- Do not make up dataset names or access pathways.
- Do not speculate about coverage or custodianship.
- Do not suggest OpenSAFELY supports EMIS or non-COVID use without checking their changelog.

---

✅ REMEMBER:
- You are here to enable faster, fairer, more responsible use of UK health data for public benefit."""

# --- DATASET LINKS DATABASE ---
DATASET_LINKS = {
    "HDR UK": "https://www.hdruk.ac.uk/",
    "Health Data Research UK": "https://www.hdruk.ac.uk/",
    "Innovation Gateway": "https://www.healthdatagateway.org/",
    "Health Data Gateway": "https://www.healthdatagateway.org/",
    "CPRD": "https://cprd.com/",
    "Clinical Practice Research Datalink": "https://cprd.com/",
    "OpenSAFELY": "https://www.opensafely.org/",
    "UK Biobank": "https://www.ukbiobank.ac.uk/",
    "NHS England": "https://www.england.nhs.uk/",
    "NHS Digital": "https://www.england.nhs.uk/",
    "SAIL": "https://saildatabank.com/",
    "SAIL Databank": "https://saildatabank.com/",
    "Research Data Scotland": "https://www.researchdata.scot/",
    "ADR UK": "https://www.adruk.org/",
    "CLOSER": "https://www.closer.ac.uk/",
    "ONS": "https://www.ons.gov.uk/",
    "Office for National Statistics": "https://www.ons.gov.uk/",
    "Our Future Health": "https://ourfuturehealth.org.uk/",
    "Genomics England": "https://www.genomicsengland.co.uk/",
    "BHF Data Science Centre": "https://www.bhf.org.uk/what-we-do/our-research/bhf-data-science-centre",
}

# --- HELPER FUNCTIONS ---
def linkify_datasets(text):
    """Convert dataset mentions to clickable links"""
    result = text
    for dataset, url in DATASET_LINKS.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(dataset) + r'\b'
        replacement = f'[{dataset}]({url})'
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def export_conversation_md():
    """Export conversation as Markdown"""
    if not st.session_state.messages:
        return "No conversation to export."

    md_content = f"# UK Health Data Assistant - Conversation Export\n\n"
    md_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "---\n\n"

    for msg in st.session_state.messages:
        role = "**You:**" if msg["role"] == "user" else "**Assistant:**"
        md_content += f"{role}\n\n{msg['content']}\n\n---\n\n"

    return md_content

def get_cache_key(prompt, model, temperature):
    """Generate cache key for a query"""
    key_string = f"{prompt}_{model}_{temperature}"
    return hashlib.md5(key_string.encode()).hexdigest()

# --- HDR UK GATEWAY API INTEGRATION ---
HDR_API_BASE = "https://api.www.healthdatagateway.org/api/v1"
HDR_WEB_BASE = "https://www.healthdatagateway.org"

@st.cache_data(ttl=3600)
def search_hdr_datasets(query, limit=5):
    """Search HDR UK Gateway for datasets"""
    try:
        # Try the public search endpoint
        response = requests.get(
            f"{HDR_WEB_BASE}/search",
            params={"search": query, "tab": "Datasets"},
            timeout=10
        )

        if response.status_code == 200:
            return {"status": "success", "message": f"Found results for '{query}'", "url": response.url}
        else:
            return {"status": "unavailable", "message": "HDR UK Gateway search temporarily unavailable"}
    except Exception as e:
        return {"status": "error", "message": f"Could not connect to HDR UK Gateway: {str(e)}"}

def get_dataset_info(dataset_name):
    """Get information about a specific dataset from HDR UK"""
    # Map common dataset names to their HDR UK pages
    dataset_pages = {
        "CPRD": f"{HDR_WEB_BASE}/search?search=CPRD",
        "UK Biobank": f"{HDR_WEB_BASE}/search?search=UK%20Biobank",
        "OpenSAFELY": f"{HDR_WEB_BASE}/search?search=OpenSAFELY",
        "SAIL": f"{HDR_WEB_BASE}/search?search=SAIL",
    }

    return dataset_pages.get(dataset_name, f"{HDR_WEB_BASE}/search?search={dataset_name}")

# --- COMPARISON TABLE GENERATION ---
DATASET_COMPARISONS = {
    "CPRD vs OpenSAFELY": pd.DataFrame({
        "Feature": ["Data Type", "Coverage", "Access Method", "Primary Care", "Linkages", "Cost", "Best For"],
        "CPRD": [
            "EHR extracts",
            "~60M patients",
            "Direct application",
            "EMIS + Vision",
            "HES, ONS, cancer",
            "Fees apply",
            "Observational studies"
        ],
        "OpenSAFELY": [
            "In-situ analysis",
            "~60M patients",
            "Code repository",
            "TPP only",
            "HES, ONS, SGSS",
            "Free (COVID research)",
            "COVID-19 research"
        ]
    }),

    "UK Biobank vs Genomics England": pd.DataFrame({
        "Feature": ["Data Type", "Participants", "Genomics", "Imaging", "Follow-up", "Access", "Best For"],
        "UK Biobank": [
            "Cohort study",
            "~500,000",
            "WGS + arrays",
            "MRI, DXA, ECG",
            "Ongoing",
            "Application required",
            "Population genomics"
        ],
        "Genomics England": [
            "Clinical genomics",
            "~100,000",
            "WGS",
            "Limited",
            "Via NHS",
            "Application required",
            "Rare diseases, cancer"
        ]
    }),

    "SAIL vs Research Data Scotland": pd.DataFrame({
        "Feature": ["Coverage", "Population", "Data Types", "Linkages", "Access Method", "Best For"],
        "SAIL": [
            "Wales",
            "~3.5M",
            "GP, hospital, social care",
            "Education, housing",
            "TRE (Data Safe Haven)",
            "Welsh population studies"
        ],
        "Research Data Scotland": [
            "Scotland",
            "~5.5M",
            "Health, social care, admin",
            "Education, justice",
            "TRE (Safe Haven)",
            "Scottish population studies"
        ]
    }),

    "NHS England vs Research Data Scotland": pd.DataFrame({
        "Feature": ["Coverage", "Population", "Primary Data", "Linkages", "Access", "Cost", "Best For"],
        "NHS England": [
            "England",
            "~57M",
            "Hospital, GP, prescribing",
            "HES, MHSDS, cancer",
            "Data Access Request Service",
            "Fees apply",
            "England-wide studies"
        ],
        "Research Data Scotland": [
            "Scotland",
            "~5.5M",
            "Health, social care",
            "Education, justice",
            "Safe Haven",
            "Varies",
            "Scottish linkage studies"
        ]
    }),

    "CLOSER vs UK Biobank": pd.DataFrame({
        "Feature": ["Data Type", "Focus", "Participants", "Studies", "Longitudinal", "Access", "Best For"],
        "CLOSER": [
            "Longitudinal studies",
            "Life course research",
            "Multiple cohorts",
            "9 major cohorts",
            "Yes (decades)",
            "Study-specific",
            "Life course epidemiology"
        ],
        "UK Biobank": [
            "Cohort + biobank",
            "Middle-aged health",
            "~500,000",
            "Single cohort",
            "Yes (ongoing)",
            "Application process",
            "Genomics, imaging"
        ]
    }),

    "CPRD vs UK Biobank": pd.DataFrame({
        "Feature": ["Data Type", "Coverage", "Genomics", "Imaging", "Linkages", "Cost", "Best For"],
        "CPRD": [
            "Primary care EHR",
            "~60M patients",
            "Limited",
            "No",
            "HES, ONS, cancer",
            "Fees apply",
            "Real-world evidence"
        ],
        "UK Biobank": [
            "Cohort + biobank",
            "~500,000",
            "WGS + arrays",
            "MRI, DXA, ECG",
            "HES, cancer, death",
            "Fees apply",
            "Genomic medicine"
        ]
    }),

    "OpenSAFELY vs SAIL": pd.DataFrame({
        "Feature": ["Analysis Model", "Coverage", "Primary Care", "Data Access", "Code Sharing", "Best For"],
        "OpenSAFELY": [
            "In-situ (code to data)",
            "England (~60M)",
            "TPP only",
            "No direct access",
            "GitHub (public)",
            "Transparent research"
        ],
        "SAIL": [
            "TRE (researcher access)",
            "Wales (~3.5M)",
            "EMIS + Vision",
            "Within Safe Haven",
            "On request",
            "Welsh linkage studies"
        ]
    }),

    "TRE Comparison": pd.DataFrame({
        "Feature": ["SAIL Databank", "Research Data Scotland", "NHS England SDE", "OpenSAFELY"],
        "Region": ["Wales", "Scotland", "England", "England"],
        "Access Model": ["Remote/on-site", "Safe Haven", "Secure environment", "Code to data"],
        "Data Holdings": ["Health, social, admin", "Health, social, justice", "NHS data", "Primary care (TPP)"],
        "Best For": ["Welsh studies", "Scottish linkage", "England NHS", "COVID/transparent"]
    })
}

def get_comparison_table(query):
    """Get a pre-built comparison table if query matches"""
    query_lower = query.lower()

    for key, df in DATASET_COMPARISONS.items():
        if all(term in query_lower for term in key.lower().split(" vs ")):
            return key, df

    return None, None

def create_custom_comparison(datasets):
    """Create a custom comparison table based on dataset names"""
    # This is a simplified version - could be enhanced with API data
    comparison_data = {
        "Feature": ["Data Type", "Geographic Coverage", "Access Method", "Typical Use Case"],
    }

    for dataset in datasets:
        comparison_data[dataset] = [
            "Health records",
            "UK",
            "Application required",
            f"{dataset} research"
        ]

    return pd.DataFrame(comparison_data)

# --- DATASET METADATA ---
DATASET_METADATA = {
    "CPRD": {
        "name": "Clinical Practice Research Datalink",
        "coverage": "~60 million patients",
        "data_type": "Primary care electronic health records",
        "update_frequency": "Regular updates",
        "access": "Application required, fees apply",
        "url": "https://cprd.com/"
    },
    "UK Biobank": {
        "name": "UK Biobank",
        "coverage": "~500,000 participants",
        "data_type": "Cohort study with genomics, imaging, and health records",
        "update_frequency": "Ongoing follow-up",
        "access": "Application required, fees apply",
        "url": "https://www.ukbiobank.ac.uk/"
    },
    "OpenSAFELY": {
        "name": "OpenSAFELY",
        "coverage": "~60 million patients (TPP)",
        "data_type": "In-situ primary care analysis platform",
        "update_frequency": "Near real-time",
        "access": "Code repository (GitHub), free for COVID research",
        "url": "https://www.opensafely.org/"
    },
    "SAIL": {
        "name": "SAIL Databank",
        "coverage": "~3.5 million (Wales population)",
        "data_type": "Linked health, social care, and administrative data",
        "update_frequency": "Regular updates",
        "access": "TRE access via Data Safe Haven",
        "url": "https://saildatabank.com/"
    },
    "Genomics England": {
        "name": "Genomics England",
        "coverage": "~100,000 genomes",
        "data_type": "Whole genome sequences with clinical data",
        "update_frequency": "Ongoing",
        "access": "Application required",
        "url": "https://www.genomicsengland.co.uk/"
    }
}

def display_dataset_metadata(dataset_name):
    """Display metadata card for a dataset"""
    if dataset_name in DATASET_METADATA:
        meta = DATASET_METADATA[dataset_name]
        return f"""
**{meta['name']}**
- 📊 Coverage: {meta['coverage']}
- 📁 Data Type: {meta['data_type']}
- 🔄 Updates: {meta['update_frequency']}
- 🔐 Access: {meta['access']}
- 🔗 [Learn more]({meta['url']})
"""
    return None

# --- AI FOLLOW-UP SUGGESTIONS ---
def generate_follow_up_questions(conversation_context, last_response):
    """Generate AI-powered follow-up questions based on conversation"""
    try:
        # Extract key topics from the last response
        prompt = f"""Based on this conversation about UK health data, suggest 3 brief, specific follow-up questions a researcher might ask.

Last response: {last_response[:500]}

Provide 3 questions that:
1. Dig deeper into mentioned datasets
2. Explore related data sources
3. Ask about practical access/usage

Format: Just the 3 questions, one per line, no numbers or bullets."""

        client = OpenAI(api_key=st.session_state.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for suggestions
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )

        suggestions = response.choices[0].message.content.strip().split('\n')
        return [s.strip() for s in suggestions if s.strip()][:3]
    except:
        # Fallback suggestions if API fails
        return [
            "What are the access requirements?",
            "How can I link this with other datasets?",
            "What's the typical research timeline?"
        ]

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    # Try to load API key from Streamlit secrets (for deployed apps)
    try:
        st.session_state.api_key = st.secrets.get("OPENAI_API_KEY", "")
    except:
        st.session_state.api_key = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}

if "usage_stats" not in st.session_state:
    st.session_state.usage_stats = {
        "total_queries": 0,
        "topics": [],
        "start_time": datetime.now()
    }

if "search_filter" not in st.session_state:
    st.session_state.search_filter = ""

if "follow_up_suggestions" not in st.session_state:
    st.session_state.follow_up_suggestions = []

if "show_metadata" not in st.session_state:
    st.session_state.show_metadata = {}

# --- HEADER SECTION ---
st.markdown("""
<div style='text-align: center; padding-bottom: 1rem;'>
    <img src="https://raw.githubusercontent.com/Seymo98/uk-health-data-assistant/main/650510F6-EB0C-4BFC-91DD-EBF8A8978931.png" width="120">
    <h1 style='margin-bottom: 0;'>UK Health Data Assistant</h1>
    <p style='font-size: 1.1rem;'>Smarter discovery, for faster impact.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- SIDEBAR FOR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")

    # API KEY INPUT
    with st.expander("🔐 OpenAI API Key", expanded=not st.session_state.api_key):
        st.markdown("Create a key at [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)")
        user_api_key = st.text_input("Paste your OpenAI API key here", type="password", value=st.session_state.api_key)

        if user_api_key and user_api_key != st.session_state.api_key:
            st.session_state.api_key = user_api_key
            st.success("API key saved!")

    # CONVERSATION MANAGEMENT
    st.divider()
    st.header("💬 Conversation")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.feedback = {}
            st.rerun()

    with col2:
        if st.button("📥 Export", use_container_width=True):
            md_content = export_conversation_md()
            st.download_button(
                label="Download MD",
                data=md_content,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

    # MESSAGE COUNT
    num_messages = len(st.session_state.messages)
    st.metric("Messages", num_messages)

    # CONVERSATION SEARCH
    if num_messages > 0:
        st.text_input("🔍 Search conversation", key="search_filter", placeholder="Type to filter...")

    # MODEL SETTINGS
    st.divider()
    st.header("🤖 Model Settings")
    model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1, help="Lower = more focused, Higher = more creative")

    # ENABLE CACHING
    use_cache = st.checkbox("Enable smart caching", value=True, help="Cache responses to reduce API calls")

    # USAGE STATISTICS
    st.divider()
    st.header("📊 Usage Stats")
    total_queries = st.session_state.usage_stats["total_queries"]
    st.metric("Total Queries", total_queries)

    if st.session_state.usage_stats["topics"]:
        topic_counts = Counter(st.session_state.usage_stats["topics"])
        most_common = topic_counts.most_common(3)
        if most_common:
            st.caption("Top Topics:")
            for topic, count in most_common:
                st.caption(f"• {topic}: {count}")

    # HDR UK GATEWAY SEARCH
    st.divider()
    st.header("🔬 HDR UK Gateway")

    search_query = st.text_input("Search datasets", placeholder="e.g., diabetes, genomics")
    if st.button("Search Gateway", use_container_width=True):
        if search_query:
            with st.spinner("Searching HDR UK Gateway..."):
                result = search_hdr_datasets(search_query)
                if result["status"] == "success":
                    st.success(result["message"])
                    st.link_button("View Results", result["url"], use_container_width=True)
                else:
                    st.warning(result["message"])

    # QUICK DATASET LINKS
    st.caption("Quick Links:")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("CPRD", key="cprd_link", use_container_width=True):
            st.link_button("Open", get_dataset_info("CPRD"), use_container_width=True)
    with col_b:
        if st.button("UK Biobank", key="ukb_link", use_container_width=True):
            st.link_button("Open", get_dataset_info("UK Biobank"), use_container_width=True)

    # ABOUT
    st.divider()
    st.markdown("""
    ### About
    This assistant helps researchers discover and access UK health datasets.

    **Version:** 3.2
    **Powered by:** OpenAI GPT-4o

    **Features:**
    - 📥 Export conversations
    - 🔗 Dataset links
    - 👍 Response feedback
    - 🔍 Conversation search
    - ⚡ Smart caching
    - 📊 Comparison tables (9 total!)
    - 🔬 HDR UK Gateway integration
    - 💡 AI follow-up suggestions
    - 📊 Dataset metadata cards
    """)

# --- CATEGORIZED PROMPT STARTERS ---
if len(st.session_state.messages) == 0:
    st.markdown("#### 💬 Choose a category or ask your own question:")

    # Tabs for categories
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Clinical", "🧬 Genomics", "🏘️ Social Care", "📊 General"])

    with tab1:
        clinical_prompts = [
            "What datasets exist for cardiovascular disease?",
            "Where can I find data on diabetes management?",
            "What data is available for maternal health in Scotland?",
        ]
        for prompt in clinical_prompts:
            if st.button(prompt, key=f"clinical_{prompt}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

    with tab2:
        genomics_prompts = [
            "How do I access Genomics England data?",
            "What genomic datasets are available through UK Biobank?",
            "Compare genomic data access across different platforms",
        ]
        for prompt in genomics_prompts:
            if st.button(prompt, key=f"genomics_{prompt}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

    with tab3:
        social_prompts = [
            "What data exists for mental health and housing?",
            "Where can I find social care datasets?",
            "What datasets link health and social determinants?",
        ]
        for prompt in social_prompts:
            if st.button(prompt, key=f"social_{prompt}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

    with tab4:
        general_prompts = [
            "Compare OpenSAFELY and CPRD access requirements.",
            "How do I access data through a Trusted Research Environment?",
            "What is the HDR UK Innovation Gateway?",
        ]
        for prompt in general_prompts:
            if st.button(prompt, key=f"general_{prompt}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

# --- DISPLAY CONVERSATION HISTORY ---
search_filter = st.session_state.search_filter.lower()
for idx, message in enumerate(st.session_state.messages):
    # Apply search filter
    if search_filter and search_filter not in message["content"].lower():
        continue

    with st.chat_message(message["role"]):
        # Check for comparison queries in user messages
        if message["role"] == "user":
            comparison_title, comparison_df = get_comparison_table(message["content"])
            if comparison_df is not None:
                st.markdown(message["content"])
                st.markdown(f"**📊 Comparison Table: {comparison_title}**")
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            else:
                st.markdown(message["content"])
        else:
            # Linkify dataset mentions in assistant responses
            content = linkify_datasets(message["content"])
            st.markdown(content)

        # Add feedback buttons and features for assistant responses
        if message["role"] == "assistant":
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedback[idx] = "positive"
                    st.toast("Thanks for your feedback!")
            with col2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedback[idx] = "negative"
                    st.toast("Thanks for your feedback!")

            # Check for dataset mentions and show metadata cards
            for dataset in DATASET_METADATA.keys():
                if dataset in message["content"]:
                    with st.expander(f"📊 {dataset} Details"):
                        metadata = display_dataset_metadata(dataset)
                        if metadata:
                            st.markdown(metadata)

            # Show follow-up suggestions for the last assistant message
            if idx == len(st.session_state.messages) - 1 and len(st.session_state.messages) > 1:
                if st.session_state.follow_up_suggestions:
                    st.markdown("**💡 You might also want to ask:**")
                    cols = st.columns(3)
                    for i, suggestion in enumerate(st.session_state.follow_up_suggestions):
                        if i < 3:
                            with cols[i]:
                                if st.button(suggestion, key=f"followup_{idx}_{i}", use_container_width=True):
                                    st.session_state.messages.append({"role": "user", "content": suggestion})
                                    st.rerun()

# --- USER INPUT ---
if prompt := st.chat_input("Ask your health data question..."):
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar first.")
    else:
        # Track usage
        st.session_state.usage_stats["total_queries"] += 1

        # Extract topic (first few words)
        topic = " ".join(prompt.split()[:4])
        st.session_state.usage_stats["topics"].append(topic)

        # Check cache
        cache_key = get_cache_key(prompt, model, temperature)
        cached_response = None
        if use_cache and cache_key in st.session_state.response_cache:
            cached_response = st.session_state.response_cache[cache_key]

        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

            # Check if this is a comparison query and show table
            comparison_title, comparison_df = get_comparison_table(prompt)
            if comparison_df is not None:
                st.markdown(f"**📊 Comparison Table: {comparison_title}**")
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                st.info("💡 The assistant will provide additional context below.")

        # Generate assistant response with streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            if cached_response:
                # Use cached response
                full_response = cached_response
                message_placeholder.markdown(f"🔄 *Cached response*\n\n{linkify_datasets(full_response)}")
            else:
                # Generate new response
                try:
                    client = OpenAI(api_key=st.session_state.api_key)
                    system_prompt = load_system_prompt()

                    # Prepare messages for API
                    api_messages = [{"role": "system", "content": system_prompt}]
                    api_messages.extend(st.session_state.messages)

                    # Stream the response
                    stream = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        temperature=temperature,
                        stream=True
                    )

                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(linkify_datasets(full_response) + "▌")

                    message_placeholder.markdown(linkify_datasets(full_response))

                    # Cache the response
                    if use_cache:
                        st.session_state.response_cache[cache_key] = full_response

                except Exception as e:
                    error_message = str(e)

                    # Provide specific error messages
                    if "invalid_api_key" in error_message or "Incorrect API key" in error_message:
                        full_response = "❌ **Invalid API Key**\n\nThe API key you provided is invalid. Please check your key in the sidebar and try again.\n\nYou can create a new key at [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)"
                    elif "insufficient_quota" in error_message or "quota" in error_message.lower():
                        full_response = "❌ **Quota Exceeded**\n\nYour OpenAI account has exceeded its quota. Please check your billing details at [platform.openai.com/account/billing](https://platform.openai.com/account/billing)"
                    elif "rate_limit" in error_message.lower():
                        full_response = "❌ **Rate Limit Exceeded**\n\nYou've sent too many requests. Please wait a moment and try again."
                    elif "timeout" in error_message.lower():
                        full_response = "❌ **Request Timeout**\n\nThe request took too long. Please try again."
                    else:
                        full_response = f"❌ **Error**\n\nAn error occurred: {error_message}\n\nPlease check your API key and try again."

                    message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Generate follow-up suggestions
            if st.session_state.api_key and full_response and not full_response.startswith("❌"):
                st.session_state.follow_up_suggestions = generate_follow_up_questions(
                    st.session_state.messages,
                    full_response
                )
                st.rerun()

# --- FOOTER SECTION ---
st.divider()
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; color: grey;'>
    <p>This is a beta prototype developed to test capabilities. Responses are generated by OpenAI's GPT-4o model and may not reflect the full UK data landscape. Always verify access routes with custodians.</p>
</div>
""", unsafe_allow_html=True)
