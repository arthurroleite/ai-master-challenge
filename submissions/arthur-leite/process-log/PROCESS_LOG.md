# Process Log — Arthur Leite — Challenge 002

Diário de trabalho, escrito durante o processo e não reconstruído no final.
Cada entrada registra o que decidi, o papel da IA, onde a IA errou ou foi corrigida e o que mudou.

**Ferramenta principal:** Claude Code (Claude Opus 5.5), operando no meu terminal com acesso ao repositório.
**LLM no protótipo:** Google Gemini (plano gratuito), como camada opcional.

---

## Fase 0 — Leitura, escolha do case e setup (2026-10-14)

### 0.1 Leitura da vaga e do repositório
- Pedi ao Claude Code que lesse a descrição da vaga (via Chrome) e clonasse o repo para ler todos os arquivos: README, submission-guide, CONTRIBUTING, template e os 4 challenges.
- Pedi também uma contagem dos PRs já abertos: 189 no total, sendo 79 no 003, 41 no 002, 33 no 001 e 18 no 004.
- **Decisão minha:** não abrir os PRs de outros candidatos, para manter a solução original.

### 0.2 Escolha do challenge: 002 (Suporte)
- A IA recomendou o 002, e eu concordei, por três motivos:
  1. Opero agentes de atendimento com IA em produção para clientes (plataforma Mavra: SDR, triagem, kanban), e esse contexto real é algo que um modelo sozinho não tem.
  2. É o único case que exige as 5 frentes da vaga ao mesmo tempo: diagnóstico, orquestração, build, ROI e o julgamento do que não automatizar.
  3. Tem metade da concorrência do 003.

### 0.3 Hipótese antes de tocar nos dados
- Antes de baixar qualquer coisa, levantei a suspeita de que o Dataset 1 é sintético: volume menor que os "~30K" do enunciado, placeholders no texto, "tempos" que são timestamps e CSAT aleatório.
- **Por que isso importa:** se os dados forem ruído, qualquer conclusão de "causa" tirada deles é falsa. O baseline de IA tende a analisar sem questionar a fonte.

### 0.4 Setup
- Branch `submission/arthur-leite` e estrutura de pastas criadas conforme o CONTRIBUTING.
- **Pegadinha encontrada:** o `.gitignore` da raiz do repo ignora `submissions/`. Um `git add .` simples gera um PR vazio. Solução: adicionar a pasta explicitamente com `git add -f`, mantendo um `.gitignore` próprio da submissão para não subir dados nem a chave de API.
- Sem chave da Anthropic. Avaliei as alternativas: LLM local inviável (7,7 GB de RAM, sem GPU); escolhi o Gemini gratuito. O LLM entra como camada **opcional**: o protótipo precisa rodar sem nenhuma chave.
- Download dos dois datasets via `kagglehub`, sem precisar de login.

### 0.5 Primeira checagem dos dados (confirma a hipótese 0.3)
| Hipótese | Resultado |
|---|---|
| Volume de ~30K tickets | **Falso: 8.469 tickets** |
| Texto com placeholders | Encontrado `{` em 8.469 de 8.469 descrições (a verificar na Fase 1) |
| "First Response Time" e "Time to Resolution" são durações | **Não são: são timestamps.** Precisam ser convertidos em duração |
| CSAT disponível | **5.700 nulos (67%).** Só os tickets Closed (2.769) têm nota |
| Dataset 2 | 47.837 textos em 8 classes, **desbalanceadas** (Hardware 13.617 × Administrative rights 1.760) |

Próximo passo: Fase 1, auditoria completa da qualidade dos dados.

---

## Fase 1 — Auditoria de qualidade dos dados (2026-10-14)

Script reproduzível: `solution/01-diagnostico/01_auditoria_dados.py`. Saída: `solution/01-diagnostico/outputs/auditoria.md`.

### Como decompus
Antes de responder "onde o fluxo trava", perguntei se os dados conseguem responder isso. Para cada campo, testei se ele carrega informação:
1. O texto é real ou template?
2. Os tempos são tempos?
3. As variáveis se relacionam entre si, como numa operação real (ex.: Critical deveria ter fluxo diferente de Low)?
4. Alguma variável explica o CSAT?

