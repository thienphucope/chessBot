import random
import chess

def get_random_move(board: chess.Board):
    """
    Chọn một nước đi ngẫu nhiên từ danh sách các nước đi hợp lệ.
    
    Args:
        board (chess.Board): Trạng thái bàn cờ hiện tại.
        
    Returns:
        chess.Move: Nước đi ngẫu nhiên được chọn.
    """
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    return random.choice(legal_moves)
