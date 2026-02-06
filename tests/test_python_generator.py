import pytest
from pathlib import Path
from typer.testing import CliRunner
from rgs_types.main import app
import importlib.util
import sys

runner = CliRunner()

def test_generate_python_simple():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "SimpleObject",
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "age": { "type": "integer" },
            "is_active": { "type": "boolean", "default": true }
          },
          "required": ["name", "age"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
        
        result = runner.invoke(app, ["schema.json", "--lang", "python", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/simpleobject.py")
        assert out_file.exists()
        
        content = out_file.read_text()
        print(f"DEBUG CONTENT:\n{content}")
        assert "class SimpleObject:" in content
        assert "name: str" in content
        assert "age: int" in content
        assert "is_active: Optional[bool] = True" in content

        # Try to import and use it
        spec = importlib.util.spec_from_file_location("simpleobject", out_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["simpleobject"] = module
        spec.loader.exec_module(module)
        
        obj = module.SimpleObject(name="Test", age=30)
        assert obj.name == "Test"
        assert obj.age == 30
        assert obj.is_active is True

def test_generate_python_enum():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "EnumObject",
          "type": "object",
          "properties": {
            "status": { 
                "type": "string",
                "enum": ["pending", "active", "completed"]
            }
          },
          "required": ["status"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "python", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/enumobject.py")
        assert out_file.exists()
        
        content = out_file.read_text()
        assert "class Status(Enum):" in content
        assert "PENDING = \"pending\"" in content
        assert "status: Status" in content

def test_generate_python_nested_and_refs():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "RootObject",
          "type": "object",
          "properties": {
            "info": {
                "type": "object",
                "properties": {
                    "version": { "type": "string" }
                },
                "required": ["version"]
            },
            "address": { "$ref": "#/$defs/address" }
          },
          "required": ["info", "address"],
          "$defs": {
            "address": {
                "title": "Address",
                "type": "object",
                "properties": {
                    "city": { "type": "string" }
                },
                "required": ["city"]
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "python", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/rootobject.py")
        content = out_file.read_text()
        print(f"DEBUG RootObject:\n{content}")
        
        # Should have 3 classes: Address, Info, RootObject
        assert "class Address:" in content
        assert "class Info:" in content
        assert "class RootObject:" in content
        
        # Check order (Address/Info before RootObject because it's a dependency)
        # Our reverse heuristic should put Address first if it was found via ref
        
        assert content.find("class Address") < content.find("class RootObject")
        assert content.find("class Info") < content.find("class RootObject")

def test_generate_python_arrays():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "ArrayObject",
          "type": "object",
          "properties": {
            "tags": {
              "type": "array",
              "items": { "type": "string" },
              "default": []
            },
            "points": {
              "type": "array",
              "items": {
                "type": "object",
                "title": "Point",
                "properties": {
                  "x": { "type": "number" },
                  "y": { "type": "number" }
                }
              }
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "python", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/arrayobject.py")
        content = out_file.read_text()
        
        assert "class Point:" in content
        assert "class ArrayObject:" in content
        assert "tags: Optional[List[str]] = field(default_factory=list)" in content or "tags: Optional[List[str]] = None" in content
        assert "points: Optional[List[Point]] = None" in content

def test_generate_python_docstrings():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "DocObject",
          "description": "This is a root description.",
          "type": "object",
          "properties": {
            "name": { 
                "type": "string",
                "description": "The name of the thing."
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "python", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/docobject.py")
        content = out_file.read_text()
        
        assert "This is a root description." in content
        # Note: Current implementation only puts description on class, not properties yet.
        # Let's check if we should add them to properties too.

def test_generate_python_namespace_and_conflicts():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "MainObject",
          "x-python-namespace": "rgs.messages",
          "type": "object",
          "properties": {
            "part1": {
                "title": "Conflict",
                "type": "object",
                "properties": { "a": { "type": "string" } }
            },
            "part2": {
                "title": "Conflict",
                "type": "object",
                "properties": { "b": { "type": "integer" } }
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "python", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/rgs/messages/mainobject.py")
        assert out_file.exists()
        assert Path("out/rgs/__init__.py").exists()
        assert Path("out/rgs/messages/__init__.py").exists()
        
        content = out_file.read_text()
        assert "class Conflict:" in content
        assert "class Conflict_1:" in content
        assert "part1: Optional[Conflict]" in content
        assert "part2: Optional[Conflict_1]" in content




