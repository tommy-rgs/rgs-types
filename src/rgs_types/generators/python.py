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
        self.generated_types: Set[str] = set()

    def _get_python_type(self, prop: JSONSchema, name: str) -> str:
        if prop.ref:
            resolved = self.resolver.resolve(prop.ref)
            ref_name = resolved.title or prop.ref.split("/")[-1]
            ref_name = pascal_case(ref_name)
            return self._collect_class(resolved, ref_name)
        
        if prop.enum:
            enum_name = pascal_case(name)
            if enum_name not in self.generated_types:
                self.enums[enum_name] = prop.enum
                self.generated_types.add(enum_name)
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
                return self._collect_class(prop, class_name)
            return "Dict[str, Any]"
        
        return "Any"

    def _collect_class(self, schema: JSONSchema, name: str) -> str:
        original_name = name
        counter = 1
        while name in self.generated_types:
            name = f"{original_name}_{counter}"
            counter += 1
        
        self.generated_types.add(name)
        
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
        
        return name

    def generate(self):
        root_name = self.schema.title or "GeneratedModel"
        root_name = pascal_case(root_name)
        
        # Determine output directory (if x-python-namespace is present)
        final_output_dir = self.output_dir
        if self.schema.python_namespace:
            # e.g. rgs.types.common -> rgs/types/common
            ns_path = self.schema.python_namespace.replace(".", "/")
            final_output_dir = self.output_dir / ns_path
            
        final_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files in parent directories if they don't exist
        # (This is optional but good for Python packages)
        curr = final_output_dir
        while curr != self.output_dir and curr != curr.parent:
            init_file = curr / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            curr = curr.parent

        self._collect_class(self.schema, root_name)
        
        template = self.env.get_template("python.py.j2")
        content = template.render(
            classes=self.classes,
            enums=self.enums
        )
        
        output_file = final_output_dir / f"{root_name.lower()}.py"
        with open(output_file, "w") as f:
            f.write(content.strip() + "\n")
        
        print(f"[bold blue]Generated Python code:[/bold blue] {output_file}")