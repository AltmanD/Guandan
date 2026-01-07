"""
Content: Engine for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

import numpy as np
import time
from copy import deepcopy
from game.comps import CardDeck, Context, Player, Table
from game.utils import legalaction, vector2card, RANK2, tribute_legal, anti_tribute, back_legal, CardToNum, give_type


class GameEnv(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.ctx.table = Table()
        self.ctx.card_decks = CardDeck()
        self.ctx.players = {}
        self.ctx.players_id_list = []
        for i in range(4):
            self.ctx.players[i] = Player(i)
            self.ctx.players_id_list.append(i)
        self.ctx.wind = False   # 接风判断
        self.ctx.win_order = []
        self.wind_num = 0
        self.round_end = False
        self.episode_end = False
        self.tribute_res = []
        self.back_res = []
        self.anti_tri = False

    def deal_cards(self):
        self.ctx.table.join(deepcopy(self.ctx.players_id_list))
        self.ctx.card_decks.init_deck(2)  # 2副牌
        deal_card_lists = self.ctx.card_decks.deal(len(self.ctx.players_id_list))
        for i in range(4):
            self.ctx.players[i].update_cards(deal_card_lists[i])
            self.ctx.players[i].update_rank(self.ctx.cur_rank)  # my_rank用数字，cur_rank用字符
            self.ctx.players[i].have_cards = True
            self.ctx.players[i].last_play_cards = None

    def battle_init(self):
        # self.deal_cards()
        if len(self.ctx.win_order) == 0:
            # self.ctx.player_waiting = np.random.randint(0, 4)
            self.ctx.player_waiting = 0
        else:
            self.tribute_phase()
        print('round end, win order', self.ctx.win_order, self.ctx.cur_rank, self.ctx.players[0].my_rank, self.ctx.players[1].my_rank)
        time.sleep(0.5)
        self.ctx.steps = 0
        self.ctx.wind = False
        self.wind_num = 0
        self.round_end = False
        self.ctx.win_order = []
        self.ctx.trick_pass = 0
        self.ctx.recv_wind = False
        self.tribute_res = []
        self.back_res = []
        self.ctx.last_action = None
        self.ctx.last_max_action = None
        self.ctx.last_max_playid = None
        self.ctx.last_playid = None
        self.anti_tri = False

    def step(self, action=None):
        print('waiting player', self.ctx.player_waiting)
        last_type, last_value = give_type(self.ctx)
        legalactions = legalaction(self.ctx, last_type=last_type, last_value=last_value)
        # legalactions = legalaction(self.ctx)
        if action is None:
            # default random action
            action = np.random.randint(0, len(legalactions))
        self.update(legalactions[action])

        print('played', vector2card(legalactions[action][:54]), legalactions[action])
        return 0

    def update(self, action): # action最后一项是last_type
        self.ctx.last_action = action
        self.ctx.players[self.ctx.player_waiting].last_play_cards = action
        self.ctx.last_playid = self.ctx.player_waiting
        self.ctx.recv_wind = False
        if len(action) == 0:
            self.ctx.trick_pass += 1
        else:
            self.ctx.trick_pass = 0
            self.ctx.last_max_action = self.ctx.last_action   # 只要不是新一轮，没人过，上一个动作就是当前轮的最大动作
            self.ctx.last_max_playid = self.ctx.player_waiting
        if self.ctx.wind:   # 如果当前是一个人出完牌的接风轮。有人出了牌，则接风失效
            if len(action) > 0:
                self.ctx.wind = False
                self.wind_num = 0
        self.ctx.players[self.ctx.player_waiting].play(action)
        # print(self.ctx.card_decks.sortcards(self.ctx.players[self.ctx.player_waiting].handcards_in_str))
        if not self.ctx.players[self.ctx.player_waiting].have_cards:   # 牌出完了，就把这个人移走
            self.ctx.table.detach(self.ctx.player_waiting)
            self.ctx.win_order.append(self.ctx.player_waiting)
            self.ctx.wind = True     # 有人出完牌，进入接风轮
            self.wind_num = self.ctx.table.players_on_table_numb
            self.whether_end()   # 判断游戏是否结束
        if not self.round_end:
            if self.ctx.wind:
                # 如果更新完动作后还是接风轮
                if self.wind_num == 0:  # 表示接风轮的最后一个人都做完动作了（因为进到这里wind是true，说明最后一个人也是过，然后就到对家接风）
                    self.ctx.wind = False
                    self.ctx.player_waiting = (self.ctx.table.players_last_end[-1] + 2) % 4
                    self.ctx.recv_wind = True
                else:
                    while (self.ctx.player_waiting + 1) % 4 not in self.ctx.table.players_on_table_id:  # 如果下家已经出完牌了，则递补继续向下
                        self.ctx.player_waiting = (self.ctx.player_waiting + 1) % 4
                    self.ctx.player_waiting = (self.ctx.player_waiting + 1) % 4
                    self.wind_num -= 1
            else:
                while (self.ctx.player_waiting + 1) % 4 not in self.ctx.table.players_on_table_id:  # 如果下家已经出完牌了，则递补继续向下
                    self.ctx.player_waiting = (self.ctx.player_waiting + 1) % 4
                self.ctx.player_waiting = (self.ctx.player_waiting + 1) % 4

    def whether_end(self):
        condition1 = len(self.ctx.table.players_on_table_id) == 1      # 3个人都出完了或者剩的俩是对家
        condition2 = len(self.ctx.table.players_on_table_id) == 2 and \
                     abs(self.ctx.table.players_on_table_id[0] - self.ctx.table.players_on_table_id[1]) == 2
        if condition1 or condition2:
            self.round_end = True
            for i in self.ctx.table.players_on_table_id:
                self.ctx.win_order.append(i)
            self.upgrade()

    def upgrade(self):
        first = self.ctx.win_order[0]
        second = self.ctx.win_order[1]
        third = self.ctx.win_order[2]
        if abs(first - second) == 2:
            uprank = 3
        elif abs(first - third) == 2:
            uprank = 2
        else:
            uprank = 1
        if self.ctx.cur_rank == 'A' and self.ctx.players[first].playing_self and uprank >= 2:
            self.episode_end = True
        if not self.episode_end:     # 这局没有完的时候更新相应的等级
            self.ctx.players[first].playing_self = True     # 下回合是打谁的level
            self.ctx.players[(first + 2) % 4].playing_self = True
            self.ctx.players[(first + 1) % 4].playing_self = False
            self.ctx.players[(first + 3) % 4].playing_self = False
            level = min(13, self.ctx.players[first].my_rank + uprank)
            self.ctx.cur_rank = RANK2[level]
            for i in range(4):
                if i == first or i == (first + 2) % 4:
                    self.ctx.players[i].my_rank = level
                self.ctx.players[i].cur_rank = RANK2[level]

    def one_episode(self):
        self.ctx.cur_rank = '2'
        while not self.episode_end:
            self.deal_cards()
            self.battle_init()
            while not self.round_end:
                self.step()

    def tribute_step(self, card_list, id, action=None, flag=0):     # flag=0表示进贡，flag=1表示还贡
        if not flag:
            legalactions = tribute_legal(card_list, self.ctx)
        else:
            legalactions = back_legal(card_list, self.ctx)
        if action is None:
            # default random action
            action = np.random.randint(0, len(legalactions))
        card = legalactions[action]

        return card

    def compare(self, card1, card2):     # 比较card1和card2哪个更大
        if card1 >= 52 and card2 >= 52:
            if card1 > card2:
                return 1
            elif card1 == card2:
                return 0
            else:
                return -1
        elif card1 >= 52 and card2 < 52:
            return 1
        elif card1 < 52 and card2 >= 52:
            return -1
        else:        # 都不是王的情况，如果是级牌则是最大的，不然按数字来
            card1 = 50 if card1 % 13 == CardToNum['H' + self.ctx.cur_rank] else card1 % 13
            card2 = 50 if card2 % 13 == CardToNum['H' + self.ctx.cur_rank] else card2 % 13
            if card1 > card2:
                return 1
            elif card1 == card2:
                return 0
            else:
                return -1

    def tribute_act(self, out, recv, card):   # out拿出card给recv，表示进贡和还贡的单向动作
        card_out = deepcopy(self.ctx.players[out].handcards_in_list)
        card_recv = deepcopy(self.ctx.players[recv].handcards_in_list)
        card_out.remove(card)
        card_recv.append(card)
        self.ctx.players[out].update_cards(card_out)
        self.ctx.players[recv].update_cards(card_recv)

    def broadcast_tribute(self):
        pass

    def broadcast_back(self):
        pass

    def broadcast_anti(self):
        pass

    def tribute_phase(self):  # 队友是下游，也要给另一个进贡
        if len(self.ctx.win_order) == 0:
            return
        else:
            card_last = deepcopy(self.ctx.players[self.ctx.win_order[-1]].handcards_in_list)
            card_first = deepcopy(self.ctx.players[self.ctx.win_order[0]].handcards_in_list)
            if abs(self.ctx.win_order[-2] - self.ctx.win_order[-1]) == 2:   # 双下游
                self.anti_tri = anti_tribute(self.ctx, flag=1)
                if self.anti_tri:
                    print('anti tribute')
                    self.broadcast_anti()
                    return
                else:
                    tribute_last = self.tribute_step(card_last, id=self.ctx.win_order[-1])
                    card_third = deepcopy(self.ctx.players[self.ctx.win_order[-2]].handcards_in_list)
                    tribute_third = self.tribute_step(card_third, id=self.ctx.win_order[-2])
                    card_second = deepcopy(self.ctx.players[self.ctx.win_order[1]].handcards_in_list)
                    if self.compare(tribute_last, tribute_third) > 0:  # 下游进贡的更大
                        self.tribute_act(self.ctx.win_order[-1], self.ctx.win_order[0], tribute_last)
                        self.tribute_act(self.ctx.win_order[-2], self.ctx.win_order[1], tribute_third)
                        self.tribute_res.append([self.ctx.win_order[-1], self.ctx.win_order[0], tribute_last])
                        self.tribute_res.append([self.ctx.win_order[-2], self.ctx.win_order[1], tribute_third])
                        self.broadcast_tribute()

                        back_first = self.tribute_step(card_first, id=self.ctx.win_order[0], flag=1)
                        back_second = self.tribute_step(card_second, id=self.ctx.win_order[1], flag=1)
                        self.tribute_act(self.ctx.win_order[0], self.ctx.win_order[-1], back_first)
                        self.tribute_act(self.ctx.win_order[1], self.ctx.win_order[-2], back_second)
                        self.back_res.append([self.ctx.win_order[0], self.ctx.win_order[-1], back_first])
                        self.back_res.append([self.ctx.win_order[1], self.ctx.win_order[-2], back_second])
                        self.broadcast_back()
                        self.ctx.player_waiting = self.ctx.win_order[-1]

                    elif self.compare(tribute_last, tribute_third) < 0:   # 三游进贡的更大
                        self.tribute_act(self.ctx.win_order[-2], self.ctx.win_order[0], tribute_third)
                        self.tribute_act(self.ctx.win_order[-1], self.ctx.win_order[1], tribute_last)
                        self.tribute_res.append([self.ctx.win_order[-2], self.ctx.win_order[0], tribute_third])
                        self.tribute_res.append([self.ctx.win_order[-1], self.ctx.win_order[1], tribute_last])
                        self.broadcast_tribute()

                        back_first = self.tribute_step(card_first, id=self.ctx.win_order[0], flag=1)
                        back_second = self.tribute_step(card_second, id=self.ctx.win_order[1], flag=1)
                        self.tribute_act(self.ctx.win_order[0], self.ctx.win_order[-1], back_first)
                        self.tribute_act(self.ctx.win_order[1], self.ctx.win_order[-2], back_second)
                        self.back_res.append([self.ctx.win_order[0], self.ctx.win_order[-2], back_first])
                        self.back_res.append([self.ctx.win_order[1], self.ctx.win_order[-1], back_second])
                        self.broadcast_back()
                        self.ctx.player_waiting = self.ctx.win_order[-2]

                    else:           # 进贡的大小一样大，按顺时针进贡（给上家进贡），逆时针还贡（给下家还贡）
                        if self.ctx.win_order[-1] == (self.ctx.win_order[0] + 1) % 4:     # 下游是上游的下家
                            self.tribute_act(self.ctx.win_order[-1], self.ctx.win_order[0], tribute_last)
                            self.tribute_act(self.ctx.win_order[-2], self.ctx.win_order[1], tribute_third)
                            self.tribute_res.append([self.ctx.win_order[-1], self.ctx.win_order[0], tribute_last])
                            self.tribute_res.append([self.ctx.win_order[-2], self.ctx.win_order[1], tribute_third])
                            self.broadcast_tribute()

                            back_first = self.tribute_step(card_first, id=self.ctx.win_order[0], flag=1)
                            back_second = self.tribute_step(card_second, id=self.ctx.win_order[1], flag=1)
                            self.tribute_act(self.ctx.win_order[0], self.ctx.win_order[-1], back_first)
                            self.tribute_act(self.ctx.win_order[1], self.ctx.win_order[-2], back_second)
                            self.back_res.append([self.ctx.win_order[0], self.ctx.win_order[-1], back_first])
                            self.back_res.append([self.ctx.win_order[1], self.ctx.win_order[-2], back_second])
                            self.broadcast_back()
                        else:
                            self.tribute_act(self.ctx.win_order[-2], self.ctx.win_order[0], tribute_third)
                            self.tribute_act(self.ctx.win_order[-1], self.ctx.win_order[1], tribute_last)
                            self.tribute_res.append([self.ctx.win_order[-2], self.ctx.win_order[0], tribute_third])
                            self.tribute_res.append([self.ctx.win_order[-1], self.ctx.win_order[1], tribute_last])
                            self.broadcast_tribute()

                            back_first = self.tribute_step(card_first, id=self.ctx.win_order[0], flag=1)
                            back_second = self.tribute_step(card_second, id=self.ctx.win_order[1], flag=1)
                            self.tribute_act(self.ctx.win_order[0], self.ctx.win_order[-1], back_first)
                            self.tribute_act(self.ctx.win_order[1], self.ctx.win_order[-2], back_second)
                            self.back_res.append([self.ctx.win_order[0], self.ctx.win_order[-2], back_first])
                            self.back_res.append([self.ctx.win_order[1], self.ctx.win_order[-1], back_second])
                            self.broadcast_back()
                        self.ctx.player_waiting = (self.ctx.win_order[0] + 1) % 4
                    # print('double tribute', self.tribute_res, self.back_res)
                    # cards_after_tribute = [card_first, card_second, card_third, card_last]
                    # for (index, ele) in enumerate(self.ctx.win_order):
                    #     self.ctx.players[ele].update_cards(cards_after_tribute[index])
                    # for i in range(4):
                    #     print(self.ctx.players[i].handcards_in_dict)
                    #     print(self.ctx.players[i].handcards_in_list)
            else:   # 只有一个下游要进贡
                self.anti_tri = anti_tribute(self.ctx, flag=0)
                if self.anti_tri:
                    print('anti tribute')
                    self.broadcast_anti()
                    return
                else:
                    tribute_last = self.tribute_step(card_last, id=self.ctx.win_order[-1])
                    self.tribute_act(self.ctx.win_order[-1], self.ctx.win_order[0], tribute_last)
                    self.tribute_res.append([self.ctx.win_order[-1], self.ctx.win_order[0], tribute_last])
                    self.broadcast_tribute()

                    back_first = self.tribute_step(card_first, id=self.ctx.win_order[0], flag=1)
                    self.tribute_act(self.ctx.win_order[0], self.ctx.win_order[-1], back_first)
                    self.back_res.append([self.ctx.win_order[0], self.ctx.win_order[-1], back_first])
                    self.broadcast_back()
                    self.ctx.player_waiting = self.ctx.win_order[-1]
                # print('single tribute', self.tribute_res, self.back_res)
                # for i in range(4):
                #     print(self.ctx.players[i].handcards_in_dict)
                #     print(self.ctx.players[i].handcards_in_list)


if __name__ == '__main__':
    ctx = Context()
    game = GameEnv(ctx)
    # game.ctx.cur_rank = '7'
    # game.battle_init()
    # game.tribute_phase()
    # for i in range(4):
    #     print(game.ctx.players[i].handcards_in_dict)
    #     print(game.ctx.players[i].handcards_in_list)
    # print(game.ctx.player_waiting)
    # game.ctx.players[game.ctx.player_waiting].update_cards('H2 H2 S2 C2 C3 D3 H4 S4 S5 C5 H6 H7 S7 H8 H9 H9 C9 D9 HT ST CT HK SK CK CA HA SA')
    # game.step()
    game.one_episode()

