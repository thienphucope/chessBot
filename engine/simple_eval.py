import chess

# ---------------------------------------------------------------------------
# Piece values (centipawns)
# ---------------------------------------------------------------------------
_PIECE_VAL = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:     0,
}

# ---------------------------------------------------------------------------
# Piece-Square Tables — White's POV, index 0 = a8 (top-left), 63 = h1
# Black automatically mirrors via chess.square_mirror()
# ---------------------------------------------------------------------------
# fmt: off
_PST = {
    chess.PAWN: [
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0,
    ],
    chess.KNIGHT: [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ],
    chess.BISHOP: [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ],
    chess.ROOK: [
         0,  0,  0,  0,  0,  0,  0,  0,
         5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
         0,  0,  0,  5,  5,  0,  0,  0,
    ],
    chess.QUEEN: [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20,
    ],
    chess.KING: [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20,
    ],
}
# fmt: on


def simple_eval(board: chess.Board) -> float:
    """
    Đánh giá vị trí theo góc nhìn White (centipawns / 100 = pawn units).
    Dương = White đang tốt, Âm = Black đang tốt.

    Gồm 2 thành phần:
      1. Material: tổng giá trị quân cờ
      2. Piece-Square Table: thưởng/phạt theo vị trí của từng quân
    """
    if board.is_checkmate():
        # Người vừa đi là bên KHÔNG bị chiếu hết
        return -100_000 if board.turn == chess.WHITE else 100_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    score = 0
    for sq, piece in board.piece_map().items():
        # PST index: python-chess sq 0=a1, PST row 0 = rank 8 (a8)
        # → dùng (63 - sq) để map a1→index 63, h8→index 0
        if piece.color == chess.WHITE:
            pst_index = 63 - sq
            score += _PIECE_VAL[piece.piece_type] + _PST[piece.piece_type][pst_index]
        else:
            # Black mirrors vertically
            mirrored = chess.square_mirror(sq)
            pst_index = 63 - mirrored
            score -= _PIECE_VAL[piece.piece_type] + _PST[piece.piece_type][pst_index]

    return float(score)


def simple_eval_for_side(board: chess.Board) -> float:
    """
    Wrapper trả về score theo góc nhìn của side to move.
    Dùng trực tiếp trong Negamax (alphabeta) và MCTS rollout.
    """
    s = simple_eval(board)
    return s if board.turn == chess.WHITE else -s