"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

from game import Context, entity_add, entity_get_all, entity_remove, entity_get_with_name
import numpy as np

def init(ctx: Context):
    init_world(ctx)
    init_card(ctx)

def init_world(ctx: Context):
    entity_add(ctx, 'world')
    entity_add(ctx, 'deck')
    entity_add(ctx, 'history')
    for i in range(4):
        entity_add(ctx, 'client{}'.format(i+1))
    
    return 0

def init_card(ctx):
    seed = np.random.seed()
    for i in range(4):
        eid = entity_get_with_name(ctx, 'client{}'.format(i+1))
    

def step(action):
    return 0

def reset():
    return 0

def close(ctx):    
    for eid in list(entity_get_all(ctx)):
        entity_remove(ctx, eid)
    return 0