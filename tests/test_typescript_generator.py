import pytest
from pathlib import Path
from typer.testing import CliRunner
from rgs_types.main import app

runner = CliRunner()

def test_generate_typescript_simple():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "SimpleObject",
          "type": "object",
          "properties": {
            "isAvailable": { "type": "boolean" },
            "count": { "type": "integer" },
            "name": { "type": "string" }
          },
          "required": ["count", "name"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
        
        result = runner.invoke(app, ["schema.json", "--lang", "typescript", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/simpleobject.ts")
        content = out_file.read_text()
        assert "export class SimpleObject {" in content
        assert "isAvailable?: boolean;" in content
        assert "count!: number;" in content
        assert "name!: string;" in content

def test_generate_typescript_enum():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "EnumObject",
          "type": "object",
          "properties": {
            "status": { 
                "type": "string",
                "enum": ["pending", "active"]
            }
          },
          "required": ["status"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "typescript", "--output", "out"])
        assert result.exit_code == 0
        
        content = Path("out/enumobject.ts").read_text()
        assert "export enum Status {" in content
        assert "PENDING = \"pending\"," in content
        assert "ACTIVE = \"active\"," in content
        assert "status!: Status;" in content

def test_generate_typescript_nested():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "Parent",
          "type": "object",
          "properties": {
            "child": {
                "title": "Child",
                "type": "object",
                "properties": { "val": { "type": "number" } }
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "typescript", "--output", "out"])
        assert result.exit_code == 0
        
        content = Path("out/parent.ts").read_text()
        assert "export class Child {" in content
        assert "export class Parent {" in content
        assert "child?: Child;" in content

def test_generate_typescript_to_from_json():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "JsonTest",
          "type": "object",
          "properties": {
            "val": { "type": "integer" }
          },
          "required": ["val"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "typescript", "--output", "out"])
        assert result.exit_code == 0
        
        content = Path("out/jsontest.ts").read_text()
        assert "export class JsonTest {" in content
        assert "static fromJson(json: string | object): JsonTest" in content
        assert "static toJson(obj: JsonTest): string" in content
        assert "return JSON.stringify(obj);" in content
