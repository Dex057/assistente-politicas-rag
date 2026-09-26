"""Parte 1: chunking por seção.

Cada seção marcada com "##" gera um chunk. O cabeçalho do documento (título
"# ..." e linha "Empresa: ...") é excluído, por já constar em metadados.csv.
"""

import pandas as pd

MARCADOR_SECAO = "## "


def dividir_em_secoes(texto: str) -> list[tuple[str, str]]:
    """Divide o documento em pares (nome_da_secao, texto_da_secao).

    Conteúdo anterior à primeira seção é descartado, o que exclui o cabeçalho.
    """
    secoes: list[tuple[str, list[str]]] = []
    for linha in texto.splitlines():
        if linha.startswith(MARCADOR_SECAO):
            secoes.append((linha[len(MARCADOR_SECAO):].strip(), []))
        elif secoes:
            secoes[-1][1].append(linha)

    return [(nome, "\n".join(corpo).strip()) for nome, corpo in secoes]


def construir_chunks(df_docs: pd.DataFrame) -> pd.DataFrame:
    """DataFrame de chunks a partir dos documentos lidos na Parte 0.

    Produz duas representações do mesmo chunk:
      `texto`           corpo da seção, sem alteração, usado como RESPOSTA extrativa.
      `texto_indexado`  nome da seção somado ao corpo, alternativa para o TF-IDF.

    Manter as duas separadas impede que o nome da seção entre na resposta
    copiada. Qual delas indexar é definido pela medição da Parte 2.
    """
    registros = []
    for _, doc in df_docs.iterrows():
        for nome_secao, texto_secao in dividir_em_secoes(doc["texto"]):
            registros.append(
                {
                    "doc_id": doc["doc_id"],
                    "titulo": doc["titulo"],
                    "secao": nome_secao,
                    "status": doc["status"],
                    "texto": texto_secao,
                    "texto_indexado": f"{nome_secao}\n{texto_secao}",
                }
            )
    return pd.DataFrame(registros)


def formatar_evidencia_p1(df_chunks: pd.DataFrame) -> str:
    """Evidência da Parte 1: total, contagem por documento e um chunk completo."""
    por_doc = df_chunks.groupby("doc_id", sort=False).size()
    tamanhos = df_chunks["texto"].str.split().map(len)

    linhas = [f"Total de chunks gerados: {len(df_chunks)}", ""]
    linhas.append("| doc_id | n_chunks |")
    linhas.append("| --- | --- |")
    for doc_id, n in por_doc.items():
        linhas.append(f"| {doc_id} | {n} |")

    linhas += [
        "",
        "Observação sobre tamanhos: os chunks têm entre "
        f"{tamanhos.min()} e {tamanhos.max()} palavras (média "
        f"{tamanhos.mean():.1f}). São trechos curtos e autocontidos, o que "
        "favorece a resposta extrativa: o chunk de maior score já é uma "
        "resposta legível, sem precisar de corte adicional.",
        "",
        "Exemplo completo de chunk (todos os campos):",
        "",
    ]

    exemplo = df_chunks[
        (df_chunks["doc_id"] == "POL-005")
        & (df_chunks["secao"] == "Regra de trabalho remoto")
    ].iloc[0]
    for campo in ["doc_id", "titulo", "secao", "status", "texto", "texto_indexado"]:
        valor = str(exemplo[campo]).replace("\n", "\n              ")
        linhas.append(f"    {campo:<14}: {valor}")

    return "\n".join(linhas)
