"""
Triage Copilot: protótipo de triagem de suporte com IA.

    streamlit run app.py

Abas:
  1. Triagem ao vivo   cole um ticket e veja a decisão, a explicação e o rascunho
  2. Fila de teste     1.000+ tickets reais nunca vistos no treino, com desempenho medido
  3. Diagnóstico       o que os dados permitem (e não permitem) afirmar
  4. ROI               premissas ajustáveis → horas e R$
  5. Como funciona     fluxo, o que não automatizamos e limitações
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src import llm, roi
from src.politica import REGRAS, ROTULOS, avaliar
from src.triagem import (COBERTURA_MINIMA, DADOS, SIMILARIDADE_MINIMA, MotorTriagem, decidir, dividir)

st.set_page_config(page_title="Triage Copilot", page_icon="🎫", layout="wide")

COR_FAIXA = {"auto": "#2E7D32", "sugere": "#F9A825", "humano": "#C62828"}
NOME_FAIXA = {"auto": "Automático", "sugere": "Sugestão (humano confirma)", "humano": "Humano"}


@st.cache_resource(show_spinner="Carregando o motor de triagem (na 1ª vez, treina em ~1 min)...")
def motor() -> MotorTriagem:
    return MotorTriagem.carregar()


@st.cache_data(show_spinner=False)
def teste() -> pd.DataFrame:
    _, _, te = dividir(pd.read_csv(DADOS))
    return te


@st.cache_data(show_spinner="Classificando o conjunto de teste...")
def avaliacao_teste() -> pd.DataFrame:
    te = teste()
    r = motor().classificar_lote(te["Document"])
    r["real"] = te["Topic_group"]
    r["acertou"] = r["categoria"] == r["real"]
    r["acertou_top2"] = (r["top2_a"] == r["real"]) | (r["top2_b"] == r["real"])
    return r


m = motor()
st.title("🎫 Triage Copilot")
st.caption("Triagem de tickets com IA que sabe quando **não** decidir sozinha. "
           "Modelo treinado em 33 mil tickets reais de TI (Dataset 2) e medido em 9,5 mil tickets que ele nunca viu.")

aba1, aba2, aba3, aba4, aba5 = st.tabs(["Triagem ao vivo", "Fila de teste", "Diagnóstico", "ROI", "Como funciona"])

# ------------------------------------------------------------------ 1. TRIAGEM AO VIVO
with aba1:
    exemplos = {
        "— escolha um exemplo —": "",
        "Hardware rotineiro": "Hi, my laptop screen is flickering and the external monitor is not detected since this morning. Can you help?",
        "Possível phishing": "URGENT: I received a suspicious email asking for my password and I clicked the link. What should I do?",
        "Aprovação de compra": "Please approve the purchase order for 3 new docking stations for the finance team.",
        "Desligamento": "John is a leaver from Friday, please remove his access to all systems and collect his laptop.",
        "Fora do domínio (português)": "Quero saber o status do meu pedido de reembolso do curso",
        "Ticket real aleatório do teste": "__aleatorio__",
    }
    escolha = st.selectbox("Exemplos", list(exemplos))
    padrao = exemplos[escolha]
    if padrao == "__aleatorio__":
        amostra = teste().sample(1, random_state=np.random.randint(1e6)).iloc[0]
        padrao = amostra["Document"]
        st.info(f"Ticket real do conjunto de teste. Categoria verdadeira: **{amostra['Topic_group']}** "
                "(texto já pré-processado na origem: sem pontuação nem stopwords).")
    texto = st.text_area("Texto do ticket (em inglês, como os dados de treino)", value=padrao, height=110)

    if texto.strip():
        r = m.classificar(texto)
        pol = avaliar(texto)
        dec = decidir(r, pol)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fila", dec.fila)
        c2.metric("Modo", NOME_FAIXA[r.faixa] if "Escalado" not in dec.modo else "Escalado")
        c3.metric("Confiança do modelo", f"{r.confianca:.0%}")
        c4.metric("Quem executa a ação", dec.executar)
        if dec.escalar:
            st.error("🚨 Escalar agora: a política detectou urgência ou incidente de segurança.")

        st.markdown("#### Por quê")
        for linha in dec.explicacao:
            st.markdown(f"- {linha}")

        e1, e2 = st.columns(2)
        with e1:
            st.markdown("**Palavras que mais pesaram**")
            if r.palavras_chave:
                st.dataframe(pd.DataFrame(r.palavras_chave, columns=["termo", "peso"]).round(3),
                             hide_index=True, use_container_width=True)
            st.markdown(f"**Top-2:** {r.top2[0][0]} ({r.top2[0][1]:.0%}) · {r.top2[1][0]} ({r.top2[1][1]:.0%})")
            st.caption(f"Travas de domínio: o modelo reconhece {r.cobertura_vocab:.0%} das palavras (mín. {COBERTURA_MINIMA:.0%}); "
                       f"similaridade com o histórico {r.similaridade:.2f} (mín. {SIMILARIDADE_MINIMA}).")
        with e2:
            st.markdown("**Tickets parecidos já resolvidos**")
            for s in r.similares:
                st.markdown(f"- `{s['categoria']}` ({s['similaridade']:.2f}) {s['texto'][:160]}...")

        st.markdown("#### Rascunho de resposta para o agente")
        if not dec.pode_rascunho:
            st.warning("Rascunho por LLM **bloqueado**: dado sensível ou ticket fora do domínio. Resposta 100% humana.")
        elif not llm.disponivel():
            st.caption("LLM desligado (sem GEMINI_API_KEY no .env). Todo o resto funciona sem ele.")
        elif st.button("Gerar rascunho com Gemini"):
            with st.spinner("Redigindo..."):
                txt = llm.rascunhar_resposta(texto, dec.fila, r.similares, [ROTULOS[a] for a in pol.alertas])
            st.text_area("Rascunho (o agente revisa antes de enviar)", txt or "API indisponível no momento.", height=180)

# ------------------------------------------------------------------ 2. FILA DE TESTE
with aba2:
    av = avaliacao_teste()
    st.markdown(f"**{len(av):,} tickets reais** que o modelo nunca viu no treino. Nada aqui é escolhido a dedo: "
                "é o conjunto de teste inteiro, ou uma amostra aleatória dele.".replace(",", "."))
    n = st.slider("Tamanho da fila", 200, len(av), 1000, step=100)
    semente = st.number_input("Semente da amostra", 0, 9999, 0)
    f = av.sample(n, random_state=int(semente))

    resumo = (f.groupby("faixa").agg(tickets=("acertou", "size"), precisao=("acertou", "mean"), top2=("acertou_top2", "mean"))
              .reindex(["auto", "sugere", "humano"]))
    resumo["% da fila"] = resumo["tickets"] / len(f)
    k = st.columns(3)
    for col, faixa in zip(k, ["auto", "sugere", "humano"]):
        lin = resumo.loc[faixa]
        extra = f"acerto da 1ª opção: {lin.precisao:.1%}" if faixa != "sugere" else f"certa entre as 2: {lin.top2:.1%}"
        col.metric(NOME_FAIXA[faixa], f"{lin['% da fila']:.1%} da fila", extra)

    g1, g2 = st.columns(2)
    with g1:
        por_cat = f.groupby(["categoria", "faixa"]).size().reset_index(name="tickets")
        st.plotly_chart(px.bar(por_cat, x="tickets", y="categoria", color="faixa", orientation="h",
                               color_discrete_map=COR_FAIXA, title="Faixa de automação por categoria prevista"),
                        use_container_width=True)
    with g2:
        cm = pd.crosstab(f["real"], f["categoria"], normalize="index")
        st.plotly_chart(px.imshow(cm, text_auto=".0%", color_continuous_scale="Greens", aspect="auto",
                                  title="Matriz de confusão (linhas = categoria real)"), use_container_width=True)

    pol_lote = teste().loc[f.index, "Document"].map(avaliar)
    alert = pd.Series([a for p in pol_lote for a in p.alertas]).map(ROTULOS).value_counts()
    st.markdown(f"**Política:** {pol_lote.map(lambda p: p.exige_humano_para_executar).mean():.1%} dos tickets da fila têm "
                "uma ação que exige humano, mesmo quando o roteamento é automático.")
    st.dataframe(alert.rename("tickets").to_frame(), use_container_width=True)
    with st.expander("Ver os erros da faixa automática"):
        erros = f[(f["faixa"] == "auto") & ~f["acertou"]].join(teste()["Document"])
        st.dataframe(erros[["Document", "real", "categoria", "confianca"]], use_container_width=True)

# ------------------------------------------------------------------ 3. DIAGNÓSTICO
with aba3:
    st.markdown("""
