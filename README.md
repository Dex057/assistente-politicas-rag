# Assistente de Perguntas e Respostas sobre Políticas Internas

Assistente de RAG (Retrieval-Augmented Generation) com recuperação local que
responde perguntas em português sobre um conjunto de políticas internas. Dada uma
pergunta, o sistema localiza o trecho da política que a responde, devolve esse
trecho sem reescrevê-lo e cita o documento e a seção de origem. Quando a
informação não existe no corpus, o assistente declara que não encontrou em vez de
produzir uma resposta plausível e errada.

Não há chamada de API nem dependência de serviço externo. Todo o processamento
ocorre localmente com pandas e scikit-learn.

## Como funciona

O pipeline tem seis etapas, executadas em ordem por `desafio/main.py`:

| Etapa | Módulo | Função |
| --- | --- | --- |
| Leitura do corpus | `corpus.py` | Carrega metadados e o texto integral dos documentos Markdown |
| Chunking | `chunking.py` | Divide cada documento em um chunk por seção, excluindo o cabeçalho |
| Indexação | `indexacao.py` | Vetoriza os chunks com TF-IDF e pré-processamento configurável |
| Recuperação | `busca.py` | Ranqueia os chunks por similaridade do cosseno, restrito a documentos vigentes |
| Resposta | `resposta.py` | Monta a saída extrativa de cinco campos e aplica a regra de não encontrado |
| Avaliação | `avaliacao.py` | Calcula Hit@1 e Hit@3 contra o gabarito e compara configurações |

### Formato da resposta

A saída é texto puro, compatível com leitor de tela, sem cor ou símbolo gráfico:

```
PERGUNTA: Quantos dias por semana posso trabalhar de forma remota?
RESPOSTA: O colaborador pode trabalhar de forma remota em até 3 dias por semana. Os dias presenciais obrigatórios são terça-feira e quinta-feira.
FONTE: POL-005 | Política de Trabalho Híbrido (versão 2) | Seção: Regra de trabalho remoto
SCORE: 0.55
STATUS: encontrado
```

Quando nenhum chunk atinge o threshold:

```
PERGUNTA: Qual é a política de estacionamento da empresa?
RESPOSTA: Não encontrei essa informação nas políticas vigentes. Procure a área de Pessoas e Cultura.
FONTE: nenhuma
SCORE: 0.22
STATUS: nao_encontrado
```

## Resultados

Medidos sobre um gabarito de 10 perguntas, das quais 9 têm documento esperado e 1
não tem resposta no corpus.

| Métrica | Valor |
| --- | --- |
| Hit@1 | 1.00 (9 de 9) |
| Hit@3 | 1.00 (9 de 9) |
| Pergunta sem resposta | Classificada corretamente como `nao_encontrado` |
| Documentos indexados | 12 (11 vigentes, 1 revogado) |
| Chunks gerados | 46 |
| Dimensão da matriz TF-IDF | 46 x 311 |
| Threshold | 0.30 |

As evidências completas ficam em [`saidas.md`](saidas.md).

## Decisões técnicas

### Regra de vigência aplicada no ranqueamento

O corpus contém uma política revogada e sua substituta vigente, tratando do mesmo
assunto com regras divergentes. A política revogada usa vocabulário mais próximo
da pergunta e vence por score: 0.74 contra 0.55. Filtrar por vigência antes de
ordenar é o que impede o assistente de responder com confiança uma regra que não
vale mais.

Os documentos revogados continuam no índice. A exclusão acontece no ranqueamento,
não na indexação, o que mantém o IDF calculado sobre o corpus completo e permite
comparar o comportamento com e sem o filtro.

### Pré-processamento escolhido por medição

As oito combinações de remoção de acentos, remoção de stopwords e inclusão do nome
da seção no texto indexado foram comparadas. Todas atingem Hit@1 igual a 1.00, o
que torna a métrica inútil como critério de escolha.

