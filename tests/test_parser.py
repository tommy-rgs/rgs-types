import pytest
from pathlib import Path
from rgs_types.parser import parse_schema_file, parse_schema_string
from rgs_types.schema_models import JSONSchema

# Get all schema.json files from test_cases
TEST_CASE_DIR = Path(__file__).parent.parent / "test_cases"
schema_files = list(TEST_CASE_DIR.glob("*/schema.json"))

@pytest.mark.parametrize("schema_path", schema_files, ids=lambda p: p.parent.name)
def test_parse_all_test_cases(schema_path):
    """Ensure all provided test cases parse correctly into the JSONSchema model."""
    schema = parse_schema_file(schema_path)
    assert isinstance(schema, JSONSchema)
    assert schema.title is not None

def test_parse_simple_schema_file():
# ... (rest of the file)
    """Test parsing a real file from test_cases."""
    schema_path = "test_cases/1_simple/schema.json"
    schema = parse_schema_file(schema_path)
    
    assert isinstance(schema, JSONSchema)
    assert schema.title == "SimplePrimitives"
    assert schema.type == "object"
    assert schema.properties is not None
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
    assert schema.properties is not None
    assert schema.properties["mockField"].type == "string"

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_schema_file("non_existent_file.json")
