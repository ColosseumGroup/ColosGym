from Actor.player import Player
from ColosGame.RenjuGame import Renju
import random
import sys
import time
import threading

import numpy as np

# 更新后的用法，大体相同，在player初始化的时候，加入游戏类别参数即可
Game = Renju()

def pseudoDecision(Oberserve):
    import random
    #In renju confict action will lead to fold
    while True:
        X = random.randint(0,14)
        Y = random.randint(0,14)
        if Oberserve[X,Y]!=0:
            continue
        return "%d/%d"%(X,Y)

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
            action = pseudoDecision(obser)
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

    port = 46821
    ply = Player(game=Game, player_index=0,port=port)

    port2 = 38293
    ply2 = Player(game=Game, player_index=1,port=port2)

    t1 = threading.Thread(target=game4palyer,args=(ply,))
    t2 = threading.Thread(target=game4palyer,args=(ply2,))
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()
