
import streamlit as st
from openai import OpenAI
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="UK Health Data Assistant", page_icon=":microscope:", layout="centered")

# --- HEADER SECTION ---
st.markdown("""
<div style='text-align: center; padding-bottom: 1rem;'>
    <img src="https://raw.githubusercontent.com/Seymo98/uk-health-data-assistant/main/650510F6-EB0C-4BFC-91DD-EBF8A8978931.png" width="120">
    <h1 style='margin-bottom: 0;'>UK Health Data Assistant</h1>
    <p style='font-size: 1.1rem;'>Smarter discovery, for faster impact.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- API KEY INPUT ---
with st.expander("🔐 Enter your OpenAI API key"):
    st.markdown("You can create a key at [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)")
    user_api_key = st.text_input("Paste your OpenAI API key here", type="password")

# --- PROMPT STARTERS ---
st.markdown("#### 💬 Ask a question or try one of these:")
example_prompts = [
    "What UK datasets are available on asthma in adults?",
    "Compare CPRD and OpenSAFELY.",
    "Where can I find pregnancy and birth outcome records?",
    "What data exists for mental health and housing?",
]
cols = st.columns(len(example_prompts))
for i, prompt in enumerate(example_prompts):
    if cols[i].button(prompt):
        st.session_state["selected_prompt"] = prompt

# --- USER QUERY AREA ---
prompt_input = st.text_area("Your health data question:", value=st.session_state.get("selected_prompt", ""), key="user_prompt")

if st.button("Ask"):
    if not user_api_key:
        st.warning("Please enter your OpenAI API key first.")
    elif not prompt_input.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                client = OpenAI(api_key=user_api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt_input}],
                    temperature=0.3
                )
                st.markdown("#### 🧠 Assistant Response:")
                st.success(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- FOOTER SECTION ---
st.divider()
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; color: grey;'>
    <p>This is a beta prototype developed for the UK Health Data Research Service. Responses are generated by OpenAI's GPT-4o model and may not reflect the full UK data landscape. Always verify access routes with custodians.</p>
</div>
""", unsafe_allow_html=True)
