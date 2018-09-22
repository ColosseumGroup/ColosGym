from Actor.player import Player
from ColosGame.PokerGame import LimitedPokerGame
import random
import sys
import time
import threading

# 更新后的用法，大体相同，在player初始化的时候，加入游戏类别参数即可
Game = LimitedPokerGame(num_players=3, num_rounds=2, num_suits=2, num_ranks=3, num_hole_cards=1,
                         num_raise_times=2, num_boardcards=1, game_path="/home/xzp/PycharmProjects/AlgScript_poker/LimitLeduc.game")
def game4palyer(player):
    Total_reward = 0.0
    error = 0
    episode = 0
    while True:
        obser,reward,done = player.reset()
        if done:
            Total_reward += reward
            episode += 1
            continue
        # 如果先开一局，对方先发牌且对方马上弃牌，就会导致reset后马上结束
        
        if obser is None:
            break
        while True:
            action = random.randint(0,2)
            action = 2
            obser_,reward,done = player.step(action)

            if done:
                Total_reward += reward
                episode += 1
                break

        print("player:",player.playerName,'now:',Total_reward,"episode:",episode)
def main():
    test = True
    if test:
        pass
    else:    
        port = int(sys.argv[1])
        logpath = sys.argv[2]
        playerName = sys.argv[3]

    port = 42653
    ply = Player(game=Game, player_index=0,port=port)

    port2 = 42947
    ply2 = Player(game=Game, player_index=1,port=port2)

    port3 = 33999
    ply3 = Player(game=Game, player_index=2, port=port3)

    t1 = threading.Thread(target=game4palyer,args=(ply,))
    t2 = threading.Thread(target=game4palyer,args=(ply2,))
    t3 = threading.Thread(target=game4palyer,args=(ply3,))
    t1.start()
    t2.start()
    t3.start()

if __name__ == '__main__':
    main()
