
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