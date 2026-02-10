# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
