class ColosGame(object):
    """
    所有游戏的基类，设置了一系列游戏API必须实现的方法
    """
    params = {}

    def get_params(self):
        if self.params is None:
            raise AssertionError('Game Must be initialized!')
        else:
            return self.params

    def get_observe(self, msg):
        raise NotImplementedError('必须实现getObser方法！')

    def get_empty_observe(self):
        raise NotImplementedError('必须实现获得空观察的方法')

    def make_action_message(self, msg, action):
        raise NotImplementedError("Action message must be implemented based on protocol")
        
    def get_reward(self, msg, episode, player_index):
        raise NotImplementedError('必须实现getReward方法！')

    def get_episode(self, msg):
        raise NotImplementedError("必须解析当前游戏局数！")

    def is_current_player(self, msg):
        raise NotImplementedError('必须对当前玩家的判断！')