### O primeiro gargalo é de medição
Antes de apontar onde o fluxo trava, testei se os dados de operação (Dataset 1, 8.469 tickets) conseguem responder isso. **Não conseguem.**

| O que testei | Resultado |
|---|---|
| Os "tempos" são tempos? | São carimbos de data e hora numa janela de 27 h; em **49%** dos fechados, a resolução vem **antes** da 1ª resposta |
| A satisfação varia com algo? | CSAT uniforme de 1 a 5; **nenhuma** variável (canal, prioridade, tipo, produto, tempo, perfil) tem efeito, e os testes detectariam 0,2 ponto |
| As variáveis conversam entre si? | **0 de 21** pares associados; um "Billing inquiry" tem a mesma chance de ter assunto "Hardware issue" que "Payment issue" |
| O texto é real? | 100% com campo não preenchido (`{product_purchased}`); 16 frases-modelo |

**Decisão:** não apresento "gargalos por canal" nem "drivers de satisfação". Seriam números com cara de verdade que levariam a decisões erradas.
A prova da automação é feita no Dataset 2 (dados reais), e o desperdício é estimado por premissas explícitas (aba ROI).
Auditoria completa e revisada por um agente juiz independente: `solution/01-diagnostico/outputs/auditoria.md`.

### Plano de instrumentação (30 dias)
Para ter um diagnóstico real, a operação precisa registrar por ticket:
1. `criado_em`, `primeira_resposta_em`, `resolvido_em` como **carimbos separados**, para medir durações de verdade
2. **Cada mudança de fila**, com horário: mede reroteamento e tempo perdido na fila errada (o maior ganho esperado da IA)
3. A categoria **atribuída na abertura** × a categoria **na resolução**: mede o erro de triagem atual
4. CSAT com taxa de resposta, e não só a nota
5. Tempo ativo do agente por ticket (o handle time), separado do tempo de espera
""")

# ------------------------------------------------------------------ 4. ROI
with aba4:
    roi.renderizar(st, avaliacao_teste())

# ------------------------------------------------------------------ 5. COMO FUNCIONA
with aba5:
    st.markdown("""
