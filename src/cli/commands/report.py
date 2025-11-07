import os
from rich.console import Console


def run(args):
    """
    Launch the Plotly Dash dashboard passing the --file argument.

    Args:
        args: CLI arguments, including '--file'.
    """
    file_path = args.file

    console = Console()

    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File '[yellow]{file_path}[/yellow]' does not exist.")
        return

    # Lanzar el dashboard de Dash como módulo de Python
    # Usamos puerto 8501 para mantener consistencia con el uso previo
    cmd = f"python -m src.dashboards.report_dashboard --file \"{file_path}\" --host 127.0.0.1 --port 8501"

    console.print("[bold cyan]Opening dashboard (Dash)[/bold cyan] at [bright_cyan]http://127.0.0.1:8501/[/bright_cyan] …")
    console.print("[dim]Press [bold]Ctrl+C[/bold] to exit.[/dim]")

    try:
        os.system(cmd)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Server stopped[/bold yellow]. Goodbye! ✨")