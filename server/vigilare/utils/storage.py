import json
from pathlib import Path


def carregar_json(caminho):
    """
    Carrega dados de um arquivo JSON.

    Se o arquivo não existir, retorna uma lista vazia.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        return []

    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    """
    Salva dados em um arquivo JSON.
    """
    caminho = Path(caminho)

    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )
