# Submissão — Arthur Leite — Challenge 002

## Sobre mim

- **Nome:** Arthur Leite
- **LinkedIn:** https://www.linkedin.com/in/arthurleite88/
- **Challenge escolhido:** 002 — Redesign de Suporte

> **🔗 Protótipo no ar:** https://ai-master-challenge-v56hxnnkz3z5z7khq8n5oz.streamlit.app/
> **📄 Relatório executivo (5 min):** [`solution/relatorio-executivo.pdf`](solution/relatorio-executivo.pdf)

---

## Executive Summary

Antes de diagnosticar, testei se os dados aguentavam um diagnóstico, e **a base de métricas (Dataset 1) é sintética**: os "tempos" caem numa janela de 27 h, metade dos tickets fechados é resolvida antes da 1ª resposta, nenhuma variável explica a satisfação e a "pior" combinação de canal × prioridade × tipo não se distingue do acaso. O primeiro gargalo é de **medição**.
Com os 48 mil tickets reais do Dataset 2, construí e medi uma **triagem com três faixas de confiança**: **65,5% roteados sozinhos com 96,4% de acerto**, 23,3% com 2 sugestões ao agente e 11,2% para humano. Uma política explícita define o que **nunca** automatizar (rotear ≠ executar ≠ responder).
Um classificador simples treinado no histórico **superou o LLM em todas as configurações testadas**: **o ativo é o histórico rotulado da empresa.** O LLM ficou onde agrega, na redação de rascunhos.
O ganho estimado é de **~1.200 h/ano de agente no cenário base (faixa de 550 a 2.100 h)**. A recomendação é instrumentar a operação e rodar 4 semanas de piloto em modo sombra antes de qualquer decisão financeira.

---

## Solução

