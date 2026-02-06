import pytest
from rgs_types.parser import parse_schema_file, parse_schema_string
from rgs_types.schema_models import JSONSchema

def test_parse_simple_schema_file():
    """Test parsing a real file from test_cases."""
    schema_path = "test_cases/1_simple/schema.json"
    schema = parse_schema_file(schema_path)
    
    assert isinstance(schema, JSONSchema)
    assert schema.title == "SimplePrimitives"
    assert schema.type == "object"
    assert "count" in schema.properties
    assert schema.properties["count"].type == "integer"

def test_parse_schema_string_mock():
    """Test parsing a raw JSON string (mock)."""
    json_str = """
    {
      "$id": "https://example.com/mock.json",
      "title": "MockObject",
      "type": "object",
      "properties": {
        "mockField": { "type": "string" }
      }
    }
    """
    schema = parse_schema_string(json_str)
    
    assert isinstance(schema, JSONSchema)
    assert schema.title == "MockObject"
    assert schema.properties["mockField"].type == "string"

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_schema_file("non_existent_file.json")
