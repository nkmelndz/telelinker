import re
from src.services.telegram_service import TelegramService
from src.scrapers import SCRAPERS
import argparse



def main():
    parser = argparse.ArgumentParser(prog="telelinker")
    subparsers = parser.add_subparsers(dest="command")

    # setup
    subparsers.add_parser("setup")

    # login
    subparsers.add_parser("login")

    # logout
    subparsers.add_parser("logout")

    # groups
    groups_parser = subparsers.add_parser("groups")
    groups_parser.add_argument("-f", "--format", type=str, choices=["csv", "json"], default=None, help="Export format for groups")
    groups_parser.add_argument("-o", "--out", type=str, required=False, help="Output file for exported groups")
    groups_parser.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo para seleccionar y exportar grupos")

    # fetch
    fetch_parser = subparsers.add_parser("fetch")
    group_group = fetch_parser.add_mutually_exclusive_group(required=False)
    group_group.add_argument("-G", "--groups-file", type=str, help="Archivo con los grupos")
    group_group.add_argument("-g", "--group", type=str, help="ID o username del grupo")
    fetch_parser.add_argument("-f", "--format", type=str, choices=["csv", "postgresql", "json"], default="csv", help="Formato de exportación (csv, postgresql o json)")
    fetch_parser.add_argument("-l", "--limit", type=str, required=False, help="Número máximo de posts a extraer")
    fetch_parser.add_argument("-o", "--out", type=str, required=False, help="Archivo de salida")
    fetch_parser.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo para elegir grupos y exportar")

    args = parser.parse_args()

    if args.command == "setup":
        from src.cli.commands import setup
        setup.run(args)
    elif args.command == "login":
        from src.cli.commands import login
        login.run(args)
    elif args.command == "logout":
        from src.cli.commands import logout
        logout.run(args)
    elif args.command == "groups":
        from src.cli.commands import groups
        groups.run(args)
    elif args.command == "fetch":
        from src.cli.commands import fetch
        fetch.run(args)
    else:
        from src.cli.commands import welcome
        welcome.print_banner_and_help(parser)

if __name__ == '__main__':
    main()


