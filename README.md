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
3. Activate the shell:
   ```bash
   eval $(poetry env activate)
   ```

### Running Tests

```bash
pytest
```

## Usage

The tool is available as a CLI command `rgs-gen` (or `poetry run rgs-gen` inside the project).

```bash
# Generate C++ code (default)
poetry run rgs-gen test_cases/1_simple/schema.json

# Generate Python code to specific directory
poetry run rgs-gen test_cases/1_simple/schema.json --lang python --output generated/python

# View help
poetry run rgs-gen --help
```