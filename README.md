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

## High-level architecture

- **Azure AI Foundry** – agent orchestration, tools, prompts, evaluation
- **Microsoft Fabric** – OneLake/Lakehouse, SQL Endpoint, notebooks, pipelines
- **Azure Functions** – tool implementations (schema, metrics, SQL generation/validation, ticketing)
- **FastAPI** on **Azure Container Apps** – backend API
- **Azure API Management** – secure front door
- **Azure Monitor / App Insights** – logging, metrics, traces
- **Azure Key Vault** – secrets and configuration

## Getting started

### Prerequisites

- Python 3.10+
- Azure subscription
- Microsoft Fabric workspace with F4 capacity
- Azure AI Foundry project
- Node.js (optional, if you add a UI)

### Setup

```bash
git clone <your-repo-url> data-concierge
cd data-concierge

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```