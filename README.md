# RGS Types

Generating data types from JSON Schema. This allows for a single source of truth for a type definition and can give types that are defined within each of the specified languages that are supported. This allows for the enforcement of data types for modules and provides the interface for each of these nodes to communicate outwards into the world. 

## Requirements

* Cross platform types for `C++`, `Python` and `Type Script`
* Handles the following property types
    * __Simple Types `primitives`__
        * `boolean`
        * `integer`: `int64_t`
        * `number`: `double`
        * `string`
    * __Simple Data Structures__
        * `object`: Nested structures of any types
            * Objects can be handled as nested objects (pythonic)
            * Or to have the nested structures defined as their own data types
        *  `array` of all the same `primitive` simple types
            * `array[boolean]`
            * `array[integer]`
            * `array[number]`
            * `array[string]`
        * `array[Object]` Containing array of nested data structures of the same type
    * __Enumerated Values__
        * Creating of `enum` types with their values storable and parsable
* __Namespace__: Objects should be able to be nested into a namespace to provide the ability to not have naming conflicts
    * Defined by JSON Schema `$id` or other applicable tag. Alternatively available via `x-cpp-namespace`
* __Referential Structures__:
    * Nested structures as defined by `$ref` tag
    * Use owned type _Composition_ for most structures
    * Use smart pointers `std::shared_ptr` and equivalent for recursive structures
* __Serialization/Deserialization__:
    * Should be able to Serialize/Deserialize to and from the `Rgs::Types::Datagram` types which is the middleware for serialization
    * An interface that provides visitation within the data structure so that they don't need a specific interface into Datagram
    * ~~Provide functions to convert between generated types and JSON.~~
        * ~~C++ should support `nlohmann/json` or similar popular libraries.~~
* __Naming Strategies__:
    * Support mapping JSON `camelCase` to C++ `snake_case`.
    * Support mapping type name to internal data name
        * Key -> Type mapping for member variables
    * Use schema `title` or filename as the base for class/struct names.
* __Validation__:
    * Ability to enforce schema constraints (e.g., `minItems`, `exclusiveMinimum`, `pattern`) during parsing/setting
* __Optional Fields__:
    * Use language-appropriate optional types
        * C++: `std::optional` or `boost::optional`
        * Python `Optional[T]` or `| None`
* __Default Values__:
    * Member variables must be automatically initialized using the `default` keyword from the JSON Schema.
* __Read-only / Write-only__:
    * Enforce `readOnly` and `writeOnly` tags to manage data visibility between internal node logic and external interfaces.
    * These tags should guide the generation of getters/setters:
        * `readOnly`: External nodes can only read; internal node can write.
        * `writeOnly`: External nodes can only write; internal node can read.
* __Documentation__:
    * Use the `description` and `title` tags into code comments (Doxygen/Docstrings).

### Explicitly Unsupported / Disallowed
* __Schema Composition__: keywords like `oneOf`, `anyOf`, and `allOf` are NOT supported.
* __Nullability__: Types that allow `null` (e.g., `type: ["string", "null"]`) are explicitly disallowed; use optional fields instead.

### Type Mapings
| JSON Schema | C++ | Python | TypeScript |
|---|---|---|---|
| boolean | bool | bool | boolean |
| integer | int32_t / int64_t | int | number |
| number | double | float | number |
| string | std::string / static_string | str | string |
| array | std::vector<T> | List[T] | Array<T> |
| object | struct / class | Dataclass / Pydantic | interface |

## Implementations

### Quicktype
* *Pros*: Excellent cross-platform support (C++, Python, TS) and good naming strategies.
* *Cons*: Poor support for strictly typed nested structures (reverts to `nlohmann::json` maps); lacks validation logic in C++ setters.

### JSON-Schema-to-Cpp (pearmaster)
* *Pros*: Strong C++ focus; supports `$ref` and uses `RapidJSON` for high-performance serialization.
* *Cons*: Depends on `boost::variant` (disallowed composition); no native Python/TS support.

### pydantic-codegen
* *Pros*: Best for Python (Default values, Pydantic validation, docstrings). Supports TS.
* *Cons*: No C++ path; often allows nullability which is disallowed here.

### datamodel-code-generator
* *Pros*: Supports Pydantic (Python) and TypeScript. Handles type-safe models, `Optional` types, and field descriptions.
* *Cons*: Primarily Python/TS focused; no C++ generation.

### Modelator
* *Pros*: Specialized C++ generator for clean models.
* *Cons*: Less mainstream; would require custom templates for `Rgs::Types::Datagram` integration.

### Jinjava/Mustache
* *Pros*: Maximum flexibility. Can satisfy all requirements (Datagram serialization, snake_case, read/write logic) by excluding unsupported features.
* *Cons*: High implementation cost (manual template and parsing logic).

### userver/Chaotic

### JSON Type Definition (JTD) and jtd-codegen