O desempate usou a margem entre a pergunta respondível de menor score e a pergunta
sem resposta, que mede o espaço disponível para posicionar o threshold. Remover
stopwords eleva essa margem de 0.042 para 0.143, porque interrogativos como
"quantos", "qual" e "posso" ocorrem tanto nas perguntas quanto no corpus.

Incluir o nome da seção no índice reduz a margem de 0.143 para 0.119. As seções do
documento de perguntas frequentes são elas próprias perguntas, de modo que
indexá-las aproxima esse documento de qualquer consulta, inclusive das que não têm
resposta. O assistente indexa apenas o corpo da seção.

### Threshold calibrado sobre os scores observados

A pergunta sem resposta no corpus atinge score máximo de 0.225. A pergunta
respondível de menor score atinge 0.368. O threshold de 0.30 fica próximo ao
centro dessa lacuna, com folga para os dois lados, em vez de colado em um dos
extremos.

## Requisitos

- Python 3.10 ou superior
- pandas
- scikit-learn

## Instalação

```bash
git clone https://github.com/Dex057/assistente-politicas-rag.git
cd assistente-politicas-rag
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Corpus

Os documentos de políticas e os arquivos de avaliação não fazem parte deste
repositório. O código espera encontrá-los na raiz do projeto com esta estrutura:

```
insumos_Desafio_Bootcamp_SEP26/
├── corpus/                     documentos em Markdown
├── metadados.csv               doc_id, titulo, area_responsavel, vigencia_inicio, versao, status, arquivo
└── perguntas_gabarito.csv      pergunta_id, pergunta, doc_esperado, secao_esperada, resposta_esperada
```

Cada documento do corpus segue o formato abaixo. O cabeçalho é ignorado no
chunking, por já constar em `metadados.csv`:

```markdown
# POL-005 Política de Trabalho Híbrido (versão 2)
Empresa: ... | Área responsável: ... | Vigência: ... | Versão: ... | Status: vigente

## Regra de trabalho remoto
O colaborador pode trabalhar de forma remota em até 3 dias por semana.
```

O caminho da pasta é definido em `desafio/corpus.py`.

## Uso

Executar o pipeline completo e gerar as evidências:

```bash
python desafio/main.py
```

Usar o assistente diretamente:

```python
from desafio.resposta import responder
from desafio.busca import buscar

print(responder("Qual é o valor do vale-refeição por dia?"))

for chunk in buscar("Como solicito férias?", k=3):
    print(chunk["doc_id"], chunk["secao"], round(chunk["score"], 2))
```

## Testes

```bash
python -m unittest testes -v
```

A suíte tem 41 testes cobrindo todas as etapas do pipeline: contagem e integridade
do corpus, exclusão do cabeçalho no chunking, composição do vocabulário, regra de
vigência, formato e literalidade da resposta, posição do threshold, métricas de
avaliação e determinismo da execução.

A suíte foi validada por mutação. Cada regra do sistema foi quebrada
deliberadamente no código para confirmar que os testes detectam a violação. O
relatório está em [`evidencias_teste.md`](evidencias_teste.md), incluindo o caso de
um teste que inicialmente não detectou sua mutação e precisou ser reescrito.

Os testes dependem dos arquivos de corpus descritos acima.

## Estrutura

```
desafio/
├── corpus.py         leitura dos documentos e metadados
├── chunking.py       divisão por seção
├── indexacao.py      vetorização TF-IDF
├── busca.py          recuperação top-k com regra de vigência
├── resposta.py       resposta extrativa e regra de não encontrado
├── avaliacao.py      métricas, calibração e comparação de configurações
└── main.py           orquestração do pipeline

testes.py             suíte de testes
saidas.md             evidências da execução
evidencias_teste.md   relatório de testes e validação por mutação
reflexao.md           notas sobre as decisões de projeto
```

## Licença

MIT
