from typer.testing import CliRunner
from rgs_types.main import app
import pytest

runner = CliRunner()

def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Generate cross-platform data types" in result.stdout

def test_generate_non_existent_file():
    result = runner.invoke(app, ["non_existent.json"])
    assert result.exit_code != 0
    # Typer should handle "exists=True" automatically
    assert "Path 'non_existent.json' does not exist" in result.stdout or "Error" in result.stdout

def test_generate_invalid_language():
    # Currently this passes because lang is just a string. 
    # We want this to fail later.
    with runner.isolated_filesystem():
        with open("schema.json", "w") as f:
            f.write("{}")
        result = runner.invoke(app, ["schema.json", "--lang", "unsupported"])
        # Expectation: Should fail due to Enum validation
        assert result.exit_code != 0
        assert "Invalid value for '--lang' / '-l'" in result.stdout or "Error" in result.stdout

def test_generate_invalid_json():
    with runner.isolated_filesystem():
        with open("invalid.json", "w") as f:
            f.write("{ invalid json }")
        result = runner.invoke(app, ["invalid.json"])
        assert result.exit_code != 0
        assert "JSON Parse Error" in result.stdout

def test_generate_invalid_schema_validation():
    # Pass a string where a number is expected
    with runner.isolated_filesystem():
        with open("bad_schema.json", "w") as f:
            f.write('{"minimum": "not_a_number"}')
        result = runner.invoke(app, ["bad_schema.json"])
        assert result.exit_code != 0
        assert "Schema Validation Error" in result.stdout 
