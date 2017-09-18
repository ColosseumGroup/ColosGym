import socket
import GameSolver
import threading
import time
# 这里的Player主要还是完成链接dealer 和 发送动作，接受信息的工作


class Player(object):
    ACTION_LIST = ['f', 'c', 'r']
    BUFFERSIZE = 256

    def __init__(self, playerName, port, logPath, ip='localhost'):
        self.result = open(logPath, 'r')
        self.playerName = playerName
        self.lastMsg = ''
        self.currentMsg = ''
        self.state = None
        self.state_ = None
        self.resetable = True
        self.finish = True
        self.exit =False
        self.connectToServer(port, ip)
        self.msgQueue=[]
        self.lock = threading.Lock()
        t = threading.Thread(target=self.recvMsg)
        t.start()
        self.log = open('log.txt','w')
        

    def connectToServer(self, port, ip):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.send(b'VERSION:2.0.0\n')
    def reset(self):
        if self.resetable == False:
            print("wrong timing to reset")
            return None
        else:
            self.resetable = False
            o, r, d = self.innerMsgloop()
            return o ,r,d
    def recvMsg(self):
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
        print("Ready to exit")
        self.exit = True
        self.resetable = False
        self.socket.close()

    def step(self,action):
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
        while True:
            if len(self.msgQueue) ==0:
                if self.exit == True:
                    return None
                else:
                    time.sleep(0.000001)
                    continue
            self.lock.acquire()
            try:
                msg = self.msgQueue.pop(0)
            finally:
                self.lock.release()
                
            flag = self.handleMsg(msg)
            if flag == 2:#act
                obser = self._getObser(msg)
                reward = 0
                done = 0
                self.currentMsg = msg
                break
            if flag ==-2:#not acting
                self.lastMsg = msg
                continue
            if flag ==3:
                obser = [0,0,0,0,0,0,0]
                episode = int(msg.split(':')[2])
                reward = self._getReward(episode)
                done = 1
                self.resetable = True#allow a reset() call
                self.lastMsg = msg
                self.log.writelines(msg)
                break

        return obser,reward,done


    def _getReward(self, episode):
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
        state = GameSolver.ifCurrentPlayer(msg, self.lastMsg)
        # flag: error=-4, finish==3, act==2, not acting==-2
        if state == -4.0:
            print("read state error")
            state = 3.0  # 根据log的规律。。。。具体我再看看
        return state
    
    def _getObser(self, msg):
        msg = msg.rstrip('\r\n')
        statelist = msg.split(":")
        action_trace = statelist[3] #eg rc/crrc/
        card = statelist[4]#eg |2c3d/5d6hTc/6d
        cardVal = getCardValList(card)
        cardVal.append(getActionVal(action_trace))
        return cardVal
        
    def _getObser_not_using_any_more(self, msg):
        msg = msg.rstrip('\r\n')
        card_num = ['A', '2', '3', '4', '5', '6',
                    '7', '8', '9', 'T', 'J', 'Q', 'K']
        num = [n for n in range(0, 13)]
        card_dict = dict(zip(card_num, num))
        suit = ['s', 'h', 'd', 'c']
        suit_dict = dict(zip(suit, num))

        statelist = msg.split(":")
        cards = statelist[4]

        deck_cards = cards.split("/")
        hand_card = deck_cards.pop(0).split('|')

        cardsstate = []
        def std2cardList(cardset):
            for card in cardset:
                i = 0
                while i < (len(card) - 1):
                    temp = ''
                    temp += card[i]
                    i += 1
                    temp += card[i]
                    i += 1
                    cardsstate.append(temp)
        std2cardList(deck_cards)
        std2cardList(hand_card)
        cardsstate.sort(key=lambda x: 4 * card_dict[x[0]] + suit_dict[x[1]])
        return cardsstate
    
    
def getActionVal(statelist_action):
    #rc/rc/rc To rcrcrc
    action_dict = {'c':2,'r':1,'f':0}
    action_trace = statelist_action.split("/")
    action_ternary = ""
    for a in action_trace:
        action_ternary += a
    #rcrcrc To TernaryValue
    trace_list = list(action_ternary)
    ternary = 1
    result = 0
    while len(trace_list)!=0:
        result += action_dict[trace_list.pop()]*ternary
        ternary = ternary*3
    return result

def calculateCardVal(card):
    if card is "":
        return 0
    card_num = ['A', '2', '3', '4', '5', '6',
            '7', '8', '9', 'T', 'J', 'Q', 'K']
    num = [n for n in range(0, 13)]
    card_dict = dict(zip(card_num, num))
    suit = ['c', 'd', 's', 'h']
    suit_dict = dict(zip(suit, num))
    return card_dict[card[0]]+suit_dict[card[1]]*13 + 1

def cards2cardValList(card,cardsstate):
    i = 0
    while i < (len(card) - 1):
        temp = ''
        temp += card[i]
        i += 1
        temp += card[i]
        i += 1
        cardsstate.append(calculateCardVal(temp))
            
def getCardValList(statelist_card):
    deck_cards = statelist_card.split("/")
    hand_card = deck_cards.pop(0).split('|')
    hand_card.remove("")
    hand_card = hand_card[0]
    cardValList = []
    cards2cardValList(hand_card,cardValList)
    for cards in deck_cards:
        cards2cardValList(cards,cardValList)
    while len(cardValList)!=7:
        cardValList.append(0)
    return cardValList