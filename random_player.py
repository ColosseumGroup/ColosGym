import random
from client import Client


def poker_decision(observation):
    """
    有限注扑克随机决策
    :param observation: 见 ColosGame/PokerGame
    :return: 数字，0-2分别代表'f', 'c', 'r'
    """
    return random.randint(0, 2)


def renju_decision(observation):
    """
    五子棋随机决策
    :param observation: 棋盘矩阵
    :return: 下子位置决策x/y
    """
    # In renju confict action will lead to fold
    while True:
        X = random.randint(0, 14)
        Y = random.randint(0, 14)
        if observation[X, Y] != 0:
            continue
        return "%d/%d" % (X, Y)


def main():

    game_type = 'holdem.limit.2p.reverse_blinds'
    ip = '139.224.114.52'
    port0 = 44203
    port1 = 37390

    if game_type == 'renju':
        client0 = Client(
            game=game_type, decision_func=renju_decision,
            player_index=0, ip=ip, port=port0
        )
        client1 = Client(
            game=game_type, decision_func=renju_decision,
            player_index=1, ip=ip, port=port1
        )
    elif game_type == 'holdem.limit.2p.reverse_blinds':
        client0 = Client(
            game=game_type, decision_func=poker_decision,
            player_index=0, ip=ip, port=port0
        )
        client1 = Client(
            game=game_type, decision_func=poker_decision,
            player_index=1, ip=ip, port=port1
        )
    elif game_type == 'LimitLeduc':
        client0 = Client(
            game=game_type, decision_func=poker_decision,
            player_index=0, ip=ip, port=port0
        )
        client1 = Client(
            game=game_type, decision_func=poker_decision,
            player_index=1, ip=ip, port=port1
        )
    else:
        pass

    client0.start()
    client1.start()


if __name__ == '__main__':
    main()