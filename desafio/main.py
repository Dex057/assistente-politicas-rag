"""Assistente de perguntas e respostas sobre políticas internas.

Executa as Partes 0 a 5 em ordem, imprime as evidências no terminal e grava
saidas.md na raiz do projeto. Não modifica a pasta de insumos.

Uso:
    python desafio/main.py
"""

import sys
from pathlib import Path

# Permite executar via `python desafio/main.py` sem instalar o pacote.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from desafio import avaliacao, busca, chunking, corpus, indexacao, resposta

SAIDAS_MD = corpus.RAIZ / "saidas.md"

# Configuração selecionada pela comparação das 8 combinações na Parte 2.
CONFIG_INDICE = {
    "remover_acentos": True,
    "remover_stopwords": True,
    "usar_secao": False,
}

CABECALHO = """# Saídas do Desafio Bootcamp SEP26

Assistente de perguntas e respostas sobre políticas internas (RAG com recuperação
local, TF-IDF + similaridade do cosseno, resposta extrativa).

Arquivo gerado por `python desafio/main.py`. A execução é determinística: rodar de
novo reproduz exatamente estes números.
"""


def executar() -> str:
    """Executa as Partes 0 a 5 em ordem e devolve o conteúdo de saidas.md."""
    partes: list[tuple[str, str]] = []

    # Parte 0 - Setup e leitura do corpus
    df_docs = corpus.carregar_corpus()
    contagem = corpus.validar_corpus(df_docs)
    partes.append(
        ("Parte 0 - Setup e leitura do corpus", corpus.formatar_evidencia_p0(df_docs, contagem))
    )

    # Parte 1 - Chunking por secao
    df_chunks = chunking.construir_chunks(df_docs)
    partes.append(("Parte 1 - Chunking por seção", chunking.formatar_evidencia_p1(df_chunks)))

    # Parte 2 - Indexacao com TF-IDF
    df_gabarito = corpus.carregar_gabarito()
    indice = indexacao.construir_indice(df_chunks, **CONFIG_INDICE)
    busca.definir_indice_padrao(indice)
    df_comparacao = avaliacao.comparar_configuracoes(df_chunks, df_gabarito)
    partes.append(
        ("Parte 2 - Indexação com TF-IDF", avaliacao.formatar_evidencia_p2(indice, df_comparacao))
    )

    # A comparação da Parte 2 constrói índices próprios; restaura o adotado.
    busca.definir_indice_padrao(indice)

    # Parte 3 - Recuperacao top-k com regra de vigencia
    partes.append(
        (
            "Parte 3 - Recuperação top-k com regra de vigência",
            busca.formatar_evidencia_p3(indice, df_gabarito),
        )
    )

    # Parte 4 - Resposta extrativa e regra de nao encontrado
    calibracao = avaliacao.calibrar_threshold(df_gabarito, indice)
    partes.append(
        (
            "Parte 4 - Resposta extrativa e regra de não encontrado",
            resposta.formatar_evidencia_p4(calibracao, df_gabarito, indice),
        )
    )

    # Parte 5 - Avaliacao com o gabarito
    df_avaliacao = avaliacao.avaliar_gabarito(df_gabarito, indice)
    partes.append(
        ("Parte 5 - Avaliação com o gabarito", avaliacao.formatar_evidencia_p5(df_avaliacao))
    )

    blocos = [CABECALHO] + [f"## {titulo}\n\n{corpo}" for titulo, corpo in partes]
    return "\n\n---\n\n".join(blocos) + "\n"


def main() -> None:
    documento = executar()
    print(documento)
    SAIDAS_MD.write_text(documento, encoding="utf-8")
    print(f"\n[ok] evidências gravadas em {SAIDAS_MD}")


if __name__ == "__main__":
    main()
