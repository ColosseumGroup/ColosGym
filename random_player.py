from client import Client
from example_strategy import *


def main():

    game_type = 'holdem.limit.2p.reverse_blinds'
    ip = 'localhost'
    port0 = 43791
    port1 = 41291

    if game_type == 'renju':
        client0 = Client(
            game=game_type, decision_func=renju_random_decision,
            player_index=0, ip=ip, port=port0
        )
        client1 = Client(
            game=game_type, decision_func=renju_random_decision,
            player_index=1, ip=ip, port=port1
        )
    elif game_type == 'holdem.limit.2p.reverse_blinds':
        client0 = Client(
            game=game_type, decision_func=poker_threshold_cautious_decision,
            player_index=0, ip=ip, port=port0
        )
        client1 = Client(
            game=game_type, decision_func=poker_threshold_aggressive_decision,
            player_index=1, ip=ip, port=port1
        )
    elif game_type == 'LimitLeduc':
        client0 = Client(
            game=game_type, decision_func=poker_random_decision,
            player_index=0, ip=ip, port=port0
        )
        client1 = Client(
            game=game_type, decision_func=poker_random_decision,
            player_index=1, ip=ip, port=port1
        )
    else:
        pass

    client0.start()
    client1.start()


if __name__ == '__main__':
    main()
