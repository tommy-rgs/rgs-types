import jinja2
from pathlib import Path
from typing import Dict, Any, List, Set
from .base import CodeGenerator
from ..schema_models import JSONSchema
from .utils import pascal_case

class PythonGenerator(CodeGenerator):
    def __init__(self, schema: JSONSchema, output_dir: Path):
        super().__init__(schema, output_dir)
        template_path = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            trim_blocks=True, 
            lstrip_blocks=True
        )
        self.classes = []
        self.enums = {}
        self.generated_classes: Set[str] = set()

    def _get_python_type(self, prop: JSONSchema, name: str) -> str:
        if prop.ref:
            resolved = self.resolver.resolve(prop.ref)
            ref_name = resolved.title or prop.ref.split("/")[-1]
            ref_name = pascal_case(ref_name)
            if ref_name not in self.generated_classes:
                self._collect_class(resolved, ref_name)
            return ref_name
        
        if prop.enum:
            enum_name = pascal_case(name)
            self.enums[enum_name] = prop.enum
            return enum_name

        json_type = prop.type
        if json_type == "string":
            return "str"
        elif json_type == "integer":
            return "int"
        elif json_type == "number":
            return "float"
        elif json_type == "boolean":
            return "bool"
        elif json_type == "array":
            if prop.items:
                if isinstance(prop.items, JSONSchema):
                    item_name = prop.items.title or (name + "Item")
                    item_type = self._get_python_type(prop.items, item_name)
                    return f"List[{item_type}]"
                elif isinstance(prop.items, list):
                    return "List[Any]"
            return "List[Any]"
        elif json_type == "object":
            if prop.properties:
                class_name = prop.title or name
                class_name = pascal_case(class_name)
                if class_name not in self.generated_classes:
                    self._collect_class(prop, class_name)
                return class_name
            return "Dict[str, Any]"
        
        return "Any"

    def _collect_class(self, schema: JSONSchema, name: str):
        if name in self.generated_classes:
            return
        self.generated_classes.add(name)
        
        properties = {}
        if schema.properties:
            for prop_name, prop in schema.properties.items():
                type_hint = self._get_python_type(prop, prop_name)
                
                is_required = schema.required and prop_name in schema.required
                if not is_required:
                    type_hint = f"Optional[{type_hint}]"
                
                default = None
                if prop.default is not None:
                    if isinstance(prop.default, str):
                        default = f'"{prop.default}"'
                    elif isinstance(prop.default, bool):
                        default = "True" if prop.default else "False"
                    elif isinstance(prop.default, list) and not prop.default:
                        default = "field(default_factory=list)"
                    else:
                        default = str(prop.default)
                elif not is_required:
                    default = "None"

                properties[prop_name] = {
                    "type_hint": type_hint,
                    "default": default,
                    "description": prop.description
                }
        
        self.classes.append({
            "name": name,
            "description": schema.description,
            "properties": properties
        })

    def generate(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        root_name = self.schema.title or "GeneratedModel"
        root_name = pascal_case(root_name)
        
        self._collect_class(self.schema, root_name)
        
        template = self.env.get_template("python.py.j2")
        content = template.render(
            classes=self.classes,
            enums=self.enums
        )
        
        output_file = self.output_dir / f"{root_name.lower()}.py"
        with open(output_file, "w") as f:
            f.write(content.strip() + "\n")
        
        print(f"[bold blue]Generated Python code:[/bold blue] {output_file}")
