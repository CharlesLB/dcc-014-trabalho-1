# Notebooks da apresentação

Gera o notebook da apresentação, `notebooks/torre_de_londres.ipynb`, a partir do código de `src/`. Ele roda sozinho no Colab: o código do projeto vai dentro dele.

Cada seção de algoritmo segue a ordem dos slides. O código que aparece nos slides fica no ponto do slide, como `%%writefile` no mesmo caminho de `src/`. Todo código que não aparece nos slides vem marcado com **(ignore)**: no título da célula, numa primeira linha `# (ignore)` ou no título da seção.

| Seção | Conteúdo |
|---|---|
| Setup (ignore) | Os módulos de `src/` que não aparecem nos slides, pasta por pasta, cada um numa célula `%%writefile`; uma célula recolhida que grava os módulos dos slides (eles são mostrados de novo nas seções); funções de apresentação e estilo dos gráficos. |
| Uma por algoritmo | Na ordem dos slides: o problema (P1), a ideia, o laço e as listas, as regras, a estratégia de controle, as duas estratégias na mesma raiz, sem poda (crescimento por nível, árvore e ABERTOS/FECHADOS iteração a iteração, crescente e decrescente), com poda (idem), pseudocódigo com o código do algoritmo, caminho solução, comparativos (caminhos, crescente contra decrescente, contra os outros algoritmos, quem explorou menos nós) e complexidade. Fecha com a conclusão e os extras (ignore): fluxograma, trace bruto e comparações no placar e nos 36 objetivos. |
| Gráficos e análise (ignore) | Matriz completa em P1 e nos 36 objetivos, gráficos de desfecho, qualidade e esforço, e a análise. |
| Integrantes | O grupo. |

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
│   └── analysis.py    gráficos e análise
└── notebooks/         saída gerada (não editar à mão)
```
