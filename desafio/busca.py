"""Parte 3: recuperação top-k com regra de vigência.

A pergunta é transformada pelo vetorizador ajustado na Parte 2 e comparada aos
chunks por similaridade do cosseno. Apenas documentos vigentes concorrem, salvo
quando `apenas_vigentes=False`.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from desafio.chunking import construir_chunks
from desafio.corpus import carregar_corpus
from desafio.indexacao import Indice, construir_indice

STATUS_VIGENTE = "vigente"

_indice_padrao: Indice | None = None


def definir_indice_padrao(indice: Indice) -> None:
    """Define o índice usado por `buscar` e `responder` quando nenhum é informado."""
    global _indice_padrao
    _indice_padrao = indice


def indice_padrao() -> Indice:
    """Índice padrão, construído sob demanda na primeira chamada."""
    global _indice_padrao
    if _indice_padrao is None:
        _indice_padrao = construir_indice(construir_chunks(carregar_corpus()))
    return _indice_padrao


def buscar(
    pergunta: str,
    k: int = 3,
    apenas_vigentes: bool = True,
    indice: Indice | None = None,
) -> list[dict]:
    """Os k chunks de maior similaridade com a pergunta.

    Cada resultado contém doc_id, titulo, secao, status, score e texto.
    Com `apenas_vigentes=True`, chunks de documentos revogados são excluídos do
    ranqueamento, impedindo que a POL-004 responda no lugar da POL-005.
    """
    indice = indice or indice_padrao()

    vetor_pergunta = indice.vetorizador.transform([pergunta])
    scores = cosine_similarity(vetor_pergunta, indice.matriz)[0]

    if apenas_vigentes:
        # Score negativo remove os revogados do topo sem reindexar o corpus.
        revogados = (indice.df_chunks["status"] != STATUS_VIGENTE).to_numpy()
        scores = np.where(revogados, -1.0, scores)

    # Ordenação decrescente estável: em caso de empate, prevalece o chunk de
    # menor índice. Inverter um argsort ascendente com [::-1] desempataria na
    # ordem oposta.
    melhores = np.argsort(-scores, kind="stable")[:k]
    return [
        {
            "doc_id": indice.df_chunks.at[i, "doc_id"],
            "titulo": indice.df_chunks.at[i, "titulo"],
            "secao": indice.df_chunks.at[i, "secao"],
            "status": indice.df_chunks.at[i, "status"],
            "score": float(scores[i]),
            "texto": indice.df_chunks.at[i, "texto"],
        }
        for i in melhores
    ]


def formatar_resultados(resultados: list[dict]) -> str:
    """Lista os chunks recuperados com doc_id, seção e score em duas casas decimais."""
    return "\n".join(
        f"    {pos}. {r['doc_id']} | Seção: {r['secao']} | score = {r['score']:.2f}"
        for pos, r in enumerate(resultados, start=1)
    )


def formatar_evidencia_p3(indice: Indice, df_gabarito: pd.DataFrame) -> str:
    """Evidência da Parte 3: top-3 de P01, P02 e P10, e verificação da regra de vigência."""
    linhas = []
    for pid in ("P01", "P02", "P10"):
        pergunta = df_gabarito.loc[df_gabarito["pergunta_id"] == pid, "pergunta"].iloc[0]
        linhas += [
            f"{pid}: {pergunta}",
            formatar_resultados(buscar(pergunta, k=3, indice=indice)),
            "",
        ]

    p02 = df_gabarito.loc[df_gabarito["pergunta_id"] == "P02", "pergunta"].iloc[0]
    com_filtro = buscar(p02, k=3, indice=indice)
    sem_filtro = buscar(p02, k=3, apenas_vigentes=False, indice=indice)

    linhas += [
        "Verificação da regra de vigência na P02",
        "",
        "Com a regra ativa (comportamento padrão do assistente):",
        formatar_resultados(com_filtro),
        "",
        "Sem a regra, apenas para demonstrar o que ela evita:",
        formatar_resultados(sem_filtro),
        "",
        f"POL-004 aparece no top-3 com a regra ativa: "
        f"{'sim' if any(r['doc_id'] == 'POL-004' for r in com_filtro) else 'não'}",
        f"POL-004 apareceria sem a regra: "
        f"{'sim' if any(r['doc_id'] == 'POL-004' for r in sem_filtro) else 'não'}",
        "",
        "A POL-004 está revogada e diz \"até 2 dias por semana\", enquanto a POL-005 "
        "vigente diz \"até 3 dias\". Sem o filtro a POL-004 vence por score "
        f"({sem_filtro[0]['score']:.2f} contra {com_filtro[0]['score']:.2f}), porque "
        "repete mais vezes os termos da pergunta. A regra de vigência é o que impede "
        "o assistente de responder com confiança uma regra que não vale mais.",
    ]
    return "\n".join(linhas)
