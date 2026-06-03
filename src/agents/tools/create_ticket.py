"""Tool: Create Ticket — creates a work item in Azure DevOps if configured, otherwise stubs.

Environment variables (all optional — stub used if not set):
  ADO_ORG_URL   e.g. https://dev.azure.com/your-org
  ADO_PROJECT   e.g. DataConcierge
  ADO_PAT       Personal Access Token with Work Items (Read & Write) scope
"""

import base64
import os
import uuid

import httpx

from src.shared.logging import get_logger

logger = get_logger(__name__)

ADO_ORG_URL = os.getenv("ADO_ORG_URL", "")
ADO_PROJECT = os.getenv("ADO_PROJECT", "")
ADO_PAT = os.getenv("ADO_PAT", "")


def _create_ado_ticket(title: str, description: str) -> dict:
    """Create a Bug work item in Azure DevOps."""
    token = base64.b64encode(f":{ADO_PAT}".encode()).decode()
    url = f"{ADO_ORG_URL}/{ADO_PROJECT}/_apis/wit/workitems/$Bug?api-version=7.1"
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json-patch+json",
    }
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description},
        {"op": "add", "path": "/fields/System.Tags", "value": "data-concierge"},
    ]

    response = httpx.patch(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    ticket_id = str(data.get("id", "unknown"))
    ticket_url = data.get("_links", {}).get("html", {}).get("href", "")
    logger.info("ADO ticket created: %s — %s", ticket_id, ticket_url)
    return {
        "ticket_id": ticket_id,
        "status": "created",
        "title": title,
        "url": ticket_url,
        "source": "azure_devops",
    }


def _create_stub_ticket(title: str, description: str) -> dict:
    ticket_id = f"STUB-{uuid.uuid4().hex[:8].upper()}"
    logger.info("CREATE TICKET (stub) | id=%s | title=%s", ticket_id, title)
    return {
        "ticket_id": ticket_id,
        "status": "created",
        "title": title,
        "note": "Ticket creation is stubbed. Set ADO_ORG_URL, ADO_PROJECT, ADO_PAT to enable Azure DevOps integration.",
        "source": "stub",
    }


def create_ticket(title: str, description: str) -> dict:
    if ADO_ORG_URL and ADO_PROJECT and ADO_PAT:
        logger.info("Creating ADO ticket: %s", title)
        return _create_ado_ticket(title, description)
    return _create_stub_ticket(title, description)
