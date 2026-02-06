from abc import ABC, abstractmethod
from pathlib import Path
from ..schema_models import JSONSchema
from ..resolver import SchemaResolver

class CodeGenerator(ABC):
    def __init__(self, schema: JSONSchema, output_dir: Path):
        self.schema = schema
        self.output_dir = output_dir
        self.resolver = SchemaResolver(schema)

    @abstractmethod
    def generate(self):
        """Perform the code generation."""
        pass
