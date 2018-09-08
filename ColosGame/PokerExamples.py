from ColosGame.PokerGame import LimitedPokerGame
"""
提供Game类Instance，注意路径的正确
TODO 取消除了路径以外的参数，直接从文件读入
"""
def get_limit_leduc():
    return LimitedPokerGame(num_players=3, num_rounds=2,
                            num_suits=2, num_ranks=3, num_hole_cards=1,
                            num_raise_times=2, num_boardcards=1,
                             game_path="ColosGame/PokerDefine/LimitLeduc.game")

def get_holdem_limit_2p():
    return LimitedPokerGame(num_players=2, num_rounds=4,
                            num_suits=4, num_ranks=13, num_hole_cards=2, 
                            num_raise_times=4, num_boardcards=5, 
                            game_path="ColosGame/PokerDefine/holdem.limit.2p.reverse_blinds.game")