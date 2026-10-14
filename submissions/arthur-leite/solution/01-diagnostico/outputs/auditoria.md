# Auditoria de qualidade dos dados

## Dataset 1: Customer Support Tickets

- Registros: **8,469** (o enunciado fala em ~30.000)
- Descrições com placeholder não preenchido (ex.: `{product_purchased}`): **8,469 (100%)**
- Frases de abertura distintas: **16**; a mais comum aparece em 5,868 tickets (69%)
- `First Response Time` e `Time to Resolution` são **timestamps, não durações**. Todos caem numa janela de **27 horas** (31/05/2023 a 02/06/2023), enquanto as compras vão de 2020 a 2021
- Resolução **antes** da primeira resposta: **1,365 de 2,769 tickets fechados (49%)**
- CSAT presente só nos tickets Closed: 2,769 de 8,469 (33%). Distribuição 1→5: {1.0: 553, 2.0: 549, 3.0: 580, 4.0: 543, 5.0: 544}, teste de uniformidade p = 0.80

### Associação entre variáveis (Cramér's V)

| Par | V | p-valor |
|---|---|---|
| Ticket Type × Ticket Subject | 0.034 | 0.98 |
| Ticket Type × Ticket Priority | 0.020 | 0.56 |
| Ticket Type × Ticket Channel | 0.022 | 0.46 |
| Ticket Type × Product Purchased | 0.064 | 0.92 |
| Ticket Type × Customer Gender | 0.019 | 0.66 |
| Ticket Type × Ticket Status | 0.023 | 0.34 |
| Ticket Subject × Ticket Priority | 0.040 | 0.65 |
| Ticket Subject × Ticket Channel | 0.039 | 0.72 |
| Ticket Subject × Product Purchased | 0.070 | 0.33 |
| Ticket Subject × Customer Gender | 0.038 | 0.77 |
| Ticket Subject × Ticket Status | 0.047 | 0.16 |
| Ticket Priority × Ticket Channel | 0.025 | 0.08 |
| Ticket Priority × Product Purchased | 0.072 | 0.26 |
| Ticket Priority × Customer Gender | 0.016 | 0.60 |
| Ticket Priority × Ticket Status | 0.022 | 0.23 |
| Ticket Channel × Product Purchased | 0.068 | 0.63 |
| Ticket Channel × Customer Gender | 0.017 | 0.57 |
| Ticket Channel × Ticket Status | 0.014 | 0.77 |
| Product Purchased × Customer Gender | 0.062 | 0.92 |
| Product Purchased × Ticket Status | 0.067 | 0.66 |
| Customer Gender × Ticket Status | 0.017 | 0.30 |

Maior V encontrado: **0.072**. Abaixo de 0,1 é considerado associação desprezível.

### O que explica o CSAT?

| Variável | teste | p-valor | amplitude das médias |
|---|---|---|---|
| Ticket Type | Kruskal-Wallis | 0.70 | 2.93–3.03 |
| Ticket Subject | Kruskal-Wallis | 0.81 | 2.80–3.18 |
| Ticket Priority | Kruskal-Wallis | 0.63 | 2.96–3.05 |
| Ticket Channel | Kruskal-Wallis | 0.28 | 2.95–3.08 |
| Product Purchased | Kruskal-Wallis | 0.67 | 2.54–3.22 |
| Customer Gender | Kruskal-Wallis | 0.63 | 2.97–3.03 |
| Duração calculada | Spearman ρ=0.022 | 0.25 | — |
| Idade | Spearman ρ=-0.004 | 0.83 | — |

### O que ainda é utilizável

- Mix de volume por canal, tipo e prioridade (contagens), para dimensionar a operação
- Backlog: **5,700 (67%)** dos tickets não estão fechados; 2,881 aguardam o cliente
- A intenção real do texto × o campo `Ticket Type`: mede a qualidade da categorização manual

## Dataset 2: IT Service Ticket Classification

- Registros: **47,837**; nulos: 0; textos duplicados: 0
- Texto real de e-mails corporativos, **pré-processado**: minúsculas, sem pontuação, sem stopwords e com dados pessoais removidos
- Tamanho: mediana de 26 palavras (p75 46, máx. 981)
- Classes **desbalanceadas**: Hardware 13,617 (28%) × Administrative rights 1,760 (4%). Por isso a métrica principal será o F1-macro, não a acurácia
- Há ruído de rótulo natural (ex.: pedido de acesso a fila rotulado como `Storage`), o que impõe um teto de acurácia abaixo de 100%