| Entregável | Arquivo |
|---|---|
| Relatório executivo (para o Diretor) | [`solution/relatorio-executivo.pdf`](solution/relatorio-executivo.pdf) · [HTML](solution/relatorio-executivo.html) |
| 1. Diagnóstico: auditoria dos dados + "onde o fluxo trava" | [`solution/01-diagnostico/outputs/auditoria.md`](solution/01-diagnostico/outputs/auditoria.md) |
| 1. Diagnóstico: tempo de triagem e ROI | [`solution/01-diagnostico/outputs/modelo_desperdicio.md`](solution/01-diagnostico/outputs/modelo_desperdicio.md) |
| 2. Proposta de automação | [`solution/02-proposta-automacao/proposta.md`](solution/02-proposta-automacao/proposta.md) |
| 3. Protótipo funcional (*Triage Copilot*) | [no ar](https://ai-master-challenge-v56hxnnkz3z5z7khq8n5oz.streamlit.app/) · [código](solution/03-prototipo/) |
| Benchmark de classificadores (TF-IDF × embeddings × kNN × LLM) | [`solution/03-prototipo/benchmark/outputs/benchmark.md`](solution/03-prototipo/benchmark/outputs/benchmark.md) |
| Avaliação final do motor (**números oficiais**) | [`solution/03-prototipo/benchmark/outputs/motor_final.md`](solution/03-prototipo/benchmark/outputs/motor_final.md) |

### Abordagem

1. **Desconfiar antes de analisar.** Antes de abrir os dados, levantei a hipótese de que a base era sintética. Depois testei cada campo: o texto é real? os tempos são tempos? as variáveis se relacionam? algo explica o CSAT? Para "não achar nada" valer como resultado, calculei o poder estatístico.
2. **Responder às perguntas do Diretor ao pé da letra, com o grau de certeza.** Inclusive "quais combinações geram os piores tempos", com o teste que mostra que é ruído.
3. **Cruzar os datasets pelo que cada um prova.** O Dataset 1 dá a *estrutura* da operação e 8.469 tickets de **outro domínio**, usados para testar as travas da IA. O Dataset 2, com rótulos reais, prova a *automação*.
4. **Comparar abordagens em vez de assumir.** TF-IDF, embeddings, kNN e LLM (zero-shot, few-shot, RAG e um modelo mais forte), todos na mesma amostra, com teste pareado.
5. **Desenhar a automação como produto:** faixas calibradas na validação e medidas no teste, limiar por categoria, travas de domínio e uma política que separa rotear, executar e responder.
6. **Revisão adversarial em cada conclusão.** Um agente juiz independente recalculou tudo do zero e tentou refutar. Os três pareceres mudaram a entrega (ver o Process Log).

### Resultados / Findings

**Diagnóstico** (Dataset 1: 8.469 tickets, não ~30 mil):

| Pergunta / teste | Resultado |
|---|---|
| **Onde o fluxo trava?** (80 combinações canal × prioridade × tipo) | A "pior" parece 7,6 h mais lenta que a "melhor", mas o acaso gera em média 8,1 h (permutação p = 0,68); as "melhores" têm duração **negativa** |
| **O que impacta a satisfação?** | CSAT uniforme de 1 a 5 (p = 0,80); 0 de 10 variáveis com efeito após Bonferroni; poder para detectar 0,21 ponto |
| Os tempos são tempos? | Janela de 27 h; resolução antes da 1ª resposta em 49% dos fechados |
| As variáveis se relacionam? | 0 de 21 pares associados; o texto não prevê nem o assunto (6,4% × 6,8% do chute) |
| "67% não fechados" é backlog? | **Não**: os 3 status são equiprováveis (p = 0,33), ou seja, sorteio |
| **Quanto estamos desperdiçando?** | Não mensurável com tempos falsos. Por premissa explícita: a triagem consome ~1.500 h/ano (cenário base), das quais a IA libera ~1.218 h |

**Automação** (Dataset 2, teste com 9.568 tickets nunca vistos):

| Faixa | % | Acerto |
|---|---|---|
| Automático | 65,5% | 96,4% (IC95% de 95,9 a 96,8%); todas as categorias ≥ 95% (Hardware no limite, 95,1%) |
| Sugestão (agente escolhe entre 2) | 23,3% | a certa está entre as 2 em 91,0% |
| Humano | 11,2% | 9,7% barrados pela trava de domínio + 1,5% por confiança baixa |
| Tickets de outro domínio (Dataset 1) | — | 34% iriam para o automático sem as travas; 11% com elas |

**Classificação: modelo simples × LLM** (mesma amostra de 400 tickets): TF-IDF + regressão logística 85,0% (86,0% no teste completo) · LLM com os 5 tickets mais parecidos no prompt (RAG) 76,9% · kNN 73,3% · LLM mais forte com exemplos 53,5% (n = 200) · LLM zero-shot 44,0%. Diferença pareada para o melhor LLM: McNemar p = 0,0003.

**Política (o que não automatizar):** segurança (0,7%), saúde/afastamento (2,0%), desligamento (2,3%), aprovação financeira (10,4%), privilégio (13,0%) e urgência (7,7%). Ao todo, 27,7% dos tickets têm uma ação que exige humano. Há exemplos reais na [proposta](solution/02-proposta-automacao/proposta.md).

### Recomendações

1. **Semana 0: instrumentar** (carimbos separados, log de mudança de fila, categoria na abertura × na resolução) e **retreinar** no histórico rotulado da operação.
2. **Semanas 1–2: modo sombra.** A IA classifica sem rotear e mede-se a concordância com os agentes.
3. **Semanas 3–4: automático em 3 categorias estáveis** (Purchase, Access, Storage: 97,8–99,0%).
4. **Política ativa desde o 1º dia**, com donos em Segurança, RH e Financeiro.
5. **Retreino mensal** com as correções dos agentes. A decisão de escalar sai dos números do piloto.

### Limitações

- O desempenho foi medido em tickets internos de TI, em inglês. Esta operação precisa retreinar no próprio histórico, e a qualidade desse histórico ainda não foi verificada.
- Os rótulos do Dataset 2 têm ruído estimado de 15 a 25%.
- O limiar das travas de domínio foi escolhido com os mesmos dados usados para avaliá-lo (resultado otimista). A trava também barra tickets normais atípicos.
- A política usa palavras-chave: há falsos alarmes e variações que escapam.
- O ROI usa premissas de mercado (a principal, de fonte fraca) até o piloto medir; é tempo liberado bruto, não caixa.
- O LLM foi testado no plano gratuito do Gemini (sobrecarga e cota limitaram o modelo mais forte a 200 tickets).

### Como rodar

**Protótipo no ar:** https://ai-master-challenge-v56hxnnkz3z5z7khq8n5oz.streamlit.app/ (na 1ª visita após inatividade, ele pode levar 1 a 2 minutos para acordar).

**Localmente** (todos os comandos a partir de `submissions/arthur-leite/solution/03-prototipo`):
```bash
pip install -r requirements.txt
python baixar_dados.py                  # baixa os 2 datasets do Kaggle (sem login)
streamlit run app.py                    # na 1ª execução, treina o motor (~1 min, CPU)
```
Opcional, para os rascunhos por LLM: crie `.env` com `GEMINI_API_KEY=...` (chave gratuita do Google AI Studio). Sem ela, todo o resto funciona.

**Reproduzir as análises** (a partir de `submissions/arthur-leite`):
```bash
python solution/01-diagnostico/01_auditoria_dados.py
python solution/01-diagnostico/02_modelo_desperdicio.py
python solution/03-prototipo/benchmark/avaliar_motor.py
# benchmark completo (inclui PyTorch, ~2 GB):
pip install -r solution/03-prototipo/requirements-benchmark.txt
python solution/03-prototipo/benchmark/embed_ds2.py
python solution/03-prototipo/benchmark/benchmark.py   # usa as respostas do LLM já versionadas; não chama API
```

---

## Process Log — Como usei IA

> Diário completo, escrito durante o trabalho: [`process-log/PROCESS_LOG.md`](process-log/PROCESS_LOG.md) · Pareceres do juiz: [`process-log/revisoes/`](process-log/revisoes/) · Conversa completa: [`process-log/chat-exports/`](process-log/chat-exports/) · Screenshots: [`process-log/screenshots/`](process-log/screenshots/)

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude Code (Claude Opus 5.5) | Agente principal: leitura do case, análise, código, protótipo, git, deploy |
| Subagentes "juiz" (Claude Code) | Revisão adversarial independente: recalcularam do zero e reproduziram a entrega a frio a partir do GitHub |
| Google Gemini (flash-lite, 3.8 flash) | Benchmark de classificação (zero-shot, few-shot, RAG) e rascunho de respostas no protótipo |
| scikit-learn, sentence-transformers | Classificadores (TF-IDF, embeddings MiniLM, kNN) |
| Streamlit (+ Streamlit Cloud) e Plotly | Protótipo e deploy |
| Claude in Chrome | Leitura da vaga e teste visual do protótipo |

### Workflow

1. Li a vaga e todos os arquivos do repo e escolhi o 002 pelo encaixe com a minha experiência: opero agentes de atendimento com IA em produção.
2. **Hipótese antes dos dados:** a base devia ser sintética. Confirmada na 1ª checagem e depois auditada com testes estatísticos.
3. Pedi que **cada conclusão** passasse por um agente juiz com contexto limpo e postura adversarial.
4. Benchmark de 4 abordagens + 4 variantes de LLM, com limiares calibrados na validação e medidos no teste.
5. Protótipo construído e testado com casos de borda (phishing, outro idioma, aprovação). Cada falha virou uma trava.
6. ROI reescrito depois do juiz: só o que é sustentável, com o resto declarado como fora.
7. Juiz final reproduziu tudo a frio a partir do GitHub; as correções dele (incluindo um bug que quebrava o deploy) foram aplicadas e testadas num ambiente limpo.

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
| O LLM inventou um id numa resposta em lote | Checagem de integridade | Respostas filtradas pelos ids válidos (1 em 1.400) |
| Faixa humana atribuída a "confiança baixa" | Juiz final (9,7 dos 11,2 pontos vêm da trava) | Decomposição gerada pelo código e citada em todos os documentos |
| **Deploy quebrou no Streamlit Cloud** (pandas 3) | Erro no deploy + juiz final, de forma independente | Código compatível com as 2 versões; testado num venv limpo com pandas 3 |
| Escrevi que os IC das combinações extremas "se sobrepõem" | Eu, ao reler a tabela | Falso para alguns pares; o argumento certo é comparações múltiplas + permutação |
| Pergunta "onde o fluxo trava" respondida só com uma recusa | Juiz final | Tabela literal das piores/melhores combinações, com o teste de ruído |

### O que eu adicionei que a IA sozinha não faria

- **Desconfiar da base antes de analisar.** O caminho padrão (o baseline) é calcular "tempo médio por canal" sobre dados sintéticos.
- **O desenho rotear ≠ executar ≠ responder** e a lista do que nunca automatizar, vindos de operar atendimento com IA em produção.
- **Exigir um revisor adversarial** para cada número. Foi ele que derrubou o "backlog de 67%", o ROI inflado e um bug que quebraria o protótipo para o avaliador.
- **Escolher entregar um ROI menor e defensável** (1.218 h no cenário base contra 1.496 h na 1ª versão) e dizer o que ficou de fora.

---

## Evidências

- [x] Chat export (conversa completa com o Claude Code, com o raciocínio interno e a memória pessoal removidos): [`process-log/chat-exports/`](process-log/chat-exports/)
- [x] Git history: commits por fase nesta branch
- [x] Pareceres do agente juiz: [`process-log/revisoes/`](process-log/revisoes/)
- [x] Respostas brutas do LLM no benchmark (versionadas): [`solution/03-prototipo/benchmark/outputs/llm_respostas/`](solution/03-prototipo/benchmark/outputs/llm_respostas/)
- [x] Screenshots do protótipo: [`process-log/screenshots/`](process-log/screenshots/)
- [x] Protótipo publicado: https://ai-master-challenge-v56hxnnkz3z5z7khq8n5oz.streamlit.app/

---

_Submissão enviada em: {{DATA}}_
