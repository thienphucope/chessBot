import chess
from engine.evaluator import evaluator

_PIECE_VAL = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:     0,
}

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

def _get_adjacent_squares(sq: int) -> list[int]:
    """Get all adjacent squares (8 directions) to a given square"""
    row, col = sq // 8, sq % 8
    adjacent = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                adjacent.append(nr * 8 + nc)
    return adjacent


def _get_controlled_squares(board: chess.Board, color: bool) -> int:
    """Count number of squares controlled by a side"""
    count = 0
    for sq in chess.SQUARES:
        if board.is_attacked_by(color, sq):
            count += 1
    return count


def simple_eval(board: chess.Board) -> float:
    if board.is_checkmate():
        return -100_000 if board.turn == chess.WHITE else 100_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    # Material score
    material_score = 0
    position_score = 0
    for sq, piece in board.piece_map().items():
        if piece.color == chess.WHITE:
            pst_index = 63 - sq
            material_score += _PIECE_VAL[piece.piece_type]
            position_score += _PST[piece.piece_type][pst_index]
        else:
            # Black mirrors vertically
            mirrored = chess.square_mirror(sq)
            pst_index = 63 - mirrored
            material_score -= _PIECE_VAL[piece.piece_type]
            position_score -= _PST[piece.piece_type][pst_index]

    # King safety score: proportional to piece distribution around kings
    white_king_sq = board.king(chess.WHITE)
    black_king_sq = board.king(chess.BLACK)
    
    KING_SAFETY_WEIGHT = 10
    king_safety_score = 0
    
    if white_king_sq:
        adjacent_sqs = _get_adjacent_squares(white_king_sq)
        white_friendly = 0
        white_enemy = 0
        for sq in adjacent_sqs:
            if sq in board.piece_map():
                piece = board.piece_map()[sq]
                if piece.color == chess.WHITE:
                    white_friendly += 1
                else:
                    white_enemy += 1
        white_safety = (white_friendly - white_enemy * 1.5) * KING_SAFETY_WEIGHT
        king_safety_score += white_safety
    
    if black_king_sq:
        adjacent_sqs = _get_adjacent_squares(black_king_sq)
        black_friendly = 0
        black_enemy = 0
        for sq in adjacent_sqs:
            if sq in board.piece_map():
                piece = board.piece_map()[sq]
                if piece.color == chess.BLACK:
                    black_friendly += 1
                else:
                    black_enemy += 1
        black_safety = (black_enemy - black_friendly * 1.5) * KING_SAFETY_WEIGHT
        king_safety_score += black_safety

    # Square control score: reward controlling more squares
    white_control = _get_controlled_squares(board, chess.WHITE)
    black_control = _get_controlled_squares(board, chess.BLACK)
    control_score = (white_control - black_control) * 5  # 5 points per controlled square

    # Combined score with weights: 0.5 material + 0.15 position + 0.2 king_safety + 0.15 control
    score = material_score * 0.5 + position_score * 0.15 + king_safety_score * 0.2 + control_score * 0.15

    return float(score)


def simple_eval_for_side(board: chess.Board) -> float:
    s = simple_eval(board)
    return s if board.turn == chess.WHITE else -s