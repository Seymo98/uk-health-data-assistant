
import streamlit as st
from openai import OpenAI
import os

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

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

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
            st.rerun()

    with col2:
        num_messages = len(st.session_state.messages)
        st.metric("Messages", num_messages)

    # MODEL SETTINGS
    st.divider()
    st.header("🤖 Model Settings")
    model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1, help="Lower = more focused, Higher = more creative")

    # ABOUT
    st.divider()
    st.markdown("""
    ### About
    This assistant helps researchers discover and access UK health datasets.

    **Version:** 2.0
    **Powered by:** OpenAI GPT-4o
    """)

# --- PROMPT STARTERS ---
if len(st.session_state.messages) == 0:
    st.markdown("#### 💬 Ask a question or try one of these:")
    example_prompts = [
        "What datasets exist for cardiovascular disease?",
        "Compare OpenSAFELY and CPRD access requirements.",
        "What data is available for maternal health in Scotland?",
        "How do I access data through a Trusted Research Environment?"
    ]
    cols = st.columns(len(example_prompts))
    for i, prompt in enumerate(example_prompts):
        if cols[i].button(prompt, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# --- DISPLAY CONVERSATION HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT ---
if prompt := st.chat_input("Ask your health data question..."):
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar first.")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response with streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

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
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

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

# --- FOOTER SECTION ---
st.divider()
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; color: grey;'>
    <p>This is a beta prototype developed to test capabilities. Responses are generated by OpenAI's GPT-4o model and may not reflect the full UK data landscape. Always verify access routes with custodians.</p>
</div>
""", unsafe_allow_html=True)
