from Actor.player import Player
from ColosGame.PokerGame import LimitedPokerGame
import random
import sys
import time

Game = LimitedPokerGame(num_players=3, num_rounds=2, num_suits=2, num_ranks=3, num_hole_cards=1,
                         num_raise_times=2, num_boardcards=1, game_path="/home/xzp/PycharmProjects/AlgScript_poker/LimitLeduc.game")
def main():
    test = True
    if test:
        port = 35654
        logpath = "/home/xzp/project_acpc_server/mm1.log"
        playerName = "Bob"
    else:    
        port = int(sys.argv[1])
        logpath = sys.argv[2]
        playerName = sys.argv[3]

    ply = Player(game=Game, player_index=1,port=port)
    Total_reward = 0.0
    episode = 0

    while True:
        obser,reward,done = ply.reset()
        if done:
            Total_reward += reward
            episode += 1
            continue
        #如果先开一局，对方先发牌且对方马上弃牌，就会导致reset后马上结束
        
        if obser is None:
            break
        while True:
            action = random.randint(0,2)
            print("h4")
            obser_,reward,done = ply.step(action)
            print(len(obser_))
            if done:
                Total_reward += reward
                episode += 1
                break

        print('now:',Total_reward,"episode:",episode)

if __name__ == '__main__':
    main()
