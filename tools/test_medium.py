import json

from src.scrapers.medium import scrap


def main():

    resultado = scrap("https://medium.com/@bhagyarana80/rag-is-dead-why-enterprises-shun-vector-dbs-for-agent-architecture-f0f85c5dd367")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
