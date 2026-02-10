# Testing Methodologies

This document outlines the testing strategies employed in `rgs-types` to ensure the reliability and correctness of code generation across multiple languages.

## Overview

The project uses a multi-layered testing approach:
1.  **Unit Tests**: Validate individual components (parsers, resolvers, generators).
2.  **Property-Based Testing (PBT)**: Uses `hypothesis-jsonschema` to generate fuzz data for schema validation.
3.  **Integration Tests**: Validates the end-to-end flow: Schema -> Code Generation -> Compilation/Execution -> Data Parsing.

## Current Test Coverage

### 1. Unit Tests (`tests/`)
*   `test_parser.py`: Validates parsing of JSON Schema files into internal Pydantic models.
*   `test_resolver.py`: Tests the `$ref` resolution logic (local references).
*   `test_schema_validation.py`: Checks correct parsing of validation constraints (min/max, regex, etc.).
*   `test_python_generator.py`: Verifies Python code generation syntax and structure.
*   `test_cpp_generator.py`: Verifies C++ header generation syntax and structure.
*   `test_typescript_generator.py`: Verifies TypeScript interface generation.

### 2. Property-Based Testing
*   **Tool**: `hypothesis-jsonschema` + `hypothesis`.
*   **Strategy**: We leverage Hypothesis `SearchStrategy` objects derived directly from JSON Schemas.
*   **Optimization**: 
    *   **Cached Strategies**: The `JsonDataGenerator` caches strategies to avoid expensive Pydantic model dumps during high-frequency sampling.
    *   **Shrinking**: We use `@given(data=st.data())` to draw from strategies, enabling Hypothesis's powerful shrinking capabilities to find minimal failing cases.
*   **Health Checks**:
    *   **`function_scoped_fixture`**: We suppress this check in integration tests because we use `tmp_path` to house generated and compiled artifacts. While Hypothesis warns that function-scoped fixtures are not reset between generated inputs, this is exactly what we want for integration: we generate and compile the code *once* per test function (which runs once for all Hypothesis examples), and then Hypothesis draws multiple data samples to run through that *same* compiled artifact.
    *   **Future Workaround**: To avoid suppression, we could migrate to `tmp_path_factory` with `module` or `session` scope, but this requires mapping of schema paths to unique temporary directories outside of standard pytest parametrization.

### 3. Integration Testing
*   **File**: `tests/test_integration.py`.
*   **Environment Requirements**:
    *   **Python**: Python 3.10+ with `poetry` installed.
    *   **C++**: 
        *   `clang++` or `g++` (supporting C++17).
        *   `nlohmann/json` library (header-only). The test runner looks in `/usr/include`, `/usr/local/include`, or a path provided via the `JSON_INCLUDE_DIR` environment variable.
    *   **TypeScript**:
        *   `tsc` (TypeScript Compiler) must be in the `PATH`.
        *   `node` (Node.js) must be in the `PATH` for runtime validation.
*   **Strategy**:
    *   Iterates through all schemas in `test_cases/`.
    *   **Compile Once, Run Many**: For each schema, the generator produces source code and (for C++/TS) compiles it exactly once. 
    *   **Data Validation Loop**: After compilation, Hypothesis draws multiple samples (`max_examples`) and executes them against the same compiled binary or imported module. This drastically reduces test execution time by avoiding redundant compilation.
    *   **Python**: Imports generated modules, instantiates classes, and performs round-trip `to_dict`/`from_dict` validation.
    *   **C++**: Compiles a test harness that parses JSON via `nlohmann::json` and verifies runtime consistency.
    *   **TypeScript**: Compiles generated interfaces and validates serialization logic.

## Validation Strategy

To ensure that the generated types correctly model the data, we perform the following validation loop:

1.  **Schema Definition**: A JSON Schema defines the type.
2.  **Data Generation**: `JsonDataGenerator` produces a random valid JSON instance `D` based on the schema using Hypothesis.
3.  **Code Generation**: The generator produces source code for the target language (e.g., Python class `T`).
4.  **Round-Trip Verification**:
    *   Parse `D` into an instance `t` of type `T`.
    *   Serialize `t` back to JSON `D'`.
    *   Assert `D` is logically equivalent to `D'`.

## Missing Tests / Future Work

*   **Recursive Data Generation**: `hypothesis-jsonschema` has limited support for recursive references. We currently skip deep recursion tests or need manual test vectors.
*   **Negative Testing**: Ensure that *invalid* JSON data correctly fails parsing/validation in the generated code.
*   **Cross-Language Consistency**: Verify that data serialized in Python can be parsed in C++ and vice versa (Interoperability).