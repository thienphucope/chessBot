import os
import threading
import datetime
import time
import chess
import chess.pgn
from config import Config

class GameManager:
    def __init__(self):
        self.board = chess.Board()
        self.lock = threading.Lock()

        self.white_role = Config.DEFAULT_WHITE_ROLE
        self.black_role = Config.DEFAULT_BLACK_ROLE
        self.is_running = False
        self.turn_count = 0
        self.total_move_time = 0.0
        self.white_total_time = 0.0
        self.black_total_time = 0.0
        self.last_move_timestamp = time.perf_counter()
        self.move_times = []

        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)

    def reset(self):
        with self.lock:
            self.board.reset()
            self.is_running = False
            self.turn_count = 0
            self.total_move_time = 0.0
            self.white_total_time = 0.0
            self.black_total_time = 0.0
            self.last_move_timestamp = time.perf_counter()
            self.move_times = []

    def update_settings(self, white=None, black=None, running=None):
        valid_roles = {'alphabeta', 'mcts', 'stockfish', 'human'}
        if white and white in valid_roles: self.white_role = white
        if black and black in valid_roles: self.black_role = black
        if running is not None: self.is_running = running

    def is_ai_turn(self):
        if not self.is_running or self.board.is_game_over(): return False
        role = self.white_role if self.board.turn == chess.WHITE else self.black_role
        return role != 'human'

    def get_current_ai_algo(self):
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

    def record_move_time(self, move_time, is_white_turn):
        with self.lock:
            self.move_times.append(move_time)
            self.total_move_time += move_time
            if is_white_turn:
                self.white_total_time += move_time
            else:
                self.black_total_time += move_time
            return self.total_move_time, self.white_total_time, self.black_total_time

    def save_log(self):
        with self.lock:
            move_stack = list(self.board.move_stack)
            move_times = list(self.move_times)
            white_total = self.white_total_time
            black_total = self.black_total_time
            res = self.board.result()

        game = chess.pgn.Game()
        node = game
        for i, move in enumerate(move_stack):
            node = node.add_variation(move)
            if i < len(move_times):
                node.comment = f"{move_times[i]:.2f}"

        if node.comment:
            node.comment += f" Total White: {white_total:.2f}, Black: {black_total:.2f}"
        else:
            node.comment = f"Total White: {white_total:.2f}, Black: {black_total:.2f}"

        game.headers["Result"] = res
        filename = f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        path = os.path.join(Config.LOG_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            print(game, file=f)
        return res

game_engine = GameManager()
