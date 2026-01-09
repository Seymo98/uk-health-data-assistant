# UK Health Data Assistant

> **Smarter discovery, for faster impact.**

A conversational AI assistant that helps researchers discover and access UK health datasets. Built with Streamlit and powered by OpenAI GPT-4o, with integrated HDR UK Gateway connectivity.

![UK Health Data Assistant](https://raw.githubusercontent.com/Seymo98/uk-health-data-assistant/main/650510F6-EB0C-4BFC-91DD-EBF8A8978931.png)

---

## AI Agent Integration

This section provides structured information for AI agents, LLMs, and automated tooling.

### Capabilities

| Capability | Description | API/Tool |
|------------|-------------|----------|
| Dataset Discovery | Find UK health datasets by topic, condition, or data type | Natural language query |
| Access Route Guidance | Understand TRE/SDE requirements and application processes | Conversational |
| Dataset Comparison | Compare data sources (CPRD vs OpenSAFELY, etc.) | Built-in comparison tables |
| HDR UK Gateway Search | Live search of the Health Data Gateway | `hdruk_gateway.GatewayClient` |
| Data Use Register Extraction | Extract SAIL Databank usage records | `extract_sail_data_use_register.py` |
| Interactive Dataset Explorer | Visual dataset search with facets and export | Streamlit page |
| CLI Dataset Search | Command-line dataset discovery | `python -m hdruk_gateway.cli` |
| Conversation Export | Export chat history as Markdown | Built-in UI |

### Supported Data Sources

```yaml
data_sources:
  national:
    - name: HDR UK Innovation Gateway
      url: https://www.healthdatagateway.org/
      type: discovery_portal
      coverage: UK-wide

    - name: NHS England
      url: https://www.england.nhs.uk/
      type: data_custodian
      coverage: England

    - name: CPRD
      url: https://cprd.com/
      type: primary_care
      coverage: ~60M patients (EMIS + Vision)
      access: fee-based

    - name: OpenSAFELY
      url: https://www.opensafely.org/
      type: in_situ_analysis
      coverage: ~60M patients (TPP only)
      access: code-repository
      primary_use: COVID-19 research

    - name: UK Biobank
      url: https://www.ukbiobank.ac.uk/
      type: cohort_study
      coverage: ~500,000 participants
      includes: [genomics, imaging, biomarkers]

  devolved_nations:
    - name: SAIL Databank
      url: https://saildatabank.com/
      region: Wales
      coverage: ~3.5M population
      type: trusted_research_environment

    - name: Research Data Scotland
      url: https://www.researchdata.scot/
      region: Scotland
      coverage: ~5.5M population
      type: safe_haven

  specialized:
    - name: Genomics England
      url: https://www.genomicsengland.co.uk/
      focus: [rare_diseases, cancer_genomics]

    - name: Our Future Health
      url: https://ourfuturehealth.org.uk/
      focus: disease_prevention

    - name: BHF Data Science Centre
      url: https://www.bhf.org.uk/what-we-do/our-research/bhf-data-science-centre
      focus: cardiovascular_research
```

### Natural Language Query Examples

AI agents can use these patterns to interact with the assistant:

```text
# Dataset Discovery
"What datasets exist for [condition]?"
"Where can I find data on [topic] in [region]?"
"What primary care data is available for [use case]?"

# Access Requirements
"How do I access data through [platform]?"
"What are the requirements for [TRE/SDE]?"
"Compare access routes for [dataset A] vs [dataset B]"

# Dataset Comparison
"Compare [CPRD] and [OpenSAFELY]"
"What's the difference between [SAIL] and [Research Data Scotland]?"
"Which dataset is best for [use case]?"

# Technical Queries
"Does [platform] support [data type]?"
"What linkages are available in [dataset]?"
"What geographic coverage does [source] provide?"
```

### API Integration

#### HDR UK Gateway Client (Full API)

```python
from hdruk_gateway import GatewayClient, DatasetSearcher

# Initialize client
client = GatewayClient()

# Search for datasets
datasets = client.search_datasets("diabetes")
for ds in datasets:
    print(f"{ds.title} - {ds.publisher_name}")
    print(f"  URL: {ds.gateway_url}")

# Get a specific dataset
dataset = client.get_dataset("dataset-id")

# Search data use register
data_uses = client.search_data_uses("cancer research")

# Advanced search with natural language parsing
searcher = DatasetSearcher()
result = searcher.search("cardiovascular data in Wales")
print(f"Found {result.total_count} results")

# Export results
csv_data = searcher.export_results_csv(result.results)
```

#### CLI Tool

```bash
# Search datasets
python -m hdruk_gateway.cli search "diabetes"

# Search with export
python -m hdruk_gateway.cli search "cancer in Wales" --export csv

# Interactive mode
python -m hdruk_gateway.cli interactive

# Get dataset details
python -m hdruk_gateway.cli dataset <dataset-id>

# Export data use register
python -m hdruk_gateway.cli export-dur --publisher SAIL
```

#### SAIL Data Use Register Extraction

```python
from extract_sail_data_use_register import HDRGatewayAPI, SAILDirectScraper

# Via HDR UK Gateway API
api = HDRGatewayAPI()
sail_records = api.get_sail_data_uses()

# Via direct scraping
scraper = SAILDirectScraper()
df = scraper.scrape(include_details=True)
```

### Programmatic Access Patterns

```python
# For AI agents building on this assistant
import streamlit as st
from openai import OpenAI

# Load the specialized system prompt
with open("system_prompt_v3_structured.txt", "r") as f:
    system_prompt = f.read()

# Create a UK health data specialist agent
client = OpenAI(api_key="...")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "What datasets are available for cardiovascular research?"}
    ]
)
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key ([get one here](https://platform.openai.com/account/api-keys))

### Installation

```bash
git clone https://github.com/Seymo98/uk-health-data-assistant.git
cd uk-health-data-assistant
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run app.py
```

Open `http://localhost:8501` and enter your OpenAI API key in the sidebar.

### Deploy to Streamlit Cloud

1. Fork this repository
2. Sign in at [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → Select your fork → Set main file to `app.py`
4. (Optional) Add `OPENAI_API_KEY` in Secrets for a default key
5. Deploy

---

## Architecture

```
uk-health-data-assistant/
├── app.py                              # Main Streamlit chat application
│
├── hdruk_gateway/                      # HDR UK Gateway API Client Library
│   ├── __init__.py                     # Package exports
│   ├── client.py                       # GatewayClient - full API integration
│   │   ├── search_datasets()           # Search datasets
│   │   ├── search_data_uses()          # Search data use register
│   │   ├── search_publications()       # Search publications
│   │   ├── get_dataset()               # Get single dataset
│   │   └── list_publishers()           # List data custodians
│   ├── models.py                       # Data models (Dataset, DataUseRegister, etc.)
│   ├── search.py                       # DatasetSearcher - advanced search
│   │   ├── parse_query()               # Natural language parsing
│   │   ├── search()                    # Enhanced search with facets
│   │   └── export_results_*()          # CSV/JSON export
│   ├── exceptions.py                   # Custom exceptions
│   └── cli.py                          # Command-line interface
│
├── pages/                              # Multi-page Streamlit app
│   └── 1_🔬_Dataset_Explorer.py        # Interactive dataset explorer
│
├── extract_sail_data_use_register.py   # SAIL data extraction tools
├── system_prompt_v3_structured.txt     # AI assistant knowledge base
├── requirements.txt                    # Python dependencies
│
├── ai-context.json                     # Machine-readable project metadata
├── llms.txt                            # AI agent discovery file
│
├── .streamlit/
│   ├── config.toml                     # Streamlit UI configuration
│   └── secrets.toml.example            # Example secrets file
│
└── scrape_sail_register.py             # Legacy SAIL scraper
```

### Data Flow

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│        UK Health Data Assistant      │
│  ┌─────────────────────────────────┐ │
│  │   System Prompt (Knowledge)      │ │
│  │   - UK health data landscape     │ │
│  │   - Access requirements          │ │
│  │   - Dataset characteristics      │ │
│  └─────────────────────────────────┘ │
│                 │                     │
│                 ▼                     │
│  ┌─────────────────────────────────┐ │
│  │         OpenAI GPT-4o            │ │
│  └─────────────────────────────────┘ │
│                 │                     │
│                 ▼                     │
│  ┌─────────────────────────────────┐ │
│  │    Response + Auto-linking       │ │
│  │    + Comparison Tables           │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────┐    ┌─────────────────┐
│ HDR UK Gateway  │    │  SAIL Databank  │
│   Search API    │    │   Data Register │
└─────────────────┘    └─────────────────┘
```

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| Conversational AI | Natural language queries about UK health datasets |
| Streaming Responses | Real-time response generation with typing indicator |
| Dataset Auto-linking | Automatic hyperlinks to official dataset pages |
| Comparison Tables | Side-by-side dataset comparisons (CPRD vs OpenSAFELY, etc.) |
| HDR UK Gateway Integration | Live search of the Health Data Gateway |
| Conversation Export | Download chat history as Markdown |
| Response Caching | Smart caching to reduce API calls |
| Usage Analytics | Track query patterns and topics |

### UI Controls

| Control | Location | Options |
|---------|----------|---------|
| API Key | Sidebar | Text input (password masked) |
| Model Selection | Sidebar | gpt-4o, gpt-4o-mini, gpt-4-turbo |
| Temperature | Sidebar | 0.0 (focused) to 1.0 (creative) |
| Clear Chat | Sidebar | Reset conversation |
| Export | Sidebar | Download as Markdown |
| Search | Sidebar | Filter conversation history |

---

## UK Health Data Landscape Reference

### Terminology

| Term | Also Known As | Context |
|------|--------------|---------|
| TRE | Trusted Research Environment | Secure data access platform |
| SDE | Secure Data Environment | Interchangeable with TRE |
| Safe Haven | Data Safe Haven | Scottish terminology |
| SPE | Secure Processing Environment | Digital Economy Act terminology |

### Key Organizations

| Organization | Role | URL |
|--------------|------|-----|
| HDR UK | National institute for health data science | hdruk.ac.uk |
| NHS England | Data custodian (merged with NHS Digital) | england.nhs.uk |
| ADR UK | Administrative data research | adruk.org |
| ONS | Official statistics | ons.gov.uk |
| CLOSER | Longitudinal studies | closer.ac.uk |

### Dataset Quick Reference

| Dataset | Coverage | Primary Use | Access Model |
|---------|----------|-------------|--------------|
| CPRD | 60M patients | Observational studies | Fee-based application |
| OpenSAFELY | 60M patients (TPP) | COVID-19 research | Code repository |
| UK Biobank | 500K participants | Population genomics | Application |
| SAIL | Wales (3.5M) | Welsh population studies | TRE |
| RDS | Scotland (5.5M) | Scottish population studies | Safe Haven |
| Genomics England | 100K+ genomes | Rare diseases, cancer | Application |

---

## Configuration

### System Prompt

The assistant's behavior is defined in `system_prompt_v3_structured.txt`. Key sections:

- **Role & Purpose**: Dataset discovery and access guidance
- **Tone**: Professional but accessible
- **Landscape Context**: Current UK health data ecosystem knowledge
- **Constraints**: What the assistant should not do

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No* | Default API key (users can override in UI) |

*Can be set in `.streamlit/secrets.toml` for deployed apps.

---

## Tools & Scripts

### SAIL Data Use Register Extractor

Extract approved research projects from SAIL Databank:

```bash
python extract_sail_data_use_register.py
```

**Output**: `sail_data_use_register.csv` with columns:
- `project_id`, `project_title`, `organisation_name`
- `lay_summary`, `public_benefit_statement`
- `datasets_used`, `access_type`, `approval_date`

---

## Privacy & Security

- **API Keys**: Stored in browser session only (not persisted)
- **Conversations**: In-memory only (cleared on refresh)
- **No Server Logging**: No user data stored on server
- **OpenAI Processing**: Queries sent to OpenAI API ([Privacy Policy](https://openai.com/policies/privacy-policy))

---

## Development

### Requirements

```
streamlit
openai>=1.0.0
requests
pandas
beautifulsoup4
lxml
```

### Testing

```bash
# Test API key configuration
python test_api_key.py

# Test SAIL extraction
python extract_sail_data_use_register.py
```

---

## Contributing

Areas for contribution:

- [ ] Additional dataset comparison tables
- [ ] Enhanced HDR UK Gateway API integration
- [ ] Multi-language support (Welsh, Gaelic)
- [ ] Citation export (BibTeX, RIS)
- [ ] Webhook notifications for new datasets
- [ ] MCP server implementation for AI agent integration

---

## Version History

| Version | Changes |
|---------|---------|
| 4.0 | Full HDR UK Gateway API client, Dataset Explorer UI, CLI tool |
| 3.1 | HDR UK Gateway integration, comparison tables |
| 3.0 | Advanced features: caching, feedback, search |
| 2.0 | Streamlit UI, conversation history |
| 1.0 | Initial prototype |

---

## License

Prototype for educational and research purposes.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Seymo98/uk-health-data-assistant/issues)
- **HDR UK**: [hdruk.ac.uk](https://www.hdruk.ac.uk/)
- **Gateway**: [healthdatagateway.org](https://www.healthdatagateway.org/)

---

## Disclaimer

This is a beta prototype. AI-generated responses may not reflect the complete UK health data landscape. Always verify dataset information and access routes with official data custodians.

---

<details>
<summary><strong>AI Agent Metadata (JSON-LD)</strong></summary>

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "UK Health Data Assistant",
  "description": "Conversational AI assistant for discovering and accessing UK health datasets",
  "applicationCategory": "HealthApplication",
  "operatingSystem": "Web, Python 3.8+",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "GBP"
  },
  "author": {
    "@type": "Organization",
    "name": "UK Health Data Assistant Contributors"
  },
  "softwareVersion": "3.1",
  "keywords": [
    "health data",
    "UK",
    "NHS",
    "HDR UK",
    "CPRD",
    "OpenSAFELY",
    "UK Biobank",
    "SAIL",
    "research data",
    "TRE",
    "trusted research environment"
  ],
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://www.healthdatagateway.org/search?search={query}",
    "query-input": "required name=query"
  },
  "hasPart": [
    {
      "@type": "Dataset",
      "name": "HDR UK Innovation Gateway",
      "url": "https://www.healthdatagateway.org/"
    },
    {
      "@type": "Dataset",
      "name": "CPRD",
      "url": "https://cprd.com/"
    },
    {
      "@type": "Dataset",
      "name": "OpenSAFELY",
      "url": "https://www.opensafely.org/"
    },
    {
      "@type": "Dataset",
      "name": "UK Biobank",
      "url": "https://www.ukbiobank.ac.uk/"
    },
    {
      "@type": "Dataset",
      "name": "SAIL Databank",
      "url": "https://saildatabank.com/"
    }
  ]
}
```

</details>
