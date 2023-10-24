from typing import Union

from utils import *


class Player:
    
    def __init__(self, id) -> None:
        self.id = id
        self.cur_rank = None
        self.my_rank = None
        self.numb_of_cards_in_hand = 0
        self.numb_of_rank_cards = 0
        self.handcards_in_dict = {}
        self.handcards_in_list = []
        self.handcards_in_str = ''
        self.handcards_in_vector = []

    def __repr__(self) -> str:
        return 'Player(id={}, numb_of_cards_in_hand={}, cards_in_hand_dict={})' \
            .format(self.id, self.numb_of_cards_in_hand, self.handcards_in_dict)
    
    def update_cards(self, cards: Union[dict, list, str]):
        if isinstance(cards, dict):
            self.handcards_in_dict = cards
            self.handcards_in_list = card_dict2list(cards)
            self.handcards_in_str = card_dict2str(cards)
        elif isinstance(cards, list):
            self.handcards_in_list = cards
            self.handcards_in_dict = card_list2dict(cards)
            self.handcards_in_str = card_list2str(cards)
        elif isinstance(cards, str):
            self.handcards_in_str = cards
            self.handcards_in_list = card_str2list(cards)
            self.handcards_in_dict = card_str2dict(cards)
    
    def update_rank(self, cur_rank, my_rank):
        self.cur_rank = cur_rank
        self.my_rank = my_rank
    
    def get_cards_vector(self):
        return card_list2vector(self.handcards_in_vector)
    
    def get_rank_card_num(self):
        return self.handcards_in_dict['H' + self.cur_rank]

    def play(self, action):
        pass

    def show(self):
        pass
