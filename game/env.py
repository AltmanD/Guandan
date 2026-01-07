from collections import Counter
import sys
sys.path.append("..//")
import gc
import time
import json
from copy import deepcopy
from game.comps import CardDeck, Context, Player, Table
from game.engine import GameEnv
from agent.agents import agent_cls
from game.utils import NumToCard, give_type, legalaction, tribute_legal, back_legal, CardToNum, RANK2, RANK1, card_list2str


# 按照比赛gamecore写，json里的PlayArea只用来给本地图形界面用，其他的都用不到（按照正常好理解的写即可）
class Env(GameEnv):
    def __init__(self, ctx):
        GameEnv.__init__(self, ctx)
        self.agent0 = agent_cls['random'](0)
        self.agent1 = agent_cls['random'](1)
        self.agent2 = agent_cls['random'](2)
        self.agent3 = agent_cls['random'](3)
        self.agents = [self.agent0, self.agent1, self.agent2, self.agent3]
        self.message = {}
        self.type = {1: 'Single', 2: 'Pair', 3: 'Trips', 4: 'Bomb', 5: 'Bomb', 6: 'Bomb', 7: 'Bomb', 8: 'Bomb',
                     9: 'ThreeWithTwo', 10: 'Straight', 11: 'ThreePair', 12: 'TwoTrips', 13: 'StraightFlush', 14: 'Bomb'}
        self.num = {0: 'A', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8', 8: '9', 9: 'T', 10: 'J', 11: 'Q', 12: 'K'}
        self.num2 = {0: 'A', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8', 8: '9', 9: 'T', 10: 'J', 11: 'Q',
                    12: 'K', 13:'A'}
        self.rev_num = dict(zip(self.num.values(), self.num.keys()))
        self.point = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12, 'B': 13, 'R': 14}
        self.rev_type = dict(zip(self.type.values(), self.type.keys()))
        self.win_nums = [0] * 4
        self.victory_num = [0] * 4
        self.type_sort = {'Single': 1e2, 'Pair': 2e2, 'Trips': 3e2, 'ThreePair': 4e2, 'ThreeWithTwo': 5e2, 'TwoTrips': 6e2,
                          'Straight': 7e2, 'Bomb_4': 8e2, 'Bomb_5': 9e2, 'StraightFlush': 1e3, 'Bomb_6': 2e3,
                          'Bomb_7': 3e3, 'Bomb_8': 4e3, 'JOKER': 5e3}
        self.point_sort = None
        self.suit_sort = ['S', 'H', 'C', 'D']
        self.sort_value1 = None
        self.sort_value2 = None
        self.take_action_time = 0

    def notify_beginning(self, id):   # 在一局刚开始的时候加上本局每张牌的大小
        self.message = {}
        self.message['type'] = 'notify'
        self.message['stage'] = 'beginning'
        self.message['handCards'] = self.sort_strcards(self.ctx.players[id].handcards_in_str)
        self.message['myPos'] = id
        self.message['selfRank'] = self.ctx.players[id].my_rank + 1
        self.message['oppoRank'] = self.ctx.players[(id + 1) % 4].my_rank + 1
        self.message['curRank'] = RANK1[self.ctx.cur_rank] + 1

        return json.dumps(self.message)

    def notify_tribute(self):
        self.message = {}
        self.message['type'] = 'notify'
        self.message['stage'] = 'tribute'
        res = self.tribute_res
        for ele in res:
            ele[-1] = NumToCard[ele[-1]]
        self.message['result'] = res
        return json.dumps(self.message)

    def notify_play(self):
        self.message = {}
        self.message['type'] = 'notify'
        self.message['stage'] = 'play'
        self.message['curPos'] = self.ctx.last_playid
        # print('notify_play', self.ctx.last_action)
        self.message['curAction'] = self.action_form(self.ctx.last_action)
        self.message['greaterPos'] = self.ctx.last_max_playid
        self.message['greaterAction'] = self.action_form(self.ctx.last_max_action)
        return json.dumps(self.message)

    def notify_back(self):
        self.message = {}
        self.message['type'] = 'notify'
        self.message['stage'] = 'back'
        res = self.back_res
        for ele in res:
            ele[-1] = NumToCard[ele[-1]]
        self.message['result'] = res
        return json.dumps(self.message)

    def notify_antitri(self):
        self.message = {}
        self.message['type'] = 'notify'
        self.message['stage'] = 'anti-tribute'
        self.message['antiNums'] = 2
        self.message['antiPos'] = self.ctx.win_order[-2:]
        return json.dumps(self.message)

    def notify_episodeover(self):
        self.message = {}
        self.message['type'] = 'notify'
        self.message['stage'] = 'episodeOver'
        self.message['order'] = self.ctx.win_order
        self.message['curRank'] = self.ctx.cur_rank
        rest_cards = []
        for i in self.ctx.win_order[2:]:    # 一定有两个人手牌打光的
            if self.ctx.players[i].have_cards:
                val = [i, self.sort_strcards(self.ctx.players[i].handcards_in_str)]
                rest_cards.append(val)
        self.message['restCards'] = rest_cards

        self.win_nums[self.ctx.win_order[0]] += 1
        self.win_nums[(self.ctx.win_order[0] + 2) % 4] += 1
        return json.dumps(self.message)

    def act_play(self):
        gc.disable() 
        self.message = {}
        self.message['type'] = 'act'
        self.message['handCards'] = self.sort_strcards(self.ctx.players[self.ctx.player_waiting].handcards_in_str)
        public_info = []
        for i in range(4):
            public_info.append({'rest': len(self.ctx.players[i].handcards_in_list), \
                                'playArea': self.action_form(self.ctx.players[i].last_play_cards)})
        self.message['publicInfo'] = public_info
        self.message['selfRank'] = RANK2[self.ctx.players[self.ctx.player_waiting].my_rank]
        self.message['oppoRank'] = RANK2[self.ctx.players[(self.ctx.player_waiting + 1) % 4].my_rank]
        self.message['curRank'] = self.ctx.cur_rank
        self.message['stage'] = 'play'
        last_type, last_value = give_type(self.ctx)
        if last_type == -1:   # 自己领出牌
            self.message['curPos'] = -1
            self.message['curAction'] = [None, None, None]
            self.message['greaterPos'] = -1
            self.message['greaterAction'] = [None, None, None]
        else:
            self.message['curPos'] = self.ctx.last_playid
            self.message['curAction'] = self.action_form(self.ctx.last_action)
            self.message['greaterPos'] = self.ctx.last_max_playid
            self.message['greaterAction'] = self.action_form(self.ctx.last_max_action)
        legalactions = legalaction(self.ctx, last_type=last_type, last_value=last_value)
        actionlist = []
        for ele in legalactions:
            val = self.action_form(ele)
            actionlist.append(self.action_innersort(val))
        self.message['actionList'] = self.sort_action(actionlist)
        self.message['indexRange'] = len(legalactions) - 1
        gc.enable()
        return json.dumps(self.message)

    def act_tribute(self, card_list, id):  # 进还贡的时候，playArea全是None
        self.message = {}
        self.message['type'] = 'act'
        card_str = card_list2str(card_list)
        self.message['handCards'] = self.sort_strcards(card_str)
        public_info = []
        for i in range(4):
            public_info.append({'rest': 27, 'playArea': None})
        self.message['publicInfo'] = public_info
        self.message['selfRank'] = RANK2[self.ctx.players[id].my_rank]
        self.message['oppoRank'] = RANK2[self.ctx.players[(id + 1) % 4].my_rank]
        self.message['curRank'] = self.ctx.cur_rank
        self.message['stage'] = 'tribute'
        self.message['curPos'] = -1
        self.message['curAction'] = [None, None, None]
        self.message['greaterPos'] = -1
        self.message['greaterAction'] = [None, None, None]
        legalactions = tribute_legal(card_list, self.ctx)
        actionlist = []
        for ele in legalactions:   # 进还贡都是单独的牌
            actionlist.append(['tribute', 'tribute', [NumToCard[ele]]])
        self.message['actionList'] = actionlist
        self.message['indexRange'] = len(legalactions) - 1
        return json.dumps(self.message)

    def act_back(self, card_list, id):
        self.message = {}
        self.message['type'] = 'act'
        card_str = card_list2str(card_list)
        self.message['handCards'] = self.sort_strcards(card_str)
        public_info = []
        if abs(self.ctx.win_order[-2] - self.ctx.win_order[-1]) == 2:  # 双下游
            wins = [self.ctx.win_order[0], self.ctx.win_order[1]]
            loses =[self.ctx.win_order[-1], self.ctx.win_order[-2]]
        else:
            wins = [self.ctx.win_order[0]]
            loses = [self.ctx.win_order[-1]]
        for i in range(4):
            if i in wins:
                public_info.append({'rest': 28, 'playArea': None})   # 收到进贡的多了一张牌
            elif i in loses:
                public_info.append({'rest': 26, 'playArea': None})    # 进贡的少了一张
            else:
                public_info.append({'rest': 27, 'playArea': None})
        self.message['publicInfo'] = public_info
        self.message['selfRank'] = RANK2[self.ctx.players[id].my_rank]
        self.message['oppoRank'] = RANK2[self.ctx.players[(id + 1) % 4].my_rank]
        self.message['curRank'] = self.ctx.cur_rank
        self.message['stage'] = 'back'
        self.message['curPos'] = -1
        self.message['curAction'] = [None, None, None]
        self.message['greaterPos'] = -1
        self.message['greaterAction'] = [None, None, None]
        legalactions = back_legal(card_list, self.ctx)
        actionlist = []
        for ele in legalactions:
            actionlist.append(['back', 'back', [NumToCard[ele]]])
        self.message['actionList'] = self.sort_action(actionlist, back=1)
        self.message['indexRange'] = len(legalactions) - 1
        return json.dumps(self.message)

    def tribute_step(self, card_list, id, flag=0):
        if not flag:
            message = self.act_tribute(card_list, id)
        else:
            message = self.act_back(card_list, id)
        actindex = self.agents[id].received_message(message)
        card = json.loads(str(message))['actionList'][actindex]
        action = self.get_action(card)
        return action

    def step(self):
        message = self.act_play()
        # start = time.perf_counter() 
        actindex = self.agents[self.ctx.player_waiting].received_message(message)
        # end = time.perf_counter() 
        # print(self.ctx.player_waiting, 'get action time', end-start)
        # self.take_action_time += end-start
        card = json.loads(str(message))['actionList'][actindex]
        action = self.get_action(card)
        self.update(action)
        message_notify_play = self.notify_play()
        if not self.round_end:
            for i in range(4):
                self.agents[i].received_message(message_notify_play)

    def broadcast_tribute(self):
        message_tribute = self.notify_tribute()
        for i in range(4):
            self.agents[i].received_message(message_tribute)

    def broadcast_back(self):
        message_back = self.notify_back()
        for i in range(4):
            self.agents[i].received_message(message_back)

    def broadcast_anti(self):
        message_anti = self.notify_antitri()
        for i in range(4):
            self.agents[i].received_message(message_anti)

    def sort_strcards(self, card_str, islist=0):
        if islist:
            cardlist = card_str
            if len(cardlist) == 1:   # 如果只有一个就不用排了
                return cardlist
        else:
            cardlist = card_str.split(' ')
        cardvalue = []
        for ele in cardlist:
            if ele in self.sort_value1:
                cardvalue.append(self.sort_value1[ele])

        cardvalue.sort()
        res = []
        for ele in cardvalue:
            res.append(self.sort_value2[ele])
        return res

    def sort_action(self, actionlist, back=0):
        action_res = []
        dic = {}
        actions = deepcopy(actionlist)
        if back:     # 对还贡的牌也排一下序
            for ele in actions:
                key = ele[-1][0]
                val = self.point_sort.index(key[-1])
                dic[key] = val
            mid = sorted(dic.items(), key=lambda x: x[1])
            for k, v in mid:
                action_res.append(['back', 'back', [k]])
        else:
            flag = 0
            for ele in actions:
                if ele[0] == 'PASS':
                    flag = 1
                else:
                    if ele[1] == 'JOKER':
                        ele[0] = 'JOKER'
                        ele[-1] = tuple(ele[-1])
                        key = tuple(ele)
                        val = self.type_sort[ele[0]]
                        dic[key] = val
                        continue
                    elif ele[0] == 'Bomb':
                        ele[0] = 'Bomb_' + str(len(ele[-1]))
                    ele[-1] = tuple(ele[-1])
                    key = tuple(ele)
                    val = self.type_sort[ele[0]] + self.point_sort.index(ele[1])  # 每种牌的大小等于类型值加上点数值
                    dic[key] = val
            mid = sorted(dic.items(), key=lambda x: x[1])
            if flag:
                action_res.append(['PASS', 'PASS', 'PASS'])
            for k, v in mid:
                if k[0][:4] == 'Bomb':
                    act = ['Bomb', k[1], list(k[-1])]
                elif k[0] == 'JOKER':
                    act = ['Bomb', 'JOKER', list(k[-1])]
                else:
                    act = [k[0], k[1], list(k[-1])]
                action_res.append(act)
        return action_res

    def whether_end(self):
        condition1 = len(self.ctx.table.players_on_table_id) == 1      # 3个人都出完了或者剩的俩是对家
        condition2 = len(self.ctx.table.players_on_table_id) == 2 and \
                     abs(self.ctx.table.players_on_table_id[0] - self.ctx.table.players_on_table_id[1]) == 2
        if condition1 or condition2:
            self.round_end = True
            message_notify_play = self.notify_play()     # 最后一个人出完牌了也给一下notify
            for i in range(4):
                self.agents[i].received_message(message_notify_play)
            for i in self.ctx.table.players_on_table_id:
                self.ctx.win_order.append(i)
            message_end = self.notify_episodeover()
            for i in range(4):
                self.agents[i].received_message(message_end)
            self.upgrade()
            if self.episode_end:  # 如果这个episode打完
                self.victory_num[self.ctx.win_order[0]] += 1
                self.victory_num[(self.ctx.win_order[0] + 2) % 4] += 1

    def begin_prepare(self):
        self.deal_cards()  # 初始发好牌后通知每个智能体自己的手牌情况
        self.point_sort = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', 'B', 'R']
        self.point_sort.remove(self.ctx.cur_rank)
        self.point_sort.insert(-2, self.ctx.cur_rank)
        self.sort_value1 = {}
        for c in self.suit_sort:
            for p in self.point_sort[:-2]:
                card = c + p
                self.sort_value1[card] = 10 * self.point_sort.index(p) + self.suit_sort.index(c)
        self.sort_value1['HR'] = 10000
        self.sort_value1['SB'] = 5000
        self.sort_value2 = dict(zip(self.sort_value1.values(), self.sort_value1.keys()))

    # @profile(precision=4, stream=open('/aiarena/nas/guandan_new/wintest/mem.log','w+'))
    # @profile
    def one_episode(self):
        self.ctx.cur_rank = '2'
        while not self.episode_end:
            self.begin_prepare()
            for i in range(4):
                message = self.notify_beginning(i)
                self.agents[i].received_message(message)
            self.battle_init()         # 决定第一个出牌的,同时初始化ctx的相关信息
            # start = time.perf_counter() 
            while not self.round_end:
                self.step()
            # end = time.perf_counter() 
            # print('one round time', end-start, self.take_action_time)
            # self.take_action_time = 0
        # print(self.win_nums)
    # @profile

    def reset(self):
        del self.ctx
        self.ctx = Context()
        self.ctx.table = Table()
        self.ctx.card_decks = CardDeck()
        self.ctx.players = {}
        self.ctx.players_id_list = []
        for i in range(4):
            self.ctx.players[i] = Player(i)
            self.ctx.players_id_list.append(i)
        self.ctx.wind = False  # 接风判断
        self.ctx.win_order = []
        self.wind_num = 0
        self.round_end = False
        self.episode_end = False
        self.tribute_res = []
        self.back_res = []
        self.anti_tri = False
        self.episode_end = False
        
    def multiple_episodes(self, num):
        for i in range(num):
            self.one_episode()
            self.reset()
            # time.sleep(1)
            gc.collect()
        print(self.win_nums, self.victory_num)

    def action_form(self, action):
        if action == None:
            return None
        if len(action) == 0:
            return ['PASS', 'PASS', 'PASS']
        res_list = []
        for (index, ele) in enumerate(action[:54]):
            if ele > 0:
                val = ele * [NumToCard[index]]
                res_list += val
        type = action[-1]
        value = action[-2]
        if type <= 9:
            if value == 13:
                res_num = 'B'
            elif value == 14:
                res_num = 'R'
            else:
                res_num = NumToCard[value][-1]
        elif type == 14:
            res_num = 'JOKER'
        else:
            res_num = self.num[value]
        res_type = self.type[type]
        return [res_type, res_num, res_list]

    def action_innersort(self, action):
        if action[0] == 'PASS':
            return action
        rank_card = 'H' + self.ctx.cur_rank
        if action[0] == 'Single':
            return action
        elif action[0] in ['Pair', 'Trips', 'Bomb']:
            if action[1] == 'JOKER':
                return ['Bomb', 'JOKER', ['SB', 'SB', 'HR', 'HR']]
            elif action[1] == 'B' or action[1] == 'R':     # 大小王就直接出，不存在顺序问题
                return action
            else: # 是级牌的多个牌(只用看花色）,不含万能牌,含万能牌（万能牌对应的值是最大的）都是一样的处理
                res = self.sort_strcards(action[-1], islist=1)
            return [action[0], action[1], res]
        elif action[0] == 'ThreeWithTwo':
            dic = {}
            for card in action[-1]:
                if card[-1] not in dic:
                    dic[card[-1]] = [card]
                else:
                    dic[card[-1]].append(card)
            if len(dic[action[1]]) < 3:     # 点数是级牌的话不会出现这种情况
                assert action[-1].count(rank_card) + len(dic[action[1]]) >= 3, 'illegal ThreeWithTwo'
                for i in range(3 - len(dic[action[1]])): # 先移掉再加进去
                    dic[self.ctx.cur_rank].remove(rank_card)
                dic[action[1]] += (3 - len(dic[action[1]])) * [rank_card]
            if action[1] != self.ctx.cur_rank and self.ctx.cur_rank in dic and len(dic[self.ctx.cur_rank]) > 0 :  # 点数不是级牌，如果还剩的有级牌
                if len(dic.keys()) == 2:   # 带的就是级牌
                    pass
                else:   # 有三个点
                    for point in dic.keys():
                        if point != self.ctx.cur_rank and point != action[1]:
                            dic[point].append(rank_card)
                            dic[self.ctx.cur_rank].remove(rank_card)
                            break
            elif action[1] == self.ctx.cur_rank:           # 点数是级牌，然后剩的还少了一张,移掉一张万能牌
                for point in dic.keys():
                    if point != self.ctx.cur_rank and len(dic[point]) < 2:
                        dic[point].append(rank_card)
                        dic[self.ctx.cur_rank].remove(rank_card)
            follow = ''
            for point in dic.keys():
                if point != action[1] and len(dic[point]) == 2:
                    follow = point
                    break
            res = self.sort_strcards(dic[action[1]], islist=1) + self.sort_strcards(dic[follow], islist=1)
            return [action[0], action[1], res]
        elif action[0] == 'ThreePair':
            return self.straight_like_sort(action, 3, 2)
        elif action[0] == 'Straight' or action[0] == 'StraightFlush':
            return self.straight_like_sort(action, 5, 1)
        elif action[0] == 'TwoTrips':
            return self.straight_like_sort(action, 2, 3)

    def straight_like_sort(self, action, length, num): # length表示牌组的长度，num表示每一张的数量
        rank_card = 'H' + self.ctx.cur_rank
        num_point = [i for i in range(self.rev_num[action[1]], self.rev_num[action[1]] + length)]
        need_point = [self.num2[i] for i in num_point]  # 需要的点数
        dic = dict([(k, []) for k in need_point])
        for card in action[-1]:
            if card[-1] not in dic:  # 如果有不在范围里的点数，一定是万能牌
                dic[card[-1]] = [card]
            else:
                dic[card[-1]].append(card)
        for point in need_point:
            if len(dic[point]) < num:  # 如果有需要的点数但是牌不够的话，那一定有万能牌
                assert len(dic[self.ctx.cur_rank]) + len(dic[point]) >= num, print(self.message, dic, action, 'illegal Straight-like combinations')
                for i in range(num - len(dic[point])):  # 先移掉再加进去
                    dic[self.ctx.cur_rank].remove(rank_card)
                dic[point] += (num - len(dic[point])) * [rank_card]
        res = []
        for point in need_point:
            res += self.sort_strcards(dic[point], islist=1)
        return [action[0], action[1], res]

    def get_action(self, res):   # 从message的动作列表里得到实际选择的动作,实际做的动作包含type和value
        if res[0] == 'tribute' or res[0] == 'back':
            return CardToNum[res[-1][0]]
        else:
            if res[0] == 'PASS':
                return []
            action = [0] * 54
            for card in res[-1]:
                val = CardToNum[card]
                action[val] += 1
            if res[1] == 'JOKER':
                action.append(14)
                action.append(14)
            elif res[0] == 'Bomb':
                action.append(self.point[res[1]])
                action.append(len(res[-1]))
            elif self.rev_type[res[0]] <= 3 or self.rev_type[res[0]] == 9:
                action.append(self.point[res[1]])
                action.append(self.rev_type[res[0]])
            else:
                action.append(self.rev_num[res[1]])
                action.append(self.rev_type[res[0]])
            return action


if __name__ == '__main__':
    ctx = Context()
    env = Env(ctx)
    # env.ctx.cur_rank = '8'
    # env.begin_prepare()
    # env.battle_init()
    # a = ['H2', 'C3', 'C4', 'D4', 'D4', 'C5', 'H6', 'S7', 'H7', 'S9', 'C9', 'CT', 'DT', 'HJ', 'SQ', 'DQ', 'SK', 'CK', 'DK', 'DK', 'SA', 'CA', 'DA', 'DA', 'H8', 'HR', 'HR']
    # card_str = ' '.join(a)
    # env.ctx.players[env.ctx.player_waiting].update_cards(
    #     card_str)
    # actionlist = []
    # legalactions = legalaction(env.ctx)
    # for ele in legalactions:
    #     val = env.action_form(ele)
    #     print(val, ele)
    #     print(env.action_innersort(val))
    #     if ele[-1] == 13 or ele[-1] == 10:
    #         print(ele)

    # print(env.agent0.id, env.agent1.id)
    # env.ctx.win_order = [0, 1, 2, 3]
    env.multiple_episodes(1)
    # env.deal_cards()

    # env.ctx.cur_rank = '3'
    # env.battle_init()


