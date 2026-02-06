from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class JSONSchema(BaseModel):
    schema_uri: Optional[str] = Field(None, alias="$schema")
    id: Optional[str] = Field(None, alias="$id")
    cpp_namespace: Optional[str] = Field(None, alias="x-cpp-namespace")
    python_namespace: Optional[str] = Field(None, alias="x-python-namespace")
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    properties: Optional[Dict[str, 'JSONSchema']] = None
    required: Optional[List[str]] = None
    items: Optional[Union['JSONSchema', List['JSONSchema']]] = None
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
    ref: Optional[str] = Field(None, alias="$ref")
    defs: Optional[Dict[str, 'JSONSchema']] = Field(None, alias="$defs")
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None
    # Validation
    minimum: Optional[Union[int, float]] = None
    exclusiveMinimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    exclusiveMaximum: Optional[Union[int, float]] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    pattern: Optional[str] = None
    minItems: Optional[int] = None
    maxItems: Optional[int] = None

    model_config = {
        "populate_by_name": True
    }

# Update forward refs for recursive definitions
JSONSchema.model_rebuild()
