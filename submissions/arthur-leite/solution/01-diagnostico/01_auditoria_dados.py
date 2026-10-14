"""
Fase 1: auditoria de qualidade dos dados.

Pergunta: antes de diagnosticar a operação, os dados conseguem sustentar
um diagnóstico? Este script testa isso e grava o resultado em
outputs/auditoria.md.

Rodar a partir da pasta submissions/arthur-leite:
    python solution/01-diagnostico/01_auditoria_dados.py
"""
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, chisquare, kruskal, spearmanr

ROOT = Path(__file__).resolve().parents[2]
DS1 = ROOT / "data/ds1_customer_support/customer_support_tickets.csv"
DS2 = ROOT / "data/ds2_it_tickets/all_tickets_processed_improved_v3.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

CSAT = "Customer Satisfaction Rating"
CATEGORICAS = ["Ticket Type", "Ticket Subject", "Ticket Priority",
               "Ticket Channel", "Product Purchased", "Customer Gender", "Ticket Status"]


def cramers_v(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    """Força de associação entre duas categóricas (0 = nenhuma, 1 = total) e p-valor do qui-quadrado."""
    tabela = pd.crosstab(a, b)
    chi2, p, _, _ = chi2_contingency(tabela)
    n = tabela.values.sum()
    return float(np.sqrt(chi2 / (n * (min(tabela.shape) - 1)))), float(p)


def auditar_ds1(d: pd.DataFrame) -> list[str]:
    L = ["## Dataset 1: Customer Support Tickets", ""]
    L.append(f"- Registros: **{len(d):,}** (o enunciado fala em ~30.000)")

    # 1. Texto: placeholders e templates
    placeholder = d["Ticket Description"].str.contains(r"\{[^}]*\}", regex=True)
    template = (d["Ticket Description"].str.replace(r"\{[^}]*\}", "<P>", regex=True)
                .str.split(r"(?<=[.?!])\s", n=1, regex=True).str[0])
    L.append(f"- Descrições com placeholder não preenchido (ex.: `{{product_purchased}}`): "
             f"**{placeholder.sum():,} ({placeholder.mean():.0%})**")
    L.append(f"- Frases de abertura distintas: **{template.nunique()}**; a mais comum aparece em "
             f"{template.value_counts().iloc[0]:,} tickets ({template.value_counts(normalize=True).iloc[0]:.0%})")

    # 2. Timestamps
    frt = pd.to_datetime(d["First Response Time"])
    ttr = pd.to_datetime(d["Time to Resolution"])
    janela = (max(frt.max(), ttr.max()) - min(frt.min(), ttr.min())).total_seconds() / 3600
    dur = (ttr - frt).dt.total_seconds() / 3600
    L.append(f"- `First Response Time` e `Time to Resolution` são **timestamps, não durações**. "
             f"Todos caem numa janela de **{janela:.0f} horas** ({frt.min():%d/%m/%Y} a {ttr.max():%d/%m/%Y}), "
             f"enquanto as compras vão de {pd.to_datetime(d['Date of Purchase']).min():%Y} a "
             f"{pd.to_datetime(d['Date of Purchase']).max():%Y}")
    L.append(f"- Resolução **antes** da primeira resposta: **{(dur < 0).sum():,} de {dur.notna().sum():,} "
             f"tickets fechados ({(dur < 0).mean() / dur.notna().mean():.0%})**")

    # 3. CSAT
    notas = d[CSAT].dropna()
    dist = notas.value_counts().sort_index()
    L.append(f"- CSAT presente só nos tickets Closed: {notas.size:,} de {len(d):,} "
             f"({notas.size / len(d):.0%}). Distribuição 1→5: {dist.astype(int).to_dict()}, "
             f"teste de uniformidade p = {chisquare(dist).pvalue:.2f}")

    # 4. Independência entre as variáveis
    L += ["", "### Associação entre variáveis (Cramér's V)", "",
          "| Par | V | p-valor |", "|---|---|---|"]
    vs = []
    for a, b in itertools.combinations(CATEGORICAS, 2):
        v, p = cramers_v(d[a], d[b])
        vs.append(v)
        L.append(f"| {a} × {b} | {v:.3f} | {p:.2f} |")
    L.append(f"\nMaior V encontrado: **{max(vs):.3f}**. Abaixo de 0,1 é considerado associação desprezível.")

    # 5. O que explica o CSAT?
    c = d[d[CSAT].notna()].assign(dur=dur)
    L += ["", "### O que explica o CSAT?", "", "| Variável | teste | p-valor | amplitude das médias |", "|---|---|---|---|"]
    for col in CATEGORICAS[:-1]:
        grupos = [g[CSAT] for _, g in c.groupby(col)]
        medias = c.groupby(col)[CSAT].mean()
        L.append(f"| {col} | Kruskal-Wallis | {kruskal(*grupos).pvalue:.2f} | {medias.min():.2f}–{medias.max():.2f} |")
    for col, nome in [("dur", "Duração calculada"), ("Customer Age", "Idade")]:
        m = c[[col, CSAT]].dropna()
        r = spearmanr(m[col], m[CSAT])
        L.append(f"| {nome} | Spearman ρ={r.statistic:.3f} | {r.pvalue:.2f} | — |")

    # 6. O que AINDA é utilizável
    status = d["Ticket Status"].value_counts()
    L += ["", "### O que ainda é utilizável", "",
          f"- Mix de volume por canal, tipo e prioridade (contagens), para dimensionar a operação",
          f"- Backlog: **{status.get('Open', 0) + status.get('Pending Customer Response', 0):,} "
          f"({1 - status.get('Closed', 0) / len(d):.0%})** dos tickets não estão fechados; "
          f"{status.get('Pending Customer Response', 0):,} aguardam o cliente",
          "- A intenção real do texto × o campo `Ticket Type`: mede a qualidade da categorização manual"]
    return L


def auditar_ds2(d: pd.DataFrame) -> list[str]:
    palavras = d["Document"].str.split().str.len()
    dist = d["Topic_group"].value_counts()
    return ["", "## Dataset 2: IT Service Ticket Classification", "",
            f"- Registros: **{len(d):,}**; nulos: {int(d.isna().sum().sum())}; "
            f"textos duplicados: {d.duplicated('Document').sum()}",
            "- Texto real de e-mails corporativos, **pré-processado**: minúsculas, sem pontuação, "
            "sem stopwords e com dados pessoais removidos",
            f"- Tamanho: mediana de {palavras.median():.0f} palavras (p75 {palavras.quantile(.75):.0f}, máx. {palavras.max()})",
            f"- Classes **desbalanceadas**: {dist.index[0]} {dist.iloc[0]:,} ({dist.iloc[0] / len(d):.0%}) × "
            f"{dist.index[-1]} {dist.iloc[-1]:,} ({dist.iloc[-1] / len(d):.0%}). "
            "Por isso a métrica principal será o F1-macro, não a acurácia",
            "- Há ruído de rótulo natural (ex.: pedido de acesso a fila rotulado como `Storage`), "
            "o que impõe um teto de acurácia abaixo de 100%"]


def main() -> None:
    d1, d2 = pd.read_csv(DS1), pd.read_csv(DS2)
    linhas = ["# Auditoria de qualidade dos dados", ""] + auditar_ds1(d1) + auditar_ds2(d2)
    (OUT / "auditoria.md").write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
