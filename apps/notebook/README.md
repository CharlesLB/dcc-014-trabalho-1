# Notebooks da apresentação

Gera o notebook da apresentação, `notebooks/torre_de_londres.ipynb`, a partir do código de `src/`. Ele roda sozinho no Colab: o código do projeto vai dentro dele.

A apresentação é feita pelo próprio Colab. Todo código marcado com **(ignore)** fica no topo, na seção Setup. Depois dela, cada seção de algoritmo segue a ordem dos slides: o código do projeto que é apresentado fica no ponto do slide, como `%%writefile` no mesmo caminho de `src/`, e o resto são chamadas de uma linha às funções do Setup.

| Seção | Conteúdo |
|---|---|
| Setup (ignore) | Os módulos de `src/` que não aparecem nos slides, pasta por pasta, cada um numa célula `%%writefile`; uma célula recolhida que grava os módulos dos slides (eles são mostrados de novo nas seções); funções de apresentação, funções dos gráficos e fluxogramas. |
| Uma por algoritmo | Na ordem dos slides: o problema (P1), a ideia, o laço e as listas, as regras, a estratégia de controle, as duas estratégias na mesma raiz, sem poda (crescimento por nível, árvore e ABERTOS/FECHADOS iteração a iteração, crescente e decrescente), com poda (idem), pseudocódigo com o código do algoritmo, caminho solução, comparativos (caminhos, crescente contra decrescente, contra os outros algoritmos, quem explorou menos nós) e complexidade. Fecha com a conclusão e os extras: fluxograma, trace bruto e comparações no placar e nos 36 objetivos. |
| Comparação dos algoritmos | Matriz completa (4 algoritmos × 2 estratégias) em P1, com a carta desenhada sobre o gráfico, e nos 36 objetivos, em boxplot; qualidade da solução, tabela de complexidade dos quatro algoritmos e a análise. Os gráficos deixam a irrevogável de fora; as tabelas mostram os quatro. |
| Integrantes | O grupo. |

A seção da busca ordenada tem, logo depois das regras, a lógica dos custos: a regra 10 + peso × distância, uma parte por vez com o porquê, e o estudo que compara 7 modelos de custo pelo motor do projeto (cerca de 5 s).

A primeira seção (busca irrevogável) mostra os módulos compartilhados: legenda e cartas no slide do problema, o motor no slide do laço, as regras e as estratégias nos slides delas. A fronteira (pilha, fila e fila por custo) aparece no slide da ideia do backtracking, o primeiro algoritmo que usa uma.

## Gerar

```bash
make notebooks                                 # ou: python apps/notebook/build.py
python apps/notebook/build.py --check          # falha se o notebook estiver atrasado em relação a src/
```

O gerador usa só a biblioteca padrão. Mudou algo em `src/`? Gere de novo e versione o notebook junto.

## Subir para o Colab

O selo "Abrir no Colab" no topo do notebook abre a versão da `main` direto do GitHub. Sem push, use **Arquivo → Fazer upload de notebook** com `notebooks/torre_de_londres.ipynb`.

Rode **Ambiente de execução → Executar tudo**. O notebook usa pandas, matplotlib e o Graphviz (`dot`), que o Colab já traz. Sem o `dot`, as árvores aparecem em texto.

## Estrutura

```
apps/notebook/
├── build.py           entrada: gera o notebook ou verifica se está em dia
├── cells.py           células, marcador (ignore) e notebook no formato .ipynb
├── source.py          lê src/ na ordem das pastas e monta a seção Setup
├── pages/
│   ├── common.py      cabeçalho, integrantes e funções de apresentação
│   ├── algorithm.py   uma seção por algoritmo, no roteiro dos slides
│   └── analysis.py    comparação dos algoritmos: gráficos, complexidade e análise
└── notebooks/         saída gerada (não editar à mão)
```
