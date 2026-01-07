import itertools as it
from copy import deepcopy
import numpy as np
from collections import Counter

from game.comps.context import Context

CardToNum = {
    'H2':0, 'H3':1, 'H4':2, 'H5':3, 'H6':4, 'H7':5, 'H8':6, 'H9':7, 'HT':8, 'HJ':9, 'HQ':10, 'HK':11, 'HA':12,
    'S2':13, 'S3':14, 'S4':15, 'S5':16, 'S6':17, 'S7':18, 'S8':19, 'S9':20, 'ST':21, 'SJ':22, 'SQ':23, 'SK':24, 'SA':25,
    'C2':26, 'C3':27, 'C4':28, 'C5':29, 'C6':30, 'C7':31, 'C8':32, 'C9':33, 'CT':34, 'CJ':35, 'CQ':36, 'CK':37, 'CA':38,
    'D2':39, 'D3':40, 'D4':41, 'D5':42, 'D6':43, 'D7':44, 'D8':45, 'D9':46, 'DT':47, 'DJ':48, 'DQ':49, 'DK':50, 'DA':51,
    'SB':52, 'HR':53
}

NumToCard = dict(zip(CardToNum.values(), CardToNum.keys()))

RANK1 = {
    '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8,
    'T': 9, 'J': 10, 'Q': 11, 'K': 12, 'A': 13
}

RANK2 = dict(zip(RANK1.values(), RANK1.keys()))


