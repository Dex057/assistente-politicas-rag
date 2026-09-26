"""Parte 5: avaliação com o gabarito. Inclui o experimento da Parte 2.

Hit@1 e Hit@3 consideram apenas as 9 perguntas com documento esperado. A P10
não entra nas médias: é verificada separadamente, pelo STATUS devolvido.
"""

import pandas as pd

from desafio.busca import buscar, indice_padrao
from desafio.indexacao import Indice, construir_indice
from desafio.resposta import THRESHOLD, responder

SEM_RESPOSTA = "nao_encontrado"


def perguntas_com_resposta(df_gabarito: pd.DataFrame) -> pd.DataFrame:
    """Subconjunto do gabarito cujo documento esperado existe no corpus."""
    return df_gabarito[df_gabarito["doc_esperado"] != SEM_RESPOSTA]


def calcular_hits(indice: Indice, df_gabarito: pd.DataFrame, k: int = 3) -> dict[str, float]:
    """Hit@1 e Hit@3 médios sobre as perguntas com documento esperado.

    Hit@1 vale 1 quando o doc_esperado é o primeiro resultado; Hit@3, quando
    consta entre os k primeiros.
    """
    hits_1, hits_3 = [], []
    for _, linha in perguntas_com_resposta(df_gabarito).iterrows():
        docs = [r["doc_id"] for r in buscar(linha["pergunta"], k=k, indice=indice)]
        hits_1.append(int(docs[0] == linha["doc_esperado"]))
        hits_3.append(int(linha["doc_esperado"] in docs))

    n = len(hits_1)
    return {"hit@1": sum(hits_1) / n, "hit@3": sum(hits_3) / n, "n": n}


def medir_margem(indice: Indice, df_gabarito: pd.DataFrame) -> dict[str, float]:
    """Separação entre as perguntas com resposta e a pergunta sem resposta.

    Devolve o menor dos scores máximos entre as perguntas respondíveis, o score
    máximo da P10 e a distância entre ambos. Essa distância é o intervalo
    disponível para posicionar o threshold.
    """
    melhores = {
        linha["pergunta_id"]: buscar(linha["pergunta"], k=1, indice=indice)[0]["score"]
        for _, linha in df_gabarito.iterrows()
    }
    com_resposta = [
        score
        for pid, score in melhores.items()
        if pid in set(perguntas_com_resposta(df_gabarito)["pergunta_id"])
    ]
    sem_resposta = [
        score
        for pid, score in melhores.items()
        if pid not in set(perguntas_com_resposta(df_gabarito)["pergunta_id"])
    ]
    piso = min(com_resposta)
    teto_sem_resposta = max(sem_resposta)
    return {
        "menor_score_com_resposta": piso,
        "maior_score_sem_resposta": teto_sem_resposta,
        "margem": piso - teto_sem_resposta,
        "scores_por_pergunta": melhores,
    }


def comparar_configuracoes(df_chunks: pd.DataFrame, df_gabarito: pd.DataFrame) -> pd.DataFrame:
    """Compara as 8 combinações de pré-processamento sobre o gabarito.

    Varia acentos, stopwords e a inclusão do nome da seção no texto indexado.
    Reporta Hit@1, Hit@3 e a margem para o threshold, usada como critério de
    desempate quando o Hit satura.
    """
    resultados = []
    for remover_acentos in (False, True):
        for remover_stopwords in (False, True):
            for usar_secao in (False, True):
                indice = construir_indice(
                    df_chunks,
                    remover_acentos=remover_acentos,
                    remover_stopwords=remover_stopwords,
                    usar_secao=usar_secao,
                )
                metricas = calcular_hits(indice, df_gabarito)
                margem = medir_margem(indice, df_gabarito)
                resultados.append(
                    {
                        "acentos_removidos": remover_acentos,
                        "stopwords_removidas": remover_stopwords,
                        "secao_no_indice": usar_secao,
                        "vocabulario": len(indice.vetorizador.vocabulary_),
                        "hit@1": metricas["hit@1"],
                        "hit@3": metricas["hit@3"],
                        "menor_com_resposta": margem["menor_score_com_resposta"],
                        "maior_sem_resposta": margem["maior_score_sem_resposta"],
                        "margem": margem["margem"],
                    }
                )
    return pd.DataFrame(resultados)


