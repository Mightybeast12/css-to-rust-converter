"""Command-line interface for CSS to Rust converter."""

import click
import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from .converter import CssToRustConverter


console = Console()


@click.group()
@click.version_option()
def main():
    """CSS to Rust converter for Yew applications."""
    pass


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_path', type=click.Path(),
              help='Output file or directory path')
@click.option('-c', '--config', 'config_path', type=click.Path(exists=True),
              help='Custom configuration file')
@click.option('--component', is_flag=True, default=False,
              help='Group by component and create module structure')
@click.option('--no-variants', is_flag=True, default=False,
              help='Disable variant extraction')
@click.option('--utilities', is_flag=True, default=False,
              help='Include utility functions')
@click.option('--analyze', is_flag=True, default=False,
              help='Show analysis of CSS before conversion')
def convert(input_path: str, output_path: Optional[str], config_path: Optional[str],
           component: bool, no_variants: bool, utilities: bool, analyze: bool):
    """Convert CSS file(s) to Rust stylist format."""

    # Initialize converter
    try:
        converter = CssToRustConverter(config_path)
    except Exception as e:
        console.print(f"[red]Error initializing converter: {e}[/red]")
        sys.exit(1)

    # Determine input type
    input_p = Path(input_path)
    is_directory = input_p.is_dir()

    # Determine output path
    if not output_path:
        if is_directory:
            output_path = str(input_p / "rust_styles")
        else:
            output_path = str(input_p.with_suffix('.rs'))

    # Conversion options
    options = {
        'group_by_component': component,
        'extract_variants': not no_variants,
        'include_utilities': utilities
    }

    # Show analysis if requested
    if analyze:
        if is_directory:
            console.print("[yellow]Analysis not supported for directories[/yellow]")
        else:
            _show_analysis(converter, input_path)

    # Perform conversion
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            if is_directory:
                task = progress.add_task("Converting directory...", total=None)
                result = converter.convert_directory(input_path, output_path, **options)
            else:
                task = progress.add_task("Converting file...", total=None)
                result = converter.convert_file(input_path, output_path, **options)

        # Show results
        _show_conversion_results(result, output_path, is_directory)

    except Exception as e:
        console.print(f"[red]Conversion failed: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument('css_file', type=click.Path(exists=True))
def analyze(css_file: str):
    """Analyze CSS file and show statistics."""

    try:
        converter = CssToRustConverter()
        _show_analysis(converter, css_file)
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument('css_file', type=click.Path(exists=True))
def validate(css_file: str):
    """Validate CSS file for conversion compatibility."""

    try:
        converter = CssToRustConverter()

        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()

        warnings = converter.validate_css(css_content)

        if not warnings:
            console.print("[green]✓ CSS file is valid for conversion[/green]")
        else:
            console.print(f"[yellow]Found {len(warnings)} potential issues:[/yellow]")
            for warning in warnings:
                console.print(f"[yellow]  • {warning}[/yellow]")

    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument('css_content', type=str)
@click.option('--component', is_flag=True, default=False,
              help='Group by component')
@click.option('--no-variants', is_flag=True, default=False,
              help='Disable variant extraction')
def preview(css_content: str, component: bool, no_variants: bool):
    """Preview Rust conversion of CSS string."""

    try:
        converter = CssToRustConverter()

        options = {
            'extract_variants': not no_variants
        }

        functions = converter.convert_string(css_content, **options)

        if not functions:
            console.print("[yellow]No functions generated from CSS[/yellow]")
            return

        console.print(f"[green]Generated {len(functions)} function(s):[/green]\n")

        for func_name, func_code in functions.items():
            console.print(f"[bold]{func_name}:[/bold]")
            syntax = Syntax(func_code, "rust", theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print()

    except Exception as e:
        console.print(f"[red]Preview failed: {e}[/red]")
        sys.exit(1)


@main.command()
def options():
    """Show available conversion options."""

    converter = CssToRustConverter()
    options = converter.get_conversion_options()

    table = Table(title="Conversion Options")
    table.add_column("Option", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Default", style="yellow")
    table.add_column("Description", style="white")

    for option_name, option_info in options.items():
        table.add_row(
            f"--{option_name.replace('_', '-')}",
            option_info["type"],
            str(option_info["default"]),
            option_info["description"]
        )

    console.print(table)


def _show_analysis(converter: CssToRustConverter, css_file: str):
    """Show analysis of CSS file."""

    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    stats = converter.analyze_css(css_content)

    # Create analysis panel
    analysis_content = f"""
[bold]File Statistics:[/bold]
• Total Rules: {stats['total_rules']}
• Unique Selectors: {stats['unique_selectors']}
• Media Queries: {stats['media_queries']}
• Pseudo Selectors: {stats['pseudo_selectors']}
• Keyframes: {stats['total_keyframes']}

[bold]Properties:[/bold]
• Total Properties: {stats['total_properties']}
• Unique Properties: {stats['unique_properties']}

[bold]Value Mapping:[/bold]
• Mappable Values: {stats['mappable_values']}
• Coverage: {stats['mapping_coverage']}

[bold]Components Detected:[/bold]
"""

    for component, rule_count in stats['components'].items():
        analysis_content += f"• {component}: {rule_count} rules\n"

    panel = Panel(
        analysis_content.strip(),
        title=f"Analysis: {Path(css_file).name}",
        border_style="blue"
    )

    console.print(panel)


def _show_conversion_results(result, output_path: str, is_directory: bool):
    """Show conversion results."""

    if is_directory:
        # Directory conversion results
        success_count = sum(1 for r in result.values() if 'error' not in r)
        error_count = len(result) - success_count

        console.print(f"\n[green]✓ Converted {success_count} files[/green]")

        if error_count > 0:
            console.print(f"[red]✗ {error_count} files failed[/red]")

        console.print(f"[blue]Output directory: {output_path}[/blue]")

        # Show file details
        table = Table(title="Conversion Results")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Functions", style="yellow")
        table.add_column("Output", style="white")

        for filename, file_result in result.items():
            if 'error' in file_result:
                table.add_row(filename, "[red]Error[/red]", "-", file_result['error'])
            else:
                table.add_row(
                    filename,
                    "[green]Success[/green]",
                    str(len(file_result.get('functions', []))),
                    file_result.get('output', '')
                )

        console.print(table)

    else:
        # Single file conversion results
        if result['type'] == 'single_file':
            console.print(f"\n[green]✓ Converted successfully[/green]")
            console.print(f"[blue]Output file: {result['output']}[/blue]")
            console.print(f"Functions generated: {len(result['functions'])}")

            if result['keyframes'] > 0:
                console.print(f"Keyframe animations: {result['keyframes']}")

        elif result['type'] == 'component_structure':
            console.print(f"\n[green]✓ Created component structure[/green]")
            console.print(f"[blue]Output directory: {result['output']}[/blue]")
            console.print(f"Components: {len(result['components'])}")
            console.print(f"Total functions: {result['functions']}")

            if result['keyframes'] > 0:
                console.print(f"Keyframe animations: {result['keyframes']}")


if __name__ == '__main__':
    main()
