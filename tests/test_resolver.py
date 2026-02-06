import pytest
from rgs_types.parser import parse_schema_file, parse_schema_string
from rgs_types.resolver import SchemaResolver
from rgs_types.schema_models import JSONSchema

def test_resolve_internal_def():
    schema_path = "test_cases/7_refs/schema.json"
    root = parse_schema_file(schema_path)
    resolver = SchemaResolver(root)
    
    # Resolve #/$defs/address
    address_schema = resolver.resolve("#/$defs/address")
    assert address_schema.type == "object"
    assert address_schema.properties is not None
    assert "street" in address_schema.properties

def test_resolve_recursive_ref():
    schema_path = "test_cases/7_refs/schema.json"
    root = parse_schema_file(schema_path)
    resolver = SchemaResolver(root)
    
    # Resolve #/$defs/recursiveNode
    node_schema = resolver.resolve("#/$defs/recursiveNode")
    assert node_schema.properties is not None
    assert "next" in node_schema.properties
    
    next_ref = node_schema.properties["next"].ref
    assert next_ref == "#/$defs/recursiveNode"
    
    # Resolve it again
    resolved_next = resolver.resolve(next_ref)
    assert resolved_next == node_schema

def test_resolve_root():
    json_str = '{"title": "Root", "type": "object"}'
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    assert resolver.resolve("#") == root

def test_resolve_invalid_ref():
    json_str = '{"title": "Root", "type": "object"}'
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    with pytest.raises(ValueError, match="Could not resolve part"):
        resolver.resolve("#/non_existent")

def test_resolve_property_ref():
    json_str = """
    {
      "type": "object",
      "properties": {
        "a": { "type": "string" },
        "b": { "$ref": "#/properties/a" }
      }
    }
    """
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    resolved = resolver.resolve("#/properties/a")
    assert resolved.type == "string"
    
    resolved_b = resolver.resolve(root.properties["b"].ref)
    assert resolved_b.type == "string"
    assert resolved_b == root.properties["a"]

def test_resolve_with_escapes():
    json_str = """
    {
      "type": "object",
      "properties": {
        "slash/prop": { "type": "integer" },
        "tilde~prop": { "type": "number" }
      }
    }
    """
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    # / -> ~1
    assert resolver.resolve("#/properties/slash~1prop").type == "integer"
    # ~ -> ~0
    assert resolver.resolve("#/properties/tilde~0prop").type == "number"

def test_resolve_list_index():
    json_str = """
    {
      "type": "object",
      "items": [
        { "type": "string" },
        { "type": "integer" }
      ]
    }
    """
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    assert resolver.resolve("#/items/0").type == "string"
    assert resolver.resolve("#/items/1").type == "integer"

def test_resolve_empty_key():
    json_str = """
    {
      "type": "object",
      "properties": {
        "": { "type": "boolean" }
      }
    }
    """
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    # #/properties/ refers to the property with empty string key
    assert resolver.resolve("#/properties/").type == "boolean"

def test_resolve_external_unsupported():
    json_str = '{"title": "Root", "type": "object"}'
    root = parse_schema_string(json_str)
    resolver = SchemaResolver(root)
    
    with pytest.raises(NotImplementedError):
        resolver.resolve("http://example.com/schema.json")
