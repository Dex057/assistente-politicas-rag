# Evidências de teste

Suíte executável com `unittest` da biblioteca padrão, sem dependência além das
já usadas no projeto.

```
python -m unittest testes -v
```

Gerado em 26/09/2026 18:27.

## Execução completa

```
test_le_os_doze_documentos (testes.TesteParte0Corpus.test_le_os_doze_documentos) ... ok
test_status_tem_onze_vigentes_e_um_revogado (testes.TesteParte0Corpus.test_status_tem_onze_vigentes_e_um_revogado) ... ok
test_todo_documento_tem_texto_nao_vazio (testes.TesteParte0Corpus.test_todo_documento_tem_texto_nao_vazio) ... ok
test_validacao_rejeita_corpus_incompleto (testes.TesteParte0Corpus.test_validacao_rejeita_corpus_incompleto) ... ok
test_cabecalho_fica_fora_dos_chunks (testes.TesteParte1Chunking.test_cabecalho_fica_fora_dos_chunks) ... ok
test_gera_um_chunk_por_secao (testes.TesteParte1Chunking.test_gera_um_chunk_por_secao) ... ok
test_secao_sem_corpo_nao_quebra_a_divisao (testes.TesteParte1Chunking.test_secao_sem_corpo_nao_quebra_a_divisao) ... ok
test_texto_do_chunk_e_literal_ao_documento (testes.TesteParte1Chunking.test_texto_do_chunk_e_literal_ao_documento) ... ok
test_todo_chunk_tem_os_campos_obrigatorios (testes.TesteParte1Chunking.test_todo_chunk_tem_os_campos_obrigatorios) ... ok
test_indice_cobre_tambem_documentos_revogados (testes.TesteParte2Indexacao.test_indice_cobre_tambem_documentos_revogados) ... ok
test_matriz_tem_uma_linha_por_chunk (testes.TesteParte2Indexacao.test_matriz_tem_uma_linha_por_chunk) ... ok
test_remocao_de_acentos_normaliza_o_vocabulario (testes.TesteParte2Indexacao.test_remocao_de_acentos_normaliza_o_vocabulario) ... ok
test_stopwords_ficam_fora_do_vocabulario (testes.TesteParte2Indexacao.test_stopwords_ficam_fora_do_vocabulario) ... ok
test_vocabulario_corresponde_as_colunas_da_matriz (testes.TesteParte2Indexacao.test_vocabulario_corresponde_as_colunas_da_matriz) ... ok
test_desempate_preserva_a_ordem_do_corpus (testes.TesteParte3Busca.test_desempate_preserva_a_ordem_do_corpus)
Com scores empatados, devem vencer os chunks de menor índice. ... ok
test_devolve_exatamente_k_resultados (testes.TesteParte3Busca.test_devolve_exatamente_k_resultados) ... ok
test_p02_recupera_pol005_e_nao_pol004 (testes.TesteParte3Busca.test_p02_recupera_pol005_e_nao_pol004) ... ok
test_pergunta_vazia_nao_quebra_a_busca (testes.TesteParte3Busca.test_pergunta_vazia_nao_quebra_a_busca) ... ok
test_regra_de_vigencia_exclui_revogados (testes.TesteParte3Busca.test_regra_de_vigencia_exclui_revogados) ... ok
test_resultados_vem_ordenados_por_score (testes.TesteParte3Busca.test_resultados_vem_ordenados_por_score) ... ok
test_sem_a_regra_a_pol004_revogada_venceria (testes.TesteParte3Busca.test_sem_a_regra_a_pol004_revogada_venceria)
Armadilha 1: confirma que o filtro de vigência é o que evita o erro. ... ok
test_fonte_cita_documento_e_secao (testes.TesteParte4Resposta.test_fonte_cita_documento_e_secao) ... ok
test_p10_cai_na_regra_de_nao_encontrado (testes.TesteParte4Resposta.test_p10_cai_na_regra_de_nao_encontrado) ... ok
test_resposta_e_extrativa (testes.TesteParte4Resposta.test_resposta_e_extrativa)
A RESPOSTA precisa ser cópia literal de um trecho do documento citado. ... ok
test_saida_nao_usa_simbolo_grafico (testes.TesteParte4Resposta.test_saida_nao_usa_simbolo_grafico) ... ok
test_saida_tem_os_cinco_campos_na_ordem (testes.TesteParte4Resposta.test_saida_tem_os_cinco_campos_na_ordem) ... ok
test_score_sai_com_duas_casas_decimais (testes.TesteParte4Resposta.test_score_sai_com_duas_casas_decimais) ... ok
test_status_aceita_apenas_dois_valores (testes.TesteParte4Resposta.test_status_aceita_apenas_dois_valores) ... ok
test_threshold_alto_forca_nao_encontrado (testes.TesteParte4Resposta.test_threshold_alto_forca_nao_encontrado) ... ok
test_threshold_fica_dentro_da_lacuna_medida (testes.TesteParte4Resposta.test_threshold_fica_dentro_da_lacuna_medida) ... ok
test_avalia_as_dez_perguntas (testes.TesteParte5Avaliacao.test_avalia_as_dez_perguntas) ... ok
test_comparacao_cobre_as_oito_configuracoes (testes.TesteParte5Avaliacao.test_comparacao_cobre_as_oito_configuracoes) ... ok
test_faq_nao_vence_a_politica_de_origem (testes.TesteParte5Avaliacao.test_faq_nao_vence_a_politica_de_origem)
Armadilha 2: a FAQ pode aparecer no top-3, mas não no primeiro lugar. ... ok
test_hit1_e_hit3_atingem_o_esperado (testes.TesteParte5Avaliacao.test_hit1_e_hit3_atingem_o_esperado) ... ok
test_hit3_nunca_e_menor_que_hit1 (testes.TesteParte5Avaliacao.test_hit3_nunca_e_menor_que_hit1) ... ok
test_metricas_usam_as_nove_perguntas_com_resposta (testes.TesteParte5Avaliacao.test_metricas_usam_as_nove_perguntas_com_resposta) ... ok
test_p10_e_contabilizada_pelo_status (testes.TesteParte5Avaliacao.test_p10_e_contabilizada_pelo_status) ... ok
test_execucao_e_deterministica (testes.TestePipelineCompleto.test_execucao_e_deterministica) ... ok
test_gera_as_seis_partes_em_ordem (testes.TestePipelineCompleto.test_gera_as_seis_partes_em_ordem) ... ok
test_nao_escreve_na_pasta_de_insumos (testes.TestePipelineCompleto.test_nao_escreve_na_pasta_de_insumos) ... ok
test_reflexao_respeita_o_limite_de_palavras (testes.TestePipelineCompleto.test_reflexao_respeita_o_limite_de_palavras) ... ok

----------------------------------------------------------------------
Ran 41 tests in 1.281s

OK
```

