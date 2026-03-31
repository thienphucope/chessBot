import chess
from engine.simple_eval import simple_eval
from config import Config

# Transposition table: zobrist_hash -> (depth, score, flag)
# flag: 'exact', 'lower', 'upper'
_tt: dict[int, tuple[int, float, str]] = {}
_TT_MAX_SIZE = 1_000_000


def _get_score(board: chess.Board) -> float:
    white_score = simple_eval(board)
    return white_score if board.turn == chess.WHITE else -white_score


def _tt_store(key: int, depth: int, score: float, flag: str) -> None:
    if len(_tt) >= _TT_MAX_SIZE:
        _tt.clear()
    _tt[key] = (depth, score, flag)


_PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20_000,
}


def _move_order_score(board: chess.Board, move: chess.Move) -> int:
    score = 0

    # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        victim_val = _PIECE_VALUE.get(victim.piece_type, 0) if victim else 0
        attacker_val = _PIECE_VALUE.get(attacker.piece_type, 100) if attacker else 100
        score += 10 * victim_val - attacker_val + 20_000  # captures always first

    # Promotions
    if move.promotion:
        score += _PIECE_VALUE.get(move.promotion, 0) + 10_000

    # Checks (slightly expensive but worth it at shallow depth)
    board.push(move)
    if board.is_check():
        score += 5_000
    board.pop()

    return score

def _quiescence(board: chess.Board, alpha: float, beta: float) -> float:
    stand_pat = _get_score(board)

    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)

    # Only look at captures
    capture_moves = sorted(
        [m for m in board.legal_moves if board.is_capture(m)],
        key=lambda m: _move_order_score(board, m),
        reverse=True,
    )

    for move in capture_moves:
        board.push(move)
        score = -_quiescence(board, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta
        alpha = max(alpha, score)

    return alpha


def alphabeta(
    board: chess.Board,
    depth: int,
    alpha: float,
    beta: float,
) -> float:
    key = board._transposition_key()

    # Transposition table lookup
    tt_entry = _tt.get(key)
    if tt_entry and tt_entry[0] >= depth:
        tt_depth, tt_score, tt_flag = tt_entry
        if tt_flag == "exact":
            return tt_score
        if tt_flag == "lower":
            alpha = max(alpha, tt_score)
        elif tt_flag == "upper":
            beta = min(beta, tt_score)
        if alpha >= beta:
            return tt_score

    if board.is_game_over():
        if board.is_checkmate():
            return -100_000 - depth  # Prefer faster mates
        return 0  # Stalemate / draw

    if depth == 0:
        return _quiescence(board, alpha, beta)

    orig_alpha = alpha
    best_value = float("-inf")

    moves = sorted(
        board.legal_moves,
        key=lambda m: _move_order_score(board, m),
        reverse=True,
    )

    for move in moves:
        board.push(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha)
        board.pop()

        if score > best_value:
            best_value = score

        alpha = max(alpha, score)
        if alpha >= beta:
            break  # Beta cutoff

    # Store in transposition table
    if orig_alpha < best_value < beta:
        flag = "exact"
    elif best_value >= beta:
        flag = "lower"
    else:  # best_value <= orig_alpha
        flag = "upper"
    _tt_store(key, depth, best_value, flag)

    return best_value


def get_alphabeta_move(board: chess.Board, depth: int | None = None) -> chess.Move | None:
    if depth is None:
        depth = getattr(Config, 'ALPHABETA_DEPTH', 3)
    if board.is_game_over():
        return None

    best_move = None
    best_value = float("-inf")
    alpha = float("-inf")
    beta = float("inf")

    moves = sorted(
        board.legal_moves,
        key=lambda m: _move_order_score(board, m),
        reverse=True,
    )

    for move in moves:
        board.push(move)
        move_value = -alphabeta(board, depth - 1, -beta, -alpha)
        board.pop()

        if move_value > best_value:
            best_value = move_value
            best_move = move

        alpha = max(alpha, move_value)

    return best_move