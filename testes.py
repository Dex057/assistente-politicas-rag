"""Suíte de testes de ponta a ponta do assistente.

Valida cada exigência do enunciado, da leitura do corpus (Parte 0) até as
métricas do gabarito (Parte 5), além das três armadilhas documentadas em
README_insumos.md.

Uso:
    python -m unittest testes -v
"""

import re
import unittest
from pathlib import Path

from desafio import avaliacao, busca, chunking, corpus, indexacao, main, resposta

CAMPOS_SAIDA = ["PERGUNTA", "RESPOSTA", "FONTE", "SCORE", "STATUS"]


class BaseAssistente(unittest.TestCase):
    """Constrói o corpus, os chunks e o índice uma única vez para toda a suíte."""

    @classmethod
    def setUpClass(cls):
        cls.df_docs = corpus.carregar_corpus()
        cls.df_chunks = chunking.construir_chunks(cls.df_docs)
        cls.df_gabarito = corpus.carregar_gabarito()
        cls.indice = indexacao.construir_indice(cls.df_chunks, **main.CONFIG_INDICE)
        busca.definir_indice_padrao(cls.indice)

    def pergunta(self, pergunta_id: str) -> str:
        linha = self.df_gabarito["pergunta_id"] == pergunta_id
        return self.df_gabarito.loc[linha, "pergunta"].iloc[0]


class TesteParte0Corpus(BaseAssistente):
    def test_le_os_doze_documentos(self):
        self.assertEqual(len(self.df_docs), 12)

    def test_todo_documento_tem_texto_nao_vazio(self):
        self.assertTrue((self.df_docs["texto"].str.strip().str.len() > 0).all())

    def test_status_tem_onze_vigentes_e_um_revogado(self):
        contagem = corpus.validar_corpus(self.df_docs)
        self.assertEqual(contagem["vigente"], 11)
        self.assertEqual(contagem["revogada"], 1)

    def test_validacao_rejeita_corpus_incompleto(self):
        with self.assertRaises(ValueError):
            corpus.validar_corpus(self.df_docs.head(11))


class TesteParte1Chunking(BaseAssistente):
    def test_gera_um_chunk_por_secao(self):
        secoes_no_disco = sum(
            texto.count("\n## ") + texto.startswith("## ")
            for texto in self.df_docs["texto"]
        )
        self.assertEqual(len(self.df_chunks), secoes_no_disco)

    def test_cabecalho_fica_fora_dos_chunks(self):
        self.assertFalse(self.df_chunks["texto"].str.contains("Empresa:").any())
        self.assertFalse(self.df_chunks["texto"].str.startswith("# ").any())

    def test_todo_chunk_tem_os_campos_obrigatorios(self):
        for campo in ["doc_id", "titulo", "secao", "status", "texto"]:
            self.assertIn(campo, self.df_chunks.columns)
            self.assertFalse(self.df_chunks[campo].isna().any(), campo)

    def test_texto_do_chunk_e_literal_ao_documento(self):
        for _, chunk in self.df_chunks.iterrows():
            original = self.df_docs.loc[
                self.df_docs["doc_id"] == chunk["doc_id"], "texto"
            ].iloc[0]
            self.assertIn(chunk["texto"], original, chunk["secao"])

    def test_secao_sem_corpo_nao_quebra_a_divisao(self):
        secoes = chunking.dividir_em_secoes("# Doc\nEmpresa: X\n\n## Vazia\n\n## Cheia\ntexto")
        self.assertEqual(secoes, [("Vazia", ""), ("Cheia", "texto")])


class TesteParte2Indexacao(BaseAssistente):
    def test_matriz_tem_uma_linha_por_chunk(self):
        self.assertEqual(self.indice.matriz.shape[0], len(self.df_chunks))

    def test_vocabulario_corresponde_as_colunas_da_matriz(self):
        self.assertEqual(self.indice.matriz.shape[1], len(self.indice.vetorizador.vocabulary_))

    def test_stopwords_ficam_fora_do_vocabulario(self):
        for stopword in ["qual", "quantos", "posso"]:
            self.assertNotIn(stopword, self.indice.vetorizador.vocabulary_)

    def test_remocao_de_acentos_normaliza_o_vocabulario(self):
        self.assertIn("ferias", self.indice.vetorizador.vocabulary_)
        self.assertNotIn("férias", self.indice.vetorizador.vocabulary_)

    def test_indice_cobre_tambem_documentos_revogados(self):
        revogados = self.indice.df_chunks["status"] == "revogada"
        self.assertGreater(revogados.sum(), 0)


