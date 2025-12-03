# UK Health Data Assistant

A conversational AI assistant that helps researchers discover and access UK health datasets. Built with Streamlit and powered by OpenAI's GPT-4o.

![UK Health Data Assistant](https://raw.githubusercontent.com/Seymo98/uk-health-data-assistant/main/650510F6-EB0C-4BFC-91DD-EBF8A8978931.png)

**Tagline:** *Smarter discovery, for faster impact.*

---

## Features

- 🤖 **Conversational AI** - Natural language queries about UK health datasets
- 💬 **Chat History** - Contextual conversations with full message history
- ⚡ **Streaming Responses** - Real-time response generation
- 🎨 **Modern UI** - Clean, intuitive chat interface
- ⚙️ **Customizable** - Choose models (GPT-4o, GPT-4o-mini, GPT-4-turbo) and adjust temperature
- 🔐 **Secure** - API keys stored in session (never logged)
- 📚 **Expert Knowledge** - Specialized in UK health data landscape (HDR UK, NHS England, CPRD, OpenSAFELY, etc.)

---

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Seymo98/uk-health-data-assistant.git
   cd uk-health-data-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   - Navigate to `http://localhost:8501`
   - Enter your OpenAI API key in the sidebar
   - Start asking questions!

---

## Deploy to Streamlit Cloud

Deploy your own instance for free:

### Step 1: Fork or Use This Repo
- Fork this repository to your GitHub account, or
- Use this repo directly (if you have access)

### Step 2: Sign Up for Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account

### Step 3: Deploy New App
1. Click **"New app"**
2. Select:
   - **Repository:** `Seymo98/uk-health-data-assistant` (or your fork)
   - **Branch:** `claude/getting-started-01FGJKi1aQCosmDuryZ1uCrN` (or `main`)
   - **Main file path:** `app.py`
3. Click **"Advanced settings"** (optional)

### Step 4: Configure Secrets (Optional)
If you want to provide a default API key for users:

1. In "Advanced settings", add to **Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-your-openai-api-key-here"
   ```
2. **Note:** Users can still override this by entering their own key in the UI

### Step 5: Deploy!
- Click **"Deploy!"**
- Wait 2-3 minutes for deployment
- Your app will be live at `https://your-app-name.streamlit.app`

---

## Usage

### Example Questions

Try asking:
- "What datasets exist for cardiovascular disease?"
- "Compare OpenSAFELY and CPRD access requirements."
- "What data is available for maternal health in Scotland?"
- "How do I access data through a Trusted Research Environment?"

### Features

**Sidebar Controls:**
- **API Key:** Enter your OpenAI API key (required)
- **Clear Chat:** Reset the conversation
- **Model Selection:** Choose between GPT-4o, GPT-4o-mini, or GPT-4-turbo
- **Temperature:** Adjust response creativity (0.0 = focused, 1.0 = creative)

---

## Configuration

### System Prompt
The assistant's behavior is defined in `system_prompt_v3_structured.txt`. Edit this file to customize the assistant's knowledge and tone.

### Streamlit Settings
Customize appearance and behavior in `.streamlit/config.toml`.

---

## Requirements

- Python 3.8+
- streamlit >= 1.0.0
- openai >= 1.0.0

See `requirements.txt` for full dependencies.

---

## Architecture

```
uk-health-data-assistant/
├── app.py                              # Main Streamlit application
├── system_prompt_v3_structured.txt     # AI assistant system prompt
├── requirements.txt                    # Python dependencies
├── .streamlit/
│   ├── config.toml                     # Streamlit configuration
│   └── secrets.toml.example            # Example secrets file
└── README.md                           # This file
```

---

## Privacy & Security

- **API Keys:** Stored only in browser session state (not persisted)
- **Conversations:** Stored in session only (cleared on refresh)
- **Data:** No user data is logged or stored on the server
- **OpenAI:** Conversations sent to OpenAI API (see [OpenAI Privacy Policy](https://openai.com/policies/privacy-policy))

---

## Contributing

Contributions welcome! Areas for improvement:
- Export conversation history
- Add dataset citations and links
- Integrate with HDR UK Gateway API
- Multi-language support
- Response feedback mechanism

---

## License

This is a prototype application for educational and research purposes.

---

## About

**Version:** 2.0
**Powered by:** OpenAI GPT-4o
**Built with:** Streamlit

This assistant helps researchers discover and access UK health datasets across the federated UK health data ecosystem, including:
- HDR UK (Health Data Research UK)
- NHS England
- CPRD (Clinical Practice Research Datalink)
- OpenSAFELY
- UK Biobank
- Research Data Scotland (SAIL)
- And many more...

---

## Disclaimer

This is a beta prototype. Responses are generated by AI and may not reflect the complete UK data landscape. Always verify access routes and dataset information with official data custodians.

---

## Support

Questions or issues? Open an issue on [GitHub](https://github.com/Seymo98/uk-health-data-assistant/issues).