### Fluxo proposto
```
ticket entra
   │
   ├─► 1. Política (regras explícitas): segurança? saúde? desligamento? aprovação? privilégio? urgência?
   │        └─ segurança → fila de Segurança + escalonamento (sobrepõe tudo)
   │
   ├─► 2. Travas de domínio: o modelo conhece este tipo de ticket?   não → HUMANO classifica
   │
   ├─► 3. Classificador (TF-IDF + regressão logística, treinado no histórico)
   │        ├─ confiança ≥ limiar da categoria → AUTOMÁTICO (precisão medida ≥ 95%)
   │        ├─ confiança média               → SUGESTÃO: humano escolhe entre 2 (a certa está entre elas em ≥ 90%)
   │        └─ confiança baixa               → HUMANO classifica
   │
   └─► 4. Na fila: agente recebe palavras-chave + tickets parecidos + rascunho (LLM, opcional)
            └─ ação sensível (aprovar, conceder, revogar) → sempre humano
```
### Por que não um LLM para classificar?
No mesmo conjunto de tickets, o modelo simples acertou **85%**. O Gemini acertou **44–54%** sozinho e **77%** quando recebeu
os 5 tickets mais parecidos do histórico no prompt (RAG). As categorias são **convenções internas**
(os termos que mais pesam em "Administrative rights" são *outlook, upgrade, install, windows*: instalação de software; em
"Miscellaneous", *change, approval, groups*). Um modelo genérico
não tem como saber isso; o histórico da empresa sabe, e o LLM só se aproxima quando recebe esse histórico. Bônus: custo zero por ticket e nenhum dado sai da empresa. O LLM fica onde ele é bom: **redigir**.
Benchmark completo: `benchmark/outputs/benchmark.md`.

### O que NÃO automatizamos
""")
    st.dataframe(pd.DataFrame([{"Regra": ROTULOS[k], "Frequência no Dataset 2": v["freq_ds2"], "O que acontece": v["acao"],
                                "Por quê": v["porque"]} for k, v in REGRAS.items()]), hide_index=True, use_container_width=True)
    st.markdown("""
### Limitações
- Treinado em tickets internos de TI, **em inglês**. Para outra operação, retreina-se com o histórico dela (minutos, sem GPU).
- Os rótulos do Dataset 2 têm ruído estimado de 15–25%: parte dos "erros" medidos é rótulo errado.
- As regras da política são por palavra-chave: alta sensibilidade de propósito, mas com falsos positivos (custam segundos de um humano).
- O ROI usa premissas de mercado, porque os tempos do Dataset 1 são sintéticos. Os números reais vêm do plano de instrumentação.
""")
