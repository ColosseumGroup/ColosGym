import numpy as np
from ColosGame.BaseGame import ColosGame


class Renju(ColosGame):
    """
    五子棋游戏，游戏规则比较单一，不需要进行特例话
    message描述：MATCHSTATE:viewingplayer:currentplayer:currentGames:currentRounds:finishedFlag:col/row
    """
    BOARD_SIZE = 15

    def __init__(self):
        """
        初始化创建空棋盘
        """
        self.board = np.zeros(shape=(Renju.BOARD_SIZE, Renju.BOARD_SIZE))

    def resset_board(self):
        self.board = np.zeros(shape=(Renju.BOARD_SIZE, Renju.BOARD_SIZE))

    def get_episode(self, msg):
        msg_list = msg.split(":")
        return int(msg_list[3])

    def get_empty_observe(self):
        return np.zeros(shape=(Renju.BOARD_SIZE, Renju.BOARD_SIZE))

    def get_reward(self, msg, episode, player_index):
        """
        有结果就返回
        :param msg: 完整消息
        :param episode:  此处无用
        :param player_index:  此处无用
        :return: 成功者获得1，失败者获得0
        """
        msg_list = msg.split(":")
        viewing_player = int(msg_list[1])
        finished_flag = int(msg_list[4])
        # 发送给的编号与完成编号不一致则是失败方，反之为成功方
        if viewing_player is finished_flag:
            return 1
        else:
            return 0

    def get_observe(self, msg):
        """
        直接返回内部的棋盘
        :param msg:
        :return:棋盘
        """
        return self.board

    def is_current_player(self, msg):
        """
        看当前玩家的状态
        :param msg: dealer提供的消息
        :return: finish==3, act==2, not acting==-2
        """
        msg_list = msg.split(":")
        viewing_player = int(msg_list[1])
        current_player = int(msg_list[2])
        finished_flag = int(msg_list[4])
        if msg_list[6] is not '':
            coordinate = msg_list[6].split('/')
            # 对每个有动作消息加一个点
            self.__add_piece(int(coordinate[0]), int(coordinate[1]), current_player)
        if finished_flag is not 0:
            self.resset_board()
            return 3
        elif viewing_player is not current_player:
            return -2
        else:
            return 2

    def __add_piece(self, col, row, current_player):
        """
        增加一个棋子
        :param col: 棋子Col坐标
        :param row: Row坐标
        :return:
        """
        self.board[col, row] = current_player