## Validação da suíte por mutação

Um teste que nunca falha não prova nada. Cada regra do enunciado foi quebrada
deliberadamente no código para confirmar que a suíte detecta a violação. O
código foi restaurado após cada mutação.

| # | Mutação aplicada | Regra violada | Resultado |
| --- | --- | --- | --- |
| 1 | `if apenas_vigentes:` para `if False:` | Regra de vigência (P3) | detectada, 2 falhas |
| 2 | Cabeçalho passa a entrar no chunk | Exclusão do cabeçalho (P1) | detectada, 3 falhas |
| 3 | `THRESHOLD` de 0.30 para 0.01 | Regra de não encontrado (P4) | detectada, 2 falhas |
| 4 | Resposta reescrita em vez de copiada | Resposta extrativa (P4) | detectada, 1 falha |
| 5 | `argsort` estável para `argsort()[::-1]` | Desempate do top-k (P3) | detectada, 1 falha |
| 6 | P10 entra no cálculo das métricas | Métricas sobre 9 perguntas (P5) | detectada, 1 falha |

A mutação 5 passou despercebida na primeira rodada: o teste de desempate
verificava apenas que duas chamadas iguais devolvem o mesmo resultado, o que
continua verdadeiro com a ordenação invertida. O teste foi reescrito para exigir
que, em caso de empate, prevaleçam os chunks de menor índice no corpus.

## Cobertura por Parte

| Parte | Testes | Verificações principais |
| --- | --- | --- |
| P0 | 4 | 12 documentos, texto não vazio, 11 vigentes e 1 revogado, validação rejeita corpus incompleto |
| P1 | 5 | Um chunk por seção contada no disco, cabeçalho excluído, campos obrigatórios, texto literal ao documento, seção vazia |
| P2 | 5 | Dimensões da matriz, vocabulário, stopwords fora do índice, acentos normalizados, revogados indexados |
| P3 | 7 | Tamanho e ordenação do top-k, vigência em todas as perguntas, P02 sem POL-004, POL-004 venceria sem o filtro, pergunta vazia, desempate |
| P4 | 9 | Cinco campos na ordem, STATUS restrito, score com duas casas, resposta extrativa, formato da FONTE, P10, threshold dentro da lacuna, threshold alto, ausência de símbolo gráfico |
| P5 | 7 | 10 perguntas avaliadas, métricas sobre 9, Hit@1 e Hit@3, coerência entre métricas, P10 pelo STATUS, FAQ não vence a política, 8 configurações |
| Pipeline | 4 | Seis Partes em ordem, execução determinística, insumos não modificados, limite de palavras da reflexão |

## Armadilhas do README_insumos.md

As três armadilhas documentadas têm teste dedicado:

1. POL-004 revogada contra POL-005 vigente: `test_p02_recupera_pol005_e_nao_pol004`
   e `test_sem_a_regra_a_pol004_revogada_venceria`, que confirma que a POL-004
   assumiria o primeiro lugar sem o filtro.
2. FAQ-001 duplicando conteúdo: `test_faq_nao_vence_a_politica_de_origem`.
3. P10 sem resposta no corpus: `test_p10_cai_na_regra_de_nao_encontrado` e
   `test_p10_e_contabilizada_pelo_status`.
