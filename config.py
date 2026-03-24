import os

class Config:
    # --- FLASK & SOCKETIO ---
    SECRET_KEY = 'chess_secret!'
    ASYNC_MODE = 'threading'
    DEBUG = True

    # --- STOCKFISH CONFIG ---
    STOCKFISH_PATH = os.path.join(os.getcwd(), "stockfish.exe")
    # Nếu không tìm thấy file .exe, dùng lệnh gọi hệ thống
    if not os.path.exists(STOCKFISH_PATH):
        STOCKFISH_PATH = "stockfish"

    SF_THREADS = 2
    SF_HASH = 256
    SF_DEPTH = 18   
    SF_AI_DEPTH = 3

    # --- GAME LOGIC ---
    LOG_DIR = "logs"
    AI_THINKING_DELAY = 0.5 # Giây (thời gian chờ giả lập)

    # --- DEFAULT ROLES ---
    DEFAULT_WHITE_ROLE = 'human'
    DEFAULT_BLACK_ROLE = 'dummy'
