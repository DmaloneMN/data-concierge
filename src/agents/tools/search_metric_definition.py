"""Tool: Search Metric Definition — searches metrics.csv for metric definitions."""

import csv
import os

from src.shared.logging import get_logger

logger = get_logger(__name__)

METRICS_PATH = os.getenv("METRICS_METADATA_PATH", "fabric/lakehouse/metadata/metrics.csv")


def search_metric_definition(query: str) -> list:
    logger.info("Searching metric definitions for: %s", query)

    if not os.path.exists(METRICS_PATH):
        raise FileNotFoundError(
            f"Metrics file not found at {METRICS_PATH}. Set METRICS_METADATA_PATH if needed."
        )

    query_lower = query.lower()
    results = []

    with open(METRICS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("metric_name") or "").lower()
            desc = (row.get("description") or "").lower()
            if query_lower in name or query_lower in desc:
                results.append(dict(row))

    logger.info("Found %d metric(s) matching '%s'", len(results), query)
    return results
