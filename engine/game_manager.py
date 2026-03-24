import os
import threading
import datetime
import chess
import chess.pgn
from config import Config

class GameManager:
    def __init__(self):
        self.board = chess.Board()
        self.lock = threading.Lock()
        
        # Cài đặt từ Config
        self.white_role = Config.DEFAULT_WHITE_ROLE
        self.black_role = Config.DEFAULT_BLACK_ROLE
        self.is_running = False
        self.turn_count = 0

        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)

    def reset(self):
        with self.lock:
            self.board.reset()
            self.is_running = False
            self.turn_count = 0

    def update_settings(self, white=None, black=None, running=None):
        if white: self.white_role = white
        if black: self.black_role = black
        if running is not None: self.is_running = running

    def is_ai_turn(self):
        if not self.is_running or self.board.is_game_over(): return False
        role = self.white_role if self.board.turn == chess.WHITE else self.black_role
        return role != 'human'

    def get_current_ai_algo(self):
        """Lấy thuật toán của AI hiện tại dựa trên lượt đi."""
        return self.white_role if self.board.turn == chess.WHITE else self.black_role

    def apply_move(self, move_uci):
        with self.lock:
            try:
                move = chess.Move.from_uci(move_uci)
                if move in self.board.legal_moves:
                    san = self.board.san(move)
                    turn = self.board.turn
                    self.board.push(move)
                    self.turn_count += 1
                    return True, san, turn
            except: pass
        return False, None, None

    def save_log(self):
        with self.lock:
            game = chess.pgn.Game.from_board(self.board)
            res = self.board.result()
        
        game.headers["Result"] = res
        filename = f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        path = os.path.join(Config.LOG_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            print(game, file=f)
        return res

game_engine = GameManager()
