import chess
from engine.evaluator import evaluator

def alphabeta(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    """
    Alpha-Beta pruning algorithm.

    Args:
        board: Current board state
        depth: Search depth remaining
        alpha: Alpha value for pruning
        beta: Beta value for pruning
        maximizing: True if maximizing player (white), False if minimizing (black)

    Returns:
        Best evaluation score
    """
    if depth == 0 or board.is_game_over():
        # Use evaluator for leaf node evaluation
        eval_score = evaluator.get_eval(board.fen())
        return eval_score if maximizing else -eval_score

    if maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score = alphabeta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score = alphabeta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval

def get_alphabeta_move(board: chess.Board, depth: int = 3) -> chess.Move:
    """
    Get the best move using Alpha-Beta pruning.

    Args:
        board: Current board state
        depth: Search depth (default 3 for basic playability)

    Returns:
        Best move found, or None if no moves available
    """
    if board.is_game_over():
        return None

    best_move = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = alphabeta(board, depth - 1, alpha, beta, False)
        board.pop()

        if move_value > best_value:
            best_value = move_value
            best_move = move

        alpha = max(alpha, move_value)

    return best_move