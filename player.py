import socket
import GameSolver
import threading
import time
import numpy as np


class PokerGame(object):
    """
    这个类用来保存游戏信息，在下面声明全局变量以调用
    """

    def __init__(self,numPlayers, numRounds,
                 numSuits, numRanks, numHoleCards, numRaiseTimes, numBoardCards, gamePath):
        self.numPlayers = numPlayers
        self.numRounds = numRounds
        self.numSuits = numSuits
        self.numRanks = numRanks
        self.numHoleCards = numHoleCards
        self.maxRaiseTimes = numRaiseTimes
        self.numBoardCards = numBoardCards
        self.gamePath = gamePath


LeducPlayer3 = PokerGame(numPlayers=3, numRounds=2, numSuits=2, numRanks=3, numHoleCards=1,
                         numRaiseTimes=2, numBoardCards=1,
                         gamePath="/home/xzp/PycharmProjects/AlgScript_poker/LimitLeduc.game")
GAME = LeducPlayer3


class Player(object):
    """
    这里说明Player的状态表示方法
    状态：大小为（玩家数×回合数×最大加注数）+ （回合数×rank×花色数）前者为动作状态，后者为牌面信息
    动作状态为当前状态的OneHot
    牌面状态为每个回合新可见的几张牌的在0-1向量中的表示，1表示牌值为该牌的牌存在
    状态大小跟据游戏的不同而不同，当前回合结束时返回全零，异常返回None
    """
    ACTION_LIST = ['f', 'c', 'r']
    BUFFERSIZE = 256

    def __init__(self, playerName, port, logPath, ip='localhost'):
        """
        初始化玩家类，在这里Player主要还是完成链接dealer 和 发送动作，接受信息的工作
        :param playerName: 玩家的名字，Example:'Alice'
        :param port: 端口
        :param logPath: 由Dealer写的Log的文档，后期会删除
        :param ip: IP地址，默认值为’localhost‘
        """
        # 下面几个变量是应该要去除的变量
        self.result = open(logPath, 'r')
        self.log = open('log.txt', 'w')
        self.playerName = playerName

        self.lastMsg = ''
        self.currentMsg = ''
        self.state = None
        self.state_ = None
        self.resetable = True
        self.finish = True
        self.exit = False
        self.connectToServer(port=port, ip=ip)
        self.msgQueue = []
        self.lock = threading.Lock()
        t = threading.Thread(target=self.recvMsg)
        t.start()
        GameSolver.initGame(GAME.gamePath)  # 必须初始化！

    def connectToServer(self, port, ip):
        """
        做了一些和Dealer的socket链接的工作
        :param port: 端口数值
        :param ip: ip字符串
        :return:
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.send(b'VERSION:2.0.0\n')

    def reset(self):
        """
        这个只是为了与Gym更相似而设值的
        :return: 在可reset的时候返回状态，回报，结束flag，不可reset时调用会返回三个None
        """
        if self.resetable == False:
            print("wrong timing to reset")
            return None, None, None
        else:
            self.resetable = False
            try:
                o, r, d = self.innerMsgloop()
                return o, r, d
            except Exception as e:
                print("error when reset:")
                print(e)
                return None, None, None

    def recvMsg(self):
        """
        处理socket的接收工作，接收了以后就存放在队列中，等待agent调用时才处理
        原则上是一个监听端口的死循环，由于socket的阻塞，所以性能并不会有问题
        正常来说这个死循环结束则dealer也结束了
        :return:
        """
        while True:
            socketInfo = self.socket.recv(Player.BUFFERSIZE).decode('ascii')
            if not socketInfo:
                break
            socketInfo = socketInfo.split('MATCHSTATE')  # 由于时间不统一，可能一次收到多条msg

            self.lock.acquire()
            try:
                for msg in socketInfo:
                    if msg == '':
                        continue
                    self.msgQueue.append("MATCHSTATE" + msg)
            finally:
                self.lock.release()
        time.sleep(1)  # 退出循环则游戏已经关闭
        print("Ready to exit")
        self.exit = True
        self.resetable = False
        self.socket.close()

    def step(self, action):
        """
        执行动作
        :param action: 接收一个数字，代表动作，动作的定义在类内静态的ACTION_LIST
        :return: 返回值是innerloop的返回值，即观察，回报，完成flag
        """
        msg = self.currentMsg.rstrip('\r\n')
        act = '{}:{}\r\n'.format(msg, Player.ACTION_LIST[action])
        act = bytes(act, encoding='ascii')
        respon = self.socket.send(act)
        if respon == len(act):
            return self.innerMsgloop()
        else:
            print("Error when sending action")
            return None

    def innerMsgloop(self):
        """
        内部的一个循环，处理类内保存的消息队列。
        做这个的原因是接收状态和算法Agent取状态的时间不一致
        将所有状态保存下来，当算法需要读出状态时再将所有的保存的状态处理
        :return: 返回三个值：观察（具体见类的说明），回报（double)，完成flag（1为完成）
        """
        # 循环直至可返回结果
        while True:
            if len(self.msgQueue) == 0:
                if self.exit == True:
                    return None, None, None
                else:
                    time.sleep(0.000001)
                    continue
            self.lock.acquire()
            try:
                msg = self.msgQueue.pop(0)
            finally:
                self.lock.release()

            flag = self.handleMsg(msg)
            if flag == 2:  # act
                obser = _getObser(msg)
                reward = 0
                done = 0
                self.currentMsg = msg
                break
            if flag == -2:  # not acting
                self.lastMsg = msg
                continue
            if flag == 3:
                obser = np.zeros(shape=(GAME.numPlayers * GAME.numRounds * GAME.maxRaiseTimes +
                                 GAME.numRounds * GAME.numSuits * GAME.numRanks))
                episode = int(msg.split(':')[2])
                reward = self._getReward(episode=episode)
                done = 1
                self.resetable = True  # allow a reset() call
                self.lastMsg = msg
                self.log.writelines(msg)
                break

        return obser, reward, done

    def _getReward(self, episode):
        """
        跟据消息返回回报
        :param episode: 当前的局数
        :return: reward，double
        """
        # TODO 取消使用读取log获得回报的方法，直接从message获取
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
        """
        处理消息，看消息代表的状态，以在后面决定消息的处理方法
        :param msg: 消息字符串
        :return: 状态的flag ： error=-4, finish==3, act==2, not acting==-2
        """
        state = GameSolver.ifCurrentPlayer(msg)
        if state == -4.0:
            print("read state error")
            state = 3.0  # 根据log的规律。。。。具体我再看看
        return state


def calculateCardVal(card):
    """
    这里计算牌在牌向量的index,改动说明：牌面由原来的从小到大，改为从大到小，即K对应2，2对应13
    :param card: 一张牌的字符串，Example:"9h"
    :return: 返回牌的index，计算方法：牌面值+
    """
    if card is "":
        return 0
    # 声明所有牌的List,但跟据游戏的类型选择
    card_num = ['A', 'K', 'Q', 'J', 'T', '9', '8'
        , '7', '6', '5', '4', '3', '2']
    num4card = [n for n in range(0, GAME.numRanks)]
    card_dict = dict(zip(card_num, num4card))

    suit = ['h', 's', 'd', 'c']  # 同上声明所有，使用部分
    num4suit = [n for n in range(0, GAME.numSuits)]
    suit_dict = dict(zip(suit, num4suit))

    return card_dict[card[0]] + suit_dict[card[1]] * GAME.numRanks + 1


def cards2cardVector(card):
    """
    把牌的字符串转化为向量，字符串的每一张牌与向量内的index相对应，可有多个
    :param card: 牌的名字，EXAMPLE：“5d6hTc”
    :return: 返回一个回合的牌面信息向量

    """
    cardVector = np.zeros(shape=(GAME.numSuits * GAME.numRanks))
    i = 0
    while i < (len(card) - 1):
        temp = ''
        temp += card[i]
        i += 1
        temp += card[i]
        i += 1
        # 此处对card的值减1是为了和Index对应，使用旧代码有点不一样
        cardVector[calculateCardVal(card=temp) - 1] = 1
    return cardVector


def getCardMtx(stateList_card):
    """
    获得牌面信息的Matrix
    :param stateList_card:仅接收非终结状态的消息，Example：|2c3d/5d6hTc/6d
    :return: 牌面信息matrix，shape：回合数×牌的种类，每一行为当前回合新看到的一个牌
    """
    cardMtx = np.zeros(shape=(GAME.numRounds, GAME.numSuits * GAME.numRanks))
    deck_cards = stateList_card.split("/")  # 不同回合亮的牌会用“/”分割
    # 不同玩家的牌会用“|”分割，但是这里为非终结态，只有自己的牌，直接删去即可
    deck_cards[0] = deck_cards[0].replace('|','')
    i = 0
    for cards in deck_cards:  # deck_cards 为一个数组，Example: ['2c3d','5d6hTc','6d']
        cardMtx[i, :] = cards2cardVector(card=cards)
        i += 1
    return cardMtx


def getActionStateMtx(action_trace, player_num):
    """
    获得动作状态的matrix
    :param action_trace: 动作的描述，是一个字符串，example：rc/crrc/
    :param player_num:  现在玩家的号码，int ， 从0开始index
    :return:一个多维数组，大小为玩家数量×回合数×最大加注次数,在相应的状态置唯一一个1（OneHot）
    """
    actionList = action_trace.split('/')
    actionMtx = np.zeros(shape=(GAME.numPlayers, GAME.numRounds, GAME.maxRaiseTimes))  # be safe
    rounds = len(actionList) - 1  # 因为数组从0开始index
    actionCurrent = actionList.pop()
    raise_size = 0
    # 计算加注次数
    for action in actionCurrent:
        if action == 'r':
            raise_size += 1
    # 解析动作完成，记录当前状态
    actionMtx[player_num, rounds, raise_size - 1] = 1
    return actionMtx


def _getObser(msg):
    """
    提供游戏状态array
    :param msg:输入Dealer传入的消息
    :return:返回游戏的状态，包括动作和牌面信息
    """
    msg = msg.rstrip('\r\n')
    statelist = msg.split(":")
    # 这里用“：”分开后分别处理各个状态
    action_trace = statelist[3]  # eg rc/crrc/
    card = statelist[4]  # eg |2c3d/5d6hTc/6d
    player_num = int(statelist[1])
    card_mtx = getCardMtx(stateList_card=card)
    action_mtx = getActionStateMtx(action_trace=action_trace, player_num=player_num)
    # 合并牌面和动作记录
    obser = np.append(action_mtx.flatten(), card_mtx.flatten())
    return obser