# 这里不考虑在本来就能组成某种牌型的情况下非要用万能牌替其中一张牌的情况，省下万能牌供以后用
def legalaction(ctx: Context, last_type=-1, last_value=-1):   # last_value在自己领出牌的时候前面是-1，因为算牌是从0开始的
    '''
    author: Yu Yan & Lu Yudong
    '''
    # print(ctx.card_decks.sortcards(ctx.players[ctx.player_waiting].handcards_in_str))
    cards = ctx.players[ctx.player_waiting].get_cards_vector()
    rank_card_num = ctx.players[ctx.player_waiting].get_rank_card_num()  # 这个是万能牌的数量
    rank_card = CardToNum['H' + ctx.cur_rank]    # 红桃是第一个编码，所以和cur_rank是相等的
    action_list = []
    if last_type != -1:  # 如果不是自己领出牌，都是可以跳过的
        action_list.append([])
    cards_num = [sum([cards[i+j*13] for j in range(4)]) for i in range(13)]  # 手中每种牌的数量（不包括大小王）

    # 单牌
    single = []
    for i in range(13):
        single.append([])
        for j in range(4):
            if cards[i+j*13]:
                tmp = [0] * 54
                tmp[i+j*13] = 1
                single[i].append(tmp)

    if cards[-2]:  # 大小王
        tmp = [0] * 54
        tmp[-2] = 1
        single.append([tmp])
    else:
        single.append([])

    if cards[-1]:
        tmp = [0] * 54
        tmp[-1] = 1
        single.append([tmp])
    else:
        single.append([])

    # 对子
    double = []
    two_combine = list(it.combinations_with_replacement(list(range(4)), 2))  # 这边range(4)代表4种花色
    for i in range(13):
        double.append([])
        if cards_num[i] >= 2:
            for co in two_combine:
                if (co[0] == co[1] and cards[i+co[0]*13] == 2) or (co[0] != co[1] and cards[i+co[0]*13] and cards[i+co[1]*13]):  # 同一花色有两张或不同花色加起来超过两张
                    tmp = [0] * 54
                    tmp[i+co[0]*13] += 1
                    tmp[i+co[1]*13] += 1
                    double[i].append(tmp)

        elif cards_num[i] == 1 and rank_card_num > 0 and rank_card != i:  # 有一张万能牌
            for j in range(4):
                if cards[i+j*13]:
                    tmp = [0] * 54
                    tmp[i+j*13] += 1
                    tmp[rank_card] += 1   # 即表示等级，也代表万能牌了
                    double[i].append(tmp)
    double_num = deepcopy(double)
            
    if cards[-2] == 2:
        tmp = [0] * 54
        tmp[-2] = 2
        double.append([tmp])
    else:
        double.append([])

    if cards[-1] == 2:
        tmp = [0] * 54
        tmp[-1] = 2
        double.append([tmp])
    else:
        double.append([])

    #三张以上
    n_card = [single, double]  # 这边的single和double实际是把每种牌符合这个要求的放进来
    for o in range(6):
        n_card.append([])
        n_combine = []
        n_combine_o = list(it.combinations_with_replacement(list(range(4)), o+3))  # 从列表里取x个元素进行组合（可重复）
        for t in n_combine_o:
            no = False
            for k in range(4):
                if list(t).count(k) > 2:  # 每个花色不能超过两张
                    no = True
                    break
            if not no:
                n_combine.append(t)

        for i in range(13):
            n_card[-1].append([])
            if cards_num[i] >= o+3:
                for nc in n_combine:
                    for n in nc:
                        find = True
                        if list(nc).count(n) > cards[i+n*13]:
                            find = False
                            break
                    if find:
                        tmp = [0] * 54
                        for n in nc:
                            tmp[i+n*13] += 1
                        n_card[-1][i].append(tmp)
            elif cards_num[i] == o+2 and rank_card_num > 0 and rank_card != i:
                tmp = deepcopy(n_card[-2][i])
                for t in tmp:
                    t[rank_card] = 1
                n_card[-1][i] = tmp
            elif cards_num[i] == o+1 and rank_card_num == 2 and rank_card != i:
                tmp = deepcopy(n_card[-3][i])
                for t in tmp:
                    t[rank_card] = 2
                n_card[-1][i] = tmp
    # 最后得到的n_card是包含了每种牌有几张（万能牌也算进去了）
    # 三带二，last_value直接加在动作里，方便后续找更大的，对应的是0-12，上面字典里的2-A
    triple_double = []
    if (last_type == 9 and last_value != rank_card) or last_type == -1:  # last_type=9是三带二
        triple_list = list(range(last_value+1, 13))    # 这里+1是为了找到比上一个三带二要大的组合
        if rank_card < last_value:      # 只有三带二是考虑级牌的，其他的下面都不考虑了，单纯按顺序来
            triple_list.append(rank_card)
        td_combine = it.product(triple_list, list(range(15)), repeat=1)  # 前一个元素和后一个元素分别组合
        for td in td_combine:
            if td[0] == td[1]:
                continue
            if n_card[2][td[0]] and double[td[1]]:
                for t in n_card[2][td[0]]:
                    for d in double[td[1]]:
                        if t[rank_card] + d[rank_card] <= rank_card_num:   # 前面组成这三带二里的，其中的万能牌数量不能超过总体数量才行
                            tmp = [t[i]+d[i] for i in range(54)]
                            tmp.append(td[0])             # 三带二比较特殊，考虑加入前面的三个是啥值（0-12，对应的2-A）
                            triple_double.append(tmp)
    # test = [[vector2card(i[:54]), i[-1]] for i in triple_double]
    # print(test)

    # 顺子， 这里last_value按+1算，即最大不能超过8（=8的情况表示前面一个人是9TJOK，还能有TJQKA打）
    straight = []
    if (last_type == 10 and last_value < 9) or last_type == -1:      # last_type=10是顺子
        for i in range(last_value+1, 10):
            gap = []
            for j in range(5):
                if cards_num[i+j-1] == 0 or ((12+i+j)%13 == rank_card and cards_num[i+j-1] == 1 and cards_num[rank_card] == 1):
                    gap.append(j)    # cards_num是每种牌的数量，gap记录一个顺子中间缺的+刚好有一张就是万能牌
            if len(gap) <= rank_card_num:   # 缺的牌数可以用万能牌补上（去掉了万能牌填充的那个点数了）
                new_cards = deepcopy(cards)
                new_cards[rank_card] -= len(gap)  # 万能牌要拿去补缺的点，下面就不能重复用了
                st = []
                for j in range(5):
                    if j in gap:
                        continue
                    st.append([])
                    for k in range(4):
                        if i == 0 and j == 0 and new_cards[12+k*13] > 0:  # 最小的顺子A2345
                            st[-1].append(12+k*13)   # 最后一个是A
                        elif new_cards[i+j-1+k*13] and not (i == 0 and j == 0):     # 对应数字的的所有花色都放进来（考虑过A了，且考虑万能牌是不是已经用去补缺的点了，所以用new_cards）
                            st[-1].append(i+j-1+k*13)  # 有减1是因为card_num的下标从0开始
                if len(gap) == 0:
                    st = it.product(st[0], st[1], st[2], st[3], st[4], repeat=1)
                elif len(gap) == 1:
                    st = it.product(st[0], st[1], st[2], st[3], repeat=1)
                elif len(gap) == 2:
                    st = it.product(st[0], st[1], st[2], repeat=1)
                for s in st:
                    tmp = [0] * 54
                    tmp[rank_card] += len(gap)   # 缺的牌用万能牌去补
                    for j in s:
                        tmp[j] += 1
                    tmp.append(i)
                    straight.append(tmp)
    # test = [[vector2card(i[:54]), i[-1]] for i in straight]
    # print(test)

    # 同花顺，大于5张的炸弹，小于6张的
    flush_straight = []
    if last_type not in [6, 7, 8, 14]:
        init = last_value + 1 if last_type == 13 else 0
        for i in range(init, 10):
            for c in range(4):
                st_f = []
                for j in range(5):
                    if i == 0 and j == 0 and cards[12+c*13] > 0:   # 考虑过A了
                        st_f.append(12+c*13)
                    elif cards[i+j-1+c*13] and not (i == 0 and j == 0):  # 要把A去掉，不然可能有-1，指到大王去了
                        st_f.append(i+j-1+c*13)
                if len(st_f) + rank_card_num < 5 or (len(st_f) + rank_card_num == 5 and rank_card in st_f):  # 算上万能牌之后不足5张
                    continue
                tmp = [0] * 54
                tmp[rank_card] += 5 - len(st_f)
                for s in st_f:
                    tmp[s] += 1
                tmp.append(i)
                flush_straight.append(tmp)
    # test = [[vector2card(i[:54]), i[-1]] for i in flush_straight]
    # print(test)
    # 连对 （只能有三对,最大QQKKAA，最小AA2233）last_value按+1算，last_value=10表示是JJQQKK，还有QQKKAA可以出
    straight_double = []
    if (last_type == 11 and last_value < 11) or last_type == -1:  # last_type=11是连对
        for i in range(last_value+1, 12):
            gap = []
            for j in range(3):
                if not double_num[i+j-1]:  # 这边double最后俩是放的大小王，这样没办法把AA2233也考虑进去
                    gap.append(j)
            if gap:
                if len(gap) == 1 and rank_card_num == 2:
                    sd = it.product(double_num[i-(0 if gap[0] == 0 else 1)], double_num[i+(0 if gap[0] == 2 else 1)], repeat=1)
                    for s in sd:
                        if s[0][rank_card] + s[1][rank_card] == 0:  # 在缺一个对的情况下，用万能牌去组，但前提是另外两个对不能包含万能牌
                            s[0][rank_card] = 2
                            tmp = [s[0][l]+s[1][l] for l in range(54)]
                            tmp.append(i)
                            straight_double.append(tmp)
                else:
                    continue
            sd = it.product(double_num[i-1], double_num[i], double_num[i+1], repeat=1)
            for s in sd:
                if s[0][rank_card] + s[1][rank_card] + s[2][rank_card] <= rank_card_num:  # 不缺对的情况下，需要三个对中万能牌的数量不超过总的万能牌数
                    tmp = [s[0][l]+s[1][l]+s[2][l] for l in range(54)]
                    tmp.append(i)
                    straight_double.append(tmp)
    # test = [[vector2card(i[:54]), i[-1]] for i in straight_double]
    # print(test)

    # 钢板（2个三对，最大是KKKAAA,最小的是AAA222）,0表示前一个是AAA222
    plates = []
    if (last_type == 12 and last_value < 12) or last_type == -1:  # last_type=12是钢板
        for i in range(last_value+1, 13):
            gap = False
            for j in range(2):
                if not n_card[2][i+j-1]:
                    gap = True
                    break
            if gap:
                continue
            pl = it.product(n_card[2][i-1], n_card[2][i], repeat=1)
            for p in pl:
                if p[0][rank_card] + p[1][rank_card] <= rank_card_num:
                    tmp = [p[0][l]+p[1][l] for l in range(54)]
                    tmp.append(i)
                    plates.append(tmp)
    # test = [[vector2card(i[:54]), i[-1]] for i in plates]
    # print(test)
    # 天王炸（4个王）
    big_bumb = []
    if cards[-2] == 2 and cards[-1] == 2:
        tmp = [0] * 54
        tmp[-1] = 2
        tmp[-2] = 2
        big_bumb.append(tmp)

    # 在所有合法动作后面加上last_type
    for index in range(len(n_card)):   # 表示有index+1张牌
        for (point, kind) in enumerate(n_card[index]):
            if len(kind) == 0:   # 第x种牌没有这么多张
                pass
            else:
                for ele in kind:
                    if len(ele) > 0:  # 单、双中大小王占的位置可能是空列表
                        ele.append(point)
                        ele.append(index+1)  # 在动作后面加上last_type
    for ele in triple_double:
        ele.append(9)
    new_straight = []  # 上面求的动作里可能就有重复的，所以用set的话可能本身数量就会变，这边直接for循环把其中的同花顺去掉来加last_type
    for ele in straight:
        if ele not in flush_straight:
            ele.append(10)
            new_straight.append(ele)
    for ele in flush_straight:
        ele.append(13)
    for ele in straight_double:
        ele.append(11)
    for ele in plates:
        ele.append(12)
    for ele in big_bumb:
        ele.append(14)

    if last_type == -1:  # 自己先出牌
        n_need = n_card
    elif last_type == 14:  # 如果有人出了王炸，直接返回空列表
        return action_list
    elif last_type == 1 or last_type == 2:  # 应该是单或者对
        # print('card 2')
        # for n in n_card[2]:
        #     print(actions2dict(n))
        if last_value == rank_card:  # 如果出的是级牌，只能打大小王或炸弹
            n_need = [n_card[last_type-1][13:]] + n_card[3:]
        elif last_value < 13:      # 这里是把级牌放在王的前面
            n_need = [n_card[last_type-1][last_value+1:]] + n_card[3:]
            if rank_card < last_value:
                n_need[0].append(n_card[last_type-1][rank_card])
        elif last_value == 13:
            n_need = [[n_card[last_type-1][14]]] + n_card[3:]
        elif last_value == 14:
            n_need = n_card[3:]
    elif last_type == 3:
        if last_value == rank_card:
            n_need = n_card[3:]
        else:
            n_need = [n_card[2][last_value+1:]] + n_card[3:]
            if rank_card < last_value:
                n_need[0].append(n_card[last_type-1][rank_card])
    elif last_type <= 8:   # 炸弹，其他特殊牌型在上面考虑了
        if last_value == rank_card:  # 如果才打的是级牌，那么必须多一张能更大
            n_need = n_card[last_type:]
        else:
            n_need = [n_card[last_type-1][last_value+1:]] + n_card[last_type:]
            if rank_card < last_value:
                n_need[0].append(n_card[last_type-1][rank_card])
    elif last_type == 13:  # 同花顺，得用6张及以上的炸弹
        n_need = n_card[5:]
    else:  # 其他特殊牌型，要么下面拼上，要么打炸弹
        n_need = n_card[3:]

    for n in n_need:
        for i in n:
            action_list += i

    # print(len(new_straight), len(triple_double), len(straight_double), len(plates), len(flush_straight))

    action_list += new_straight + triple_double + straight_double + plates + big_bumb + flush_straight
    action_list = list(set([tuple(t) for t in action_list]))   # 去一遍重
    action_list = [list(v) for v in action_list]

    return action_list        # 在每个动作的后面加上last_type，方便下面给值


