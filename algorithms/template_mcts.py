"""
Monte Carlo Tree Search (MCTS) Algorithm for Chess

MCTS gồm 4 bước chính:
1. Selection - Dùng UCB1 để chọn node tốt nhất
2. Expansion - Mở rộng node bằng cách thêm nước đi mới
3. Simulation - Mô phỏng ván cờ ngẫu nhiên (rollout)
4. Backpropagation - Cập nhật thống kê ngược lên root

QUAN TRỌNG về góc nhìn (perspective):
- Mỗi node lưu thống kê từ góc nhìn của PARENT (người đã đi nước dẫn đến node này)
- wins/visits = tỷ lệ thắng cho PARENT khi đi nước này
- UCB1 chọn nước tốt nhất cho current player (parent của children)
"""

import chess
import math
import random
from typing import Optional, List
from engine.simple_eval import simple_eval
from config import Config


class MCTSNode:
    """Node trong cây MCTS"""
    
    def __init__(
        self, 
        board: chess.Board, 
        parent: Optional['MCTSNode'] = None, 
        move: Optional[chess.Move] = None,
        depth: int = 0
    ):
        self.board = board.copy()
        self.parent = parent
        self.move = move  # Nước đi dẫn đến node này
        self.depth = depth
        self.children: List['MCTSNode'] = []
        
        # Lấy danh sách nước đi, shuffle trước để tạo sự đa dạng giữa các ván đấu
        moves = list(board.legal_moves)
        random.shuffle(moves)
        
        # Sau đó sắp xếp theo độ ưu tiên để mở rộng các nước tốt trước (MVV-LVA)
        # Sắp xếp tăng dần để pop() lấy phần tử cuối (phần tử tốt nhất)
        self.untried_moves = sorted(
            moves,
            key=lambda m: self._move_priority(board, m)
        )
        
        # Thống kê MCTS - từ góc nhìn của PARENT (người đi nước dẫn đến node này)
        self.visits = 0
        self.wins = 0.0  # Số điểm thắng cho PARENT
        
    def _move_priority(self, board: chess.Board, move: chess.Move) -> int:
        """Heuristic đơn giản để đánh giá độ ưu tiên của nước đi"""
        score = 0
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
            victim_val = getattr(victim, 'piece_type', 0) * 10 if victim else 0
            attacker_val = getattr(attacker, 'piece_type', 0) if attacker else 0
            score += 100 + victim_val - attacker_val
        
        if move.promotion:
            score += 50
            
        if board.gives_check(move):
            score += 30
            
        return score

    def is_terminal(self) -> bool:
        """Kiểm tra node có phải trạng thái kết thúc hoặc đạt độ sâu tối đa"""
        max_depth = getattr(Config, 'MCTS_MAX_DEPTH', 10)
        return self.board.is_game_over() or self.depth >= max_depth
    
    def is_fully_expanded(self) -> bool:
        """Kiểm tra đã mở rộng hết các nước đi chưa"""
        return len(self.untried_moves) == 0
    
    def ucb1(self, c_param: float = 2.0) -> float:
        """
        Tính UCB1 score cho node (từ góc nhìn parent)
        Tăng c_param lên 2.0 để bot chịu khó khám phá các nước đi khác (giảm deterministic)
        """
        if self.visits == 0:
            # Thêm một chút nhiễu nhỏ để các node chưa thăm không bị chọn theo thứ tự cố định
            return float('inf') + random.random()
        
        exploitation = self.wins / self.visits
        exploration = c_param * math.sqrt(math.log(self.parent.visits) / self.visits)
        
        return exploitation + exploration
    
    def best_child(self, c_param: float = 1.414) -> 'MCTSNode':
        """Chọn child node tốt nhất theo UCB1"""
        return max(self.children, key=lambda child: child.ucb1(c_param))
    
    def expand(self) -> 'MCTSNode':
        """
        Expansion: Thêm một child node mới từ nước đi chưa thử
        """
        move = self.untried_moves.pop()
        new_board = self.board.copy()
        new_board.push(move)
        
        child_node = MCTSNode(new_board, parent=self, move=move, depth=self.depth + 1)
        self.children.append(child_node)
        
        return child_node
    
    def simulate(self) -> float:
        """
        Simulation: Đánh giá node lá bằng Quiescence Search.
        Điều này cực kỳ quan trọng để tránh việc 'ăn quân xong bị bắt lại' (Horizon Effect).
        """
        parent_color = not self.board.turn
        
        if self.is_terminal():
            return self._evaluate_result(self.board, parent_color)
        
        # Sử dụng Quiescence Search để nhìn thấy các nước bắt quân phản hồi
        score = self._quiescence(self.board, float('-inf'), float('inf'), depth=0)
            
        return self._score_to_probability(score, parent_color)

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, depth: int) -> float:
        """Tìm kiếm tĩnh: Chỉ đánh giá các nước ăn quân để đảm bảo thế trận ổn định"""
        stand_pat = simple_eval(board)
        
        # Nếu đang ở vị trí tối ưu hóa cho Đen (min), đảo ngược logic nếu cần
        # Nhưng simple_eval trả về điểm tuyệt đối cho Trắng, nên ta dùng chuẩn minimax
        
        curr_eval = stand_pat if board.turn == chess.WHITE else -stand_pat
        
        if curr_eval >= beta:
            return beta
        if alpha < curr_eval:
            alpha = curr_eval
            
        # Giới hạn độ sâu quiescence để tránh đệ quy quá sâu (thường 2-3 nước ăn quân là đủ)
        if depth > 3:
            return curr_eval

        for move in board.legal_moves:
            if board.is_capture(move):
                board.push(move)
                score = -self._quiescence(board, -beta, -alpha, depth + 1)
                board.pop()
                
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    def _score_to_probability(self, score: float, perspective_color: bool) -> float:
        """Chuyển đổi điểm số (White perspective) sang xác suất [0, 1] cho perspective_color"""
        # Tránh lỗi overflow khi exp quá lớn
        try:
            if perspective_color == chess.WHITE:
                return 1.0 / (1.0 + math.exp(-score / 400.0))
            else:
                return 1.0 / (1.0 + math.exp(score / 400.0))
        except OverflowError:
            if perspective_color == chess.WHITE:
                return 1.0 if score > 0 else 0.0
            else:
                return 1.0 if score < 0 else 0.0
    
    def _evaluate_result(self, board: chess.Board, perspective_color: bool) -> float:
        """
        Đánh giá kết quả từ góc nhìn của perspective_color
        
        Args:
            board: Trạng thái bàn cờ cuối
            perspective_color: Màu quân cần đánh giá (True=WHITE, False=BLACK)
        
        Returns:
            1.0 nếu perspective_color thắng
            0.5 nếu hòa
            0.0 nếu perspective_color thua
        """
        if board.is_checkmate():
            # Người đang đi (board.turn) bị chiếu hết => họ thua
            if board.turn == perspective_color:
                return 0.0  # perspective_color thua
            else:
                return 1.0  # perspective_color thắng
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.5
        
        if board.can_claim_draw():
            return 0.5
        
        # Dùng evaluation function nếu chưa kết thúc
        score = simple_eval(board)
        return self._score_to_probability(score, perspective_color)
    
    def backpropagate(self, result: float) -> None:
        """
        Backpropagation: Cập nhật thống kê từ node này lên root
        
        result: kết quả từ góc nhìn PARENT của node lá
        
        Mỗi node lưu stats từ góc nhìn parent của nó, nên:
        - Node lá: cập nhật với result (đã là góc nhìn parent của nó)
        - Node cha: cập nhật với 1-result (vì parent của node cha là đối thủ)
        """
        node = self
        
        while node is not None:
            node.visits += 1
            node.wins += result
            
            # Đảo kết quả vì lên level cha, góc nhìn đổi sang đối thủ
            result = 1.0 - result
            node = node.parent


