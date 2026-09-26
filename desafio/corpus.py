"""Parte 0: leitura do corpus e dos metadados.

Acesso somente leitura aos insumos. Nenhuma função deste módulo escreve na
pasta do corpus.
"""

from pathlib import Path

import pandas as pd

# Caminhos resolvidos a partir de __file__ para que o pipeline rode a partir de
# qualquer diretório de trabalho.
RAIZ = Path(__file__).resolve().parent.parent
INSUMOS = RAIZ / "insumos_Desafio_Bootcamp_SEP26 (1)"
CORPUS = INSUMOS / "corpus"
METADADOS_CSV = INSUMOS / "metadados.csv"
GABARITO_CSV = INSUMOS / "perguntas_gabarito.csv"


def carregar_metadados() -> pd.DataFrame:
    """Uma linha por documento, conforme metadados.csv (UTF-8, separado por vírgula)."""
    return pd.read_csv(METADADOS_CSV, encoding="utf-8")


def carregar_corpus() -> pd.DataFrame:
    """Metadados acrescidos das colunas `texto` (conteúdo integral do .md) e `n_palavras`."""
    df = carregar_metadados()
    df["texto"] = [
        (CORPUS / nome).read_text(encoding="utf-8") for nome in df["arquivo"]
    ]
    df["n_palavras"] = [len(texto.split()) for texto in df["texto"]]
    return df


def carregar_gabarito() -> pd.DataFrame:
    """As 10 perguntas de avaliação, conforme perguntas_gabarito.csv."""
    return pd.read_csv(GABARITO_CSV, encoding="utf-8")


def validar_corpus(df: pd.DataFrame) -> dict[str, int]:
    """Valida as premissas do enunciado e devolve a contagem por status.

    Levanta exceção se o corpus divergir de: 12 documentos, todos os arquivos
    presentes, 11 vigentes e 1 revogado.
    """
    if len(df) != 12:
        raise ValueError(f"esperados 12 documentos em metadados.csv, encontrados {len(df)}")

    faltando = [nome for nome in df["arquivo"] if not (CORPUS / nome).exists()]
    if faltando:
        raise FileNotFoundError(f"arquivos ausentes na pasta corpus: {faltando}")

    contagem = df["status"].value_counts().to_dict()
    if contagem.get("vigente") != 11 or contagem.get("revogada") != 1:
        raise ValueError(f"esperados 11 vigentes e 1 revogada, encontrado {contagem}")

    return contagem


def formatar_evidencia_p0(df: pd.DataFrame, contagem: dict[str, int]) -> str:
    """Evidência da Parte 0: tabela com doc_id, status e número de palavras."""
    linhas = [
        "| doc_id | titulo | status | n_palavras |",
        "| --- | --- | --- | --- |",
    ]
    for _, doc in df.iterrows():
        linhas.append(
            f"| {doc['doc_id']} | {doc['titulo']} | {doc['status']} | {doc['n_palavras']} |"
        )
    linhas.append("")
    linhas.append(f"Total de documentos lidos: {len(df)}")
    linhas.append(
        "Contagem por status: "
        + ", ".join(f"{status} = {n}" for status, n in sorted(contagem.items()))
    )
    linhas.append(f"Total de palavras no corpus: {int(df['n_palavras'].sum())}")
    return "\n".join(linhas)
