import pytest
from pathlib import Path
from typer.testing import CliRunner
from rgs_types.main import app

runner = CliRunner()

def test_generate_cpp_simple():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "SimpleObject",
          "type": "object",
          "properties": {
            "isAvailable": { "type": "boolean" },
            "itemCount": { "type": "integer" },
            "priceValue": { "type": "number", "default": 1.0 },
            "itemName": { "type": "string" }
          },
          "required": ["isAvailable", "itemCount", "itemName"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
        
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        if result.exit_code != 0:
            print(result.stdout)
        assert result.exit_code == 0
        
        out_file = Path("out/simpleobject.hpp")
        assert out_file.exists()
        
        content = out_file.read_text()
        assert content.count("{") == content.count("}")
        assert "struct SimpleObject {" in content
        assert "bool is_available" in content
        assert "int64_t item_count" in content
        assert "std::optional<double> price_value = 1.0" in content
        assert "std::string item_name" in content

def test_generate_cpp_enum():
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
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        if result.exit_code != 0:
            print(result.stdout)
        assert result.exit_code == 0
        
        out_file = Path("out/enumobject.hpp")
        assert out_file.exists()
        
        content = out_file.read_text()
        assert content.count("{") == content.count("}")
        assert "enum class Status {" in content
        assert "PENDING," in content
        assert "ACTIVE," in content
        assert "COMPLETED," in content
        assert "Status status" in content

def test_generate_cpp_nested():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "RootObject",
          "type": "object",
          "properties": {
            "child": {
                "type": "object",
                "title": "ChildObject",
                "properties": {
                    "val": { "type": "integer" }
                }
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        if result.exit_code != 0:
            print(result.stdout)
        assert result.exit_code == 0
        
        out_file = Path("out/rootobject.hpp")
        content = out_file.read_text()
        assert content.count("{") == content.count("}")
        assert "struct ChildObject {" in content
        assert "struct RootObject {" in content
        assert "std::optional<ChildObject> child" in content

def test_generate_cpp_arrays_and_namespace():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "$id": "https://rogorous.co/types/my_messages.schema.json",
          "title": "ArrayMessage",
          "type": "object",
          "properties": {
            "tags": {
              "type": "array",
              "items": { "type": "string" }
            },
            "scores": {
              "type": "array",
              "items": { "type": "integer" }
            }
          },
          "required": ["tags"]
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/arraymessage.hpp")
        content = out_file.read_text()
        
        assert content.count("{") == content.count("}")
        assert "namespace my_messages {" in content
        assert "std::vector<std::string> tags;" in content
        assert "std::optional<std::vector<int64_t>> scores;" in content

def test_generate_cpp_refs():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "RefObject",
          "type": "object",
          "properties": {
            "main_address": { "$ref": "#/$defs/address" }
          },
          "required": ["main_address"],
          "$defs": {
            "address": {
                "title": "Address",
                "type": "object",
                "properties": {
                    "street": { "type": "string" }
                }
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/refobject.hpp")
        content = out_file.read_text()
        
        assert content.count("{") == content.count("}")
        assert "struct Address {" in content
        assert "struct RefObject {" in content
        assert "Address main_address;" in content

def test_generate_cpp_documentation():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "DocObject",
          "description": "A very useful object.",
          "type": "object",
          "properties": {
            "speed": {
                "type": "number",
                "description": "Speed in m/s"
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/docobject.hpp")
        content = out_file.read_text()
        
        assert content.count("{") == content.count("}")
        assert "A very useful object." in content
        assert "Speed in m/s" in content

def test_generate_cpp_custom_namespace():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "MyType",
          "type": "object",
          "x-cpp-namespace": "Rgs::Types::Common",
          "properties": {
            "id": { "type": "integer" }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/mytype.hpp")
        content = out_file.read_text()
        
        assert content.count("{") == content.count("}")
        assert "namespace Rgs {" in content
        assert "namespace Types {" in content
        assert "namespace Common {" in content
        assert "} // namespace Common" in content
        assert "} // namespace Types" in content
        assert "} // namespace Rgs" in content

def test_generate_cpp_naming_conflicts():
    with runner.isolated_filesystem():
        schema_content = """
        {
          "title": "ConflictObject",
          "type": "object",
          "properties": {
            "part1": {
                "title": "SharedName",
                "type": "object",
                "properties": { "a": { "type": "string" } }
            },
            "part2": {
                "title": "SharedName",
                "type": "object",
                "properties": { "b": { "type": "integer" } }
            }
          }
        }
        """
        with open("schema.json", "w") as f:
            f.write(schema_content)
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        assert result.exit_code == 0
        
        out_file = Path("out/conflictobject.hpp")
        content = out_file.read_text()
        assert "struct SharedName {" in content
        assert "struct SharedName_1 {" in content

def test_generate_cpp_to_from_json():
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
            
        result = runner.invoke(app, ["schema.json", "--lang", "cpp", "--output", "out"])
        assert result.exit_code == 0
        
        content = Path("out/jsontest.hpp").read_text()
        assert "#include <nlohmann/json.hpp>" in content
        assert "friend void to_json(nlohmann::json& j, const JsonTest& p)" in content
        assert "j = nlohmann::json{" in content
        assert "friend void from_json(const nlohmann::json& j, JsonTest& p)" in content
        assert "j.at(\"val\").get_to(p.val);" in content