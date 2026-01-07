from typing import Union

from game.utils import *


class Player:
    
    def __init__(self, id) -> None:
        self.id = id
        self.cur_rank = None
        self.my_rank = 1
        self.playing_myself = True
        self.numb_of_cards_in_hand = 0
        self.numb_of_rank_cards = 0
        self.handcards_in_dict = {}
        self.handcards_in_list = []
        self.handcards_in_str = ''
        self.have_cards = True
        self.last_play_cards = None
        self.last_play_flag = 0

    def __repr__(self) -> str:
        return 'Player(id={}, numb_of_cards_in_hand={}, cards_in_hand_dict={})' \
            .format(self.id, self.numb_of_cards_in_hand, self.handcards_in_dict)
    
    def update_cards(self, cards: Union[dict, list, str]):
        if isinstance(cards, dict):
            self.handcards_in_dict = cards
            self.handcards_in_list = card_dict2list(cards)
            self.handcards_in_str = card_list2str(self.handcards_in_list)
        elif isinstance(cards, list):
            self.handcards_in_list = cards
            self.handcards_in_dict = card_list2dict(cards)
            self.handcards_in_str = card_list2str(cards)
        elif isinstance(cards, str):
            self.handcards_in_str = cards
            self.handcards_in_list = card_str2list(cards)
            self.handcards_in_dict = card_str2dict(cards)
    
    def update_rank(self, cur_rank):
        self.cur_rank = cur_rank

    def get_cards_vector(self):
        return card_list2vector(self.handcards_in_list)
    
    def get_rank_card_num(self):
        rank_card = 'H' + self.cur_rank
        if rank_card in self.handcards_in_dict:
            return self.handcards_in_dict['H' + self.cur_rank]
        else:
            return 0

    def play(self, action):
        if len(action) == 0:   # 如果是pass，就是空列表
            pass
        else:
            before_cards = self.get_cards_vector()
            true_action = action[:54]
            current_cards = before_cards - true_action
            assert np.min(current_cards) >= 0, print(current_cards, action, vector2card(action[:54]), 'play illegal action')
            if np.max(current_cards) == 0:
                self.have_cards = False
                self.update_cards([])
            else:
                card_list = []
                for i in range(len(current_cards)):
                    if current_cards[i] == 1:
                        card_list.append(i)
                    elif current_cards[i] == 2:
                        card_list.append(i)
                        card_list.append(i)
                self.update_cards(card_list)

    def show(self):
        pass
