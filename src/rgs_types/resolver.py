from typing import Any, Union, Optional
from .schema_models import JSONSchema

class SchemaResolver:
    """
    A resolver for JSON Schema $ref tags.
    Currently supports internal references (starting with #) using JSON Pointer (RFC 6901).
    """
    def __init__(self, root_schema: JSONSchema):
        self.root = root_schema

    def _decode_pointer(self, part: str) -> str:
        """Decodes JSON Pointer escape sequences ~0 and ~1."""
        return part.replace("~1", "/").replace("~0", "~")

    def resolve(self, ref: str) -> JSONSchema:
        """
        Resolves a $ref string to a JSONSchema object.
        
        Args:
            ref: The $ref string (e.g., "#/$defs/myType").
            
        Returns:
            The resolved JSONSchema object.
            
        Raises:
            ValueError: If the reference is invalid or cannot be resolved.
            NotImplementedError: If the reference is external (not starting with #).
        """
        if not ref:
            raise ValueError("Empty reference")

        if not ref.startswith("#"):
            # Future: handle file paths or URLs
            raise NotImplementedError(f"External references are not supported yet: {ref}")

        if ref == "#":
            return self.root

        # Split and skip the '#' part
        parts = ref.split("/")[1:]
        
        current: Any = self.root
        for part in parts:
            if not part and part != "0": # "" can be a valid key, but usually it's trailing slash
                # Handle trailing slash or ## cases if necessary, 
                # but RFC 6901 says "" is a valid key.
                # However, in our context we likely want to ignore it if it's the only thing.
                if part == "" and current == self.root and len(parts) == 1:
                    return self.root
                # If part is empty, it means we have something like /properties//foo which is valid
                # if there is a property named "".
                pass

            decoded_part = self._decode_pointer(part)
            
            # Handle both $defs and defs (JSON Schema drafts vary)
            if decoded_part in ("$defs", "defs"):
                if hasattr(current, "defs") and current.defs is not None:
                    current = current.defs
                elif isinstance(current, dict) and decoded_part in current:
                    current = current[decoded_part]
                else:
                    raise ValueError(f"No definitions found while resolving {ref} at {decoded_part}")
            elif isinstance(current, dict):
                if decoded_part in current:
                    current = current[decoded_part]
                else:
                    raise ValueError(f"Part '{decoded_part}' not found in dictionary while resolving {ref}")
            elif isinstance(current, list):
                try:
                    idx = int(decoded_part)
                    current = current[idx]
                except (ValueError, IndexError):
                    raise ValueError(f"Invalid index '{decoded_part}' for list while resolving {ref}")
            elif hasattr(current, decoded_part):
                current = getattr(current, decoded_part)
                if current is None:
                    # It might be None because it's an optional field not set
                    raise ValueError(f"Part '{decoded_part}' is None while resolving {ref}")
            else:
                raise ValueError(f"Could not resolve part '{decoded_part}' in reference '{ref}'")

        if not isinstance(current, JSONSchema):
            # Fallback: if we reached a dict that should have been a JSONSchema, 
            # pydantic might not have converted it if it was in a generic Dict[str, Any].
            # But our model uses Dict[str, 'JSONSchema'] so it should be fine.
            if isinstance(current, dict):
                return JSONSchema(**current)
            raise ValueError(f"Resolved object is not a JSONSchema instance: {type(current)}")
            
        return current