import jinja2
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
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

    def _get_cpp_type(self, prop: JSONSchema, name: str) -> str:
        if prop.ref:
            resolved = self.resolver.resolve(prop.ref)
            ref_name = resolved.title or prop.ref.split("/")[-1]
            ref_name = pascal_case(ref_name)
            return self._collect_type(resolved, ref_name)
        
        if prop.enum:
            enum_name = pascal_case(name)
            if enum_name not in self.generated_types:
                self.enum_list.append({
                    "name": enum_name,
                    "enum_values": [str(v) for v in prop.enum]
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

    def _collect_type(self, schema: JSONSchema, name: str) -> str:
        # Check if this exact schema object has been collected already
        # To do this properly we'd need a map of schema object id to generated name.
        # For now, let's just disambiguate by name if it's already used.
        
        original_name = name
        counter = 1
        while name in self.generated_types:
            # We should ideally check if it's the SAME structure.
            # But let's assume if it's already in generated_types, we might need a new name
            # unless it's literally the same JSONSchema object (by id).
            # This is a bit complex without a schema registry.
            # Let's simple: if title is same, we'll append a suffix for now.
            name = f"{original_name}_{counter}"
            counter += 1
        
        self.generated_types.add(name)
        
        properties = []
        if schema.properties:
            for prop_name, prop in schema.properties.items():
                cpp_type = self._get_cpp_type(prop, prop_name)
                
                is_required = schema.required and prop_name in schema.required
                if not is_required:
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