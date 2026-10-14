# Submissão — Arthur Leite — Challenge 002

## Sobre mim

- **Nome:** Arthur Leite
- **LinkedIn:** {{LINKEDIN}}
- **Challenge escolhido:** 002 — Redesign de Suporte

---

## Executive Summary

Antes de diagnosticar, testei se os dados aguentavam um diagnóstico: **a base de métricas (Dataset 1) é sintética.** Os "tempos" são carimbos numa janela de 27 h, em metade dos tickets fechados a resolução vem antes da 1ª resposta, e nenhuma variável explica a satisfação. Por isso não apresento "gargalos por canal": o primeiro gargalo é de **medição**, e entrego um plano de instrumentação de 30 dias.
Com os 48 mil tickets reais do Dataset 2, construí e medi uma **triagem automática com três faixas de confiança**: **65,5% dos tickets roteados sozinhos com 96,4% de acerto**, 23% com 2 sugestões ao agente e 11% para humano. Há travas para tickets fora do domínio e uma política explícita do que **nunca** automatizar (segurança, saúde, desligamento, aprovações, privilégios).
Um classificador simples treinado no histórico **superou o LLM** em todas as configurações testadas: **o ativo é o histórico rotulado da empresa.** O LLM ficou onde agrega, na redação de rascunhos.
O ganho estimado é de **~1.200 h/ano de agente no cenário base (faixa: 550 a 2.100 h)**, com premissas explícitas que o piloto de 4 semanas substitui por medição.

**Comece por aqui:** [`solution/relatorio-executivo.pdf`](solution/relatorio-executivo.pdf) (5 minutos de leitura) → protótipo (setup abaixo) → [`process-log/PROCESS_LOG.md`](process-log/PROCESS_LOG.md).

---

## Solução

| Entregável | Arquivo |
|---|---|
| Relatório executivo (para o Diretor) | [`solution/relatorio-executivo.pdf`](solution/relatorio-executivo.pdf) · [HTML](solution/relatorio-executivo.html) |
| 1. Diagnóstico: auditoria dos dados | [`solution/01-diagnostico/outputs/auditoria.md`](solution/01-diagnostico/outputs/auditoria.md) |
| 1. Diagnóstico: tempo de triagem e ROI | [`solution/01-diagnostico/outputs/modelo_desperdicio.md`](solution/01-diagnostico/outputs/modelo_desperdicio.md) |
| 2. Proposta de automação | [`solution/02-proposta-automacao/proposta.md`](solution/02-proposta-automacao/proposta.md) |
| 3. Protótipo funcional (*Triage Copilot*) | [`solution/03-prototipo/`](solution/03-prototipo/) |
| Benchmark de classificadores (TF-IDF × embeddings × kNN × LLM) | [`solution/03-prototipo/benchmark/outputs/benchmark.md`](solution/03-prototipo/benchmark/outputs/benchmark.md) |
| Avaliação final do motor | [`solution/03-prototipo/benchmark/outputs/motor_final.md`](solution/03-prototipo/benchmark/outputs/motor_final.md) |

### Abordagem

1. **Desconfiar antes de analisar.** Antes de abrir os dados, levantei a hipótese de que a base era sintética. Depois testei cada campo: o texto é real? os tempos são tempos? as variáveis se relacionam? algo explica o CSAT? Para "não achar nada" valer como resultado, calculei o poder estatístico.
2. **Separar o que cada dataset prova.** O Dataset 1 dá a *estrutura* da operação (status, canais, prioridades). O Dataset 2, com rótulos reais, prova a *automação*.
3. **Comparar abordagens em vez de assumir.** TF-IDF, embeddings, kNN e LLM (zero-shot, few-shot, RAG, modelo mais forte), todos na mesma amostra.
4. **Desenhar a automação como produto:** faixas de confiança calibradas na validação e medidas no teste, limiar por categoria, travas de domínio e uma política que separa rotear, executar e responder.
5. **Revisão adversarial em cada conclusão.** Um agente juiz independente recalculou tudo do zero e tentou refutar. Três pareceres mudaram a entrega (ver Process Log).

