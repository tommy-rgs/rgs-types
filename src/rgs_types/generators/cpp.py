import jinja2
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from rich import print
from .base import CodeGenerator
from ..schema_models import JSONSchema
from .utils import pascal_case, snake_case

class CppGenerator(CodeGenerator):
    def __init__(self, schema: JSONSchema, output_dir: Path):
        super().__init__(schema, output_dir)
        template_path = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            trim_blocks=True, 
            lstrip_blocks=True
        )
        self.struct_list = []
        self.enum_list = []
        self.generated_types: Set[str] = set()
        self.ref_map: Dict[str, str] = {} # Map ref string to generated struct name
        self.collecting_stack: List[str] = [] # Track current collection to detect recursion

    def _get_cpp_type(self, prop: JSONSchema, name: str) -> str:
        if prop.ref:
            if prop.ref in self.ref_map:
                res_name = self.ref_map[prop.ref]
                # If we are currently collecting this type, it's recursive!
                if res_name in self.collecting_stack:
                    return f"std::shared_ptr<{res_name}>"
                return res_name

            resolved = self.resolver.resolve(prop.ref)
            ref_name = resolved.title or prop.ref.split("/")[-1]
            ref_name = pascal_case(ref_name)
            return self._collect_type(resolved, ref_name, ref=prop.ref)
        
        if prop.enum:
            enum_name = pascal_case(name)
            if enum_name not in self.generated_types:
                # Sanitise enum values: prefix numbers
                sanitized_values = []
                for v in prop.enum:
                    val_str = str(v)
                    if val_str[0].isdigit():
                        sanitized_values.append(f"VALUE_{val_str}")
                    else:
                        sanitized_values.append(val_str)

                self.enum_list.append({
                    "name": enum_name,
                    "enum_values": sanitized_values
                })
                self.generated_types.add(enum_name)
            return enum_name

        json_type = prop.type
        if json_type == "string":
            return "std::string"
        elif json_type == "integer":
            return "int64_t"
        elif json_type == "number":
            return "double"
        elif json_type == "boolean":
            return "bool"
        elif json_type == "array":
            if prop.items and isinstance(prop.items, JSONSchema):
                item_name = prop.items.title or (name + "Item")
                item_type = self._get_cpp_type(prop.items, item_name)
                return f"std::vector<{item_type}>"
            return "std::vector<nlohmann::json>"
        elif json_type == "object":
            if prop.properties:
                struct_name = prop.title or name
                struct_name = pascal_case(struct_name)
                return self._collect_type(prop, struct_name)
            return "nlohmann::json"
        
        return "nlohmann::json"

    def _collect_type(self, schema: JSONSchema, name: str, ref: Optional[str] = None) -> str:
        if ref and ref in self.ref_map:
            return self.ref_map[ref]

        original_name = name
        counter = 1
        while name in self.generated_types:
            name = f"{original_name}_{counter}"
            counter += 1
        
        self.generated_types.add(name)
        if ref:
            self.ref_map[ref] = name
        
        self.collecting_stack.append(name)
        
        properties = []
        if schema.properties:
            for prop_name, prop in schema.properties.items():
                cpp_type = self._get_cpp_type(prop, prop_name)
                
                is_required = schema.required and prop_name in schema.required
                # If it's already a shared_ptr (recursive), don't wrap in optional
                if not is_required and not cpp_type.startswith("std::shared_ptr"):
                    cpp_type = f"std::optional<{cpp_type}>"
                
                default = None
                if prop.default is not None:
                    if isinstance(prop.default, str):
                        default = f'"{prop.default}"'
                    elif isinstance(prop.default, bool):
                        default = "true" if prop.default else "false"
                    elif isinstance(prop.default, (int, float)):
                        default = str(prop.default)

                properties.append({
                    "name": snake_case(prop_name),
                    "type": cpp_type,
                    "default": default,
                    "description": prop.description
                })
        
        self.struct_list.append({
            "name": name,
            "description": schema.description,
            "properties": properties
        })
        
        self.collecting_stack.pop()
        return name

    def generate(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        root_name = self.schema.title or "GeneratedModel"
        root_name = pascal_case(root_name)
        
        self._collect_type(self.schema, root_name)
        
        # Determine namespace
        namespace = self.schema.cpp_namespace
        if not namespace and self.schema.id:
            namespace = self.schema.id.split("/")[-1].split(".")[0]
            namespace = snake_case(namespace)

        template = self.env.get_template("cpp.hpp.j2")
        content = template.render(
            namespace=namespace,
            structs=self.struct_list,
            enums=self.enum_list
        )
        
        output_file = self.output_dir / f"{root_name.lower()}.hpp"
        with open(output_file, "w") as f:
            f.write(content.strip() + "\n")
        
        print(f"[bold blue]Generated C++ code:[/bold blue] {output_file}")
