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
    ALPHABETA_DEPTH = 4       # Tăng lên 5 để bot Alpha-Beta tính toán chắc chắn hơn
    MCTS_ITERATIONS = 5000     # Giảm số lần lặp nhưng mỗi lần lặp sẽ sâu hơn (Python chạy chậm nên 2000 là vừa)
    MCTS_MAX_DEPTH = 8       # Độ sâu 10 là đủ để MCTS không bị "ảo tưởng" quá xa
    MCTS_EVAL_DEPTH = 0       
    MCTS_TEMPERATURE = 0.0    # Cực kỳ thấp để bot chỉ chọn nước đi tốt nhất mà nó tìm được
    ALPHABETA_NOISE = 5.0     # Giảm nhiễu để bot không đi những nước "tầm bậy"




    LOG_DIR = "logs"
    AI_THINKING_DELAY = 0

    DEFAULT_WHITE_ROLE = 'alphabeta'
    DEFAULT_BLACK_ROLE = 'mcts'
