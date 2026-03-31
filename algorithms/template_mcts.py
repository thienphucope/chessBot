import math
import random
import chess
from engine.simple_eval import simple_eval
from config import Config


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

    return math.tanh(simple_eval(sim) / 5.0)


def _mcts_iteration(root: MCTSNode) -> None:
    node = root
    while node.is_fully_expanded() and node.children:
        node = node.best_child()

    if not node.is_fully_expanded() and not node.board.is_game_over():
        node = node.expand()

    white_score = _simulate(node.board)  

    # Backpropagation: accumulate value from perspective of the player who made the move
    current = node
    while current is not None:
        current.visits += 1
        if current.parent is not None:
            # Check who made the move leading to current node
            is_white_made_move = (current.parent.board.turn == chess.WHITE)
            # Accumulate score from that player's perspective
            current.value += white_score if is_white_made_move else -white_score
        current = current.parent


def mcts_search(root: MCTSNode, iterations: int = 800) -> None:
    for _ in range(iterations):
        _mcts_iteration(root)


def get_mcts_move(board: chess.Board, iterations: int | None = None) -> chess.Move | None:
    if iterations is None:
        iterations = getattr(Config, 'MCTS_ITERATIONS', 800)
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

    # Select move by visit count (most robust), not by UCT score (noisy)
    return max(root.children, key=lambda c: c.visits).move