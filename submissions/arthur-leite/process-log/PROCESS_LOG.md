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
