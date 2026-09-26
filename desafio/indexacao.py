"""Parte 2: indexação com TF-IDF.

Vetoriza o texto dos chunks. As opções de pré-processamento (acentos,
stopwords) e a escolha da coluna a indexar são parâmetros, comparados em
`avaliacao.comparar_configuracoes`.
"""

import unicodedata
from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# O scikit-learn fornece stopwords apenas para inglês. Além dos conectivos, a
# lista cobre os interrogativos ("quantos", "qual", "posso"), que ocorrem tanto
# nas perguntas quanto no corpus e elevam o score de chunks sem relação
# semântica com a pergunta.
STOPWORDS_PT = [
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as",
    "até", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles",
    "depois", "devo", "do", "dos", "e", "ela", "elas", "ele", "eles", "em",
    "entre", "era", "eram", "essa", "essas", "esse", "esses", "esta", "estas",
    "este", "estes", "eu", "foi", "for", "há", "isso", "isto", "já", "lhe",
    "lhes", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas",
    "muito", "na", "nas", "nem", "no", "nos", "nós", "num", "numa", "o", "onde",
    "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "posso",
    "pode", "podem", "qual", "quais", "quando", "quanto", "quantos", "quantas",
    "que", "quem", "se", "sem", "ser", "seu", "seus", "só", "sua", "suas",
    "são", "também", "te", "tem", "tenho", "ter", "teu", "um", "uma", "vocé",
    "você", "é",
]


@dataclass
class Indice:
    """Vetorizador ajustado, matriz TF-IDF dos chunks e os chunks correspondentes."""

    vetorizador: TfidfVectorizer
    matriz: Any
    df_chunks: pd.DataFrame
    config: dict[str, bool]

    @property
    def descricao(self) -> str:
        return (
            f"acentos_removidos={self.config['remover_acentos']}, "
            f"stopwords_removidas={self.config['remover_stopwords']}, "
            f"secao_no_indice={self.config['usar_secao']}"
        )


def _sem_acentos(palavra: str) -> str:
    """Remove acentos, equivalente a strip_accents="unicode" do TfidfVectorizer."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", palavra) if not unicodedata.combining(c)
    )


def construir_indice(
    df_chunks: pd.DataFrame,
    remover_acentos: bool = True,
    remover_stopwords: bool = True,
    usar_secao: bool = False,
) -> Indice:
    """Ajusta o TF-IDF sobre os chunks e devolve o índice.

    Os valores padrão reproduzem a configuração selecionada na Parte 2, de modo
    que `busca.buscar` importado isoladamente se comporte como o pipeline.

    Documentos revogados também são indexados: a regra de vigência atua no
    ranqueamento (Parte 3), não na indexação. Isso mantém o IDF calculado sobre
    o corpus completo e permite comparar a busca com e sem o filtro.
    """
    stopwords = None
    if remover_stopwords:
        # A lista recebe a mesma normalização do analisador. Sem isso o
        # scikit-learn emite UserWarning de inconsistência e parte das
        # stopwords nunca é casada.
        stopwords = sorted({_sem_acentos(p) if remover_acentos else p for p in STOPWORDS_PT})

    vetorizador = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode" if remover_acentos else None,
        stop_words=stopwords,
    )
    coluna = "texto_indexado" if usar_secao else "texto"
    matriz = vetorizador.fit_transform(df_chunks[coluna])

    return Indice(
        vetorizador=vetorizador,
        matriz=matriz,
        df_chunks=df_chunks.reset_index(drop=True),
        config={
            "remover_acentos": remover_acentos,
            "remover_stopwords": remover_stopwords,
            "usar_secao": usar_secao,
        },
    )
