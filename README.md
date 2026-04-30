# Data Concierge – Azure AI Foundry + Fabric Agentic Platform

## Overview

Data Concierge is an enterprise-grade, agentic "data assistant" that helps users:
- Discover tables and metrics
- Generate SQL/dbt/pySpark code
- Validate queries against Microsoft Fabric
- File data requests/tickets with human-in-the-loop approval

It is built to demonstrate:
- AI-enabled, agentic workflows on **Azure AI Foundry**
- Integration with **Microsoft Fabric (F4)** as the unified data layer
- Production engineering practices (tests, CI/CD, logging, runbooks)
- Reusable assets (prompts, tools, evaluation harness, patterns)

This project is designed as an interview-ready artifact for senior AI engineering roles.

---

## High-Level Architecture

| Layer | Technology |
|---|---|
| Agent Orchestration | Azure AI Foundry |
| Data Layer | Microsoft Fabric (OneLake / SQL Endpoint) |
| Tool Implementations | Azure Functions |
| Backend API | FastAPI on Azure Container Apps |
| API Gateway | Azure API Management |
| Observability | Azure Monitor + Application Insights |
| Secrets | Azure Key Vault |

---

## What's in this Repo

```
data-concierge/
│
├── README.md                        # You are here
│
├── docs/                            # All project documentation
│   ├── architecture.md              # System design and component diagram
│   ├── prompts.md                   # Prompt design rationale
│   ├── runbook.md                   # Setup, deployment, and ops guide
│   ├── evaluation.md                # Evaluation methodology and metrics
│   └── api.md                       # API reference (chat + health endpoints)
│
├── infra/                           # Infrastructure as Code (Bicep)
│   ├── bicep/
│   │   ├── main.bicep               # Entry point – wires all modules
│   │   ├── ai_foundry.bicep         # Azure AI Foundry workspace
│   │   ├── container_apps.bicep     # Container Apps environment + app
│   │   ├── key_vault.bicep          # Key Vault + access policies
│   │   ├── api_management.bicep     # APIM instance + APIs
│   │   └── monitor.bicep            # Log Analytics + App Insights
│   ├── environments/
│   │   ├── dev.json                 # Dev environment parameters
│   │   ├── test.json                # Test environment parameters
│   │   └── prod.json                # Prod environment parameters
│   └── pipelines/
│       ├── github-actions-ci.yml    # CI – lint, test, build
│       └── github-actions-cd.yml    # CD – deploy Bicep + container image
│
├── src/
│   ├── api/                         # FastAPI application
│   │   ├── main.py                  # App entry point + router registration
│   │   ├── routers/
│   │   │   ├── chat.py              # POST /chat endpoint
│   │   │   └── health.py            # GET /health endpoint
│   │   ├── models/
│   │   │   ├── chat_request.py      # Pydantic request model
│   │   │   └── chat_response.py     # Pydantic response model
│   │   └── dependencies.py          # Shared FastAPI dependencies
│   │
│   ├── agents/                      # AI agent logic
│   │   ├── core_agent.py            # Main agent orchestration loop
│   │   ├── agent_config.py          # Agent configuration loader
│   │   ├── prompts/
│   │   │   ├── system/
│   │   │   │   └── core_agent_system.txt     # System prompt
│   │   │   ├── tools/
│   │   │   │   ├── sql_generator_prompt.txt  # SQL generation prompt
│   │   │   │   ├── validator_prompt.txt      # SQL validation prompt
│   │   │   │   └── metadata_prompt.txt       # Metadata search prompt
│   │   │   └── safety/
│   │   │       └── safety_policy.txt         # Safety guardrails
│   │   └── tools/                   # Agent tool wrappers (called by agent)
│   │       ├── tool_registry.py
│   │       ├── get_table_schema.py
│   │       ├── search_metric_definition.py
│   │       ├── generate_sql.py
│   │       ├── validate_sql.py
│   │       └── create_ticket.py
│   │
│   ├── tools/                       # Azure Function implementations
│   │   ├── get_table_schema/        # Returns schema for a given table
│   │   ├── search_metric_definition/ # Searches metrics catalogue
│   │   ├── generate_sql/            # LLM-based SQL generation
│   │   ├── validate_sql/            # LLM-based SQL validation
│   │   └── create_ticket/           # Creates a data request ticket
│   │
│   └── shared/                      # Shared utilities
│       ├── config.py                # Environment config loader
│       ├── logging.py               # Structured logging setup
│       └── utils.py                 # Helper functions
│
├── fabric/                          # Microsoft Fabric assets
│   ├── lakehouse/
│   │   ├── metadata/
│   │   │   ├── tables.csv           # Table catalogue
│   │   │   └── metrics.csv          # Metrics catalogue
│   │   └── sample_data/
│   │       └── sales/
│   │           └── sales_data.parquet
│   ├── notebooks/
│   │   ├── evaluation.ipynb         # Agent evaluation notebook
│   │   ├── monitoring.ipynb         # Monitoring dashboard notebook
│   │   └── lineage_extraction.ipynb # Data lineage extraction
│   └── pipelines/
│       ├── metadata_refresh.json    # Scheduled metadata refresh pipeline
│       └── sample_data_refresh.json # Scheduled sample data refresh
│
└── tests/
    ├── unit/
    │   ├── test_tools.py            # Unit tests for agent tools
    │   ├── test_agent.py            # Unit tests for core agent
    │   └── test_api.py              # Unit tests for FastAPI endpoints
    ├── integration/
    │   ├── test_end_to_end.py       # End-to-end integration tests
    │   └── test_sql_validation.py   # SQL validation integration tests
    └── prompts/
        ├── test_prompt_regressions.py  # Prompt regression tests
        └── golden_responses/
            └── sample_cases.json    # Golden response dataset
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Azure subscription
- Microsoft Fabric workspace with F4 capacity
- Azure AI Foundry project
- Azure CLI + Bicep CLI

### Local Setup

```bash
git clone <your-repo-url> data-concierge
cd data-concierge

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in your Azure credentials in .env
```

### Run the API Locally

```bash
uvicorn src.api.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Run Tests

