import player
import random
import sys
import time
import threading

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
        #如果先开一局，对方先发牌且对方马上弃牌，就会导致reset后马上结束
        
        if obser == None:
            break
        while True:
            action = random.randint(0,2)
            obser_,reward,done = player.step(action)
            if done:
                Total_reward += reward
                episode += 1
                break

        print("player:",player.playerName,'now:',Total_reward,"episode:",episode)
def main():
    test = True
    if test:
        port = 18374
        logpath = "/home/goodman/POKER/project_acpc_server_v1.0.41/project_acpc_server/match1.log"
        playerName = "Bob"
    else:    
        port = int(sys.argv[1])
        logpath = sys.argv[2]
        playerName = sys.argv[3]

    ply = player.Player(playerName,port,logpath)

    port2 = 18791
    playerName2 = "Alice"
    ply2 = player.Player(playerName2,port2,logpath)
    t1 = threading.Thread(target=game4palyer,args=(ply,))
    t2 = threading.Thread(target=game4palyer,args=(ply2,))
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()
