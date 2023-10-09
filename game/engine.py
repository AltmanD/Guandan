"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

import numpy as np
from comps import Table, Player, Context, CardDeck
from utils import ctx2info


def init(ctx: Context):
    ctx.table = Table()
    ctx.card_decks = CardDeck(2)
    for i in range(4):
        ctx.players[i] = Player(i)
        ctx.players_id_list.append(i)
    battle_init(ctx)


def battle_init(ctx: Context):
    ctx.table.join(ctx.players_id_list)
    card_lists = ctx.card_decks.deal(4)
    for i in range(4):
        ctx.players[i].update_cards(card_lists[i])


def step(ctx: Context, action: int):
    if action is None:
        # default random action
        action = 0
    update(ctx)
    return 0


def update(ctx: Context):
    pass


def reset(ctx):
    return 0


def close(ctx):
    del ctx


if __name__ == '__main__':
    ctx = Context()
    print(ctx)
    init(ctx)
    info = ctx2info(ctx)
    while not info['done']:
        step(ctx, None)
        info = ctx2info(ctx)
    reset(ctx)