### Resultado: o Dataset 1 é aleatório
- **100%** das descrições têm placeholder não preenchido; só existem **16** frases de abertura.
- Os "tempos" são timestamps concentrados numa janela de **27 horas**, e em **49%** dos tickets fechados a resolução acontece *antes* da primeira resposta.
- O CSAT é **uniforme** de 1 a 5 (p = 0,80).
- **Nenhum par de variáveis tem associação** (maior Cramér's V = 0,072). O tipo do ticket é independente do assunto: há "Billing inquiry" com assunto "Hardware issue".
- **Nada explica o CSAT**: canal, prioridade, tipo, produto, duração e idade têm todos p > 0,25.

### Resultado: o Dataset 2 é real
- Texto real de e-mails de TI, pré-processado e anonimizado, com rótulos coerentes e desbalanceados. Serve para treinar e avaliar classificadores de verdade.

### Onde a IA (e o baseline) erraria
Se eu colasse o brief num LLM, ele responderia "Critical demora mais, chat tem melhor CSAT, reduzir o tempo de primeira resposta aumenta a satisfação". Testei isso: **as diferenças entre grupos estão dentro do ruído** (ex.: a mediana de "duração" é 6,0 h para Critical e 7,1 h para Low, num dado em que metade das durações é negativa). Qualquer "insight" desse tipo seria inventado.

### Decisão (pendente de validação com o Arthur)
Mudar o enquadramento do diagnóstico: o primeiro gargalo é **de medição**. A entrega vai mostrar o que dá para afirmar, o que não dá, e o que precisaria ser instrumentado. Os números de desperdício serão construídos a partir de volume × premissas explícitas e ajustáveis, nunca a partir das durações falsas.

### 1.1 Revisão pelo agente juiz (pedido do Arthur: toda conclusão passa por um juiz)
Criei um protocolo (`process-log/revisoes/PROTOCOLO_JUIZ.md`): um subagente com contexto limpo recebe só as afirmações e os CSVs brutos, **recalcula tudo com código próprio** sem ver o meu e tenta refutar.
Parecer completo: `process-log/revisoes/fase1_auditoria_parecer.md`.

**Resultado:** a tese central foi confirmada, mas 7 de 10 afirmações vieram "com ressalva". As correções mais importantes:

| O que eu tinha dito | O que o juiz mostrou | Correção aplicada |
|---|---|---|
| "67% dos tickets não fechados = backlog real" (eu cheguei a dizer isso ao Arthur como algo aproveitável) | Os 3 status são equiprováveis (p = 0,33): é sorteio, não backlog | **Removido** como achado e transformado em mais uma evidência de dado sintético |
| "Dataset é aleatório" | Forte demais | "Sintético, com variáveis geradas de forma independente" |
| "Maior Cramér's V = 0,072" | Inflado pelos 42 produtos | V corrigido para viés (máx. 0,021) + "0 de 21 pares significativos" |
| "Nada explica o CSAT, todos p > 0,25" | Omiti testes com p ≈ 0,035 e 0,041 (hora da resposta, data de compra) | Bateria completa com correção de Bonferroni, mostrando os dois p < 0,05 e explicando por que não são sinal |
| (não declarado) | Faltava o poder estatístico | Adicionado: os testes detectariam 0,21 ponto de CSAT, então "não achar nada" não é falta de amostra |

**Evidências novas trazidas pelo juiz e incorporadas:** timestamps que acompanham o Ticket ID (rastro do gerador), e-mails `@example`, resoluções no estilo Faker, máquina de estados sem exceção e um classificador sobre a descrição que fica abaixo do chute.

**Aprendizado:** o erro do "backlog de 67%" é exatamente o tipo de conclusão plausível que passaria sem um revisor. Ele estava na minha mensagem ao Arthur antes da revisão.

---

## Fase 3 (adiantada) — Benchmark de classificadores no Dataset 2

Adiantei esta fase enquanto o juiz revisava a Fase 1, porque ela não dependia do parecer.
Scripts: `solution/03-prototipo/benchmark/` (`embed_ds2.py`, `llm_classify.py`, `benchmark.py`). Resultado: `benchmark/outputs/benchmark.md`.

### Desenho
- Mesmo conjunto de teste para tudo (20%, estratificado, seed 42). O restante foi dividido em treino (70%) e validação (10%).
- **Limiares escolhidos na validação e medidos no teste**, para não superestimar.
- Três abordagens: A) TF-IDF + regressão logística; B) embeddings MiniLM + regressão logística; C) LLM Gemini zero-shot e few-shot, com 20 tickets por chamada e as respostas brutas em cache como evidência.

### Erros meus corrigidos durante a fase
1. **Faixa "sugere" com precisão de 60%.** Eu usava a precisão *acumulada*, inflada pelos tickets de alta confiança. Corrigi para a precisão *dentro da faixa*.
2. **Faixa "sugere" vazia** depois da correção: logo abaixo do limiar de 95%, a precisão da 1ª opção despenca. Redesenhei a faixa como produto: o humano escolhe entre as **2 sugestões**, e o critério passa a ser "a categoria certa está entre as 2" ≥ 90%.
3. **Cache contaminado:** um teste com 40 tickets usou uma amostra diferente da de 400. Apaguei o cache antes da rodada oficial.

