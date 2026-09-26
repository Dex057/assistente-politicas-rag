# Saídas do Desafio Bootcamp SEP26

Assistente de perguntas e respostas sobre políticas internas (RAG com recuperação
local, TF-IDF + similaridade do cosseno, resposta extrativa).

Arquivo gerado por `python desafio/main.py`. A execução é determinística: rodar de
novo reproduz exatamente estes números.


---

## Parte 0 - Setup e leitura do corpus

| doc_id | titulo | status | n_palavras |
| --- | --- | --- | --- |
| POL-001 | Política de Onboarding | vigente | 164 |
| POL-002 | Política de Férias | vigente | 136 |
| POL-003 | Política de Benefícios | vigente | 128 |
| POL-004 | Política de Home Office (versão 1) | revogada | 90 |
| POL-005 | Política de Trabalho Híbrido (versão 2) | vigente | 119 |
| POL-006 | Política de Reembolso de Despesas | vigente | 117 |
| POL-007 | Política de Avaliação de Desempenho | vigente | 114 |
| POL-008 | Política de Desligamento | vigente | 119 |
| POL-009 | Política de Segurança da Informação | vigente | 142 |
| POL-010 | Política de Treinamento e Desenvolvimento | vigente | 92 |
| POL-011 | Código de Conduta e Canal de Denúncias | vigente | 102 |
| FAQ-001 | Perguntas Frequentes de Novos Colaboradores | vigente | 145 |

Total de documentos lidos: 12
Contagem por status: revogada = 1, vigente = 11
Total de palavras no corpus: 1468

---

## Parte 1 - Chunking por seção

Total de chunks gerados: 46

| doc_id | n_chunks |
| --- | --- |
| POL-001 | 3 |
| POL-002 | 4 |
| POL-003 | 4 |
| POL-004 | 3 |
| POL-005 | 3 |
| POL-006 | 4 |
| POL-007 | 4 |
| POL-008 | 4 |
| POL-009 | 4 |
| POL-010 | 3 |
| POL-011 | 4 |
| FAQ-001 | 6 |

Observação sobre tamanhos: os chunks têm entre 10 e 64 palavras (média 21.0). São trechos curtos e autocontidos, o que favorece a resposta extrativa: o chunk de maior score já é uma resposta legível, sem precisar de corte adicional.

Exemplo completo de chunk (todos os campos):

    doc_id        : POL-005
    titulo        : Política de Trabalho Híbrido (versão 2)
    secao         : Regra de trabalho remoto
    status        : vigente
    texto         : O colaborador pode trabalhar de forma remota em até 3 dias por semana. Os dias presenciais obrigatórios são terça-feira e quinta-feira.
    texto_indexado: Regra de trabalho remoto
              O colaborador pode trabalhar de forma remota em até 3 dias por semana. Os dias presenciais obrigatórios são terça-feira e quinta-feira.

---

## Parte 2 - Indexação com TF-IDF

Forma da matriz TF-IDF: (46, 311): 46 chunks por 311 termos de vocabulário.

Decisão de pré-processamento: converter para minúsculas (obrigatório), remover acentos e remover stopwords de português, indexando apenas o corpo da seção. Motivo: os interrogativos ("quantos", "qual", "posso") aparecem em quase toda pergunta e inflam o score de chunks que não respondem nada. Removê-los triplica a separação entre perguntas com e sem resposta no corpus.

Medição que sustenta a decisão (8 combinações, 10 perguntas do gabarito):

| acentos | stopwords | seção no índice | vocab | Hit@1 | Hit@3 | menor com resposta | maior sem resposta | margem |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mantém | mantém | não | 350 | 1.00 | 1.00 | 0.308 | 0.266 | 0.042 |
| mantém | mantém | sim | 366 | 1.00 | 1.00 | 0.300 | 0.215 | 0.086 |
| mantém | remove | não | 313 | 1.00 | 1.00 | 0.368 | 0.225 | 0.143 |
| mantém | remove | sim | 324 | 1.00 | 1.00 | 0.331 | 0.212 | 0.119 |
| remove | mantém | não | 348 | 1.00 | 1.00 | 0.308 | 0.266 | 0.042 |
| remove | mantém | sim | 364 | 1.00 | 1.00 | 0.301 | 0.215 | 0.086 |
| remove | remove | não | 311 | 1.00 | 1.00 | 0.368 | 0.225 | 0.143 |
| remove | remove | sim | 322 | 1.00 | 1.00 | 0.331 | 0.212 | 0.119 |

