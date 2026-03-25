import math
import random
import chess
from engine.simple_eval import simple_eval


class MCTSNode:
    __slots__ = ('board', 'parent', 'move', 'children', 'visits', 'value', 'untried_moves')

    def __init__(self, board: chess.Board, parent=None, move=None):
        self.board = board.copy()
        self.parent = parent
        self.move = move            # Move that led to this node
        self.children: list['MCTSNode'] = []
        self.visits: int = 0
        self.value: float = 0.0    # Total value from the perspective of the PARENT (who made the move)
        self.untried_moves = list(board.legal_moves)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def uct_score(self, c_param: float = 1.4) -> float:
        """UCT score from the perspective of this node's parent (who is choosing among children)."""
        if self.visits == 0:
            return float('inf')
        exploitation = self.value / self.visits
        exploration = c_param * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def best_child(self, c_param: float = 1.4) -> 'MCTSNode':
        return max(self.children, key=lambda c: c.uct_score(c_param))

    def expand(self) -> 'MCTSNode':
        move = self.untried_moves.pop()
        new_board = self.board.copy()
        new_board.push(move)
        child = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child)
        return child


def _simulate(board: chess.Board, max_moves: int = 50) -> float:
    """
    Random rollout from position. Returns score in [-1, 1] from WHITE's perspective.
    Uses evaluator at cutoff so non-terminal positions are still meaningful.
    """
    sim = board.copy()
    for _ in range(max_moves):
        if sim.is_game_over():
            break
        sim.push(random.choice(list(sim.legal_moves)))

    if sim.is_game_over():
        result = sim.result()
        if result == '1-0':
            return 1.0
        elif result == '0-1':
            return -1.0
        return 0.0

    # simple_eval() is White-centric centipawn score
    return math.tanh(simple_eval(sim) / 5.0)


def _mcts_iteration(root: MCTSNode) -> None:
    """One full MCTS iteration: select → expand → simulate → backpropagate."""

    # --- Selection ---
    node = root
    while node.is_fully_expanded() and node.children:
        node = node.best_child()

    # --- Expansion ---
    if not node.is_fully_expanded() and not node.board.is_game_over():
        node = node.expand()

    # --- Simulation ---
    white_score = _simulate(node.board)  # always White-centric

    # --- Backpropagation ---
    # Each node stores value from its PARENT's perspective (the side that chose to go there).
    # The parent is the position BEFORE the move, so parent.board.turn is the side that moved.
    current = node
    while current is not None:
        current.visits += 1
        if current.parent is not None:
            # parent.board.turn = side that made the move leading to current
            if current.parent.board.turn == chess.WHITE:
                current.value += white_score
            else:
                current.value += -white_score
        current = current.parent


def mcts_search(root: MCTSNode, iterations: int = 800) -> None:
    """
    Sequential MCTS — parallelising tree traversal causes race conditions
    on visits/value without locks, which breaks UCT math entirely.
    """
    for _ in range(iterations):
        _mcts_iteration(root)


def get_mcts_move(board: chess.Board, iterations: int = 800) -> chess.Move | None:
    """
    Get the best move using Monte Carlo Tree Search.

    Args:
        board:      Current board state
        iterations: MCTS iterations (800 is a reasonable baseline)

    Returns:
        Best move found, or None if no legal moves
    """
    if board.is_game_over():
        return None

    root = MCTSNode(board)

    legal = list(root.untried_moves)
    if not legal:
        return None
    if len(legal) == 1:
        return legal[0]

    mcts_search(root, iterations)

    if not root.children:
        return random.choice(legal)

    # c_param=0 → pure exploitation (most visited = most robust choice)
    return root.best_child(c_param=0).move