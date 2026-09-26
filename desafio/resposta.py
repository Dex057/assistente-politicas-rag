"""Parte 4: resposta extrativa e regra de não encontrado.

A saída segue o Modelo de saída acessível: texto puro, cinco campos, rótulos em
maiúsculas, sem cor, emoji ou símbolo gráfico. A RESPOSTA é o texto do chunk de
maior score, copiado sem alteração.
"""

import pandas as pd

from desafio.busca import buscar
from desafio.indexacao import Indice

# Calibrado sobre os scores do gabarito: a P10, sem resposta no corpus, atinge
# 0.225; a pergunta respondível de menor score (P09) atinge 0.368. O valor fica
# próximo ao centro dessa lacuna. Medição em `avaliacao.calibrar_threshold`.
THRESHOLD = 0.30

MENSAGEM_NAO_ENCONTRADO = (
    "Não encontrei essa informação nas políticas vigentes. "
    "Procure a área de Pessoas e Cultura."
)

STATUS_ENCONTRADO = "encontrado"
STATUS_NAO_ENCONTRADO = "nao_encontrado"


def montar_saida(
    pergunta: str, resposta: str, fonte: str, score: float, status: str
) -> str:
    """Formata os cinco campos obrigatórios, nesta ordem e com estes rótulos."""
    return (
        f"PERGUNTA: {pergunta}\n"
        f"RESPOSTA: {resposta}\n"
        f"FONTE: {fonte}\n"
        f"SCORE: {score:.2f}\n"
        f"STATUS: {status}"
    )


def formatar_fonte(chunk: dict) -> str:
    """Citação da fonte: doc_id, título do documento e seção de origem."""
    return f"{chunk['doc_id']} | {chunk['titulo']} | Seção: {chunk['secao']}"


def responder(
    pergunta: str, threshold: float = THRESHOLD, indice: Indice | None = None
) -> str:
    """Resposta extrativa com o trecho da política vigente de maior score.

    Abaixo do threshold, devolve a mensagem padrão de não encontrado em vez de
    um trecho que não responde à pergunta.
    """
    melhor = buscar(pergunta, k=1, indice=indice)[0]

    if melhor["score"] < threshold:
        return montar_saida(
            pergunta,
            MENSAGEM_NAO_ENCONTRADO,
            "nenhuma",
            melhor["score"],
            STATUS_NAO_ENCONTRADO,
        )

    # O texto do chunk é copiado sem reescrita.
    return montar_saida(
        pergunta,
        melhor["texto"],
        formatar_fonte(melhor),
        melhor["score"],
        STATUS_ENCONTRADO,
    )


def formatar_evidencia_p4(
    calibracao: dict, df_gabarito: pd.DataFrame, indice: Indice | None = None
) -> str:
    """Evidência da Parte 4: threshold justificado e saídas completas de P02 e P10."""
    scores = calibracao["scores_por_pergunta"]
    linhas = [
        "Maior score de cada pergunta do gabarito (base da calibração):",
        "",
        "| pergunta_id | maior_score | tem resposta no corpus |",
        "| --- | --- | --- |",
    ]
    for pid, score in scores.items():
        tem = "não" if pid == "P10" else "sim"
        linhas.append(f"| {pid} | {score:.3f} | {tem} |")

    linhas += [
        "",
        f"Menor score entre as perguntas com resposta: {calibracao['piso_com_resposta']:.3f} (P09)",
        f"Maior score da pergunta sem resposta (P10): {calibracao['teto_sem_resposta']:.3f}",
        f"Meio da lacuna: {calibracao['meio_da_lacuna']:.3f}",
        f"THRESHOLD ESCOLHIDO: {calibracao['threshold_escolhido']:.2f}",
        "",
        "Justificativa: existe uma lacuna limpa entre "
        f"{calibracao['teto_sem_resposta']:.3f} (a P10, que não tem resposta no corpus) e "
        f"{calibracao['piso_com_resposta']:.3f} (a P09, a pergunta respondível de menor score). "
        f"O valor {calibracao['threshold_escolhido']:.2f} fica praticamente no meio dessa "
        "lacuna, com folga para os dois lados: seria preciso uma pergunta respondível pontuar "
        "18% abaixo da pior observada, ou uma pergunta sem resposta pontuar 33% acima da P10, "
        "para o assistente errar. Um valor colado em qualquer um dos extremos acertaria o "
        "gabarito do mesmo jeito, mas quebraria na primeira pergunta um pouco diferente.",
        "",
        "Saída completa para P02:",
        "",
    ]

    for pid in ("P02", "P10"):
        if pid == "P10":
            linhas += ["", "Saída completa para P10:", ""]
        pergunta = df_gabarito.loc[df_gabarito["pergunta_id"] == pid, "pergunta"].iloc[0]
        linhas.append(responder(pergunta, indice=indice))

    return "\n".join(linhas)