# 给定合法动作的类型
def give_type(ctx):
    if ctx.last_action is None or (ctx.trick_pass == ctx.table.players_on_table_numb - 1 and not ctx.wind) or ctx.recv_wind:
        # 一开始出牌、上一轮其余玩家都过(不能是接风轮，不然少了一个人，最后一个轮到出牌的就不对了）、接风出牌的情况下任意出牌
        last_type = -1
        last_value = -1
    else:     # 在n_card类型时，last_value按照字典中的对应值来(即第一行的0~12)
        rank_card = CardToNum['H' + ctx.cur_rank]
        cards_vector = ctx.last_max_action   # 当前轮最大的动作
        cards_list = []
        last_type = cards_vector[-1]  # 牌的类型
        for index, val in enumerate(cards_vector[:54]):
            if val > 0:
                if index < 52:     # 0-12
                    cards_list += val * [index % 13]
                else:
                    cards_list += val * [index]
        if last_type <= 2:  # 单或者对,因为可能有王，所以单独考虑
            if rank_card not in cards_list or len(cards_list) == 1:
                assert len(set(cards_list)) == 1, 'exist illegal single or double'
                if 52 in cards_list:
                    last_value = 13
                elif 53 in cards_list:
                    last_value = 14
                else:
                    last_value = cards_list[0]
            else:
                card = rank_card       # 防止都是级牌
                for i in range(len(cards_list)):
                    if cards_list[i] != rank_card:
                        card = cards_list[i]
                        break
                last_value = card
        elif 2 < last_type <= 8:  # 都是一样的牌
            if rank_card not in cards_list:  # 无级牌或万能牌
                assert len(set(cards_list)) == 1, 'exist illegal n_cards'
                last_value = cards_list[0]
            else:
                card = rank_card      # 因为存的是点数，有可能几张都是级牌
                for i in range(len(cards_list)):
                    if cards_list[i] != rank_card:
                        card = cards_list[i]
                        break
                last_value = card
        elif last_type == 14:    # 王炸的话这里其实无所谓，设大一点省的算其他特殊动作麻烦
            last_value = 14
        else:        # 特殊牌型的last_value都在上面直接放在动作里
            last_value = cards_vector[-2]   # 三带二的value是0-12，对应字典里的2-A；其他的是点数-1，0-A，1-2···，12-K
    return last_type, last_value


