# Notebooks da apresentação

Gera os notebooks que vão para o Google Colab a partir do código de `src/`. Cada notebook é uma página e roda sozinho: o código do projeto vai dentro dele.

| Página | Arquivo | Conteúdo |
|---|---|---|
| Projeto | `00_projeto.ipynb` | `src/` pasta por pasta, na ordem do repositório; cada módulo numa célula `%%writefile` no mesmo caminho. Termina com uma demonstração e a linha de comando. |
| Busca irrevogável | `01_busca_irrevogavel.ipynb` | Fluxograma, código, execução em P1 com as três estratégias, passo a passo, árvores de busca e caminho solução. |
| Backtracking | `02_backtracking.ipynb` | Idem. |
| Busca em largura | `03_busca_em_largura.ipynb` | Idem. |
| Busca ordenada | `04_busca_ordenada.ipynb` | Idem. |
| Gráficos e análise | `05_analise.ipynb` | Matriz completa em P1 e nos 36 objetivos, gráficos de desfecho, qualidade e esforço, e a análise. |

Nas páginas de algoritmo e de análise, a primeira célula de código (recolhida no Colab) grava o restante de `src/`. Nas páginas de algoritmo, o módulo do próprio algoritmo aparece por inteiro numa célula visível.

## Gerar

```bash
make notebooks                                 # ou: python apps/notebook/build.py
python apps/notebook/build.py --check          # falha se algum notebook estiver atrasado em relação a src/
```

O gerador usa só a biblioteca padrão. Mudou algo em `src/`? Gere de novo e versione os notebooks junto.

## Subir para o Colab

Depois do push para `main`, o selo "Abrir no Colab" no topo de cada página abre o notebook direto do GitHub, e os links entre as páginas também levam ao Colab. Sem push, use **Arquivo → Fazer upload de notebook** no Colab com os arquivos de `notebooks/`.

Rode **Ambiente de execução → Executar tudo**. As páginas usam pandas, matplotlib e o Graphviz (`dot`), que o Colab já traz. Sem o `dot`, as árvores aparecem em texto.

## Estrutura

```
apps/notebook/
├── build.py           entrada: gera os notebooks ou verifica se estão em dia
├── cells.py           células e notebook no formato .ipynb
├── source.py          lê src/ na ordem das pastas e monta as células de código
├── pages/
│   ├── common.py      navegação, preparação e funções de apresentação
│   ├── project.py     página do projeto
│   ├── algorithm.py   uma página por algoritmo
│   └── analysis.py    gráficos e análise
└── notebooks/         saída gerada (não editar à mão)
```
