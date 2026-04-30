# Data Concierge

An AI-powered data concierge service built on Azure AI Foundry, Azure Container Apps, and Microsoft Fabric.

## Overview
Data Concierge is an intelligent agent that helps users query and understand business data through natural language. It translates user questions into SQL, validates them, and returns results backed by a governed data lakehouse.

## Project Structure
- `docs/` – Architecture, API, prompt, and runbook documentation
- `infra/` – Bicep IaC, environment configs, and CI/CD pipelines
- `src/` – FastAPI application, AI agent, tools, and shared utilities
- `fabric/` – Lakehouse metadata, sample data, notebooks, and pipelines
- `tests/` – Unit, integration, and prompt regression tests

## Getting Started
See [docs/runbook.md](docs/runbook.md) for setup and deployment instructions.
