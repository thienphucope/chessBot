import time
import chess
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Thử nạp Config, nếu lỗi dùng fallback để server không sập
try:
    from config import Config
except (ImportError, SyntaxError, AttributeError) as e:
    print(f"⚠️ Cảnh báo: Lỗi nạp config.py ({e}). Đang dùng cấu hình mặc định.")
    class Config:
        SECRET_KEY = 'fallback_secret'
        ASYNC_MODE = 'threading'
        DEBUG = True
        AI_THINKING_DELAY = 1.0

from engine.game_manager import game_engine
from engine.evaluator import evaluator
from algorithms.random_bot import get_random_move

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=Config.ASYNC_MODE)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# --- CORE LOGIC ---
def sync_board(last_san=None, annotation=None):
    fen = game_engine.board.fen()
    eval_val = evaluator.get_eval(fen)
    socketio.emit('board_state', {
        'fen': fen,
        'last_move_san': last_san,
        'move_annotation': annotation,
        'turn_count': game_engine.turn_count,
        'evaluation': round(eval_val, 2)
    })

def perform_turn(move_uci):
    fen_before = game_engine.board.fen()
    eval_before = evaluator.get_eval(fen_before)
    
    success, san, turn = game_engine.apply_move(move_uci)
    if not success: return sync_board()

    if game_engine.board.is_checkmate():
        annotation = "!!"
    else:
        eval_after = evaluator.get_eval(game_engine.board.fen())
        annotation = evaluator.get_annotation(eval_before, eval_after, turn)
    
    sync_board(last_san=san, annotation=annotation)
    
    if game_engine.board.is_game_over():
        res = game_engine.save_log()
        socketio.emit('game_over', {'result': res})
    elif game_engine.is_ai_turn():
        socketio.start_background_task(run_ai)

def run_ai():
    # Sử dụng giá trị từ Config, nếu Config đang lỗi thì dùng AI_THINKING_DELAY mặc định
    delay = getattr(Config, 'AI_THINKING_DELAY', 0.5)
    time.sleep(delay)
    
    if not game_engine.is_ai_turn(): return
    algo = game_engine.get_current_ai_algo()
    move_uci = None

    if algo == 'stockfish':
        ai_depth = getattr(Config, 'SF_AI_DEPTH', 15)
        move_uci = evaluator.get_best_move(game_engine.board.fen(), depth=ai_depth)
    else:
        move = get_random_move(game_engine.board)
        if move: move_uci = move.uci()

    if move_uci:
        perform_turn(move_uci)

# --- SOCKET HANDLERS ---
@socketio.on('move')
def handle_player_move(data):
    if not game_engine.is_ai_turn(): perform_turn(data.get('move'))

@socketio.on('set_roles')
def handle_settings(data):
    game_engine.update_settings(white=data.get('white'), black=data.get('black'))
    if game_engine.is_ai_turn(): socketio.start_background_task(run_ai)

@socketio.on('toggle_game')
def handle_toggle(data):
    game_engine.update_settings(running=data.get('running'))
    if game_engine.is_ai_turn(): socketio.start_background_task(run_ai)

@socketio.on('reset')
def handle_reset():
    game_engine.reset()
    sync_board()
    socketio.emit('game_state_sync', {'is_running': False})

if __name__ == '__main__':
    # Đảm bảo Debug luôn bật để reloader hoạt động
    socketio.run(app, debug=True)