def whether_flush(card_list, card):
    suit = card // 13
    point = card % 13
    if point == 12:
        avail_points = [[12, 0, 1, 2, 3], [8, 9, 10, 11, 12]]
    else:
        avail_points = []
        minpoint = max(0, point - 4)
        maxpoint = min(12, point + 4)
        for i in range(minpoint, maxpoint-3):
            avail_points.append([i, i+1, i+2, i+3, i+4])
    for ele in avail_points:
        flag = 1
        for i in ele:
            val = suit * 13 + i
            if val not in card_list:
                flag = 0
                break
        if flag:
            return True
    return False


# 进贡是要进贡手里除了万能牌之外最大的牌（这边加个判断，如果有一样大的牌，看看能不能有同花顺，有的话就不给放进去，如果都可以组，就随机留一个）
def tribute_legal(cards_list, ctx):
    tri_dic = {}
    if 53 in cards_list:
        return [53]
    elif 52 in cards_list:
        return [52]
    else:
        for ele in cards_list:
            if ele % 13 != CardToNum['H' + ctx.cur_rank]:
                val = ele % 13
            else:
                val = 50
            if ele != CardToNum['H' + ctx.cur_rank]:
                if val not in tri_dic:
                    tri_dic[val] = [ele]
                else:
                    tri_dic[val].append(ele)
    sorted_dic = list(sorted(tri_dic.items(), key=lambda x: x[0], reverse=True))
    res = sorted_dic[0][1]
    backup = []
    if len(res) == 1:
        return res
    else:
        for card in res:
            judge = whether_flush(cards_list, card)
            if judge:  # 如果存在同花顺
                res.remove(card)
                backup.append(card)
        if len(res) == 0:
            res.append(backup[0])
        res = list(set(res))
    return res


