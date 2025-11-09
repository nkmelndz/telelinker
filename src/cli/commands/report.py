import os
import pandas as pd
from rich.console import Console
from waitress import serve
from src.dashboards import report_dashboard


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

    # Integrar el dashboard en el mismo proceso (sin invocar 'python -m')
    # Esto asegura que PyInstaller incluya las dependencias (Flask/Dash/Waitress)
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not read CSV file: [yellow]{e}[/yellow]")
        return

    app = report_dashboard.build_app(df)

    port = getattr(args, "port", 8501)
    console.print(f"[bold cyan]Opening dashboard (Dash)[/bold cyan] at [bright_cyan]http://127.0.0.1:{port}/[/bright_cyan] …")
    console.print("[dim]Press [bold]Ctrl+C[/bold] to exit.[/dim]")

    try:
        serve(app.server, host="127.0.0.1", port=port, threads=8, backlog=64)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Server stopped[/bold yellow]. Goodbye! ✨")