class TesteParte3Busca(BaseAssistente):
    def test_devolve_exatamente_k_resultados(self):
        for k in (1, 3, 5):
            self.assertEqual(len(busca.buscar(self.pergunta("P01"), k=k)), k)

    def test_resultados_vem_ordenados_por_score(self):
        scores = [r["score"] for r in busca.buscar(self.pergunta("P01"), k=5)]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_regra_de_vigencia_exclui_revogados(self):
        for _, linha in self.df_gabarito.iterrows():
            resultados = busca.buscar(linha["pergunta"], k=3)
            self.assertTrue(all(r["status"] == "vigente" for r in resultados))

    def test_p02_recupera_pol005_e_nao_pol004(self):
        docs = [r["doc_id"] for r in busca.buscar(self.pergunta("P02"), k=3)]
        self.assertEqual(docs[0], "POL-005")
        self.assertNotIn("POL-004", docs)

    def test_sem_a_regra_a_pol004_revogada_venceria(self):
        """Armadilha 1: confirma que o filtro de vigência é o que evita o erro."""
        docs = [r["doc_id"] for r in busca.buscar(self.pergunta("P02"), k=3, apenas_vigentes=False)]
        self.assertEqual(docs[0], "POL-004")

    def test_pergunta_vazia_nao_quebra_a_busca(self):
        resultados = busca.buscar("", k=3)
        self.assertEqual(len(resultados), 3)
        self.assertTrue(all(r["score"] == 0.0 for r in resultados))

    def test_desempate_preserva_a_ordem_do_corpus(self):
        """Com scores empatados, devem vencer os chunks de menor índice."""
        vigentes = self.indice.df_chunks[self.indice.df_chunks["status"] == "vigente"]
        esperado = list(zip(vigentes["doc_id"].head(5), vigentes["secao"].head(5)))
        obtido = [(r["doc_id"], r["secao"]) for r in busca.buscar("", k=5)]
        self.assertEqual(obtido, esperado)


class TesteParte4Resposta(BaseAssistente):
    def test_saida_tem_os_cinco_campos_na_ordem(self):
        linhas = resposta.responder(self.pergunta("P02")).splitlines()
        self.assertEqual([linha.split(":")[0] for linha in linhas], CAMPOS_SAIDA)

    def test_status_aceita_apenas_dois_valores(self):
        for _, linha in self.df_gabarito.iterrows():
            status = resposta.responder(linha["pergunta"]).splitlines()[-1]
            self.assertIn(status, ["STATUS: encontrado", "STATUS: nao_encontrado"])

    def test_score_sai_com_duas_casas_decimais(self):
        saida = resposta.responder(self.pergunta("P02"))
        self.assertRegex(saida, r"\nSCORE: \d+\.\d{2}\n")

    def test_resposta_e_extrativa(self):
        """A RESPOSTA precisa ser cópia literal de um trecho do documento citado."""
        for _, linha in self.df_gabarito.iterrows():
            saida = resposta.responder(linha["pergunta"])
            if "STATUS: nao_encontrado" in saida:
                continue
            texto = re.search(r"RESPOSTA: (.*?)\nFONTE:", saida, re.S).group(1)
            doc_id = re.search(r"FONTE: ([\w-]+) \|", saida).group(1)
            arquivo = self.df_docs.loc[self.df_docs["doc_id"] == doc_id, "arquivo"].iloc[0]
            original = (corpus.CORPUS / arquivo).read_text(encoding="utf-8")
            self.assertIn(texto, original, linha["pergunta_id"])

    def test_fonte_cita_documento_e_secao(self):
        fonte = [
            linha for linha in resposta.responder(self.pergunta("P02")).splitlines()
            if linha.startswith("FONTE:")
        ][0]
        self.assertRegex(fonte, r"^FONTE: [\w-]+ \| .+ \| Seção: .+$")

    def test_p10_cai_na_regra_de_nao_encontrado(self):
        saida = resposta.responder(self.pergunta("P10"))
        self.assertIn("STATUS: nao_encontrado", saida)
        self.assertIn("FONTE: nenhuma", saida)
        self.assertIn(resposta.MENSAGEM_NAO_ENCONTRADO, saida)

    def test_threshold_fica_dentro_da_lacuna_medida(self):
        calibracao = avaliacao.calibrar_threshold(self.df_gabarito, self.indice)
        self.assertGreater(resposta.THRESHOLD, calibracao["teto_sem_resposta"])
        self.assertLess(resposta.THRESHOLD, calibracao["piso_com_resposta"])

    def test_threshold_alto_forca_nao_encontrado(self):
        saida = resposta.responder(self.pergunta("P02"), threshold=0.99)
        self.assertIn("STATUS: nao_encontrado", saida)

    def test_saida_nao_usa_simbolo_grafico(self):
        for _, linha in self.df_gabarito.iterrows():
            saida = resposta.responder(linha["pergunta"])
            self.assertTrue(saida.isprintable() or "\n" in saida)
            self.assertNotRegex(saida, r"[✅❌⚠\U0001F300-\U0001FAFF]")


