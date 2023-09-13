"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

from game import Context, entity_add, entity_get_all, entity_remove, entity_get_with_name, entity_add_comp
from comps import card_deck
import numpy as np

def init(ctx: Context):
    init_table(ctx)
    init_card(ctx)


def init_table(ctx: Context):
    entity_add(ctx, 'card_history')
    for i in range(4):
        entity_add(ctx, 'palyer{}'.format(i+1))
    

def init_card(ctx):
    seed = np.random.seed()
    card_decks = card_deck(2)
    cards = card_decks.deal4player(4)
    for i, card in enumerate(cards):
        entity_add_comp(ctx, 'player{}'.format(i+1), card)
    

def step(action):
    return 0

def reset():
    return 0

def close(ctx):    
    for eid in list(entity_get_all(ctx)):
        entity_remove(ctx, eid)
    return 0