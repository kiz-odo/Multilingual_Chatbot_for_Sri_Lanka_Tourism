"""
Unit tests for the GraphQL schema (backend/app/graphql).

Builds the schema and runs an introspection query to verify the API surface
is well-formed. Skips cleanly in environments without strawberry installed.
"""

import pytest

pytest.importorskip("strawberry")

from backend.app.graphql.schema import schema  # noqa: E402


def test_schema_builds():
    assert schema is not None


def test_schema_prints_sdl():
    sdl = schema.as_str()
    assert "type Query" in sdl


def test_introspection_query_type():
    result = schema.execute_sync("{ __schema { queryType { name } } }")
    assert result.errors is None
    assert result.data["__schema"]["queryType"]["name"] == "Query"


def test_expected_types_present():
    result = schema.execute_sync("{ __schema { types { name } } }")
    assert result.errors is None
    names = {t["name"] for t in result.data["__schema"]["types"]}
    for expected in ["AttractionType", "HotelType", "RestaurantType", "UserType"]:
        assert expected in names


def test_query_has_fields():
    result = schema.execute_sync(
        "{ __type(name: \"Query\") { fields { name } } }"
    )
    assert result.errors is None
    fields = result.data["__type"]["fields"]
    assert isinstance(fields, list) and len(fields) > 0
