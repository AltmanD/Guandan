from typing import Union

from utils import *


class Player:
    
    def __init__(self, id) -> None:
        self.id = id
        self.numb_of_cards_in_hand = 0
        self.cards_in_hand_dict = {}
        self.cards_in_hand_list = []
        self.cards_in_hand_str = ''

    def __repr__(self) -> str:
        return 'Player(id={}, numb_of_cards_in_hand={}, cards_in_hand_dict={})' \
            .format(self.id, self.numb_of_cards_in_hand, self.cards_in_hand_dict)
    
    def update_cards(self, cards: Union[dict, list, str]):
        if isinstance(cards, dict):
            self.cards_in_hand_dict = cards
            self.cards_in_hand_list = card_dict2list(cards)
            self.cards_in_hand_str = card_dict2str(cards)
        elif isinstance(cards, list):
            self.cards_in_hand_list = cards
            self.cards_in_hand_dict = card_list2dict(cards)
            self.cards_in_hand_str = card_list2str(cards)
        elif isinstance(cards, str):
            self.cards_in_hand_str = cards
            self.cards_in_hand_list = card_str2list(cards)
            self.cards_in_hand_dict = card_str2dict(cards)
    
    def play(self, action):
        pass

    def show(self):
        pass