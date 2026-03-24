import math
import threading
import chess
from stockfish import Stockfish
from config import Config

class ChessEvaluator:
    def __init__(self):
        self.lock = threading.Lock()
        try:
            self.sf = Stockfish(
                path=Config.STOCKFISH_PATH, 
                parameters={"Threads": Config.SF_THREADS, "Hash": Config.SF_HASH}
            )
            self.sf.set_depth(Config.SF_DEPTH)
            print(f"✅ Stockfish (Judge) đã sẵn sàng! Depth: {Config.SF_DEPTH}")
        except:
            self.sf = None
            print(f"⚠️ Cảnh báo: Không khởi động được Stockfish.")

    def cp_to_wp(self, cp):
        """Chuyển đổi centipawn sang Win Probability."""
        return 0.5 + 0.5 * (2 / (1 + math.exp(-0.003682 * cp * 100)) - 1)

    def get_eval(self, fen):
        """Lấy điểm đánh giá White-centric."""
        if not self.sf: return 0.0
        board = chess.Board(fen)
        with self.lock:
            try:
                self.sf.set_fen_position(fen)
                data = self.sf.get_evaluation()
                val = data['value']
                if board.turn == chess.BLACK: val = -val
                
                if data['type'] == 'cp':
                    return val / 100.0
                return 100.0 if val > 0 else -100.0
            except: 
                return 0.0

    def get_best_move(self, fen, depth=None):
        """Lấy nước đi tốt nhất từ Stockfish."""
        if not self.sf: return None
        with self.lock:
            try:
                self.sf.set_fen_position(fen)
                if depth:
                    self.sf.set_depth(depth)
                move_uci = self.sf.get_best_move()
                # Sau khi lấy nước đi, trả lại depth gốc cho trọng tài
                if depth:
                    self.sf.set_depth(Config.SF_DEPTH)
                return move_uci
            except:
                return None

    def get_annotation(self, eval_before, eval_after, turn):
        """Phân loại nước đi theo Chess.com."""
        v_before = eval_before if turn == chess.WHITE else -eval_before
        v_after = eval_after if turn == chess.WHITE else -eval_after
        
        wp_before = self.cp_to_wp(v_before)
        wp_after = self.cp_to_wp(v_after)
        delta_wp = wp_after - wp_before
        loss = wp_before - wp_after

        if delta_wp > 0.05: return "!!"
        if delta_wp > 0.02: return "!"
        if loss <= 0.01:    return "Best"
        if loss <= 0.03:    return "Excellent"
        if loss <= 0.06:    return "Good"
        if loss <= 0.12:    return "?!"
        if loss <= 0.25:    return "?"
        return "??"

evaluator = ChessEvaluator()
