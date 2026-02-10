# Requirements

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
    * Support for parsing and converting to and from the native programming language models (e.g., Python dataclasses, C++ structs, TS interfaces) with full fidelity.
    * Ensure data consistency and interoperability when sending data between different language models (e.g., Python -> Datagram -> C++).
* __Testing & Data Generation__:
    * Use `hypothesis-jsonschema` to generate valid JSON data from schemas.
    * Use generated data to validate that the parsing logic in all target languages correctly handles the full range of the JSON specification supported.
    * _Note_: `hypothesis-jsonschema` has limited support for recursive references; these may need manual test case generation.
* __Naming Strategies__:
    * Naming of the local variables should be maintained from the JSON Schema to the codebase member variable
    * ~~Support mapping JSON `camelCase` to C++ `snake_case`.~~
    * ~~Support mapping JSON name to programming specific naming conventions~~
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

__Pros__
* Excellent cross-platform support (C++, Python, TS) and good naming strategies.
* Support for primitive typing `int64`, `float64`

__Cons__
* Poor support for strictly typed nested structures (reverts to `nlohmann::json` maps); lacks validation logic in C++ setters.
* Doesn't support validation procedures
* References can only be located within the same schema file

### JSON Type Definition (JTD) and jtd-codegen

__Pros__
* Supports TS, Python, and other langues not in our framework

__Cons__
* Doesn't support validation logic

### JSON-Schema-to-Cpp (pearmaster)

__Pros__
* Strong C++ focus; supports `$ref` and uses `RapidJSON` for high-performance serialization.

__Cons__
* Depends on `boost::variant` (disallowed composition); no native Python/TS support.

### pydantic-codegen

__Pros__
* Best for Python (Default values, Pydantic validation, docstrings). Supports TS.

__Cons__
* No C++ path; often allows nullability which is disallowed here.

### datamodel-code-generator

__Pros__
* Supports Pydantic (Python) and TypeScript. Handles type-safe models, `Optional` types, and field descriptions.

__Cons__
* Primarily Python/TS focused; no C++ generation.

### Modelator
__Pros__
* Specialized C++ generator for clean models.

__Cons__
* Less mainstream; would require custom templates for `Rgs::Types::Datagram` integration.

### Jinjava/Mustache

__Pros__
* Maximum flexibility. Can satisfy all requirements (Datagram serialization, snake_case, read/write logic) by excluding unsupported features.

__Cons__
* High implementation cost (manual template and parsing logic).

### userver/Chaotic

__Pros__
* Good support for `$ref` types

__Cons__
* Relies heavily on the userver ecosystem
* C++ Code generation only
* Uses `.yaml` files for JSON Schema