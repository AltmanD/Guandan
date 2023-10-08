"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

import numpy as np
from comps import Table, Player, Context
from utils import ctx2info


def init(ctx: Context):
    ctx.table = Table()
    for i in range(4):
        ctx.players[i] = Player(i)
    deal(ctx)


def deal(ctx: Context):
    pass


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
