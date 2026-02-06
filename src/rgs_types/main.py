import typer
import json
from enum import Enum
from typing import Optional
from pathlib import Path
from rich import print
from pydantic import ValidationError
from .parser import parse_schema_file

app = typer.Typer()

class TargetLanguage(str, Enum):
    cpp = "cpp"
    python = "python"
    typescript = "typescript"

@app.command()
def generate(
    schema_path: Path = typer.Argument(
        ..., 
        help="Path to the JSON Schema file to be parsed.", 
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
    Generate cross-platform data types from a JSON Schema file.

    This tool parses a standard JSON Schema file and generates corresponding data models
    in the specified target language (C++, Python, or TypeScript).
    """
    print(f"[bold green]Parsing schema:[/bold green] {schema_path}")
    
    try:
        schema = parse_schema_file(schema_path)
        print(f"[bold blue]Schema Title:[/bold blue] {schema.title}")
        print(f"[bold blue]Schema Type:[/bold blue] {schema.type}")
        
        # Placeholder for generation logic
        print(f"[yellow]Generating {lang.value} code to {output_dir}... (Not implemented yet)[/yellow]")
        
    except json.JSONDecodeError as e:
        print(f"[bold red]JSON Parse Error:[/bold red] The file '{schema_path}' is not valid JSON.")
        print(f"Details: {e}")
        raise typer.Exit(code=1)
    except ValidationError as e:
        print(f"[bold red]Schema Validation Error:[/bold red] The JSON file does not match the expected schema structure.")
        print(f"Details: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
