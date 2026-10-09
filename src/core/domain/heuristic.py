"""Heurística de discos mal posicionados.

Um disco está BEM POSICIONADO quando está na haste e na altura do objetivo e
todos os discos abaixo dele também estão. Cada disco contribui com o mínimo de
movimentos que ainda precisa fazer:

    0   bem posicionado: não precisa sair dali
    1   em outra haste: pode chegar ao destino com um movimento
    2   na haste certa, mas mal posicionado: precisa sair e voltar

    h(estado) = soma das contribuições dos três discos

Estar na haste certa fora do lugar é pior que estar na haste errada: o disco
está na altura errada ou apoiado num disco errado, e esse disco de baixo só sai
depois que ele sair.

Exemplo, objetivo ([], [R, V], [A]):
    ([V, R], [A], [])   V e R em H1 (haste errada): 1 + 1; A em H2: 1   h = 3
    ([V], [R], [A])     V: 1; R e A bem posicionados: 0 + 0              h = 1
    ([], [V, R], [A])   V e R em H2, trocados: 2 + 2; A: 0              h = 4

Admissível: cada movimento leva um disco só, e cada contribuição é um mínimo
real de movimentos daquele disco. Então h nunca passa do número de movimentos
que falta.
"""

from __future__ import annotations

from core.domain.state import Disk, Peg, Stack, State


def misplacement(state: State, goal: State) -> int:
    return sum(contributions(state, goal).values())


def contributions(state: State, goal: State) -> dict[Disk, int]:
    """O que cada disco soma em h: 0, 1 ou 2, como na tabela acima."""
    result: dict[Disk, int] = {}
    for peg in Peg:
        stack, target = state[peg], goal[peg]
        placed = _common_base(stack, target)
        for height, disk in enumerate(stack):
            if height < placed:
                result[disk] = 0
            else:
                result[disk] = 2 if disk in target else 1
    return result


def _common_base(stack: Stack, target: Stack) -> int:
    """Quantos discos, de baixo para cima, já coincidem com o objetivo."""
    count = 0
    for disk, wanted in zip(stack, target, strict=False):
        if disk != wanted:
            break
        count += 1
    return count