### Resultados / Findings

**Diagnóstico** (Dataset 1, 8.469 tickets, não ~30 mil):

| Teste | Resultado |
|---|---|
| Tempos | Janela de 27 h; resolução antes da 1ª resposta em 49% dos fechados |
| CSAT | Uniforme de 1 a 5 (p = 0,80); 0 variáveis com efeito após correção de Bonferroni; poder para detectar 0,21 ponto |
| Variáveis | 0 de 21 pares associados (V corrigido máx. 0,021); o texto não prevê nem o assunto (6,4% × 6,8% do chute) |
| Status | Os 3 status são equiprováveis: os "67% não fechados" são sorteio, **não backlog** |

**Automação** (Dataset 2, teste com 9.568 tickets nunca vistos):

| Faixa | % | Acerto |
|---|---|---|
| Automático | 65,5% | 96,4% (IC95% de 95,9 a 96,8%) · todas as categorias ≥ 95% |
| Sugestão (agente escolhe entre 2) | 23,3% | certa entre as 2: 91,0% |
| Humano | 11,2% | — |
| Tickets de outro domínio | — | 34% iriam para o automático sem as travas; 11% com elas |

**Classificação: modelo simples × LLM** (mesma amostra de 400): ver [`benchmark.md`](solution/03-prototipo/benchmark/outputs/benchmark.md). O TF-IDF + regressão logística (85%) supera todas as variantes de LLM testadas.

**Protótipo:** `streamlit run app.py`, com 5 abas: triagem ao vivo (decisão + explicação + casos parecidos + rascunho), fila de teste com milhares de tickets reais, diagnóstico, ROI ajustável e "como funciona".

### Recomendações

1. **Instrumentar a operação (semana 0):** carimbos separados, log de mudança de fila, categoria na abertura × na resolução. Sem isso, nenhum diagnóstico é confiável.
2. **Modo sombra (semanas 1–2):** a IA classifica sem rotear; mede-se a concordância com os agentes.
3. **Ligar o automático em 3 categorias estáveis (semanas 3–4):** Purchase, Access e Storage (97,8–99,0%).
4. **Expandir com a política ativa desde o 1º dia:** segurança, saúde, desligamento, aprovação e privilégio, sempre com humano.
5. **Retreino mensal** com as correções dos agentes.

### Limitações

- O desempenho foi medido em tickets internos de TI, em inglês. Outra operação retreina com o próprio histórico e mede de novo.
- Os rótulos do Dataset 2 têm ruído estimado de 15 a 25%.
- O limiar das travas de domínio foi escolhido com os mesmos dados usados para avaliá-lo (resultado otimista).
- O ROI usa premissas de mercado (a principal, de fonte fraca) até o piloto medir; é tempo liberado bruto, não caixa.
- O LLM foi testado no plano gratuito do Gemini (sobrecarga e cota limitaram as variantes).

### Setup do protótipo

```bash
cd submissions/arthur-leite/solution/03-prototipo
pip install -r requirements.txt
python baixar_dados.py          # baixa os 2 datasets do Kaggle (sem login)
streamlit run app.py            # na 1ª execução, treina o motor (~1 min, CPU)
```
Opcional, para os rascunhos por LLM: crie `03-prototipo/.env` com `GEMINI_API_KEY=...` (chave gratuita do Google AI Studio). Sem ela, todo o resto funciona.
Para reproduzir as análises: `python solution/01-diagnostico/01_auditoria_dados.py`, `02_modelo_desperdicio.py` e `solution/03-prototipo/benchmark/benchmark.py` / `avaliar_motor.py`.

---

## Process Log — Como usei IA

