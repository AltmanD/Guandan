"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

import numpy as np
from comps import CardDeck, Context, Player, Table
from utils import ctx2info, legalaction


def init(ctx: Context):
    ctx.table = Table()
    ctx.card_decks = CardDeck()
    ctx.players = {}
    ctx.players_id_list = []
    for i in range(4):
        ctx.players[i] = Player(i)
        ctx.players_id_list.append(i)
    battle_init(ctx)


def battle_init(ctx: Context):
    ctx.cur_rank = '2'
    ctx.table.join(ctx.players_id_list)
    ctx.card_decks.update_deck(2)
    deal_card_lists = ctx.card_decks.deal(len(ctx.players_id_list))
    for i in range(4):
        ctx.players[i].update_cards(deal_card_lists[i])
        ctx.players[i].update_rank(ctx.cur_rank, ctx.cur_rank)
    if ctx.win_order_last_round is None:
        ctx.player_waiting = np.random.randint(0, 4)
    ctx.action_history_by_player_id = {
            0: {},
            1: {},
            2: {},
            3: {},
        }
    ctx.steps = 0


def step(ctx: Context, action: int):
    legalactions = legalaction(ctx)
    if action is None:
        # default random action
        action = np.random.randint(0, len(legalactions))
    update(ctx, legalactions[action])
    return 0


def update(ctx: Context, action: str):
    ctx.last_action = action
    ctx.action_history_by_player_id[ctx.player_waiting][ctx.steps] = action
    ctx.players[ctx.player_waiting].play(action)
    ctx.player_waiting = (ctx.player_waiting + 1) % 4


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
