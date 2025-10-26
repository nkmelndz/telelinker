import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box


def print_banner_and_help(parser: argparse.ArgumentParser) -> None:
    console = Console()
    console.print(Panel.fit(
        "[bold magenta]Telelinker[/]\n[cyan]Scrapea y exporta enlaces de redes sociales[/]",
        title="🚀 Bienvenido",
        border_style="magenta"
    ))

    table = Table(title="Comandos disponibles", box=box.SIMPLE)
    table.add_column("Comando", style="bold", no_wrap=True)
    table.add_column("Descripción")
    table.add_row("setup", "Configura credenciales de Telegram")
    table.add_row("login", "Inicia sesión en Telegram")
    table.add_row("logout", "Cierra sesión y elimina archivo de sesión")
    table.add_row("groups", "Lista y exporta tus grupos (csv/json)")
    table.add_row("fetch", "Extrae enlaces y exporta (csv/postgresql)")
    console.print(table)

    console.print("\nUso básico:")
    console.print("  telelinker setup")
    console.print("  telelinker login")
    console.print("  telelinker groups --format csv --out grupos.csv")
    console.print("  telelinker fetch --group <id_or_username> --limit 50 --format csv --out enlaces.csv")
    console.print("  telelinker fetch --groups-file groups.json --format postgresql --out posts.sql")
    console.print("\n[dim]Para más opciones detalladas, usa[/] [bold]--help[/] en cada comando, por ejemplo: [bold]telelinker fetch --help[/]")

    # Mostrar la ayuda general del parser
    console.print(Panel.fit(parser.format_help(), title="Ayuda general", border_style="blue"))