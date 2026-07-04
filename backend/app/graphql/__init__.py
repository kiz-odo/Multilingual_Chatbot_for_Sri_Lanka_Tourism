"""
GraphQL Package
Complete GraphQL API for Sri Lanka Tourism Chatbot
"""

try:
	from backend.app.graphql.schema import schema
	from backend.app.graphql.context import get_graphql_context
except Exception:
	schema = None

	def get_graphql_context(*args, **kwargs):
		return None

__all__ = ["schema", "get_graphql_context"]