class TesteParte5Avaliacao(BaseAssistente):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tabela = avaliacao.avaliar_gabarito(cls.df_gabarito, cls.indice)

    def test_avalia_as_dez_perguntas(self):
        self.assertEqual(len(self.tabela), 10)

    def test_metricas_usam_as_nove_perguntas_com_resposta(self):
        metricas = avaliacao.calcular_hits(self.indice, self.df_gabarito)
        self.assertEqual(metricas["n"], 9)

    def test_hit1_e_hit3_atingem_o_esperado(self):
        metricas = avaliacao.calcular_hits(self.indice, self.df_gabarito)
        self.assertEqual(metricas["hit@1"], 1.0)
        self.assertEqual(metricas["hit@3"], 1.0)

    def test_hit3_nunca_e_menor_que_hit1(self):
        metricas = avaliacao.calcular_hits(self.indice, self.df_gabarito)
        self.assertGreaterEqual(metricas["hit@3"], metricas["hit@1"])

    def test_p10_e_contabilizada_pelo_status(self):
        p10 = self.tabela[self.tabela["pergunta_id"] == "P10"].iloc[0]
        self.assertEqual(p10["STATUS"], "nao_encontrado")
        self.assertEqual(p10["acerto"], "sim")
        self.assertTrue(self.tabela[self.tabela["pergunta_id"] == "P10"]["hit@1"].isna().all())

    def test_faq_nao_vence_a_politica_de_origem(self):
        """Armadilha 2: a FAQ pode aparecer no top-3, mas não no primeiro lugar."""
        com_resposta = self.tabela[self.tabela["doc_esperado"] != "nao_encontrado"]
        self.assertNotIn("FAQ-001", com_resposta["doc_retornado_1"].tolist())

    def test_comparacao_cobre_as_oito_configuracoes(self):
        comparacao = avaliacao.comparar_configuracoes(self.df_chunks, self.df_gabarito)
        self.assertEqual(len(comparacao), 8)
        self.assertTrue((comparacao["margem"] > 0).all())


class TestePipelineCompleto(unittest.TestCase):
    def test_gera_as_seis_partes_em_ordem(self):
        documento = main.executar()
        titulos = re.findall(r"^## (Parte \d)", documento, re.M)
        self.assertEqual(titulos, [f"Parte {i}" for i in range(6)])

    def test_execucao_e_deterministica(self):
        self.assertEqual(main.executar(), main.executar())

    def test_nao_escreve_na_pasta_de_insumos(self):
        antes = {
            caminho: caminho.stat().st_mtime
            for caminho in sorted(corpus.INSUMOS.rglob("*"))
            if caminho.is_file()
        }
        main.executar()
        depois = {
            caminho: caminho.stat().st_mtime
            for caminho in sorted(corpus.INSUMOS.rglob("*"))
            if caminho.is_file()
        }
        self.assertEqual(antes, depois)

    def test_reflexao_respeita_o_limite_de_palavras(self):
        palavras = len(Path("reflexao.md").read_text(encoding="utf-8").split())
        self.assertGreaterEqual(palavras, 150)
        self.assertLessEqual(palavras, 300)


if __name__ == "__main__":
    unittest.main(verbosity=2)
