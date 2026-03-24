import os
import threading
import datetime
import chess
import chess.pgn

class GameManager:
    """
    Lớp quản lý trạng thái ván cờ, xử lý nước đi và lưu trữ log.
    Thread-safe: dùng board_lock để tránh race condition khi nhiều thread
    cùng đọc/ghi board.
    """

    def __init__(self):
        self.board = chess.Board()
        self.board_lock = threading.Lock()
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def reset_game(self):
        with self.board_lock:
            self.board.reset()

    def make_move(self, move_uci: str) -> bool:
        """
        Thực hiện nước đi. Trả về (success, fen_before, fen_after) để
        app.py tính annotation chính xác mà không lo race condition.
        """
        with self.board_lock:
            try:
                move = chess.Move.from_uci(move_uci)
                if move in self.board.legal_moves:
                    fen_before = self.board.fen()
                    turn_before = self.board.turn
                    self.board.push(move)
                    fen_after = self.board.fen()
                    return True, fen_before, fen_after, turn_before
            except ValueError:
                pass
        return False, None, None, None

    def get_fen(self) -> str:
        with self.board_lock:
            return self.board.fen()

    def is_game_over(self) -> bool:
        with self.board_lock:
            return self.board.is_game_over()

    def is_checkmate(self) -> bool:
        with self.board_lock:
            return self.board.is_checkmate()

    def get_san(self, move_uci: str) -> str:
        """Lấy SAN của nước đi TRƯỚC khi push (cần gọi trước make_move)."""
        with self.board_lock:
            try:
                move = chess.Move.from_uci(move_uci)
                return self.board.san(move)
            except Exception:
                return move_uci

    def get_legal_moves(self):
        with self.board_lock:
            return list(self.board.legal_moves)

    def get_turn(self):
        with self.board_lock:
            return self.board.turn

    def save_log(self, result_text: str = "*"):
        with self.board_lock:
            game = chess.pgn.Game.from_board(self.board)
        game.headers["Event"] = "Chess AI Duel Local Match"
        game.headers["Site"] = "Localhost"
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["Result"] = result_text

        filename = f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        filepath = os.path.join(self.log_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            print(game, file=f, end="\n\n")

        print(f"Lưu log ván cờ tại: {filepath}")
        return filepath

# Singleton dùng chung cho toàn server
game_engine = GameManager()