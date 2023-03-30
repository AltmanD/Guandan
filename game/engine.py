__author__ = 'Lu Yudong'

from game import Context

def init(ctx: Context):
    init_world(ctx)


def init_world(ctx):
    ctx.entity_types['world'] = 0
    for i in range(4):
        ctx.entity_types['Client{}'.format(i+1)] = 0
    return 0

def step():
    return 0

def close():
    return 0