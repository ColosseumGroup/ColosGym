from ColosGame.GeneralPokerGame import GeneralPokerGame
from ColosGame.LimitedPokerGameMtx import LimitedPokerGameMtx
from ColosGame.RenjuGame import Renju


class GameFactory(object):
    """
    提供Game类Instance，注意路径的正确
    TODO：取消除了路径以外的参数，直接从文件读入
    """

    first_type = ''

    SUPPORTED_GAME = [
        'LimitLeduc_Mtx',
        'holdem.limit.2p.reverse_blinds_Mtx',
        'LimitLeduc',
        'holdem.limit.2p.reverse_blinds',
        'renju'
    ]

    def getGame(self, game:str):
        if GameFactory.first_type != game and GameFactory.first_type != '':
            raise ValueError("Different game in one client is no allowed!")
        else:
            GameFactory.first_type = game

        if game not in GameFactory.SUPPORTED_GAME:
            raise ValueError("%s is not supported yet." % game)

        if game == 'LimitLeduc_Mtx':
            return LimitedPokerGameMtx(num_players=3, num_rounds=2,
                            num_suits=2, num_ranks=3, num_hole_cards=1,
                            num_raise_times=2, num_boardcards=1,
                             game_path="ColosGame/PokerDefine/LimitLeduc.game")

        elif game == 'holdem.limit.2p.reverse_blind_Mtxs':
            return LimitedPokerGameMtx(num_players=2, num_rounds=4,
                            num_suits=4, num_ranks=13, num_hole_cards=2, 
                            num_raise_times=4, num_boardcards=5, 
                            game_path="ColosGame/PokerDefine/holdem.limit.2p.reverse_blinds.game")

        elif game == 'LimitLeduc':
            return LimitedPokerGameMtx(num_players=3, num_rounds=2,
                            num_suits=2, num_ranks=3, num_hole_cards=1,
                            num_raise_times=2, num_boardcards=1,
                             game_path="ColosGame/PokerDefine/LimitLeduc.game")

        elif game == 'holdem.limit.2p.reverse_blinds':
            return GeneralPokerGame(num_players=2, num_rounds=4,
                                       num_suits=4, num_ranks=13, num_hole_cards=2,
                                       num_raise_times=4, num_boardcards=5,
                                       game_path="ColosGame/PokerDefine/holdem.limit.2p.reverse_blinds.game")
        elif game == 'renju':
            return Renju()
        else:
            raise ValueError("%s is not supported yet." % game)


