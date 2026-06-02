"""Tool registry — all available tools for the Data Concierge agent."""

from src.agents.tools.create_ticket import create_ticket
from src.agents.tools.execute_sql import execute_sql
from src.agents.tools.generate_sql import generate_sql
from src.agents.tools.get_table_schema import get_table_schema
from src.agents.tools.search_metric_definition import search_metric_definition
from src.agents.tools.validate_sql import validate_sql

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_table_schema",
            "description": "Look up metadata for a table by name. Returns table description, schema, and primary key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "The exact table name to look up.",
                    }
                },
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_metric_definition",
            "description": "Search for business metric definitions by name or description. Returns matching metrics with their formula and source table.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword to search metric names and descriptions.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_sql",
            "description": "Generate a T-SQL query given a user question and table schema context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The user's data question.",
                    },
                    "schema_context": {
                        "type": "string",
                        "description": "Schema metadata for relevant tables, formatted as a string.",
                    },
                },
                "required": ["question", "schema_context"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_sql",
            "description": "Validate a SQL query for correctness, safety, and alignment with user intent before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to validate.",
                    },
                    "user_intent": {
                        "type": "string",
                        "description": "The original user question or intent.",
                    },
                },
                "required": ["sql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute a validated SQL query against the Microsoft Fabric SQL Analytics Endpoint and return results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "The SQL query to execute."}
                },
                "required": ["sql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support or data quality ticket when an issue is identified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title for the ticket.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue.",
                    },
                },
                "required": ["title", "description"],
            },
        },
    },
]

TOOL_CALLABLES = {
    "get_table_schema": get_table_schema,
    "search_metric_definition": search_metric_definition,
    "generate_sql": generate_sql,
    "validate_sql": validate_sql,
    "execute_sql": execute_sql,
    "create_ticket": create_ticket,
}