### Resultados preliminares (ainda vão ao juiz)
- A: 86,0% de acurácia, F1-macro 0,86, custo zero, 0,04 ms por ticket.
- B: 80,8% de acurácia (pior que A: o texto pré-processado e sem stopwords favorece palavras-chave).
- C: o LLM ficou em 44% (zero-shot) e 48% (few-shot) com flash-lite. **Hipótese:** as categorias são convenções internas da organização ("Miscellaneous", "Internal Project"), que um LLM não tem como adivinhar. Um modelo mais forte (gemini-3.5-flash) está rodando para garantir que a comparação seja justa e não um espantalho.

### 3.1 Revisão pelo agente juiz (benchmark + ROI)
Parecer: `process-log/revisoes/fase3_benchmark_roi_parecer.md`. Todos os números foram recalculados e **conferem**. As ressalvas mudaram a narrativa:

| Ponto | O que o juiz mostrou | O que mudei |
|---|---|---|
| Faixa auto com 95,1% | IC95% de 94,6 a 95,9%: cerca de 20% de chance de ficar abaixo da meta. Hardware em 92,6%; 12% dos tickets de Admin rights vão sozinhos para Hardware | **Limiar por categoria** (Hardware sobe para 0,78) → faixa auto com 96,4% |
| "LLM perde por ~40 pontos" | O teste favorece o modelo local (flash-lite, texto pré-processado, só o nome das categorias) | Redação qualificada. Rodando também `gemini-3.8-flash`, o modelo mais forte disponível, para não comparar com um espantalho |
| ROI: erro de roteamento de 15% → 7,5% | **Não demonstrado.** O erro da IA é medido contra o rótulo humano; o "15%" é taxa de transferência de mercado, que inclui escalonamentos legítimos | **Removido do número principal.** No app, virou uma hipótese opcional, desligada por padrão |
| Faixa "sugere": humano erra igual a hoje | Não é conservador: com ancoragem na 1ª sugestão, o erro chega a 38% | O cálculo opcional usa o pior caso de ancoragem |
| R$ 57 mil/ano | Benefício bruto, sem custo de implantação; é tempo, não caixa | Linguagem trocada para "tempo liberado bruto", com faixa entre cenários |
| Premissa de 3 min de triagem | Responde por 84% do resultado e tem fonte fraca | Explicitado; vira o **1º item medido no piloto** |

**Número final:** 552 a 2.106 h/ano de tempo liberado (base: 1.218 h ≈ 0,7 pessoa ≈ R$ 47 mil). É menor que a 1ª versão (1.496 h), porém defensável.

---

## Fase 4 — Protótipo "Triage Copilot" (Streamlit)

Código: `solution/03-prototipo/` (`app.py`, `src/triagem.py`, `src/politica.py`, `src/llm.py`, `src/roi.py`).

### Problemas encontrados ao testar e corrigidos
1. **A confiança não detecta ticket fora do domínio.** Testei o modelo de TI nos tickets de cliente do Dataset 1: **43%** seriam roteados automaticamente "com confiança". Criei uma trava de similaridade com o vizinho mais próximo no histórico. Limiar de 0,20: barra 82% dos tickets fora do domínio e 9,5% dos normais. Antes de concluir, igualei o pré-processamento do Dataset 1 ao do Dataset 2, para não favorecer o teste.
2. **Texto em português passou pela trava.** Com uma única palavra conhecida ("status"), a similaridade era alta. Adicionei uma 2ª trava: a fração das palavras que o modelo reconhece (mínimo 50%).
3. **Phishing foi roteado automaticamente para Access.** A política detectava o alerta, mas não sobrepunha a decisão. Agora a política sempre vence: segurança vai para a fila de Segurança, com escalonamento.
4. **O rascunho do LLM inverteu o sentido** ("not detected" virou "was detected"), porque recebia o texto pré-processado, sem stopwords (e "not" é stopword). Agora o LLM recebe o texto original.

### Decisões de produto baseadas em dados
- **Rotear ≠ executar ≠ responder.** A política de "não automatizar" é por regras explícitas, não pela categoria, porque no Dataset 2 os temas sensíveis cruzam as categorias (ex.: segurança cai 41% em Hardware, 19% em Admin rights e 17% em Access). 27,7% dos tickets acionam alguma regra (a execução exige humano); 2,7% bloqueiam o rascunho por LLM (saúde/LGPD, segurança); 8,1% são escalados.
- **As categorias não significam o que o nome diz.** Os termos mais fortes de "Administrative rights" são *outlook, upgrade, install, windows*: instalação de software. Isso ajuda a explicar a dificuldade do LLM.
- **Motor final, no teste:** 65,5% automático (96,4% de acerto) · 23,3% sugestão (a certa está entre as 2 em 91%) · 11,2% humano.

