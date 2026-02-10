# Requirements

## 1. Core Data Representation

* **Cross-platform Compatibility**: Support `C++`, `Python`, and `TypeScript` with consistent data behavior.
* **Primitive Types**:
    * `boolean`
    * `integer`: (C++: `int64_t`, Python: `int`, TS: `number`)
    * `number`: (C++: `double`, Python: `float`, TS: `number`)
    * `string`
* **Enumerated Values**: Support `enum` types with storable and parsable values.
* **Complex Structures**:
    * **Objects**: Support nested structures. Allow choice between inline nested definitions or extracting them as independent types.
    * **Arrays**: Support homogenous arrays of primitives and objects (e.g., `array[string]`, `array[Object]`).

## 2. Structure & Relationships

* **Namespacing**: Prevent naming conflicts by nesting objects into namespaces.
    * Controlled by JSON Schema `$id`, `x-cpp-namespace`, or `x-python-namespace`.
* **Referential Structures ($ref)**:
    * Support internal and recursive references.
    * Use owned type *Composition* for standard structures.
    * Use smart pointers (e.g., `std::shared_ptr`) for recursive structures in C++.
* **Optionality & Defaults**:
    * **Optional Fields**: Any field not in the `required` section AND lacking an explicit `default` value.
    * **Default Values**: Fields with a `default` value are NOT treated as optional in the type system, as they can always be resolved from the schema.
    * **Language Mapping**: Use `std::optional` (C++), `Optional[T] | None` (Python), and `?` (TS) for true optional fields.
* **Versioning & Compatibility**:
    * Maintain backwards compatibility by ensuring new fields are either non-required or provide defaults.
    * Types must remain parseable even if data is missing non-required fields (old version data).

## 3. Logic & Interfaces

* **Serialization/Deserialization**:
    * **Middleware**: Support `Rgs::Types::Datagram` for internal middleware serialization.
    * **Native JSON**:
        * **C++**: `nlohmann::json` integration (`to_json`/`from_json`).
        * **Python**: `to_dict()` and `from_dict()`.
        * **TypeScript**: `toJson()` and `fromJson()` helpers.
    * **Visitation**: Provide a visitation interface so structures can be traversed without direct dependencies on serialization libraries.
* **Validation**: Enforce schema constraints (e.g., `minItems`, `exclusiveMinimum`, `pattern`) during parsing and mutation.
* **Visibility (Read/Write Only)**:
    * `readOnly`: External nodes can only read; internal logic can write.
    * `writeOnly`: External nodes can only write; internal logic can read.
* **Documentation**: Transform `title` and `description` tags into native code comments (Doxygen/Docstrings/JSDoc).

## 4. Development & Quality

* **Naming Strategies**:
    * Maintain original JSON Schema property names for member variables.
    * Use schema `title` or filename as the basis for class/struct names.
* **Automated Testing**:
    * Use `hypothesis-jsonschema` for property-based testing.
    * Validate that parsing logic handles the full range of supported JSON specifications.
* **Integration Testing**:
    * Continuous verification via compilation and execution checks.
    * **C++**: `clang`/`gcc` build checks.
    * **Python**: `pytest` import and logic checks.
    * **TypeScript**: `tsc` compilation and `node` execution checks.

---

### Explicitly Unsupported / Disallowed
* **Schema Composition**: Keywords like `oneOf`, `anyOf`, and `allOf` are NOT supported.
* **Nullability**: Explicit `null` types (e.g., `type: ["string", "null"]`) are disallowed; use optionality instead.

### Type Mappings
| JSON Schema | C++ | Python | TypeScript |
|---|---|---|---|
| boolean | bool | bool | boolean |
| integer | int64_t | int | number |
| number | double | float | number |
| string | std::string | str | string |
| array | std::vector<T> | List[T] | Array<T> |
| object | struct / class | Dataclass | interface |
