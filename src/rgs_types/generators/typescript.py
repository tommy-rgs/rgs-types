import jinja2
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from .base import CodeGenerator
from ..schema_models import JSONSchema
from .utils import pascal_case

class TypeScriptGenerator(CodeGenerator):
    def __init__(self, schema: JSONSchema, output_dir: Path):
        super().__init__(schema, output_dir)
        template_path = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            trim_blocks=True, 
            lstrip_blocks=True
        )
        self.interface_list = []
        self.enum_list = []
        self.generated_types: Set[str] = set()
        self.ref_map: Dict[str, str] = {} # Map ref string to generated interface name

    def _get_ts_type(self, prop: JSONSchema, name: str) -> str:
        if prop.ref:
            if prop.ref in self.ref_map:
                return self.ref_map[prop.ref]
            
            resolved = self.resolver.resolve(prop.ref)
            ref_name = resolved.title or prop.ref.split("/")[-1]
            ref_name = pascal_case(ref_name)
            return self._collect_interface(resolved, ref_name, ref=prop.ref)
        
        if prop.enum:
            enum_name = pascal_case(name)
            if enum_name not in self.generated_types:
                self.enum_list.append({
                    "name": enum_name,
                    "enum_values": prop.enum
                })
                self.generated_types.add(enum_name)
            return enum_name

        json_type = prop.type
        if json_type == "string":
            return "string"
        elif json_type in ("integer", "number"):
            return "number"
        elif json_type == "boolean":
            return "boolean"
        elif json_type == "array":
            if prop.items and isinstance(prop.items, JSONSchema):
                item_name = prop.items.title or (name + "Item")
                item_type = self._get_ts_type(prop.items, item_name)
                return f"Array<{item_type}>"
            return "Array<any>"
        elif json_type == "object":
            if prop.properties:
                struct_name = prop.title or name
                struct_name = pascal_case(struct_name)
                return self._collect_interface(prop, struct_name)
            return "{ [key: string]: any }"
        
        return "any"

    def _collect_interface(self, schema: JSONSchema, name: str, ref: Optional[str] = None) -> str:
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
        
        properties = []
        if schema.properties:
            for prop_name, prop in schema.properties.items():
                ts_type = self._get_ts_type(prop, prop_name)
                is_required = schema.required and prop_name in schema.required
                
                properties.append({
                    "name": prop_name,
                    "type": ts_type,
                    "required": is_required,
                    "description": prop.description
                })
        
        self.interface_list.append({
            "name": name,
            "description": schema.description,
            "properties": properties
        })
        
        return name

    def generate(self):
        root_name = self.schema.title or "GeneratedModel"
        root_name = pascal_case(root_name)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._collect_interface(self.schema, root_name)
        
        template = self.env.get_template("typescript.ts.j2")
        content = template.render(
            interfaces=self.interface_list,
            enums=self.enum_list
        )
        
        output_file = self.output_dir / f"{root_name.lower()}.ts"
        with open(output_file, "w") as f:
            f.write(content.strip() + "\n")
        
        print(f"[bold blue]Generated TypeScript code:[/bold blue] {output_file}")