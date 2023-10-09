from typing import Union

class Player:
    
    def __init__(self, id) -> None:
        self.id = id
        self.numb_of_cards_in_hand = 0
        self.cards_in_hand_dict = {}
        self.cards_in_hand_list = []
        self.cards_in_hand_str = ''

    def update_cards(cards: Union[dict, list, str]):
        pass