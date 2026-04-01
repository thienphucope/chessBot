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
    SF_DEPTH = 5  
    SF_AI_DEPTH = 1

    # Algorithm depths/iterations
    ALPHABETA_DEPTH = 4       # Alpha-Beta quét cạn 4 plies (chắc chắn)
    MCTS_ITERATIONS = 5000    # Tăng lần lặp
    MCTS_MAX_DEPTH = 10       # Cho phép MCTS nhìn sâu hơn (12 plies)
    MCTS_EVAL_DEPTH = 0       # Giữ 0 để nhanh


    LOG_DIR = "logs"
    AI_THINKING_DELAY = 0

    DEFAULT_WHITE_ROLE = 'alphabeta'
    DEFAULT_BLACK_ROLE = 'mcts'
