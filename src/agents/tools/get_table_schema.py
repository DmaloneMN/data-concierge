"""Tool: Get Table Schema.

Reads table metadata from fabric/lakehouse/metadata/tables.csv for local dev.

Callers should format the returned dict with src.shared.utils.format_schema_context
before passing it to generate_sql for LLM context.
"""

import csv
import os

from src.shared.logging import get_logger

logger = get_logger(__name__)

METADATA_PATH = os.getenv("TABLES_METADATA_PATH", "fabric/lakehouse/metadata/tables.csv")


def get_table_schema(table_name: str) -> dict:
    """Return table metadata for the requested table name."""
    logger.info("Looking up schema for table: %s", table_name)

    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(
            f"Metadata file not found at {METADATA_PATH}. Set TABLES_METADATA_PATH if needed."
        )

    with open(METADATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("table_name") or "").lower() == table_name.lower():
                return dict(row)

    raise ValueError(f"Table '{table_name}' not found in {METADATA_PATH}")
