# import chess
# from engine.evaluator import evaluator
# from config import Config

# def get_stockfish_move(board: chess.Board, depth=None):
#     if depth is None:
#         depth = getattr(Config, 'SF_AI_DEPTH', 15)
    
#     move_uci = evaluator.get_best_move(board.fen(), depth=depth)
#     if move_uci:
#         try:
#             return chess.Move.from_uci(move_uci)
#         except ValueError:
#             return None
#     return None
