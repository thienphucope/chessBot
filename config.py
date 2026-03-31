import os

class Config:
    SECRET_KEY = 'chess_secret!'
    ASYNC_MODE = 'threading'
    DEBUG = True

    STOCKFISH_PATH = os.path.join(os.getcwd(), "stockfish.exe")
    if not os.path.exists(STOCKFISH_PATH):
        STOCKFISH_PATH = "D:\\Documents\\252\\nmttnt\\Minimax\\.venv\\stockfish.exe"

    SF_THREADS = 2
    SF_HASH = 256
    SF_DEPTH = 2   
    SF_AI_DEPTH = 1

    # Algorithm depths/iterations
    ALPHABETA_DEPTH = 3
    MCTS_ITERATIONS = 1200

    LOG_DIR = "logs"
    AI_THINKING_DELAY = 0

    DEFAULT_WHITE_ROLE = 'alphabeta'
    DEFAULT_BLACK_ROLE = 'mcts'

