"""Tool registry — minimal set for local runnable MVP."""

from src.agents.tools.generate_sql import generate_sql
from src.agents.tools.get_table_schema import get_table_schema

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_table_schema",
            "description": "Look up metadata for a table by name.",
            "parameters": {
                "type": "object",
                "properties": {"table_name": {"type": "string"}},
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_sql",
            "description": "Generate a SQL query given question and schema context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "schema_context": {"type": "string"},
                },
                "required": ["question", "schema_context"],
            },
        },
    },
]

TOOL_CALLABLES = {
    "get_table_schema": get_table_schema,
    "generate_sql": generate_sql,
}
