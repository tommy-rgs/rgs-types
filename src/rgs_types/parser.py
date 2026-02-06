import json
from pathlib import Path
from typing import Union
from .schema_models import JSONSchema

def parse_schema_file(file_path: Union[str, Path]) -> JSONSchema:
    """Parses a JSON schema file into a JSONSchema model."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return JSONSchema(**data)

def parse_schema_string(schema_string: str) -> JSONSchema:
    """Parses a JSON schema string into a JSONSchema model."""
    data = json.loads(schema_string)
    return JSONSchema(**data)
