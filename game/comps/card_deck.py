from comps import comp
class card_deck(comp):
    def __init__(self, number_of_decks) -> None:
        self.total_card_num = 54 * number_of_decks

    def deal4player(self, number_of_players):
        return [[]]
