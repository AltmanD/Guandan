"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

import numpy as np
from comps import CardDeck, Context, Player, Table
from utils import ctx2info


def init(ctx: Context):
    ctx.table = Table()
    ctx.card_decks = CardDeck()
    for i in range(4):
        ctx.players[i] = Player(i)
        ctx.players_id_list.append(i)
    battle_init(ctx)


def battle_init(ctx: Context):
    ctx.table.join(ctx.players_id_list)
    ctx.card_decks.update_deck(2)
    deal_card_lists = ctx.card_decks.deal(len(ctx.players_id_list))
    for i in range(4):
        ctx.players[i].update_cards(deal_card_lists[i])
    if ctx.win_order_last_round is None:
        ctx.player_waiting = np.random.randint(0, 4)


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
    input()
    info = ctx2info(ctx)
    while not info['done']:
        step(ctx, None)
        info = ctx2info(ctx)
    reset(ctx)
