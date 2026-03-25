from .random_bot import get_random_move
from .stockfish_bot import get_stockfish_move
from .template_alphabeta import get_alphabeta_move
from .template_mcts import get_mcts_move

__all__ = ['get_random_move', 'get_stockfish_move', 'get_alphabeta_move', 'get_mcts_move']
