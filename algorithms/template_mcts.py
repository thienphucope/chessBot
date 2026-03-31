import math
import random
import chess
from engine.simple_eval import simple_eval
from config import Config

class MCTSNode:
    __slots__ = ('board', 'parent', 'move', 'children', 'visits', 'value', 'untried_moves')

    def __init__(self, board: chess.Board, parent=None, move=None):
        self.board = board  # Lưu board hiện tại của node
        self.parent = parent
        self.move = move            # Nước đi dẫn đến node này
        self.children: list['MCTSNode'] = []
        self.visits: int = 0
        self.value: float = 0.0     # Tổng giá trị tích lũy từ góc nhìn của PARENT
        
        # FIX LỖI THỨ TỰ CỐ ĐỊNH: Lấy list các nước đi hợp lệ
        moves = list(board.legal_moves)
        
        # 1. Trộn ngẫu nhiên để phá vỡ thứ tự A1->H8 mặc định của python-chess
        random.shuffle(moves)
        
        # 2. Tối ưu nhỏ: Đưa các nước ăn quân (captures) về CUỐI list.
        # Vì hàm expand() dùng .pop() (rút từ cuối), nó sẽ ưu tiên mở rộng các nước ăn quân trước tiên.
        moves.sort(key=lambda m: board.is_capture(m))
        
        self.untried_moves = moves

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def uct_score(self, c_param: float = 1.414) -> float:
        """
        Tính điểm UCT từ góc nhìn của parent (người chọn nước đi này).
        """
        if self.visits == 0:
            return float('inf')
        
        # exploitation: Tỷ lệ thắng trung bình
        exploitation = self.value / self.visits
        # exploration: Độ ưu tiên khám phá các node ít lượt truy cập
        exploration = c_param * math.sqrt(math.log(self.parent.visits) / self.visits)
        
        return exploitation + exploration

    def best_child(self, c_param: float = 1.414) -> 'MCTSNode':
        """Chọn node con tốt nhất dựa trên công thức UCT."""
        return max(self.children, key=lambda c: c.uct_score(c_param))

    def expand(self) -> 'MCTSNode':
        """Mở rộng một nước đi chưa thử nghiệm."""
        move = self.untried_moves.pop() # Lấy từ cuối danh sách (ưu tiên capture nhờ hàm sort ở trên)
        new_board = self.board.copy()
        new_board.push(move)
        child = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child)
        return child

def _simulate(board: chess.Board, max_depth: int = 20) -> float:
    """
    Mô phỏng trận đấu (Rollout). 
    Trả về điểm số từ góc nhìn của quân TRẮNG (1.0 = Trắng thắng, -1.0 = Đen thắng).
    """
    sim = board.copy()
    
    # Giới hạn độ sâu mô phỏng để tiết kiệm tài nguyên và tăng độ chính xác của heuristic
    for _ in range(max_depth):
        if sim.is_game_over():
            break
            
        # CẢI TIẾN SIMULATION: Thay vì random mù quáng, ưu tiên bắt quân (capture)
        legal_moves = list(sim.legal_moves)
        captures = [m for m in legal_moves if sim.is_capture(m)]
        
        if captures:
            sim.push(random.choice(captures))
        else:
            sim.push(random.choice(legal_moves))

    # Kiểm tra kết quả cuối cùng
    if sim.is_game_over():
        result = sim.result()
        if result == '1-0': return 1.0
        if result == '0-1': return -1.0
        return 0.0 # Hòa

    # Nếu chưa kết thúc, sử dụng simple_eval và ép về khoảng [-1, 1]
    # Chia cho 1000 (tương đương 10 pawn) để đảm bảo hàm tanh hoạt động hiệu quả
    return math.tanh(simple_eval(sim) / 1000.0)

def _mcts_iteration(root: MCTSNode) -> None:
    """Một chu kỳ MCTS: Selection -> Expansion -> Simulation -> Backpropagation."""
    node = root
    
    # 1. Selection
    while node.is_fully_expanded() and node.children:
        node = node.best_child()

    # 2. Expansion
    if not node.board.is_game_over() and not node.is_fully_expanded():
        node = node.expand()

    # 3. Simulation
    white_score = _simulate(node.board)

    # 4. Backpropagation
    current = node
    while current is not None:
        current.visits += 1
        if current.parent is not None:
            # Nếu người vừa thực hiện nước đi là Trắng, họ nhận white_score
            # Nếu là Đen, họ nhận -white_score
            was_white_turn = (current.parent.board.turn == chess.WHITE)
            reward = white_score if was_white_turn else -white_score
            current.value += reward
        current = current.parent

def mcts_search(root: MCTSNode, iterations: int = 800) -> None:
    """Thực hiện lặp lại quá trình tìm kiếm."""
    for _ in range(iterations):
        _mcts_iteration(root)

def get_mcts_move(board: chess.Board, iterations: int | None = None) -> chess.Move | None:
    """Hàm chính để lấy nước đi tốt nhất từ MCTS."""
    if iterations is None:
        iterations = getattr(Config, 'MCTS_ITERATIONS', 800)
        
    if board.is_game_over():
        return None

    root = MCTSNode(board.copy())
    
    # Trường hợp đặc biệt: chỉ có 1 nước đi hợp lệ
    if len(root.untried_moves) == 1:
        return root.untried_moves[0]

    # Thực hiện tìm kiếm
    mcts_search(root, iterations)

    if not root.children:
        # Fallback an toàn (không nên xảy ra nếu iterations > 0)
        return random.choice(list(board.legal_moves))

    # CHUẨN MCTS: Chọn nước đi có số lượt truy cập (visits) cao nhất.
    # Đây được gọi là "Robust Child", ổn định hơn là chọn theo "Max Value" (vốn bị nhiễu).
    best_node = max(root.children, key=lambda c: c.visits)
    
    return best_node.move