> Diário completo, escrito durante o trabalho: [`process-log/PROCESS_LOG.md`](process-log/PROCESS_LOG.md). Pareceres do juiz: [`process-log/revisoes/`](process-log/revisoes/). Conversa completa: [`process-log/chat-exports/`](process-log/chat-exports/).

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude Code (Claude Opus 5.5) | Agente principal: leitura do case, análise, código, protótipo, git |
| Subagentes "juiz" (Claude Code) | Revisão adversarial independente de cada conclusão, recalculando do zero |
| Google Gemini (flash-lite, 3.8 flash) | Benchmark de classificação (zero-shot, few-shot, RAG) e rascunho de respostas no protótipo |
| scikit-learn, sentence-transformers | Classificadores (TF-IDF, embeddings MiniLM, kNN) |
| Streamlit + Plotly | Protótipo |
| Claude in Chrome | Leitura da vaga e teste visual do protótipo |

### Workflow

1. Li a vaga e todos os arquivos do repo e escolhi o 002 pelo encaixe com a minha experiência: opero agentes de atendimento com IA em produção.
2. **Hipótese antes dos dados:** a base devia ser sintética. Confirmada na 1ª checagem e depois auditada com testes estatísticos.
3. Pedi que **cada conclusão** passasse por um agente juiz com contexto limpo e postura adversarial.
4. Benchmark de 4 abordagens + 4 variantes de LLM, com limiares calibrados na validação e medidos no teste.
5. Protótipo construído e testado com casos de borda (phishing, outro idioma, aprovação). Cada falha virou uma trava.
6. ROI reescrito depois do juiz: só o que é sustentável, com o resto declarado como fora.

### Onde a IA errou e como corrigi

| Erro | Quem pegou | Correção |
|---|---|---|
| Afirmei "67% de backlog real" | Juiz (status equiprováveis, p = 0,33) | Removido; virou evidência de dado sintético |
| Omiti dois p < 0,05 na análise de CSAT | Juiz | Bateria completa com Bonferroni + poder estatístico |
| Faixa "sugere" com 60% de precisão (usava a precisão *acumulada*) | Eu, ao ler a tabela | Precisão *dentro da faixa*; depois, critério top-2 |
| ROI assumia que o erro de roteamento cairia de 15% para 7,5% | Juiz (não demonstrado; "transferência" ≠ erro de triagem) | Removido do número principal; virou hipótese opcional |
| Comparação com LLM era um espantalho (modelo barato, sem contexto) | Juiz | Testei RAG e o modelo mais forte; a redação foi qualificada |
| Confiança alta em ticket de outro domínio (34% passariam) | Teste fora do domínio | Travas de similaridade e de vocabulário |
| Phishing roteado automaticamente para "Access" | Teste de borda | A política sobrepõe o classificador |
| Rascunho do LLM inverteu o sentido ("not detected" → "detected") | Teste do rascunho | O LLM recebe o texto original (o pré-processamento removia "not") |

### O que eu adicionei que a IA sozinha não faria

- **Desconfiar da base antes de analisar.** O caminho padrão (o baseline) é calcular "tempo médio por canal" sobre dados sintéticos.
- **O desenho rotear ≠ executar ≠ responder** e a lista do que nunca automatizar, vindos de operar atendimento com IA em produção.
- **Exigir um revisor adversarial** para cada número. Foi ele que derrubou o "backlog de 67%" e o ROI inflado.
- **Escolher entregar um ROI menor e defensável** (1.218 h no cenário base contra 1.496 h na 1ª versão) e dizer o que ficou de fora.

---

## Evidências

- [x] Chat export (conversa completa com o Claude Code): `process-log/chat-exports/`
- [x] Git history: commits por fase nesta branch
- [x] Pareceres do agente juiz: `process-log/revisoes/`
- [x] Respostas brutas do LLM no benchmark: geradas por `llm_classify.py` (cache local, não versionado)
- [x] Screenshots do protótipo: `process-log/screenshots/`

---

_Submissão enviada em: {{DATA}}_