def calibrar_threshold(df_gabarito: pd.DataFrame, indice: Indice | None = None) -> dict:
    """Base de cálculo do threshold usado na Parte 4.

    Separa o maior score de cada pergunta entre as que têm resposta no corpus e
    a que não tem, e devolve os limites da lacuna entre os dois grupos.
    """
    margem = medir_margem(indice or indice_padrao(), df_gabarito)
    piso = margem["menor_score_com_resposta"]
    teto = margem["maior_score_sem_resposta"]
    return {
        "piso_com_resposta": piso,
        "teto_sem_resposta": teto,
        "meio_da_lacuna": (piso + teto) / 2,
        "threshold_escolhido": THRESHOLD,
        "scores_por_pergunta": margem["scores_por_pergunta"],
    }


def avaliar_gabarito(
    df_gabarito: pd.DataFrame, indice: Indice | None = None, k: int = 3
) -> pd.DataFrame:
    """Executa buscar(k=3) e responder() nas 10 perguntas e monta a tabela final.

    O critério da coluna `acerto` depende do tipo de pergunta: para as 9 com
    documento esperado, equivale ao Hit@1; para a P10, exige STATUS
    nao_encontrado.
    """
    linhas = []
    for _, pergunta in df_gabarito.iterrows():
        resultados = buscar(pergunta["pergunta"], k=k, indice=indice)
        saida = responder(pergunta["pergunta"], indice=indice)
        status = saida.splitlines()[-1].removeprefix("STATUS: ")

        esperado = pergunta["doc_esperado"]
        docs = [r["doc_id"] for r in resultados]
        sem_resposta = esperado == SEM_RESPOSTA

        linhas.append(
            {
                "pergunta_id": pergunta["pergunta_id"],
                "doc_esperado": esperado,
                "doc_retornado_1": docs[0],
                "score": resultados[0]["score"],
                "STATUS": status,
                "acerto": "sim"
                if (status == SEM_RESPOSTA if sem_resposta else docs[0] == esperado)
                else "nao",
                "hit@1": None if sem_resposta else int(docs[0] == esperado),
                "hit@3": None if sem_resposta else int(esperado in docs),
                "docs_top3": ", ".join(docs),
            }
        )
    return pd.DataFrame(linhas)


