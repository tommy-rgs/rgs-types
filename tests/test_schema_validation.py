import pytest
from rgs_types.parser import parse_schema_string
from rgs_types.schema_models import JSONSchema

def test_parse_documentation_fields():
    json_str = """
    {
        "title": "TestTitle",
        "description": "TestDescription",
        "type": "string"
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.title == "TestTitle"
    assert schema.description == "TestDescription"

def test_parse_default_value():
    json_str = """
    {
        "type": "integer",
        "default": 42
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.default == 42

def test_parse_read_write_only():
    json_str = """
    {
        "type": "object",
        "properties": {
            "ro": { "type": "string", "readOnly": true },
            "wo": { "type": "string", "writeOnly": true }
        }
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.properties["ro"].readOnly is True
    assert schema.properties["wo"].writeOnly is True

def test_parse_numeric_validation():
    json_str = """
    {
        "type": "number",
        "minimum": 0.5,
        "maximum": 10.0,
        "exclusiveMinimum": 0.1,
        "exclusiveMaximum": 11.0
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.minimum == 0.5
    assert schema.maximum == 10.0
    assert schema.exclusiveMinimum == 0.1
    assert schema.exclusiveMaximum == 11.0

def test_parse_string_validation():
    json_str = """
    {
        "type": "string",
        "minLength": 3,
        "maxLength": 10,
        "pattern": "^[a-z]+$"
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.minLength == 3
    assert schema.maxLength == 10
    assert schema.pattern == "^[a-z]+$"

def test_parse_array_validation():
    json_str = """
    {
        "type": "array",
        "minItems": 1,
        "maxItems": 5,
        "items": { "type": "string" }
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.minItems == 1
    assert schema.maxItems == 5
    assert schema.items.type == "string"

def test_parse_enum():
    json_str = """
    {
        "type": "string",
        "enum": ["a", "b", "c"]
    }
    """
    schema = parse_schema_string(json_str)
    assert schema.enum == ["a", "b", "c"]
