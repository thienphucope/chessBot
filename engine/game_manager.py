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
        self.move_data = [] # Lưu danh sách (time, eval)

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
            self.move_data = []

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

    def record_move_time(self, move_time, is_white_turn, evaluation=0.0):
        with self.lock:
            # Chuyển điểm sang góc nhìn của người vừa đi (Side-to-move perspective)
            # Nếu Trắng đi: giữ nguyên (vì eval là White-centric)
            # Nếu Đen đi: đảo dấu (nếu Trắng thắng (+), Đen sẽ nhận điểm âm (-))
            actual_eval = evaluation if is_white_turn else -evaluation
            
            self.move_data.append((move_time, actual_eval))
            self.total_move_time += move_time
            if is_white_turn:
                self.white_total_time += move_time
            else:
                self.black_total_time += move_time
            return self.total_move_time, self.white_total_time, self.black_total_time

    def save_log(self):
        with self.lock:
            move_stack = list(self.board.move_stack)
            move_data = list(self.move_data)
            white_total = self.white_total_time
            black_total = self.black_total_time
            res = self.board.result()

        # Tính toán thống kê
        white_times = [d[0] for i, d in enumerate(move_data) if i % 2 == 0]
        black_times = [d[0] for i, d in enumerate(move_data) if i % 2 != 0]
        white_evals = [d[1] for i, d in enumerate(move_data) if i % 2 == 0]
        black_evals = [d[1] for i, d in enumerate(move_data) if i % 2 != 0]

        avg_white_time = sum(white_times) / len(white_times) if white_times else 0
        avg_black_time = sum(black_times) / len(black_times) if black_times else 0
        avg_white_eval = sum(white_evals) / len(white_evals) if white_evals else 0
        avg_black_eval = sum(black_evals) / len(black_evals) if black_evals else 0

        game = chess.pgn.Game()
        game.headers["White"] = self.white_role
        game.headers["Black"] = self.black_role
        game.headers["Result"] = res
        
        # Thêm thống kê vào Header để dễ so sánh
        game.headers["AvgWhiteTime"] = f"{avg_white_time:.3f}s"
        game.headers["AvgBlackTime"] = f"{avg_black_time:.3f}s"
        game.headers["AvgWhiteEval"] = f"{avg_white_eval:.2f}"
        game.headers["AvgBlackEval"] = f"{avg_black_eval:.2f}"

        node = game
        for i, move in enumerate(move_stack):
            node = node.add_variation(move)
            if i < len(move_data):
                m_time, m_eval = move_data[i]
                node.comment = f"t:{m_time:.2f}s, e:{m_eval:.2f}"

        summary_comment = (
            f"\n[Summary]\n"
            f"White ({self.white_role}): Total {white_total:.2f}s, Avg {avg_white_time:.3f}s, Avg Eval {avg_white_eval:.2f}\n"
            f"Black ({self.black_role}): Total {black_total:.2f}s, Avg {avg_black_time:.3f}s, Avg Eval {avg_black_eval:.2f}"
        )
        
        # Đặt comment tổng kết ở node cuối cùng
        if node.comment:
            node.comment += summary_comment
        else:
            node.comment = summary_comment

        filename = f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        path = os.path.join(Config.LOG_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            print(game, file=f)
        return res

game_engine = GameManager()
