# RGS Types

Generating data types from JSON Schema. This allows for a single source of truth for a type definition and can give types that are defined within each of the specified languages that are supported. This allows for the enforcement of data types for modules and provides the interface for each of these nodes to communicate outwards into the world. 

## Documentation

* [Requirements](docs/Requirements.md)
* [Testing Methodologies](docs/Testing_Methodologies.md)

## Development Setup

This project uses modern Python tooling for dependency management and packaging.

### Prerequisites

* Python 3.10 or higher
* Poetry (https://python-poetry.org/)
* `nlohmann-json3-dev` (for C++ integration tests)
* `typescript` and `node` (for TypeScript integration tests)

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

To run the full suite of tests, including integration tests that compile and execute generated code, the following tools must be available in your environment:

* **Python**: `pytest` (via `poetry run`)
* **C++**: `clang++` or `g++` (C++17) and `nlohmann/json` headers.
    * If `nlohmann/json` is not in a standard include path, set the `JSON_INCLUDE_DIR` environment variable.
    * `export JSON_INCLUDE_DIR=/path/to/nlohmann/json/include`
* **TypeScript**: `tsc` (TypeScript compiler) and `node` (Node.js runtime).
    * `npm install -g typescript`

Standard test execution:
```bash
poetry run pytest
```

Parallel execution (using all available cores):
```bash
poetry run pytest -n auto
```

Running with a specific C++ include path:
```bash
poetry run pytest
```

Skip slow property-based and integration tests:
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

## Generated Code Features

### JSON Conversion

All generated models include helper methods for JSON serialization/deserialization:

* **C++**:
    * Uses `nlohmann/json`.
    * Provides `to_json(json& j, const T& obj)` and `from_json(const json& j, T& obj)` ADL-friendly functions.
* **Python**:
    * Dataclasses include `to_dict()` instance method and `from_dict(data)` class method.
* **TypeScript**:
    * Namespaces matching the interface name provide `fromJson(json)` and `toJson(obj)` helper functions.