Leitura dos números:

1. Hit@1 e Hit@3 dão 1.00 nas oito configurações. Com 46 chunks e perguntas bem alinhadas ao corpus, a métrica satura e não serve para escolher. Por isso o desempate usa a margem, que é a distância entre a pergunta respondível de pior score e a pergunta sem resposta: ela mede quanto espaço sobra para o threshold.
2. Remover stopwords é a decisão de maior efeito: a margem sobe de 0.042 para 0.143 sem a seção no índice. Confirma o diagnóstico do enunciado sobre os interrogativos em português.
3. Incluir o nome da seção no índice piora a margem (0.143 para 0.119). As seções da FAQ-001 são perguntas ("Como peço reembolso?"), então indexá-las aproxima a FAQ de qualquer pergunta, inclusive das que não têm resposta. Por isso o assistente indexa só o corpo da seção, apesar de o campo `secao` continuar no chunk e na citação.
4. Remover acentos empata em margem (0.143 nas duas). O desempate veio da robustez: uma pergunta digitada sem acento, como "Quantos dias de ferias tenho direito?", pontua 0.549 com acentos removidos contra 0.447 sem remover. O corpus é acentuado, mas quem pergunta nem sempre é.

Configuração adotada pelo assistente: acentos_removidos=True, stopwords_removidas=True, secao_no_indice=False

---

## Parte 3 - Recuperação top-k com regra de vigência

P01: Com quantos dias de antecedência devo solicitar minhas férias?
    1. POL-002 | Seção: Como solicitar | score = 0.42
    2. POL-002 | Seção: Venda de dias | score = 0.38
    3. POL-002 | Seção: Direito a férias | score = 0.25

P02: Quantos dias por semana posso trabalhar de forma remota?
    1. POL-005 | Seção: Regra de trabalho remoto | score = 0.55
    2. FAQ-001 | Seção: Posso trabalhar remoto todos os dias? | score = 0.15
    3. FAQ-001 | Seção: Quem é o meu buddy? | score = 0.11

P10: Qual é a política de estacionamento da empresa?
    1. POL-008 | Seção: Aviso | score = 0.22
    2. POL-001 | Seção: Objetivo | score = 0.22
    3. POL-003 | Seção: Auxílio para trabalho remoto | score = 0.20

Verificação da regra de vigência na P02

Com a regra ativa (comportamento padrão do assistente):
    1. POL-005 | Seção: Regra de trabalho remoto | score = 0.55
    2. FAQ-001 | Seção: Posso trabalhar remoto todos os dias? | score = 0.15
    3. FAQ-001 | Seção: Quem é o meu buddy? | score = 0.11

Sem a regra, apenas para demonstrar o que ela evita:
    1. POL-004 | Seção: Regra de trabalho remoto | score = 0.74
    2. POL-005 | Seção: Regra de trabalho remoto | score = 0.55
    3. FAQ-001 | Seção: Posso trabalhar remoto todos os dias? | score = 0.15

POL-004 aparece no top-3 com a regra ativa: não
POL-004 apareceria sem a regra: sim

A POL-004 está revogada e diz "até 2 dias por semana", enquanto a POL-005 vigente diz "até 3 dias". Sem o filtro a POL-004 vence por score (0.74 contra 0.55), porque repete mais vezes os termos da pergunta. A regra de vigência é o que impede o assistente de responder com confiança uma regra que não vale mais.

---

## Parte 4 - Resposta extrativa e regra de não encontrado

Maior score de cada pergunta do gabarito (base da calibração):

| pergunta_id | maior_score | tem resposta no corpus |
| --- | --- | --- |
| P01 | 0.421 | sim |
| P02 | 0.545 | sim |
| P03 | 0.542 | sim |
| P04 | 0.389 | sim |
| P05 | 0.392 | sim |
| P06 | 0.544 | sim |
| P07 | 0.381 | sim |
| P08 | 0.498 | sim |
| P09 | 0.368 | sim |
| P10 | 0.225 | não |

Menor score entre as perguntas com resposta: 0.368 (P09)
Maior score da pergunta sem resposta (P10): 0.225
Meio da lacuna: 0.296
THRESHOLD ESCOLHIDO: 0.30