# 返回抗贡的合法动作，这里同样默认不返回级牌
def back_legal(cards_list, ctx):
    res = []
    rank_card = CardToNum['H' + ctx.cur_rank]
    for i in cards_list:
        if i % 13 <= 8 and i % 13 != rank_card and i < 52:  # 还贡的牌不能是大小王
            res.append(i)
    res = list(set(res))
    return res


# 如果满足抗贡条件则自动抗贡
def anti_tribute(ctx, flag):
    if flag == 0:       # 针对下游的情况,有两张大王可抗贡
        cards = ctx.players[ctx.win_order[-1]].get_cards_vector()
        if cards[-1] == 2:
            return True
    else:         # 双下游的情况，两个人手里加起来两张大王可抗贡
        cards1 = ctx.players[ctx.win_order[-1]].get_cards_vector()
        cards2 = ctx.players[(ctx.win_order[-1] + 2) % 4].get_cards_vector()
        if cards1[-1] + cards2[-1] == 2:
            return True
    return False


def card_list2vector(list_cards):
    tmp = np.zeros(54, np.int8)
    counter = Counter(list_cards)
    for card, num_times in counter.items():
        tmp[card] = num_times
    return tmp        # 因为是环境里自己展开看的，不用和训练代码的vector一样


def vector2card(cardarray):
    res = ''
    for i in range(len(cardarray)):
        if cardarray[i] != 0:
            card = NumToCard[i] + ' '
            res += card * cardarray[i]
    return res


def card_dict2list(card_info: dict):
    res = []
    for k, v in card_info.items():
        res.extend([CardToNum[k]] * v)
    res.sort()
    return res


def card_list2dict(card_info: list):
    res = {}
    cards = Counter(card_info)
    for ele in cards:
        res[NumToCard[ele]] = cards[ele]
    return res


def card_list2str(card_info: list):
    res = ''
    for ele in card_info:
        res += NumToCard[ele] + ' '
    return res[:-1]


def card_str2dict(card_info: str):
    cardlist = card_info.split(' ')
    res = Counter(cardlist)
    return res


def card_str2list(card_info: str):
    cardlist = card_info.split(' ')
    res = []
    for ele in cardlist:
        res.append(CardToNum[ele])
    return res
