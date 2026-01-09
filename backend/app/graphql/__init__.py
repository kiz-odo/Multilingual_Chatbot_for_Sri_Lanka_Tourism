"""
GraphQL Package
Complete GraphQL API for Sri Lanka Tourism Chatbot
"""

from backend.app.graphql.schema import schema
from backend.app.graphql.context import get_graphql_context

__all__ = ["schema", "get_graphql_context"]

