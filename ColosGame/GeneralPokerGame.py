from ColosGame.BaseGame import ColosGame
try:
    import GameSolver
except ImportError as e:
    print(e)


class GeneralPokerGame(ColosGame):
    """
    这个类型提供了基本的扑克游戏,利用Json传递状态
    """
    def __init__(self, num_players, num_rounds,
                 num_suits, num_ranks, num_hole_cards,
                 num_raise_times, num_boardcards, game_path, possible_action=('f', 'c', 'r')):
        self.params['numPlayers'] = num_players
        self.params['numRounds'] = num_rounds
        self.params['numSuits'] = num_suits
        self.params['numRanks'] = num_ranks
        self.params['numHoleCards'] = num_hole_cards
        self.params['maxRaiseTimes'] = num_raise_times
        self.params['numBoardCards'] = num_boardcards
        self.params['gamePath'] = game_path
        self.params['actions'] = possible_action
        self.current_round = dict()
        self.__clean_round_information()
        GameSolver.initGame(game_path)  # 必须初始化！

    def set_from_config(self, game_path):
        pass

    def get_observe(self, msg):
        """
        从字符串转换为观察
        :param msg:输入Dealer传入的消息
        :return:返回游戏的状态，包括动作和牌面信息Json
        """
        msg = msg.rstrip('\r\n')
        state_list = msg.split(":")
        # 这里用“：”分开后分别处理各个状态
        action_trace = state_list[3]  # eg rc/crrc/
        card = state_list[4]  # eg |2c3d/5d6hTc/6d

        total_raise = action_trace.count('r')
        total_call = action_trace.count('c')
        self.current_round['opponent_raise'] = total_raise - self.current_round['my_raise']
        self.current_round['opponent_call'] = total_call - self.current_round['my_call']

        action_dict = {'action_trace': action_trace}
        observe = {'cards': self.__get_card_dict(card),
                   'actions': action_dict,
                   'details': self.current_round}
        return observe

    def get_empty_observe(self):
        return {'cards': {'hand_card': '', 'flop_card': '', 'turn_card': '', 'river_card': ''},
                'actions': '',
                'details': ''}

    def get_reward(self, msg, episode, player_index):
        """
        利用GameSolver完成从msg获得Reward的工作
        :param msg: 完整消息
        :param episode: 当前的局数
        :param player_index: 玩家的位置
        :return: reward，double
        """
        self.__clean_round_information()
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

    def make_action_message(self, msg, action):
        """
        concate the action message at the back of the line
        :param msg: message without /r/n at its back
        :param action: index of the action type 0==fold 1==call 2==raise
        :return: message
        """
        if isinstance(action, int):
            action = self.params['actions'][action]
        if action == 'r':
            self.current_round['my_raise'] += 1
        elif action == 'c':
            self.current_round['my_call'] += 1
        return '{}:{}\r\n'.format(msg, action)

    @staticmethod
    def __get_card_dict(card_str: str):
        """
        将牌面字符串转化为字典
        :param card_str: eg. |2c3d/5d6hTc/6d
        :return: 字典
        """
        card_dict = {'hand_card': '',
                     'flop_card': '',
                     'turn_card': '',
                     'river_card': ''}
        card_list = card_str.replace('|', '').split('/')
        card_dict['hand_card'] = card_list[0]
        if len(card_list) > 1:
            card_dict['flop_card'] = card_list[1]
        if len(card_list) > 2:
            card_dict['turn_card'] = card_list[2]
        if len(card_list) > 3:
            card_dict['river_card'] = card_list[3]

        return card_dict

    def __clean_round_information(self):
        """
        清空当前回合保存的信息
        :return:
        """
        self.current_round['my_raise'] = 0
        self.current_round['my_call'] = 0
        self.current_round['opponent_raise'] = 0
        self.current_round['opponent_call'] = 0
