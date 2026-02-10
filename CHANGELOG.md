# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.4] - 2026-02-10

### Added
- **New Test Cases**:
    - `9_namespacing`: Validates complex cross-platform namespace requirements.
    - `10_complex_arrays`: Tests nested arrays and shared references.
    - `11_evolution`: Verifies backwards compatibility and schema evolution.

## [0.4.3] - 2026-02-10

### Added
- **Full TypeScript Class-Based Generation**:
    - Replaced TypeScript interfaces with full `class` definitions.
    - Added support for default values in TypeScript classes.
    - Included a `constructor` with `Partial<T>` initialization.
    - Added static `fromJson`/`toJson` methods for easier runtime conversion.
- **Integration Testing Enhancements**:
    - **"Compile Once, Run Many" Strategy**: Optimized tests to perform generation and compilation only once per schema while running multiple Hypothesis data samples.
    - **Runtime Execution**: Integration tests now execute compiled C++ binaries and TypeScript modules (via Node.js) to verify actual JSON parsing behavior.
    - **Strict Requirements**: Integration tests now fail explicitly (rather than skip) if compilers (`clang++`, `tsc`) or critical headers (`nlohmann/json`) are missing, ensuring high-fidelity local validation.
- **Improved Testing Documentation**:
    - Created `docs/Testing_Methodologies.md` to detail unit, property-based, and integration testing strategies.
    - Documented the use of `HealthCheck.function_scoped_fixture` in Hypothesis tests and potential future workarounds.
    - Updated `README.md` with explicit tool requirements and setup instructions for running the full test suite.

## [0.4.2] - 2026-02-10

### Added
- **JSON Serialization Support**:
    - **C++**: Added `to_json`/`from_json` bindings for `nlohmann/json` integration.
    - **Python**: Added `to_dict`/`from_dict` methods for dataclasses.
    - **TypeScript**: Added `fromJson`/`toJson` helper namespaces for interfaces.
- **Integration Testing**: Added `tests/test_integration.py` to verify generated code across target languages.

### Fixed
- **Recursion Support**: Resolved `RecursionError` in all generators when handling circular structures using a reference mapping cache.
- **Python Forward References**: Added `from __future__ import annotations` to support recursive type hints.
- **Python Field Ordering**: Sorted dataclass fields so that those with default values correctly follow those without.

## [0.4.1] - 2026-02-10

### Added
- Requirements for automated testing with `hypothesis-jsonschema`.
- Requirements for cross-platform model consistency and bidirectional conversion.
- `JsonDataGenerator` implementation using `hypothesis-jsonschema`.
    - Optimized `JsonDataGenerator` by caching `SearchStrategy` and exposing `schema_dict`.
    - Reduced default `max_examples` for slow tests to improve routine developer workflow.
- Support for parallel test execution using `pytest-xdist`.
- `slow` marker for long-running property-based tests.
- Updated test suite to use `@given(data=st.data())` for better Hypothesis shrinking support.

## [0.4.0] - 2026-02-10

### Added
- TypeScript generator support for basic types.

## [0.3.0] - 2026-02-09

### Added
- C++ code generation and testing suite.

## [0.2.0] - 2026-02-08

### Added
- Python data class creation through templating.

## [0.1.2] - 2026-02-07

### Added
- JSON Schema increased test cases with schema validation.
- `$ref` resolver base class with unit tests.

## [0.1.1] - 2026-02-06

### Added
- CLI argument parsing testing validation.

## [0.1.0] - 2026-02-05

### Added
- Initial framework for building out schema parsing and basic unit testing.

## [0.0.3] - 2026-02-04

### Added
- Added test case schemas to use as a basis for generation.

## [0.0.2] - 2026-02-03

### Added
- Updated requirements for code generation.

## [0.0.1] - 2026-02-02

### Added
- Defined requirements for JSON Schema to types generation.