```bash
pytest tests/unit/
pytest tests/integration/   # Requires Azure credentials
```

---

## Deployment

### 1. Infrastructure (Bicep)

```bash
# Login to Azure
az login
az account set --subscription <your-subscription-id>

# Create resource group
az group create --name rg-data-concierge-dev --location eastus

# Deploy all infrastructure
az deployment group create \
  --resource-group rg-data-concierge-dev \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/environments/dev.json
```

### 2. Build & Push Container Image

```bash
# Build the Docker image
docker build -t data-concierge-api .

# Tag and push to Azure Container Registry
az acr login --name <your-acr-name>
docker tag data-concierge-api <your-acr-name>.azurecr.io/data-concierge-api:latest
docker push <your-acr-name>.azurecr.io/data-concierge-api:latest
```

### 3. Deploy Azure Functions (Tool Implementations)

```bash
cd src/tools
func azure functionapp publish <your-function-app-name>
```

### 4. CI/CD (GitHub Actions)

The pipelines in `infra/pipelines/` automate the above:

| Pipeline | Trigger | What it does |
|---|---|---|
| `github-actions-ci.yml` | Push / PR to `main` or `dev` | Lint, test, build |
| `github-actions-cd.yml` | Push to `main` | Deploy Bicep + container image |

Set the following repository secrets:

| Secret | Description |
|---|---|
| `AZURE_CREDENTIALS` | Service principal JSON (`az ad sp create-for-rbac`) |
| `AZURE_RG` | Target resource group name |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `ACR_NAME` | Azure Container Registry name |

---

## Key Design Decisions

- **Azure AI Foundry** is used for agent orchestration rather than LangChain to stay on the Microsoft-native stack and align with enterprise customers.
- **Azure Functions** back each tool so they can be scaled, versioned, and secured independently.
- **Microsoft Fabric** provides a single governed data layer — metadata CSVs are used as a lightweight catalogue during development and replaced by the Fabric REST API in production.
- **Prompt files are stored as `.txt`** files (not hardcoded) so they can be iterated and evaluated independently of code.
- **Golden response dataset** (`tests/prompts/golden_responses/sample_cases.json`) enables prompt regression testing on every CI run.

---

## Documentation

| Doc | Description |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Full system architecture |
| [docs/api.md](docs/api.md) | API reference |
| [docs/prompts.md](docs/prompts.md) | Prompt design and rationale |
| [docs/runbook.md](docs/runbook.md) | Deployment and ops runbook |
| [docs/evaluation.md](docs/evaluation.md) | Evaluation methodology |

---

## Contributing

1. Branch from `dev`
2. Follow the existing code structure
3. Add or update tests for any changes
4. Open a PR — CI will run automatically
