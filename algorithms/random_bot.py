import random
import chess

def get_random_move(board: chess.Board):
    """
    Selects a random move from the list of legal moves.
    
    Args:
        board (chess.Board): The current board state.
        
    Returns:
        chess.Move: The randomly selected move.
    """
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    return random.choice(legal_moves)