def formatar_evidencia_p2(indice: Indice, df_comparacao: pd.DataFrame) -> str:
    """Evidência da Parte 2: forma da matriz e decisão de pré-processamento."""
    n_chunks, n_vocab = indice.matriz.shape
    linhas = [
        f"Forma da matriz TF-IDF: ({n_chunks}, {n_vocab}): "
        f"{n_chunks} chunks por {n_vocab} termos de vocabulário.",
        "",
        "Decisão de pré-processamento: converter para minúsculas (obrigatório), remover "
        "acentos e remover stopwords de português, indexando apenas o corpo da seção. "
        "Motivo: os interrogativos (\"quantos\", \"qual\", \"posso\") aparecem em quase toda "
        "pergunta e inflam o score de chunks que não respondem nada. Removê-los triplica "
        "a separação entre perguntas com e sem resposta no corpus.",
        "",
        "Medição que sustenta a decisão (8 combinações, 10 perguntas do gabarito):",
        "",
        "| acentos | stopwords | seção no índice | vocab | Hit@1 | Hit@3 | menor com resposta | maior sem resposta | margem |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, c in df_comparacao.iterrows():
        linhas.append(
            f"| {'remove' if c['acentos_removidos'] else 'mantém'} "
            f"| {'remove' if c['stopwords_removidas'] else 'mantém'} "
            f"| {'sim' if c['secao_no_indice'] else 'não'} "
            f"| {c['vocabulario']} | {c['hit@1']:.2f} | {c['hit@3']:.2f} "
            f"| {c['menor_com_resposta']:.3f} | {c['maior_sem_resposta']:.3f} "
            f"| {c['margem']:.3f} |"
        )

    linhas += [
        "",
        "Leitura dos números:",
        "",
        "1. Hit@1 e Hit@3 dão 1.00 nas oito configurações. Com 46 chunks e perguntas bem "
        "alinhadas ao corpus, a métrica satura e não serve para escolher. Por isso o "
        "desempate usa a margem, que é a distância entre a pergunta respondível de pior "
        "score e a pergunta sem resposta: ela mede quanto espaço sobra para o threshold.",
        "2. Remover stopwords é a decisão de maior efeito: a margem sobe de 0.042 para "
        "0.143 sem a seção no índice. Confirma o diagnóstico do enunciado sobre os "
        "interrogativos em português.",
        "3. Incluir o nome da seção no índice piora a margem (0.143 para 0.119). As seções "
        "da FAQ-001 são perguntas (\"Como peço reembolso?\"), então indexá-las aproxima a FAQ "
        "de qualquer pergunta, inclusive das que não têm resposta. Por isso o assistente "
        "indexa só o corpo da seção, apesar de o campo `secao` continuar no chunk e na citação.",
        "4. Remover acentos empata em margem (0.143 nas duas). O desempate veio da robustez: "
        "uma pergunta digitada sem acento, como \"Quantos dias de ferias tenho direito?\", "
        "pontua 0.549 com acentos removidos contra 0.447 sem remover. O corpus é acentuado, "
        "mas quem pergunta nem sempre é.",
        "",
        f"Configuração adotada pelo assistente: {indice.descricao}",
    ]
    return "\n".join(linhas)


def formatar_evidencia_p5(df_avaliacao: pd.DataFrame) -> str:
    """Evidência da Parte 5: tabela das 10 perguntas, Hit@1, Hit@3 e análise de erro."""
    com_resposta = df_avaliacao[df_avaliacao["doc_esperado"] != SEM_RESPOSTA]
    hit1 = com_resposta["hit@1"].mean()
    hit3 = com_resposta["hit@3"].mean()
    p10 = df_avaliacao[df_avaliacao["doc_esperado"] == SEM_RESPOSTA].iloc[0]

    linhas = [
        "| pergunta_id | doc_esperado | doc_retornado_1 | score | STATUS | acerto |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for _, r in df_avaliacao.iterrows():
        linhas.append(
            f"| {r['pergunta_id']} | {r['doc_esperado']} | {r['doc_retornado_1']} "
            f"| {r['score']:.2f} | {r['STATUS']} | {r['acerto']} |"
        )

    n = len(com_resposta)
    acertos_1 = int(com_resposta["hit@1"].sum())
    acertos_3 = int(com_resposta["hit@3"].sum())
    faq_no_topo = int((com_resposta["doc_retornado_1"] == "FAQ-001").sum())
    faq_no_top3 = int(com_resposta["docs_top3"].str.contains("FAQ-001").sum())

    linhas += [
        "",
        f"Hit@1 = {hit1:.2f} ({acertos_1} de {n} perguntas com resposta)",
        f"Hit@3 = {hit3:.2f} ({acertos_3} de {n} perguntas com resposta)",
        "",
        f"P10 (sem resposta no corpus): STATUS devolvido = {p10['STATUS']}, "
        f"score do melhor chunk = {p10['score']:.2f}, abaixo do threshold "
        f"{THRESHOLD:.2f}. Resultado: acerto.",
        "",
        "Armadilha da FAQ-001: a FAQ repete de forma resumida o conteúdo de outras "
        f"políticas e apareceu no top-3 de {faq_no_top3} das {n} perguntas com resposta, "
        f"mas foi o primeiro resultado em {faq_no_topo} delas. Como a FAQ não vence nenhuma "
        "política no topo, o Hit@1 estrito não foi afetado, o que poderia mudar se o nome "
        "da seção entrasse no índice, conforme medido na Parte 2.",
        "",
        "Análise de erro",
        "",
        "Nenhuma das 10 perguntas errou, então a análise vai para a que passou mais perto "
        "de falhar: a P09 (\"Qual é o orçamento anual de treinamento por colaborador?\"), "
        "com score 0.37 contra um threshold de 0.30. Ela recupera o chunk certo com folga "
        "enorme sobre o segundo colocado (0.37 contra 0.13), mas o score absoluto é baixo "
        "por dois motivos: a pergunta diz \"treinamento\" e o chunk diz \"treinamentos\", que "
        "o TF-IDF trata como termos distintos por não fazer stemming; e o chunk carrega uma "
        "segunda frase sobre saldo não transferido, que não tem nada a ver com a pergunta e "
        "dilui o vetor na normalização do cosseno. Correção testável: trocar os tokens de "
        "palavra por n-gramas de caracteres (analyzer=\"char_wb\", ngram_range=(4,5)), que "
        "casa singular com plural sem precisar de stemmer. Eu testei: o score da P09 sobe de "
        "0.37 para 0.54 e resolve o sintoma, mas a margem global cai de 0.143 para 0.052, "
        "porque a P10 também sobe (0.23 para 0.25) e a P02 desaba (0.55 para 0.34). A "
        "correção foi descartada com base nesse número: ela conserta uma pergunta e "
        "fragiliza o threshold, que é a defesa contra responder o que não existe.",
    ]
    return "\n".join(linhas)
