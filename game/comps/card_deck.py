from utils import *
color = ['S', 'H', 'C', 'D'] # 黑桃 ♠ spade, 红心 ♥ heart, 方片 ♦ dianmond, 梅花 ♣ club

class CardDeck:

    def __init__(self, number_of_decks) -> None:
        self.total_card_num = 54 * number_of_decks
        self.cards_in_dict = {}
        for c in range(len(color)):
            for index in range(13):
                if index < 9:
                    self.cards_in_dict.update({'{}{}'.format(c, index+1): number_of_decks})
                elif index == 10:
                    self.cards_in_dict.update({'{}X'.format(c): number_of_decks})
                elif index == 11:
                    self.cards_in_dict.update({'{}J'.format(c): number_of_decks})
                elif index == 12:
                    self.cards_in_dict.update({'{}Q'.format(c): number_of_decks})
                elif index == 13:
                    self.cards_in_dict.update({'{}K'.format(c): number_of_decks})
        self.cards_in_dict.update({'BJ': number_of_decks})
        self.cards_in_dict.update({'RJ': number_of_decks})
        self.cards_in_list = card_dict2list(self.cards_in_dict)
        self.cards_in_str = card_dict2str(self.cards_in_dict)

    def __repr__(self) -> str:
        return 'CardDeck(total_card_num={}, cards_in_dict={})' \
            .format(self.total_card_num, self.cards_in_dict)
        
    def deal(self, number_of_players: int):
        return [[]]
