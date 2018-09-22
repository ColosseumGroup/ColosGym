from Actor.player import Player
from ColosGame.PokerGame import LimitedPokerGame
import random
import sys
import time
import threading
from ColosGame.z import get_holdem_limit_2p

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
            print('action:', action)
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

    port = 37369
    ply = Player(game=get_holdem_limit_2p(), player_index=0,ip='139.224.114.52',port=port)

    port2 = 33898
    ply2 = Player(game=get_holdem_limit_2p(), player_index=1,ip='139.224.114.52',port=port2)


    t1 = threading.Thread(target=game4palyer,args=(ply,))
    t2 = threading.Thread(target=game4palyer,args=(ply2,))
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()