**Nota sobre o "43% × 34%":** o primeiro teste fora do domínio (43%) usava o limiar global e o texto do Dataset 1 sem o mesmo pré-processamento do Dataset 2. Com os limiares por categoria e o pré-processamento igualado, o número correto é **34,1%** sem as travas → **10,8%** com elas (`motor_final.md`). Vale o 34%.

---

## Fase 5 — Comparação justa com LLM, entregáveis, deploy e revisão final (2026-10-14)

### 5.1 Comparação justa com LLM (pedido do juiz 2)
- **RAG:** cada ticket vai ao LLM com os 5 tickets mais parecidos do histórico, já rotulados (o melhor cenário para o LLM). Resultado: **76,9%**.
- **Modelo mais forte** (`gemini-3.8-flash`): **53,5%**. Parou em 200 tickets: a cota diária do plano gratuito acabou, e antes disso o `gemini-3.5-flash` deu erro 503 (sobrecarga).
- **Referência sem LLM** (voto dos 5 vizinhos): 73,3%. O LLM com RAG pouco acrescenta ao próprio histórico.
- **Teste pareado (McNemar):** o modelo simples (85,0%) × RAG → p = 0,0003. Os 21 tickets que só o RAG acerta sugerem testar o LLM como "segunda opinião" na faixa de sugestão (não testado).
- **Integridade:** o LLM inventou um id numa resposta em lote (973, inexistente). Ele foi filtrado; 1 em 1.400 respostas. As respostas brutas foram versionadas como evidência.

### 5.2 Entregáveis
Proposta (`02-proposta-automacao/proposta.md`), relatório executivo (HTML + PDF), README no template e avaliação final do motor (`motor_final.md`, a fonte dos números oficiais).

### 5.3 Deploy no Streamlit Cloud
- Preparei o app para rodar sem arquivos locais: baixa os dados na 1ª execução, lê a chave do Gemini dos Secrets e usa um `requirements` sem PyTorch.
- Testei a frio com `AppTest` numa pasta limpa: sem exceções, 86 s na 1ª carga.
- **Mesmo assim, o deploy quebrou:** o servidor instalou o **pandas 3** (eu testara com o 2.2), e `.values[:, None]` não funciona em colunas de texto Arrow. **Lição:** o teste a frio precisa reproduzir as versões do servidor, não só a pasta limpa. Correção: `to_numpy(dtype=object)` + `pandas<3`, validada num venv novo com pandas 3.0.6. Números idênticos.

### 5.4 Juiz final: reprodução a frio a partir do GitHub
Parecer: `process-log/revisoes/fase5_final_parecer.md`. O juiz clonou a branch, seguiu o README, rodou tudo e conferiu cada número entre os documentos.
- **Achou o mesmo bug do pandas 3 de forma independente**, ao mesmo tempo que o erro do deploy.
- Todos os demais números se reproduzem.

| Correção apontada | O que fiz |
|---|---|
| Pergunta "onde o fluxo trava" respondida só com recusa | Tabela literal das 3 piores e 3 melhores combinações (80 no total), com IC e **teste de permutação**: o gap observado (7,6 h) é menor que o que o acaso gera (8,1 h), p = 0,68 |
| Faixa humana atribuída a "confiança baixa" | Decomposição gerada pelo código: 9,7% pela trava de domínio (o modelo acertaria 79%) + 1,5% por confiança baixa |
| `benchmark.py` apagava as linhas do LLM quando rodado a frio | Lê as respostas versionadas; rodada incompleta grava `benchmark_parcial.md` |
| Erro de codificação no Windows | `stdout` em UTF-8 nos 4 scripts |
| JSON órfão da v1, README com links e afirmações desatualizados | JSON removido; README reescrito |
| "Já pode ser automatizada com segurança", "provado" | "Validado em dados reais; nesta operação, retreina e começa em modo sombra" |
| A aba de fila abria com uma amostra de 1.000 (números ≠ README) | Abre no teste inteiro: 65,5 / 23,3 / 11,2% |
| Cruzamento dos datasets implícito; faltavam exemplos reais | Parágrafo explícito + 4 tickets reais na proposta (ex.: um alerta de domínio suspeito rotulado como Hardware) |
| Faltava pedir uma decisão ao Diretor | Seção "O que preciso de você" no relatório |

**Erro meu pego ao reler:** escrevi que os intervalos das combinações extremas "se sobrepõem", o que é falso para alguns pares. O argumento correto é o de comparações múltiplas: com 80 grupos, os extremos sempre parecem diferentes, e é por isso que o teste de permutação é o teste certo.
