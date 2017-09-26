import player
import random
import sys
import time

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
    f = open('log.txt','w')
    Total_reward = 0.0
    error = 0
    episode = 0

    while True:
        obser,reward,done = ply.reset()
        if done:
            Total_reward += reward
            episode += 1
            continue
        #如果先开一局，对方先发牌且对方马上弃牌，就会导致reset后马上结束
        
        if obser == None:
            break
        while True:
            action = random.randint(0,2)
            obser_,reward,done = ply.step(action)
            print(len(obser_))
            if done:
                Total_reward += reward
                episode += 1
                break

        print('now:',Total_reward,"episode:",episode)

if __name__ == '__main__':
    main()
