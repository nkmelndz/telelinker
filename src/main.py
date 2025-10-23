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
    groups_parser.add_argument("--format", type=str, choices=["csv", "json"], default="csv", help="Export format for groups")
    groups_parser.add_argument("--out", type=str, required=False, help="Output file for exported groups")

    # fetch
    fetch_parser = subparsers.add_parser("fetch")
    group_group = fetch_parser.add_mutually_exclusive_group(required=True)
    group_group.add_argument("--groups-file", type=str, help="Archivo con los grupos")
    group_group.add_argument("--group", type=str, help="ID o username del grupo")
    fetch_parser.add_argument("--format", type=str, choices=["csv", "postgresql"], default="csv", help="Export format (csv or postgresql)")
    fetch_parser.add_argument("--limit", type=str, required=False, help="Numero máximo de posts a fetch")
    fetch_parser.add_argument("--out", type=str, required=False, help="Archivo de salida")

    # scrape_instagram
    insta_parser = subparsers.add_parser("scrape_instagram")
    insta_parser.add_argument("--group", type=str, required=True, help="ID o username del grupo de Telegram")
    insta_parser.add_argument("--out", type=str, required=True, help="Archivo CSV de salida")
    insta_parser.add_argument("--limit", type=int, required=False, help="Número máximo de mensajes a analizar")

    args = parser.parse_args()

    if args.command == "setup":
        from src.cli import setup
        setup.run(args)
    elif args.command == "login":
        from src.cli import login
        login.run(args)
    elif args.command == "groups":
        from src.cli import groups
        groups.run(args)
    elif args.command == "fetch":
        from src.cli import fetch
        fetch.run(args)
    elif args.command == "scrape_instagram":
        from src.cli import scrape_instagram
        scrape_instagram.run(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()


