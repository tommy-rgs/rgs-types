# RGS Types

Generating data types from JSON Schema. This allows for a single source of truth for a type definition and can give types that are defined within each of the specified languages that are supported. This allows for the enforcement of data types for modules and provides the interface for each of these nodes to communicate outwards into the world. 


## Development Setup

This project uses modern Python tooling for dependency management and packaging.

### Prerequisites

* Python 3.10 or higher
* Poetry (https://python-poetry.org/)

### Setup
1. Set up poetry to install in local `.venv`
   ```bash
   poetry config virtualenvs.in-project true
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```

### Running Tests

Standard test execution:
```bash
poetry run pytest
```

Parallel execution (using all available cores):
```bash
poetry run pytest -n auto
```

Skip slow property-based tests:
```bash
poetry run pytest -m "not slow"
```

## Usage

The tool is available as a CLI command `rgs-gen`.

```bash
# Generate C++ code (default)
poetry run rgs-gen schema1.json schema2.json --output generated/cpp

# Generate Python code to specific directory
poetry run rgs-gen test_cases/**/*.json --lang python --output generated/python

# View help
poetry run rgs-gen --help
```

### Schema Extensions

RGS Types supports custom extensions to control generation:

* `x-cpp-namespace`: Sets the C++ namespace. Supports nested namespaces via `::` (e.g., `Rgs::Types`).
* `x-python-namespace`: Sets the Python package/module path (e.g., `rgs.messages`).
