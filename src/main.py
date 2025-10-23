import re
from src.services.telegram_service import TelegramService
from src.scrapers import SCRAPERS
from src.config import get_config
from src.db import DB

import argparse

def main():
    parser = argparse.ArgumentParser(prog="telelinker")
    subparsers = parser.add_subparsers(dest="command")

    # setup
    subparsers.add_parser("setup")

    # login
    subparsers.add_parser("login")

    # groups
    groups_parser = subparsers.add_parser("groups")
    groups_parser.add_argument("--save", type=str, help="Archivo donde guardar los grupos")
    groups_parser.add_argument("--format", type=str, choices=["csv", "json"], default="csv", help="Formato de exportación de grupos")
    groups_parser.add_argument("--out", type=str, required=False, help="Archivo de salida para exportar los grupos")

    # fetch
    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("--groups-file", type=str, required=False, help="Archivo con los grupos")
    fetch_parser.add_argument("--group", type=str, required=True, help="ID o username del grupo")
    fetch_parser.add_argument("--format", type=str, choices=["csv"], default="csv", help="Formato de exportación")
    fetch_parser.add_argument("--limit", type=str, required=True, help="Numero máximo de posts a fetch")
    fetch_parser.add_argument("--out", type=str, required=False, help="Archivo de salida")

    args = parser.parse_args()

    if args.command == "setup":
        from cli import setup
        setup.run(args)
    elif args.command == "login":
        from cli import login
        login.run(args)
    elif args.command == "groups":
        from cli import groups
        groups.run(args)
    elif args.command == "fetch":
        from cli import fetch
        fetch.run(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()


