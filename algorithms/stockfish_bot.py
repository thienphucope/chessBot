import chess
from engine.evaluator import evaluator
from config import Config

def get_stockfish_move(board: chess.Board, depth=None):
    """
    Uses Stockfish from the evaluator to find the best move.
    
    Args:
        board (chess.Board): The current board state.
        depth (int, optional): The search depth for Stockfish. 
                              Defaults to Config.SF_AI_DEPTH.
        
    Returns:
        chess.Move: The best move found.
    """
    if depth is None:
        depth = getattr(Config, 'SF_AI_DEPTH', 15)
    
    move_uci = evaluator.get_best_move(board.fen(), depth=depth)
    if move_uci:
        try:
            return chess.Move.from_uci(move_uci)
        except ValueError:
            return None
    return None
