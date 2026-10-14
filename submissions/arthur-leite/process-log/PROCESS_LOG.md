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
