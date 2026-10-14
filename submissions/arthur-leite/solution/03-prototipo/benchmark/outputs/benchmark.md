# Benchmark de classificadores — Dataset 2

Treino 33,485 · Validação 4,784 · Teste 9,568 (estratificado, seed 42)

## 1. Teste completo

| Modelo | Acurácia | F1-macro | Treino | Latência/ticket |
|---|---|---|---|---|
| A. TF-IDF + Regressão Logística | 0.860 | 0.860 | 27 s | 0.04 ms |
| B. Embeddings MiniLM + Regressão Logística | 0.808 | 0.813 | 4 s | ver nota |

## 2. Amostra de 400 tickets do teste (comparação com LLM)

| Modelo | n | Acurácia | F1-macro | Tokens/ticket (entrada+saída) | Segundos/ticket |
|---|---|---|---|---|---|
| C. gemini-3.5-flash-lite_few-shot | 400 | 0.480 | 0.490 | 117 | 0.31 |
| A na mesma amostra | 400 | 0.850 | 0.864 | 0 | <0,01 |
| B na mesma amostra | 400 | 0.782 | 0.786 | 0 | <0,01 |
| C. gemini-3.5-flash-lite_zero-shot | 400 | 0.440 | 0.412 | 77 | 0.09 |
| A na mesma amostra | 400 | 0.850 | 0.864 | 0 | <0,01 |
| B na mesma amostra | 400 | 0.782 | 0.786 | 0 | <0,01 |

## 3. Faixas de automação (limiares escolhidos na validação, medidos no teste)

Regra: **auto** quando a 1ª categoria acerta ≥ 95%; **sugere** (humano escolhe entre 2) quando a certa está entre as 2 primeiras ≥ 90%; abaixo disso, **humano** classifica do zero.

| Modelo | Limiares (auto / sugere) | Auto: cobertura · precisão | Sugere: cobertura · precisão · top-2 | Humano: cobertura · precisão do modelo |
|---|---|---|---|---|
| A | 0.71 / 0.35 | 74.2% · 95.1% | 24.1% · 61.8% · 90.3% | 1.8% · 35.5% |
| B | 0.78 / 0.74 | 63.0% · 94.2% | 4.2% · 79.6% · 94.0% | 32.9% · 55.2% |

## 4. Desempenho por categoria — modelo A

```
                       precision    recall  f1-score   support

               Access      0.907     0.884     0.896      1425
Administrative rights      0.895     0.679     0.772       352
           HR Support      0.865     0.872     0.869      2183
             Hardware      0.811     0.887     0.847      2724
     Internal Project      0.900     0.825     0.861       424
        Miscellaneous      0.828     0.829     0.828      1412
             Purchase      0.975     0.872     0.921       493
              Storage      0.939     0.834     0.884       555

             accuracy                          0.860      9568
            macro avg      0.890     0.835     0.860      9568
         weighted avg      0.863     0.860     0.860      9568

```

### Matriz de confusão

| real                  |   Access |   Administrative rights |   HR Support |   Hardware |   Internal Project |   Miscellaneous |   Purchase |   Storage |
|:----------------------|---------:|------------------------:|-------------:|-----------:|-------------------:|----------------:|-----------:|----------:|
| Access                |     1260 |                       3 |           34 |         83 |                  6 |              35 |          1 |         3 |
| Administrative rights |        7 |                     239 |           13 |         83 |                  1 |               9 |          0 |         0 |
| HR Support            |       31 |                       1 |         1904 |        160 |                 11 |              66 |          2 |         8 |
| Hardware              |       59 |                      17 |          115 |       2415 |                  9 |              94 |          8 |         7 |
| Internal Project      |        3 |                       1 |           25 |         29 |                350 |              16 |          0 |         0 |
| Miscellaneous         |       22 |                       2 |           71 |        126 |                 11 |            1170 |          0 |        10 |
| Purchase              |        2 |                       2 |            9 |         37 |                  1 |              10 |        430 |         2 |
| Storage               |        5 |                       2 |           29 |         43 |                  0 |              13 |          0 |       463 |