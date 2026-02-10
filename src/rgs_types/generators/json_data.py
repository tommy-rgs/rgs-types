from typing import Any, Optional

from hypothesis.strategies import SearchStrategy
from hypothesis_jsonschema import from_schema

from rgs_types.schema_models import JSONSchema


class JsonDataGenerator:
    """
    Generates Hypothesis strategies compliant with a given JSON Schema.
    """

    def __init__(self, root_schema: JSONSchema):
        self.root_schema = root_schema
        # Cache the root strategy to avoid re-parsing/dumping on every call
        self._root_schema_dict = self.root_schema.model_dump(
            exclude_none=True, by_alias=True
        )
        self._root_strategy = from_schema(self._root_schema_dict)

    @property
    def schema_dict(self) -> dict[str, Any]:
        """Returns the raw JSON Schema dictionary used for generation."""
        return self._root_schema_dict

    def get_strategy(self, schema: Optional[JSONSchema] = None) -> SearchStrategy:
        """
        Returns a hypothesis strategy for the given schema node.

        If schema is None or the root schema, returns the cached root strategy.
        Otherwise, creates a new strategy for the provided sub-schema.
        """
        if schema is None or schema is self.root_schema:
            return self._root_strategy

        # For sub-schemas, we must dump and create a new strategy
        schema_dict = schema.model_dump(exclude_none=True, by_alias=True)
        return from_schema(schema_dict)

    def generate_sample(self, schema: Optional[JSONSchema] = None) -> Any:
        """
        Generates a single instance of valid data.

        WARNING: Only use for debugging or one-off scripts.
        For testing, use @given(generator.get_strategy()) to enable shrinking.
        """
        return self.get_strategy(schema).example()