Justificativa: existe uma lacuna limpa entre 0.225 (a P10, que não tem resposta no corpus) e 0.368 (a P09, a pergunta respondível de menor score). O valor 0.30 fica praticamente no meio dessa lacuna, com folga para os dois lados: seria preciso uma pergunta respondível pontuar 18% abaixo da pior observada, ou uma pergunta sem resposta pontuar 33% acima da P10, para o assistente errar. Um valor colado em qualquer um dos extremos acertaria o gabarito do mesmo jeito, mas quebraria na primeira pergunta um pouco diferente.

Saída completa para P02:

PERGUNTA: Quantos dias por semana posso trabalhar de forma remota?
RESPOSTA: O colaborador pode trabalhar de forma remota em até 3 dias por semana. Os dias presenciais obrigatórios são terça-feira e quinta-feira.
FONTE: POL-005 | Política de Trabalho Híbrido (versão 2) | Seção: Regra de trabalho remoto
SCORE: 0.55
STATUS: encontrado

Saída completa para P10:

PERGUNTA: Qual é a política de estacionamento da empresa?
RESPOSTA: Não encontrei essa informação nas políticas vigentes. Procure a área de Pessoas e Cultura.
FONTE: nenhuma
SCORE: 0.22
STATUS: nao_encontrado

---

## Parte 5 - Avaliação com o gabarito

| pergunta_id | doc_esperado | doc_retornado_1 | score | STATUS | acerto |
| --- | --- | --- | --- | --- | --- |
| P01 | POL-002 | POL-002 | 0.42 | encontrado | sim |
| P02 | POL-005 | POL-005 | 0.55 | encontrado | sim |
| P03 | POL-003 | POL-003 | 0.54 | encontrado | sim |
| P04 | POL-006 | POL-006 | 0.39 | encontrado | sim |
| P05 | POL-009 | POL-009 | 0.39 | encontrado | sim |
| P06 | POL-007 | POL-007 | 0.54 | encontrado | sim |
| P07 | POL-008 | POL-008 | 0.38 | encontrado | sim |
| P08 | POL-009 | POL-009 | 0.50 | encontrado | sim |
| P09 | POL-010 | POL-010 | 0.37 | encontrado | sim |
| P10 | nao_encontrado | POL-008 | 0.22 | nao_encontrado | sim |

Hit@1 = 1.00 (9 de 9 perguntas com resposta)
Hit@3 = 1.00 (9 de 9 perguntas com resposta)

P10 (sem resposta no corpus): STATUS devolvido = nao_encontrado, score do melhor chunk = 0.22, abaixo do threshold 0.30. Resultado: acerto.

Armadilha da FAQ-001: a FAQ repete de forma resumida o conteúdo de outras políticas e apareceu no top-3 de 4 das 9 perguntas com resposta, mas foi o primeiro resultado em 0 delas. Como a FAQ não vence nenhuma política no topo, o Hit@1 estrito não foi afetado, o que poderia mudar se o nome da seção entrasse no índice, conforme medido na Parte 2.

Análise de erro

Nenhuma das 10 perguntas errou, então a análise vai para a que passou mais perto de falhar: a P09 ("Qual é o orçamento anual de treinamento por colaborador?"), com score 0.37 contra um threshold de 0.30. Ela recupera o chunk certo com folga enorme sobre o segundo colocado (0.37 contra 0.13), mas o score absoluto é baixo por dois motivos: a pergunta diz "treinamento" e o chunk diz "treinamentos", que o TF-IDF trata como termos distintos por não fazer stemming; e o chunk carrega uma segunda frase sobre saldo não transferido, que não tem nada a ver com a pergunta e dilui o vetor na normalização do cosseno. Correção testável: trocar os tokens de palavra por n-gramas de caracteres (analyzer="char_wb", ngram_range=(4,5)), que casa singular com plural sem precisar de stemmer. Eu testei: o score da P09 sobe de 0.37 para 0.54 e resolve o sintoma, mas a margem global cai de 0.143 para 0.052, porque a P10 também sobe (0.23 para 0.25) e a P02 desaba (0.55 para 0.34). A correção foi descartada com base nesse número: ela conserta uma pergunta e fragiliza o threshold, que é a defesa contra responder o que não existe.
