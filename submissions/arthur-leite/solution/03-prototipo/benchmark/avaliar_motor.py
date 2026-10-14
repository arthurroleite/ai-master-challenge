"""
Avaliação final do motor de triagem do protótipo: a fonte dos números citados no relatório.

Diferente de benchmark.py (que compara abordagens), aqui se mede o motor COMO ELE RODA no app:
limiar por categoria + travas de domínio + política.

    python benchmark/avaliar_motor.py      (a partir de solution/03-prototipo)
Saída: benchmark/outputs/motor_final.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROTO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTO))
from src.politica import ROTULOS, avaliar  # noqa: E402
from src.triagem import DADOS, RAIZ, MotorTriagem, dividir, preparar  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"


def pct(x: float, casas: int = 1) -> str:
    return f"{100 * x:.{casas}f}%".replace(".", ",")


def bootstrap_ic(acertos: np.ndarray, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    medias = [rng.choice(acertos, len(acertos)).mean() for _ in range(n)]
    return float(np.quantile(medias, 0.025)), float(np.quantile(medias, 0.975))


def main() -> None:
    m = MotorTriagem.carregar()
    _, _, te = dividir(pd.read_csv(DADOS))
    r = m.classificar_lote(te["Document"])
    r["real"] = te["Topic_group"]
    r["ok"] = r["categoria"] == r["real"]
    r["ok2"] = (r["top2_a"] == r["real"]) | (r["top2_b"] == r["real"])

    L = ["# Motor de triagem final: avaliação no conjunto de teste", "",
         f"_{len(r):,} tickets reais do Dataset 2 que o modelo nunca viu. Gerado por `benchmark/avaliar_motor.py`._".replace(",", "."), "",
         "## 1. Faixas de automação", "",
         "| Faixa | % dos tickets | Acerto da 1ª opção | Certa entre as 2 primeiras |", "|---|---|---|---|"]
    for f, nome in [("auto", "Automático"), ("sugere", "Sugestão (humano escolhe entre 2)"), ("humano", "Humano")]:
        g = r[r["faixa"] == f]
        L.append(f"| {nome} | {pct(len(g) / len(r))} | {pct(g['ok'].mean())} | {pct(g['ok2'].mean())} |")
    lo, hi = bootstrap_ic(r.loc[r["faixa"] == "auto", "ok"].values.astype(float))
    L += ["", f"Intervalo de confiança de 95% (bootstrap) para o acerto da faixa automática: **{pct(lo)} a {pct(hi)}**.", "",
          f"Para comparar: o modelo sem as travas acerta {pct(r['ok'].mean())} no geral.", "",
          "## 2. Faixa automática por categoria prevista", "",
          "| Categoria | Limiar | Tickets automáticos | Acerto |", "|---|---|---|---|"]
    auto = r[r["faixa"] == "auto"]
    for c, g in auto.groupby("categoria"):
        L.append(f"| {c} | {m.limiares[c]:.2f} | {len(g)} | {pct(g['ok'].mean())} |")

    # Para onde vão sozinhos os tickets de cada categoria real (erros da faixa automática)
    err = auto[~auto["ok"]].groupby(["real", "categoria"]).size().sort_values(ascending=False).head(5)
    L += ["", "**Principais erros automáticos (real → previsto):** " +
          "; ".join(f"{a} → {b}: {v}" for (a, b), v in err.items())]

    # Fora do domínio: tickets de cliente (Dataset 1) com o mesmo pré-processamento
    d1 = pd.read_csv(RAIZ / "data/ds1_customer_support/customer_support_tickets.csv")
    x1 = d1["Ticket Description"].str.replace(r"\{[^}]*\}", " ", regex=True).map(preparar)
    r1 = m.classificar_lote(x1)
    L += ["", "## 3. Teste fora do domínio (tickets de cliente do Dataset 1)", "",
          "Um modelo de TI interna recebendo tickets de clientes de produto deveria perceber que não sabe.", "",
          "| Faixa | % dos 8.469 tickets |", "|---|---|"]
    L += [f"| {f} | {pct((r1['faixa'] == f).mean())} |" for f in ["auto", "sugere", "humano"]]
    so_conf = (r1["confianca"] >= pd.Series([m.limiares[c] for c in r1["categoria"]], index=r1.index)).mean()
    L += ["", f"Sem as travas de domínio, **{pct(so_conf)}** desses tickets teriam ido para a faixa automática."]

    # Política no teste
    pol = te["Document"].map(avaliar)
    alertas = pd.Series([a for p in pol for a in p.alertas]).map(ROTULOS).value_counts()
    L += ["", "## 4. Política no conjunto de teste", "",
          f"- {pct(pol.map(lambda p: p.exige_humano_para_executar).mean())} dos tickets têm uma ação que exige humano",
          f"- {pct((~pol.map(lambda p: p.pode_gerar_rascunho)).mean())} bloqueiam o rascunho por LLM",
          f"- {pct(pol.map(lambda p: p.escalar).mean())} são escalados", "",
          "| Regra | Tickets |", "|---|---|"] + [f"| {k} | {v} |" for k, v in alertas.items()]

    OUT.mkdir(exist_ok=True)
    (OUT / "motor_final.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
