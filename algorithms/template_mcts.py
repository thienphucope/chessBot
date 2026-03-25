import math
import random
import chess
from engine.evaluator import evaluator

class MCTSNode:
    def __init__(self, board: chess.Board, parent=None, move=None):
        self.board = board.copy()
        self.parent = parent
        self.move = move  # Move that led to this node
        self.children = []
        self.visits = 0
        self.value = 0.0  # Total value accumulated
        self.untried_moves = list(board.legal_moves)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        """Select child with highest UCT value."""
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def expand(self):
        """Expand by adding a new child node."""
        move = self.untried_moves.pop()
        new_board = self.board.copy()
        new_board.push(move)
        child_node = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child_node)
        return child_node

def simulate_random(board: chess.Board) -> float:
    """Simulate a random game from current position."""
    current_board = board.copy()
    max_moves = 50  # Limit to prevent infinite games
    moves_count = 0

    while not current_board.is_game_over() and moves_count < max_moves:
        legal_moves = list(current_board.legal_moves)
        if not legal_moves:
            break
        move = random.choice(legal_moves)
        current_board.push(move)
        moves_count += 1

    # Evaluate final position
    if current_board.is_game_over():
        result = current_board.result()
        if result == '1-0':
            return 1.0  # White wins
        elif result == '0-1':
            return -1.0  # Black wins
        else:
            return 0.0  # Draw
    else:
        # Use evaluator for non-terminal positions
        eval_score = evaluator.get_eval(current_board.fen())
        # Convert to win probability-like score
        return math.tanh(eval_score / 10.0)  # Scale down for reasonable range

def mcts_search(root: MCTSNode, iterations: int = 1000):
    """Perform MCTS search for given number of iterations."""
    for _ in range(iterations):
        # Selection
        node = root
        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        # Expansion
        if not node.is_fully_expanded():
            node = node.expand()

        # Simulation
        result = simulate_random(node.board)

        # Backpropagation
        while node is not None:
            node.visits += 1
            node.value += result if node.board.turn == chess.WHITE else -result
            node = node.parent

def get_mcts_move(board: chess.Board, iterations: int = 1000) -> chess.Move:
    """
    Get the best move using Monte Carlo Tree Search.

    Args:
        board: Current board state
        iterations: Number of MCTS iterations (default 1000 for basic playability)

    Returns:
        Best move found, or None if no moves available
    """
    if board.is_game_over():
        return None

    root = MCTSNode(board)

    # If only one move, return it immediately
    if len(root.untried_moves) == 1:
        return root.untried_moves[0]

    # Perform MCTS search
    mcts_search(root, iterations)

    # Select the most visited child
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move