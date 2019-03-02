import threading
from Actor.player import Player
from ColosGame.GameFactory import GameFactory


class Client(threading.Thread):

    def __init__(self, game: str, decision_func, ip: str, port: int, player_index: int):
        super().__init__()
        assert(callable(decision_func))
        self.decision_function = decision_func
        game_factory = GameFactory()
        self.player = Player(game=game_factory.getGame(game), player_index=player_index,
                            ip=ip, port=port)

    def run(self):
        Warning('建议修改Client代码以便模型训练的便利')
        Total_reward = 0.0
        episode = 0
        while True:
            obser, reward, done = self.player.reset()
            if done:
                Total_reward += reward
                episode += 1
                continue
            # 如果先开一局，对方先发牌且对方马上弃牌，就会导致reset后马上结束
            
            if obser is None:
                break
            while True:
                action = self.decision_function(obser)
                obser_, reward, done = self.player.step(action)

                if done:
                    Total_reward += reward
                    episode += 1
                    break

            print("player:", self.player.playerName, 'now:', Total_reward, "episode:", episode)
