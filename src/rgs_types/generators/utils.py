import re

def pascal_case(s: str) -> str:
    """Converts a string to PascalCase."""
    # Split by non-alphanumeric characters or by transitions between lowercase and uppercase
    words = re.findall(r'[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z0-9]|\b)', s)
    if not words:
        return s.capitalize()
    return "".join(word.capitalize() for word in words)

def snake_case(s: str) -> str:
    """Converts a string to snake_case."""
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()
