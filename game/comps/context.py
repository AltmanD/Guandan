class Context:
    def __init__(self) -> None:
        self.table = None
        self.players = {}
        self.steps = 0
        self.player_waiting = None
        self.last_action = None

    def __repr__(self) -> str:
        return 'Context(table={}, players={}, steps={}, player_waiting={}, last_action={})' \
            .format(self.table, self.players, self.steps, self.player_waiting, self.last_action)
