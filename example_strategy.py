import random
import json

try:
    import PokerCalculator as PC
except ImportError as e:
    print('Should install poker calculator first!!!!!!!!!')


PREFLOP_DICT = None


def poker_random_decision(observation):
    """
    有限注扑克随机决策
    :param observation: 见 ColosGame/PokerGame
    :return: 数字，0-2分别代表'f', 'c', 'r'
    """
    return random.randint(0, 2)


def renju_random_decision(observation):
    """
    五子棋随机决策
    :param observation: 棋盘矩阵
    :return: 下子位置决策x/y
    """
    # In Renju conflict action will lead to fold
    while True:
        x = random.randint(0, 14)
        y = random.randint(0, 14)
        if observation[x, y] != 0:
            continue
        return "%d/%d" % (x, y)


def poker_always_call(observation):
    return 'c'


def poker_threshold_cautious_decision(observation):
    """
    期望的观测是json形式的, 见General Poker Game的empty observation
    :param observation:
    :return: 数字，0-2分别代表'f', 'c', 'r'
    """
    if not observation['cards'] or not observation['actions']:
        return None
    public_card = observation['cards']['flop_card'] +\
                  observation['cards']['turn_card'] + observation['cards']['river_card']
    stage = (len(public_card) // 2)
    win_rate = __poker_win_rate(public_card, observation['cards']['hand_card'], stage)

    my_raise = observation['details']['my_raise']
    opponent_raise = observation['details']['opponent_raise']

    if stage == 0:
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.45, call_rate=0.55, stage=stage
                                    , my_raise=my_raise, opponent_raise=opponent_raise)  # no all_in in deal
    elif stage == 3:
        # 取消Raise的bluff    不敢allin来bluff.... 效果极差
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.70, call_rate=0.85, stage=stage
                                    , my_raise=my_raise, opponent_raise=opponent_raise)
    elif stage == 4:
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.75, call_rate=0.80, stage=stage
                                    , my_raise=my_raise, opponent_raise=opponent_raise)
    else:  # stage == 5
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.65, call_rate=0.85, stage=stage
                                    , my_raise=my_raise, opponent_raise=opponent_raise)


def poker_threshold_aggressive_decision(observation):
    """
    期望的观测是json形式的, 见General Poker Game的empty observation
    :param observation:
    :return: 数字，0-2分别代表'f', 'c', 'r'
    """
    if not observation['cards'] or not observation['actions']:
        return None
    public_card = observation['cards']['flop_card'] + \
                  observation['cards']['turn_card'] + observation['cards']['river_card']
    stage = (len(public_card) // 2)
    win_rate = __poker_win_rate(public_card, observation['cards']['hand_card'], stage)

    my_raise = observation['details']['my_raise']
    opponent_raise = observation['details']['opponent_raise']

    if stage == 0:
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.3, call_rate=0.4, raise_rate=0.5, stage=stage
                                    , my_raise=my_raise, opponent_raise=opponent_raise)  # no all_in in deal
    elif stage == 3:
        # 取消Raise的bluff    不敢allin来bluff.... 效果极差
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.3, call_rate=0.50, raise_rate=0.5, stage=stage
                                    , my_raise=my_raise, opponent_raise=opponent_raise)
    elif stage == 4:
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.35, call_rate=0.55, stage=stage, raise_rate=0.55
                                    , my_raise=my_raise, opponent_raise=opponent_raise)
    else:  # stage == 5
        return __threshold_decision(win_rate=win_rate, attempt_rate=0.30, call_rate=0.30, stage=stage, raise_rate=0.40
                                    , my_raise=my_raise, opponent_raise=opponent_raise)


def __threshold_decision(win_rate, attempt_rate, stage, call_rate, my_raise, opponent_raise
                         , bluff_rate=0, raise_rate=0.9):
    """
    根据阈值做决策
    :param win_rate:
    :param bluff_rate:  使用Bluff的阈值
    :param attempt_rate:  没人激进可以尝试一下
    :param stage:   要是我没花钱就不尝试了，针对DEAL阶段
    :param call_rate:
    :param raise_rate:
    :param opponent_raise:  对手raise的次数
    :param my_raise:  赢面比较大就Raise吧
    :return:
    """
    if win_rate > raise_rate:
        return 'r'
    elif win_rate > call_rate:
        return 'c'
    elif opponent_raise == 0 and win_rate > attempt_rate and stage == 0:
        return 'c'
    # 保证可读性不做修改,bluff
    elif opponent_raise == 0 and my_raise == 0 and win_rate > bluff_rate > 0:
        return 'r'
    else:
        return 'f'


def __poker_win_rate(public_card, private_card, stage):
    global PREFLOP_DICT
    if stage == 5:
        win_rate = PC.estimate_river(public_card, private_card, 5)
    elif stage == 4:
        win_rate = PC.estimate_turn(public_card, private_card, 4)
    elif stage == 3:
        win_rate = PC.estimate_flop(public_card, private_card, 3)
    elif stage == 0:
        if not PREFLOP_DICT:
            with open("ColosGame/PokerUtils/preflop.json", 'r') as loaded_f:
                PREFLOP_DICT = json.load(loaded_f)
        win_rate = PREFLOP_DICT[private_card.upper()]
    else:
        return None
    return win_rate
