import socket
import threading
import queue

class Player(object):
    """
    Player类完成与Dealer的交互工作，状态，奖励等信息取决于输入的游戏
    值得注意的是，交互的信息头必须是MATCHSTATE
    """

    def __init__(self, port, game, player_index, ip='localhost', player_name='www', buffersize=1024, get_timeout=10):
        """
        初始化玩家类，在这里Player主要还是完成链接dealer 和 发送动作，接受信息的工作
        :param port: 端口
        :param ip: IP地址，默认值为’localhost‘
        :param player_index: 玩家的位置
        :param game: 游戏定义
        :param player_name: 玩家的名字，非必须，Example:'Alice'，默认值为www+playerNum
        :param buffersize: 接收字串的buffer大小，默认为1024
        :param get_timeout: 读取状态超时
        """
        # 下面几个变量是应该要去除的变量
        self.GameParams = game.get_params()
        if player_name is 'www':
            self.playerName = player_name + str(player_index)
        else:
            self.playerName = player_name
        self.PlayerIndex = player_index
        self.BUFFER_SIZE = buffersize
        self.Game = game
        self.lastMsg = ''
        self.currentMsg = ''
        self.state = None
        self.state_ = None
        self.resetable = True
        self.finish = True
        self.exit = False
        self.timeout = get_timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server(port=port, ip=ip)
        self.msgQueue = queue.Queue()
        t = threading.Thread(target=self.receive_message)
        t.start()

    def connect_to_server(self, port, ip):
        """
        做了一些和Dealer的socket链接的工作
        :param port: 端口数值
        :param ip: ip字符串
        :return:
        """
        self.socket.connect((ip, port))
        self.socket.send(b'VERSION:2.0.0\n')

    def reset(self):
        """
        这个只是为了与Gym更相似而设值的。
        由于是多人游戏，如果在不可reset的时候，reset,在后面会考虑放弃类操作
        :return: 在可reset的时候返回状态，回报，结束flag，不可reset时调用会返回三个None
        """
        if not self.resetable:
            print("wrong timing to reset")
            return None, None, None
        else:
            self.resetable = False
            try:
                o, r, d = self.inner_message_loop()
                return o, r, d
            except Exception as e:
                print("error when reset:")
                print(e)
                return None, None, None

    def receive_message(self):
        """
        处理socket的接收工作，接收了以后就存放在队列中，等待agent调用时才处理
        原则上是一个监听端口的死循环，由于socket的阻塞，所以性能并不会有问题
        正常来说这个死循环结束则dealer也结束了
        :return:
        """
        while True:
            socket_info = self.socket.recv(self.BUFFER_SIZE).decode('ascii')
            if not socket_info:
                break
            socket_info = socket_info.split('MATCHSTATE')  # 由于时间不统一，可能一次收到多条msg

            for msg in socket_info:
                if msg == '':
                    continue
                self.msgQueue.put("MATCHSTATE" + msg)
                
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
        act = self.Game.make_action_message(msg,action)
        act = bytes(act, encoding='ascii')
        respon = self.socket.send(act)
        if respon == len(act):
            return self.inner_message_loop()
        else:
            print("Error when sending action")
            return None

    def inner_message_loop(self):
        """
        内部的一个循环，处理类内保存的消息队列。
        做这个的原因是接收状态和算法Agent取状态的时间不一致
        将所有状态保存下来，当算法需要读出状态时再将所有的保存的状态处理
        :return: 返回三个值：观察（具体见类的说明），回报（double)，完成flag（1为完成）
        """
        # 循环直至可返回结果
        while True:

            if self.exit:
                return None, None, None

            msg = self.msgQueue.get(timeout=self.timeout)

            flag = self.handle_message(msg)
            if flag == 2:  # act
                observe = self.Game.get_observe(msg)
                reward = 0
                done = 0
                self.currentMsg = msg
                self.msgQueue.task_done()
                break
            elif flag == -2:  # not acting
                self.lastMsg = msg
                self.msgQueue.task_done()
                continue
            elif flag == 3:
                observe = self.Game.get_empty_observe()
                episode = self.Game.get_episode(msg)
                reward = self.Game.get_reward(msg, episode, self.PlayerIndex)
                done = 1
                self.resetable = True  # allow a reset() call
                self.lastMsg = msg
                self.msgQueue.task_done()
                break
            else:
                self.msgQueue.task_done()
                raise ValueError('状态错误！')

        return observe, reward, done

    def handle_message(self, msg):
        """
        处理消息，看消息代表的状态，以在后面决定消息的处理方法
        :param msg: 消息字符串
        :return: 状态的flag ： error=-4, finish==3, act==2, not acting==-2
        """
        return self.Game.is_current_player(msg)
