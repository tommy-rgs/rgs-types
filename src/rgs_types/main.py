import typer
from typing import Optional
from pathlib import Path
from rich import print
from .parser import parse_schema_file

app = typer.Typer()

@app.command()
def generate(
    schema_path: Path = typer.Argument(..., help="Path to the JSON Schema file", exists=True),
    output_dir: Path = typer.Option(Path("."), "--output", "-o", help="Directory to save generated code"),
    lang: str = typer.Option("cpp", help="Target language (cpp, python, typescript)")
):
    """
    Generate code from a JSON Schema file.
    """
    print(f"[bold green]Parsing schema:[/bold green] {schema_path}")
    
    try:
        schema = parse_schema_file(schema_path)
        print(f"[bold blue]Schema Title:[/bold blue] {schema.title}")
        print(f"[bold blue]Schema Type:[/bold blue] {schema.type}")
        
        # Placeholder for generation logic
        print(f"[yellow]Generating {lang} code to {output_dir}... (Not implemented yet)[/yellow]")
        
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
