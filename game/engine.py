__author__ = 'Lu Yudong'

from game import Context, entity_add

def init(ctx: Context):
    init_world(ctx)

def init_world(ctx: Context):
    entity_add(ctx, 'world')
    entity_add(ctx, 'deck')
    entity_add(ctx, 'history')
    for i in range(4):
        entity_add(ctx, 'Client{}'.format(i+1))
    return 0

def step(action):
    return 0

def reset():
    return 0

def close():    
    for eid in list(entity_get_all(ctx)):
        entity_remove(ctx, eid)
    return 0