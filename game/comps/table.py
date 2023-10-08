from card_deck import card_deck

class Table:
    
    def __init__(self) -> None:
        self.players_on_table_numb = 0
        self.players_on_table_id = {}
        self.card_decks = card_deck(2)
        self.card_history_by_id = {}