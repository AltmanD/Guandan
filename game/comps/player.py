class Player:
    
    def __init__(self, id) -> None:
        self.id = id
        self.numb_of_cards_in_hand = 0
        self.cards_in_hand = {}