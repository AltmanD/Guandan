import itertools as it
from copy import deepcopy
from game.comps.context import Context

def legalaction(cards, rank_card_num, rank_card, last_type=-1, last_value=0):
    '''
    author: Yu Yan
    '''
    action_list = []
    if last_type != -1:
        action_list.append([])
    cards_num = [sum([cards[i+j*13] for j in range(4)]) for i in range(13)]

    # 单牌
    single = []
    for i in range(13):
        single.append([])
        for j in range(4):
            if cards[i+j*13]:
                tmp = [0] * 54
                tmp[i+j*13] = 1
                single[i].append(tmp)

    if cards[-2]:
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
    two_combine = list(it.combinations_with_replacement(list(range(4)), 2))
    for i in range(13):
        double.append([])
        if cards_num[i] >= 2:
            for co in two_combine:
                if (co[0] == co[1] and cards[i+co[0]*13] == 2) or (co[0] != co[1] and cards[i+co[0]*13] and cards[i+co[1]*13]):
                    tmp = [0] * 54
                    tmp[i+co[0]*13] += 1
                    tmp[i+co[1]*13] += 1
                    double[i].append(tmp)
        elif cards_num[i] == 1 and rank_card_num > 0 and rank_card != i:
            for j in range(4):
                if cards[i+j*13]:
                    tmp = [0] * 54
                    tmp[i+j*13] += 1
                    tmp[rank_card] += 1
                    double[i].append(tmp)
            
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
    n_card = [single, double]
    for o in range(6) :
        n_card.append([])
        n_combine = []
        n_combine_o = list(it.combinations_with_replacement(list(range(4)), o+3))
        for t in n_combine_o:
            no = False
            for k in range(4):
                if list(t).count(k) > 2:
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
    
    #三带二
    triple_double = []
    if (last_type == 9 or last_type == -1) and last_value != rank_card:
        triple_list = list(range(last_value+1, 13))
        if rank_card < last_value:
            triple_list.append(rank_card)
        td_combine = it.product(triple_list, list(range(15)), repeat=1)
        for td in td_combine:
            if td[0] == td[1]:
                continue
            if n_card[2][td[0]] and double[td[1]]:
                for t in n_card[2][td[0]]:
                    for d in double[td[1]]:
                        if t[rank_card] + d[rank_card] <= rank_card_num:
                            triple_double.append([t[i]+d[i] for i in range(54)])

    #顺子
    straight = []
    if (last_type == 10 or last_type == -1) and last_value < 9:
        for i in range(last_value+1, 10):
            gap = []
            for j in range(5):
                if cards_num[i+j-1] == 0 or ((12+i+j)%13 == rank_card and cards_num[i+j-1] == 1 and cards_num[rank_card] == 1):
                    gap.append(j)
            if len(gap) <= rank_card_num:
                st = []
                for j in range(5):
                    if j in gap:
                        continue
                    
                    st.append([])
                    for k in range(4):
                        if i == 0 and j == 0 and cards[12+k*13] > 0:
                            st[-1].append(12+k*13)
                        elif cards[i+j-1+k*13]:
                            st[-1].append(i+j-1+k*13)
                if len(gap) == 0:
                    st = it.product(st[0], st[1], st[2], st[3], st[4], repeat=1)
                elif len(gap) == 1:
                    st = it.product(st[0], st[1], st[2], st[3], repeat=1)
                elif len(gap) == 2:
                    st = it.product(st[0], st[1], st[2], repeat=1)
                for s in st:
                    tmp = [0] * 54
                    tmp[rank_card] += len(gap)
                    for j in s:
                        tmp[j] += 1
                    straight.append(tmp)
    
    #同花顺
    if last_type not in [6, 7, 8, 14]:
        init = last_value + 1 if last_type == 13 else 0
        for i in range(init, 10):
            gap = []
            for c in range(4):
                st_f = []
                for j in range(5):
                    if i == 0 and j == 0 and cards[12+c*13] > 0:
                        st_f.append(12+c*13)
                    elif cards[i+j-1+c*13]:
                        st_f.append(i+j-1+c*13)
                if len(st_f) + rank_card_num < 5 or (len(st_f) + rank_card_num == 5 and rank_card in st_f):
                    continue
                tmp = [0] * 54
                tmp[rank_card] += 5 - len(st_f)
                for s in st_f:
                    tmp[s] += 1
                straight.append(tmp)

    #连对        
    straight_double = []
    if (last_type == 11 or last_type == -1) and last_value < 11:
        for i in range(last_value+1, 12):
            gap = []
            for j in range(3):
                if not double[i+j-1]:
                    gap.append(j)
            if gap:
                if len(gap) == 1 and rank_card_num == 2:

                    sd = it.product(double[i-(0 if gap[0] == 0 else 1)], double[i+(0 if gap[0] == 2 else 1)], repeat=1)
                    for s in sd:
                        if s[0][rank_card] + s[1][rank_card] == 0:
                            s[0][rank_card] = 2
                            straight_double.append([s[0][l]+s[1][l] for l in range(54)])
                else:
                    continue
            sd = it.product(double[i-1], double[i], double[i+1], repeat=1)
            for s in sd:
                if s[0][rank_card] + s[1][rank_card] + s[2][rank_card] <= rank_card_num:
                    straight_double.append([s[0][l]+s[1][l]+s[2][l] for l in range(54)])
                
    #钢板
    plates = []
    if (last_type == 12 or last_type == -1) and last_value < 12:
        for i in range(13):
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
                    plates.append([p[0][l]+p[1][l] for l in range(54)])
                
    #天王炸
    big_bumb = []
    if cards[-2] == 2 and cards[-1] == 2:
        tmp = [0] * 54
        tmp[-1] = 2
        tmp[-2] = 2
        big_bumb.append(tmp)

    if last_type == -1:
        n_need = n_card
    elif last_type == 1 or last_type == 2:
        # print('card 2')
        # for n in n_card[2]:
        #     print(actions2dict(n))
        if last_value == rank_card:
            n_need = [n_card[last_type-1][13:]] + n_card[3:]
        elif last_value == 13:
            n_need = [[n_card[last_type-1][14]]] + n_card[3:]
        elif last_value == 14:
            n_need = n_card[3:]
        else:
            n_need = [n_card[last_type-1][last_value+1:]] + n_card[3:]
            n_need[0].append(n_card[last_type-1][rank_card])
    elif last_type == 3:
        if last_value == rank_card:
            n_need = n_card[3:]
        else:
            n_need = [n_card[2][last_value+1:]] + n_card[3:]
            n_need[0].append(n_card[last_type-1][rank_card])
    elif last_type <= 8:
        n_need = [n_card[last_type-1][last_value+1:]] 
        n_need[0].append(n_card[last_type-1][rank_card])
        if last_type < 8:
            n_card[last_type:]
    elif last_type == 13:
        n_need = n_card[5:]
    else:
        n_need = n_card[3:]
        
        
    for n in n_need:
        for i in n:
            action_list += i
    for i in n_card:
        print(len(i))

    action_list += straight + triple_double + straight_double + plates + big_bumb
    action_list = list(set([tuple(t) for t in action_list]))
    action_list = [list(v) for v in action_list]

    return action_list


def ctx2info(ctx: Context):
    info = {
        'obs': None,
        'action': None,
        'reward': None,
        'done': None
    }
    return info

def card_dict2list(card_info: dict):
    return []

def card_dict2str(card_info: dict):
    return ''

def card_list2dict(card_info: list):
    return {}

def card_list2str(card_info: list):
    return ''

def card_str2dict(card_info: str):
    return {}

def card_str2list(card_info: str):
    return []