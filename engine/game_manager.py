import os
import datetime
import chess
import chess.pgn

class GameManager:
    """
    Lớp quản lý trạng thái ván cờ, xử lý nước đi và lưu trữ log.
    Nhiệm vụ:
    - Lưu giữ đối tượng chess.Board duy nhất.
    - Thực hiện các nước đi (move) và kiểm tra tính hợp lệ.
    - Xuất file PGN (log) sau khi ván cờ kết thúc.
    """

    def __init__(self):
        self.board = chess.Board()
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def reset_game(self):
        """
        Khởi động lại ván cờ về trạng thái ban đầu.
        """
        self.board.reset()

    def make_move(self, move_uci: str) -> bool:
        """
        Thực hiện một nước đi từ chuỗi UCI (ví dụ: 'e2e4').
        
        Args:
            move_uci (str): Nước đi ở định dạng UCI.
            
        Returns:
            bool: True nếu nước đi hợp lệ và thực hiện thành công, ngược lại False.
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
        except ValueError:
            pass
        return False

    def get_fen(self) -> str:
        """
        Trả về chuỗi FEN hiện tại của bàn cờ.
        """
        return self.board.fen()

    def is_game_over(self) -> bool:
        """
        Kiểm tra ván cờ đã kết thúc chưa.
        """
        return self.board.is_game_over()

    def save_log(self, result_text: str = "*"):
        """
        Lưu lịch sử ván cờ dưới định dạng PGN vào thư mục logs.
        """
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

# Tạo instance duy nhất để dùng chung cho cả server Flask
game_engine = GameManager()
