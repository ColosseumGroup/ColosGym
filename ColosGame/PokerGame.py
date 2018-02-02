from ColosGame.BaseGame import ColosGame
import numpy as np
try:
    import GameSolver
except ImportError as e:
    print(e)


class LimitedPokerGame(ColosGame):
    """
    状态：大小为（玩家数×回合数×最大加注数）+ （回合数×rank×花色数）前者为动作状态，后者为牌面信息
    动作状态为当前状态的OneHot
    牌面状态为每个回合新可见的几张牌的在0-1向量中的表示，1表示牌值为该牌的牌存在
    状态大小跟据游戏的不同而不同，当前回合结束时返回全零，异常返回None
    """

    def __init__(self, num_players, num_rounds,
                 num_suits, num_ranks, num_hole_cards, num_raise_times, num_boardcards, game_path):
        self.params['numPlayers'] = num_players
        self.params['numRounds'] = num_rounds
        self.params['numSuits'] = num_suits
        self.params['numRanks'] = num_ranks
        self.params['numHoleCards'] = num_hole_cards
        self.params['maxRaiseTimes'] = num_raise_times
        self.params['numBoardCards'] = num_boardcards
        self.params['gamePath'] = game_path
        self.params['actions'] = ['f', 'c', 'r']
        GameSolver.initGame(game_path)  # 必须初始化！

    def set_from_config(self, game_path):
        pass

    def get_observe(self, msg):
        """
        提供游戏状态array
        :param msg:输入Dealer传入的消息
        :return:返回游戏的状态，包括动作和牌面信息
        """
        msg = msg.rstrip('\r\n')
        state_list = msg.split(":")
        # 这里用“：”分开后分别处理各个状态
        action_trace = state_list[3]  # eg rc/crrc/
        card = state_list[4]  # eg |2c3d/5d6hTc/6d
        player_num = int(state_list[1])
        card_mtx = self.__get_card_matrix(card)
        action_mtx = self.__get_action_state_matrix(action_trace=action_trace, player_num=player_num)
        # 合并牌面和动作记录
        observe = np.append(action_mtx.flatten(), card_mtx.flatten())
        return observe

    def get_empty_observe(self):
        """
        创造空观察，保持类型一致性
        :return: 返回空观察
        """
        return np.zeros(shape=(self.params['numPlayers'] * self.params['numRounds'] * self.params['maxRaiseTimes']
                               + self.params['numRounds'] * self.params['numSuits'] * self.params['numRanks']))

    def get_reward(self, msg, episode, player_index):
        """
        利用GameSolver完成从msg获得Reward的工作
        :param msg: 完整消息
        :param episode: 当前的局数
        :param player_index: 玩家的位置
        :return: reward，double
        """
        return GameSolver.getReward(msg, episode, player_index, 0)

    def is_current_player(self, msg):
        """
        看当前玩家的状态
        :param msg: dealer提供的消息
        :return:error=-4, finish==3, act==2, not acting==-2
        """
        return GameSolver.ifCurrentPlayer(msg)

    def get_episode(self, msg):
        """
        解析当前局数
        :param msg:
        :return: 对局次数
        """
        return int(msg.split(':')[2])

    def __calculate_card_value(self, card):
        """
        这里计算牌在牌向量的index,改动说明：牌面由原来的从小到大，改为从大到小，即K对应2，2对应13
        :param card: 一张牌的字符串，Example:"9h"
        :return: 返回牌的index，计算方法：牌面值+
        """
        if card is "":
            return 0
        # 声明所有牌的List,但跟据游戏的类型选择
        card_num = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        num4card = [n for n in range(0, self.params['numRanks'])]
        card_dict = dict(zip(card_num, num4card))

        suit = ['h', 's', 'd', 'c']  # 同上声明所有，使用部分
        num4suit = [n for n in range(0, self.params['numSuits'])]
        suit_dict = dict(zip(suit, num4suit))
        return card_dict[card[0]] + suit_dict[card[1]] * self.params['numRanks'] + 1

    def __cards_to_card_vector(self, card):
        """
        把牌的字符串转化为向量，字符串的每一张牌与向量内的index相对应，可有多个
        :param card: 牌的名字，EXAMPLE：“5d6hTc”
        :return: 返回一个回合的牌面信息向量

        """
        card_vector = np.zeros(shape=(self.params['numSuits'] * self.params['numRanks']))
        i = 0
        while i < (len(card) - 1):
            temp = ''
            temp += card[i]
            i += 1
            temp += card[i]
            i += 1
            # 此处对card的值减1是为了和Index对应，使用旧代码有点不一样
            card_vector[self.__calculate_card_value(card=temp) - 1] = 1
        return card_vector

    def __get_card_matrix(self, state_list_card):
        """
        获得牌面信息的Matrix
        :param state_list_card:仅接收非终结状态的消息，Example：|2c3d/5d6hTc/6d
        :return: 牌面信息matrix，shape：回合数×牌的种类，每一行为当前回合新看到的一个牌
        """
        card_matrix = np.zeros(shape=(self.params['numRounds'], self.params['numSuits'] * self.params['numRanks']))
        deck_cards = state_list_card.split("/")  # 不同回合亮的牌会用“/”分割
        # 不同玩家的牌会用“|”分割，但是这里为非终结态，只有自己的牌，直接删去即可
        deck_cards[0] = deck_cards[0].replace('|', '')
        i = 0
        for cards in deck_cards:  # deck_cards 为一个数组，Example: ['2c3d','5d6hTc','6d']
            card_matrix[i, :] = self.__cards_to_card_vector(card=cards)
            i += 1
        return card_matrix

    def __get_action_state_matrix(self, action_trace, player_num):
        """
        获得动作状态的matrix
        :param action_trace: 动作的描述，是一个字符串，example：rc/crrc/
        :param player_num:  现在玩家的号码，int ， 从0开始index
        :return:一个多维数组，大小为玩家数量×回合数×最大加注次数,在相应的状态置唯一一个1（OneHot）
        """
        action_list = action_trace.split('/')
        action_matrix = np.zeros(shape=(self.params['numPlayers'], self.params['numRounds'],
                                        self.params['maxRaiseTimes']))  # be safe
        rounds = len(action_list) - 1  # 因为数组从0开始index
        current_action = action_list.pop()
        raise_size = 0
        # 计算加注次数
        for action in current_action:
            if action == 'r':
                raise_size += 1
        # 解析动作完成，记录当前状态
        action_matrix[player_num, rounds, raise_size - 1] = 1
        return action_matrix
