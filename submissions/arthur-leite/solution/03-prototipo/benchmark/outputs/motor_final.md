# Motor de triagem final: avaliação no conjunto de teste

_9.568 tickets reais do Dataset 2 que o modelo nunca viu. Gerado por `benchmark/avaliar_motor.py`._

## 1. Faixas de automação

| Faixa | % dos tickets | Acerto da 1ª opção | Certa entre as 2 primeiras |
|---|---|---|---|
| Automático | 65,5% | 96,4% | 99,4% |
| Sugestão (humano escolhe entre 2) | 23,3% | 63,4% | 91,0% |
| Humano | 11,2% | 72,4% | 90,2% |

Intervalo de confiança de 95% (bootstrap) para o acerto da faixa automática: **95,9% a 96,8%**.

Para comparar: o modelo sem as travas acerta 86,0% no geral.

## 2. Faixa automática por categoria prevista

| Categoria | Limiar | Tickets automáticos | Acerto |
|---|---|---|---|
| Access | 0.71 | 1060 | 97,8% |
| Administrative rights | 0.71 | 174 | 96,0% |
| HR Support | 0.71 | 1569 | 95,8% |
| Hardware | 0.78 | 1563 | 95,1% |
| Internal Project | 0.71 | 281 | 96,4% |
| Miscellaneous | 0.75 | 810 | 96,0% |
| Purchase | 0.71 | 410 | 99,0% |
| Storage | 0.71 | 401 | 97,8% |

**Principais erros automáticos (real → previsto):** Hardware → HR Support: 26; Administrative rights → Hardware: 22; HR Support → Hardware: 20; Miscellaneous → HR Support: 17; Hardware → Miscellaneous: 15

## 3. Teste fora do domínio (tickets de cliente do Dataset 1)

Um modelo de TI interna recebendo tickets de clientes de produto deveria perceber que não sabe.

| Faixa | % dos 8.469 tickets |
|---|---|
| auto | 10,8% |
| sugere | 8,7% |
| humano | 80,5% |

Sem as travas de domínio, **34,1%** desses tickets teriam ido para a faixa automática.

## 4. Política no conjunto de teste

- 27,9% dos tickets têm uma ação que exige humano
- 2,7% bloqueiam o rascunho por LLM
- 7,9% são escalados

| Regra | Tickets |
|---|---|
| Privilégio de acesso | 1265 |
| Aprovação financeira | 1009 |
| Urgência / indisponibilidade | 710 |
| Desligamento | 216 |
| Saúde / afastamento | 194 |
| Segurança | 70 |