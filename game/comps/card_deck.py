import random

from game.utils import *

color = ['H', 'S', 'C', 'D']  # 黑桃 ♠ Spade, 红心 ♥ Heart, 方片 ♦ Diamond, 梅花 ♣ Club
points = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']


class CardDeck:

    def __init__(self) -> None:
        self.total_card_num = None
        self.cards_in_dict = {}
        self.cards_in_list = []
        self.cards_in_str = ''
        self.sort_value1 = {}
        for c in color:
            for p in points:
                card = c + p
                self.sort_value1[card] = 10 * points.index(p) + color.index(c)
        self.sort_value1['HR'] = 10000
        self.sort_value1['SB'] = 5000
        self.sort_value2 = dict(zip(self.sort_value1.values(), self.sort_value1.keys()))

    def __repr__(self) -> str:
        return 'CardDeck(total_card_num={}, cards_in_dict={})' \
            .format(self.total_card_num, self.cards_in_dict)

    def init_deck(self, number_of_decks):
        for c in color:
            for index in range(13):
                if index < 9:
                    if index == 0:
                        self.cards_in_dict.update({'{}A'.format(c): number_of_decks})
                    else:
                        self.cards_in_dict.update({'{}{}'.format(c, index+1): number_of_decks})
                elif index == 9:
                    self.cards_in_dict.update({'{}T'.format(c): number_of_decks})
                elif index == 10:
                    self.cards_in_dict.update({'{}J'.format(c): number_of_decks})
                elif index == 11:
                    self.cards_in_dict.update({'{}Q'.format(c): number_of_decks})
                elif index == 12:
                    self.cards_in_dict.update({'{}K'.format(c): number_of_decks})
        self.cards_in_dict.update({'SB': number_of_decks})
        self.cards_in_dict.update({'HR': number_of_decks})
        self.cards_in_list = card_dict2list(self.cards_in_dict)
        self.cards_in_str = card_list2str(self.cards_in_list)
        self.total_card_num = number_of_decks * 54

    def deal(self, number_of_players: int):
        cards_per_player = self.total_card_num // number_of_players
        rand_card_list = sorted(self.cards_in_list, key=lambda x: random.random())
        start_index = 0
        end_index = cards_per_player
        res = []
        for _ in range(number_of_players):
            res.append(rand_card_list[start_index:end_index])
            start_index = end_index
            end_index += cards_per_player
        return res

    def sortcards(self, card_str):
        cardlist = card_str.split(' ')
        cardvalue = []
        for ele in cardlist:
            if ele in self.sort_value1:
                cardvalue.append(self.sort_value1[ele])

        cardvalue.sort()
        res = []
        for ele in cardvalue:
            res.append(self.sort_value2[ele])
            # res += self.sort_value2[ele] + ' '
        return res






