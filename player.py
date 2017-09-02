import socket
import GameSolver
# 这里的Player主要还是完成链接dealer 和 发送动作，接受信息的工作


class Player(object):
    ACTION_LIST = ['f', 'c', 'r']
    BUFFERSIZE = 256

    def __init__(self, playerName, port, logPath, ip='localhost'):
        self.result = open(logPath, 'r')
        self.playerName = playerName
        self.lastMsg = ''
        self.state = None
        self.state_ = None
        self.reward = 0.0
        self.done = False
        self.connectToServer(port, ip)

    def connectToServer(self, port, ip):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.send(b'VERSION:2.0.0\n')

    def recvMsg(self):
        socketInfo = self.socket.recv(Player.BUFFERSIZE).decode('ascii')
        socketInfo = socketInfo.split('MATCHSTATE')  # 由于时间不统一，可能一次收到多条msg
        msgQueue = []
        for msg in socketInfo:
            if msg == '':
                continue
            msgQueue.append("MATCHSTATE" + msg)
        assert(len(msgQueue) > 0)
        return msgQueue

    def step(self, msg, action):
        msg = msg.rstrip('\r\n')
        act = '{}:{}\r\n'.format(msg, Player.ACTION_LIST[action])
        act = bytes(act, encoding='ascii')
        respon = self.socket.send(act)
        if respon == len(act):
            return 1
        else:
            return 0

    def getReward(self, episode):
        # 如果遇到了注释可跳过，一般这个循环不会执行两次。。
        while True:
            state_str = self.result.readline().rstrip('\n')
            state_list = state_str.split(":")
            if len(state_list) == 6:
                if episode == int(state_list[1]):
                    break
        reward_dict = dict(
            zip(state_list[5].split('|'), state_list[4].split('|')))
        reward = float(reward_dict[self.playerName])
        return reward

    def handleMsg(self, msg):
        episode = int(msg.split(':')[2])
        state = GameSolver.ifCurrentPlayer(msg, self.lastMsg)
        self.lastMsg = msg
        # flag == -4 error, ==3 finish, ==2 act, ==-2 not acting
        if state == -4.0:
            print("read state error")
            state = 3.0  # 根据log的规律。。。。具体我再看看
        if state == 2.0:
            return 0
        else:
            if state == 3:
                reward = self.getReward(episode)
                return reward
            else:
                if state == -2:
                    return 9999999
                else:
                    return 999999  # error

    def getCurrentState(self):
        pass

    def _decomposeMsg(self, msg):
        msg = msg.split(':')
        match_flag = msg[0]  # msg[0]总是MATCHSTATE
        current_player = int(msg[1])  # 当前玩家的编号
        episode = int(msg[2])  # 当前对局是第几局
        action_trace = msg[3]  # 当前对局所有的决策记录
        cards = msg[4]  # 所有牌面信息
        return current_player, episode, action_trace, cards

    def _msgToState(self, msg):
        return [], 0.0, [], False