def mcts_search(board: chess.Board, iterations: int) -> Optional[chess.Move]:
    """
    Chạy MCTS search và trả về nước đi tốt nhất
    
    Args:
        board: Trạng thái bàn cờ hiện tại
        iterations: Số lần lặp MCTS
    
    Returns:
        Nước đi tốt nhất hoặc None nếu game over
    """
    if board.is_game_over():
        return None
    
    root = MCTSNode(board)
    
    for _ in range(iterations):
        node = root
        
        # 1. Selection: Đi xuống cây theo UCB1
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child()
        
        # 2. Expansion: Mở rộng nếu có thể
        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()
        
        # 3. Simulation: Rollout ngẫu nhiên
        if node.is_terminal():
            # Node terminal - đánh giá từ góc nhìn parent
            parent_color = not node.board.turn
            result = node._evaluate_result(node.board, parent_color)
        else:
            result = node.simulate()
        
        # 4. Backpropagation: Cập nhật thống kê
        node.backpropagate(result)
    
    # Chọn nước đi có visits nhiều nhất (most robust)
    # Hoặc có thể chọn theo win rate cao nhất
    if not root.children:
        return None
    
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move


def get_mcts_move(board: chess.Board, iterations: Optional[int] = None) -> Optional[chess.Move]:
    """
    Lấy nước đi tốt nhất dùng MCTS
    
    Args:
        board: Trạng thái bàn cờ hiện tại
        iterations: Số lần lặp (mặc định từ Config)
    
    Returns:
        Nước đi tốt nhất hoặc None nếu game over
    """
    if iterations is None:
        iterations = getattr(Config, 'MCTS_ITERATIONS', 1000)
    
    return mcts_search(board, iterations)
