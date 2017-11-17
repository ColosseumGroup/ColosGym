import player
import random
import sys
import time
import threading

# 更新后的用法，大体相同，在player初始化的时候，加入游戏类别参数即可

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

    logpath = "/home/xzp/project_acpc_server/mm1.log"

    port = 45112
    playerName = "Alice"
    ply = player.Player(playerName=playerName,port=port,logPath=logpath)

    port2 = 32952
    playerName2 = "Bob"
    ply2 = player.Player(playerName=playerName2,port=port2,logPath=logpath)

    port3 = 42596
    playerName3 = "James"
    ply3 = player.Player(playerName=playerName3, port=port3, logPath=logpath)

    t1 = threading.Thread(target=game4palyer,args=(ply,))
    t2 = threading.Thread(target=game4palyer,args=(ply2,))
    t3 = threading.Thread(target=game4palyer,args=(ply3,))
    t1.start()
    t2.start()
    t3.start()

if __name__ == '__main__':
    main()
