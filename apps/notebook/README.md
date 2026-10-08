# Notebooks da apresentação

Gera o notebook da apresentação, `notebooks/torre_de_londres.ipynb`, a partir do código de `src/`. Ele roda sozinho no Colab: o código do projeto vai dentro dele.

A apresentação é feita pelo próprio Colab. Todo código marcado com **(ignore)** fica no topo, na seção Setup. Depois dela, cada seção de algoritmo segue a ordem dos slides: o código do projeto que é apresentado fica no ponto do slide, como `%%writefile` no mesmo caminho de `src/`, e o resto são chamadas de uma linha às funções do Setup.

| Seção | Conteúdo |
|---|---|
| Setup (ignore) | Os módulos de `src/` que não aparecem nos slides, pasta por pasta, cada um numa célula `%%writefile`; uma célula recolhida que grava os módulos dos slides (eles são mostrados de novo nas seções); funções de apresentação, funções dos gráficos e fluxogramas. |
| Uma por algoritmo | Na ordem dos slides: o problema (P1), a ideia, o laço e as listas, as regras, a estratégia de controle, as duas estratégias na mesma raiz, sem poda (crescimento por nível, árvore e ABERTOS/FECHADOS iteração a iteração, crescente e decrescente), com poda (idem), pseudocódigo com o código do algoritmo, caminho solução, comparativos (caminhos, crescente contra decrescente, contra os outros algoritmos com o melhor de cada critério em verde, quem explorou menos nós) e complexidade. Fecha com a conclusão e os extras: fluxograma, trace bruto e comparações no placar e nos 36 objetivos. |
| Comparação dos algoritmos | Matriz completa (4 algoritmos × 2 estratégias) em P1, com a carta desenhada sobre o gráfico, e nos 36 objetivos, em boxplot; qualidade da solução, tabela de complexidade dos quatro algoritmos e a análise. Os gráficos deixam a irrevogável de fora; as tabelas mostram os quatro. |
| Integrantes | O grupo. |

A seção da busca ordenada tem, logo depois das regras, a lógica dos custos: a regra 10 + peso × distância, uma parte por vez com o porquê.

1. **10 por jogada**: garante o mínimo de movimentos.
2. **Distância**: a viagem longa (H1 ↔ H3) fica com o disco leve. Exemplo G17: dois caminhos de 4 movimentos empatam em 46 só com o peso; com a distância, custam 48 e 50, e as duas estratégias passam a achar o mesmo.
3. **Peso**: o azul pesa mais. Exemplo G11, ordem decrescente: 41 na largura, 39 na ordenada.

Cada jogada dos exemplos aparece desenhada, antes e depois, com o cálculo do custo (`show_hop`). Fecha com o ganho real: nos 1.260 pares início → objetivo, a ordenada sai em média 0,4% mais barata que a largura. O estudo roda pelo motor do projeto com 7 modelos de custo (cerca de 5 s) e mede também a maior economia, os nós gerados em relação à largura, as trocas de nó por execução e os movimentos a mais.

Depois dos comparativos, a seção da ordenada tem ainda os 36 objetivos: boxplot e quartis de nós expandidos, iterações, nós gerados e custo da solução para todas as combinações, da menor para a maior média, e o custo da solução só em P1.

A primeira seção (busca irrevogável) mostra os módulos compartilhados: legenda e cartas no slide do problema, o motor no slide do laço, as regras e as estratégias nos slides delas. O contrato da fronteira aparece no slide da ideia do backtracking, o primeiro algoritmo que usa uma; cada algoritmo com fronteira mostra a sua (pilha, fila ou fila por custo) no próprio slide da ideia.

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
