from game import Context


def ctx2info(ctx: Context):
    info = {
        'obs': None,
        'action': None,
        'reward': None,
        'done': None
    }
    return info