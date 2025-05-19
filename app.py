
import streamlit as st
import openai
import os

# App settings
st.set_page_config(page_title="UK Health Data Assistant", page_icon=":microscope:")

# Header
st.image("650510F6-EB0C-4BFC-91DD-EBF8A8978931.png", width=200)
st.title("UK Health Data Assistant")
st.markdown("Smarter discovery, for faster impact.")

# Disclaimer
st.markdown("**Disclaimer:** This is a beta prototype. Responses may not reflect the full UK health data landscape. Always verify dataset access with the custodian or official platform.")
st.markdown("---")

# Input API key
openai.api_key = st.text_input("Enter your OpenAI API key", type="password")

# User input
prompt = st.text_area("Ask a health data question (e.g., 'What datasets are available for cancer research in the UK?')")

# Submit button
if st.button("Ask"):
    if not openai.api_key:
        st.warning("Please enter your OpenAI API key.")
    elif not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                st.success(response["choices"][0]["message"]["content"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
