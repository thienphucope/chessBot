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
    SF_DEPTH = 18   
    SF_AI_DEPTH = 18

    LOG_DIR = "logs"
    AI_THINKING_DELAY = 0.5

    DEFAULT_WHITE_ROLE = 'human'
    DEFAULT_BLACK_ROLE = 'dummy'

