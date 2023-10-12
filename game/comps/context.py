class Context:
    def __init__(self) -> None:
        self.table = None
        self.card_decks = None
        self.players = None
        self.players_id_list = None
        self.action_history_by_player_id = None
        self.steps = None
        self.player_waiting = None
        self.last_action = None
        self.rank = None
        self.win_order_last_round = None

    def __repr__(self) -> str:
        return 'Context(table={}, players={}, steps={}, player_waiting={}, last_action={})' \
            .format(self.table, self.players, self.steps, self.player_waiting, self.last_action)
