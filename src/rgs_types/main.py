import typer
import json
from enum import Enum
from typing import Optional, List
from pathlib import Path
from rich import print
from pydantic import ValidationError
from .parser import parse_schema_file
from .generators.python import PythonGenerator
from .generators.cpp import CppGenerator
from .generators.typescript import TypeScriptGenerator

app = typer.Typer()

class TargetLanguage(str, Enum):
    cpp = "cpp"
    python = "python"
    typescript = "typescript"

@app.command()
def generate(
    schema_paths: List[Path] = typer.Argument(
        ..., 
        help="Path(s) to the JSON Schema file(s) to be parsed.", 
        exists=True, 
        file_okay=True, 
        dir_okay=False, 
        readable=True, 
        resolve_path=True
    ),
    output_dir: Path = typer.Option(
        Path("."), 
        "--output", "-o", 
        help="Directory where the generated code will be saved.", 
        file_okay=False, 
        dir_okay=True, 
        writable=True, 
        resolve_path=True
    ),
    lang: TargetLanguage = typer.Option(
        TargetLanguage.cpp, 
        "--lang", "-l", 
        help="Target programming language for code generation."
    )
):
    """
    Generate cross-platform data types from JSON Schema files.

    This tool parses standard JSON Schema files and generates corresponding data models
    in the specified target language (C++, Python, or TypeScript).
    """
    for path in schema_paths:
        print(f"[bold green]Parsing schema:[/bold green] {path}")
        
        try:
            schema = parse_schema_file(path)
            print(f"[bold blue]Schema Title:[/bold blue] {schema.title}")
            
            if lang == TargetLanguage.python:
                generator = PythonGenerator(schema, output_dir)
                generator.generate()
            elif lang == TargetLanguage.cpp:
                generator = CppGenerator(schema, output_dir)
                generator.generate()
            elif lang == TargetLanguage.typescript:
                generator = TypeScriptGenerator(schema, output_dir)
                generator.generate()
            else:
                print(f"[yellow]Generating {lang.value} code to {output_dir}... (Not implemented yet)[/yellow]")

        except json.JSONDecodeError as e:
            print(f"[bold red]JSON Parse Error:[/bold red] The file '{path}' is not valid JSON.")
            print(f"Details: {e}")
            raise typer.Exit(code=1)
        except ValidationError as e:
            print(f"[bold red]Schema Validation Error:[/bold red] The file '{path}' does not match the expected schema structure.")
            print(f"Details: {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            print(f"[bold red]Unexpected Error processing '{path}':[/bold red] {e}")
            raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
