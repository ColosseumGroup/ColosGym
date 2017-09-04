import player
import random
import sys
import time

def main():
    port = 18791
    playerName = 'Alice'
    #port = int(sys.argv[1])
    #seatNum = int(sys.argv[2])
    #playerName = sys.argv[3]
    logpath = '/home/goodman/POKER/project_acpc_server_v1.0.41/project_acpc_server/matchtry.log'
    p1 = player.Player(playerName,port,logpath)
    f = open('log.txt','w')
    Total_reward = 0.0
    error = 0
    episode = 0

    msgQueue = []
    # 不断接受dealer的信息，判别是不是自己的动作时机，如果是自己的动作时机就生成动作
    # 这里不考虑动作是否合法
    while episode<1001:
        msgQueue = p1.recvMsg()
        for m in msgQueue:
            msg = m
            flag = p1.handleMsg(msg)
            if flag == 0:#act
                action = random.randint(0, 2)
                p1.step(msg, action)
                continue
            if flag ==9999999:#clusy way of show flag
                continue
            if flag ==999999:
                f.write(m)
                continue
            Total_reward += flag

        print('now:',Total_reward)

if __name__ == '__main__':
    main()