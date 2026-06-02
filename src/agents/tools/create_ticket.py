"""Tool: Create Ticket — stub implementation (logs intent, returns mock ticket ID).

TODO: Integrate with ServiceNow or Azure DevOps REST API using config credentials.
"""

import uuid

from src.shared.logging import get_logger

logger = get_logger(__name__)


def create_ticket(title: str, description: str) -> dict:
    ticket_id = f"STUB-{uuid.uuid4().hex[:8].upper()}"
    logger.info("CREATE TICKET (stub) | id=%s | title=%s", ticket_id, title)
    return {
        "ticket_id": ticket_id,
        "status": "created",
        "title": title,
        "note": "Ticket creation is stubbed. Integrate with your ticketing system.",
    }
