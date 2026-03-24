import time
import threading
import chess
from flask import Flask, render_template
from flask_socketio import SocketIO
from engine.game_manager import game_engine
from algorithms.random_bot import get_random_move
from stockfish import Stockfish

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chess_secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- CẤU HÌNH STOCKFISH ---
import os
STOCKFISH_PATH = os.path.join(os.getcwd(), "stockfish.exe")
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = "stockfish"

try:
    sf_judge = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2})
    sf_judge.set_depth(15)
    print(f"✅ Stockfish (Judge) đã sẵn sàng! Path: {STOCKFISH_PATH}")
except Exception as e:
    print(f"⚠️ Không khởi động được Stockfish tại '{STOCKFISH_PATH}': {e}")
    sf_judge = None

sf_lock = threading.Lock()

game_state = {
    'white_role': 'human',
    'black_role': 'dummy',
    'is_running': False,
    'turn_count': 0
}

# --- HELPERS ---
def _parse_eval(eval_result):
    """Parse kết quả Stockfish về float, clamp về [-20, 20]."""
    if eval_result['type'] == 'cp':
        return max(-20.0, min(20.0, eval_result['value'] / 100.0))
    return 20.0 if eval_result['value'] > 0 else -20.0

def get_stockfish_eval(fen):
    """Lấy điểm đánh giá từ Stockfish. Thread-safe."""
    if not sf_judge:
        return 0.0
    with sf_lock:
        try:
            sf_judge.set_fen_position(fen)
            return _parse_eval(sf_judge.get_evaluation())
        except Exception:
            return 0.0

def get_both_evals(fen_before, fen_after):
    """
    Lấy eval_before VÀ eval_after trong một lock duy nhất.
    Tránh thread khác chen vào giữa 2 lần gọi làm sai kết quả.
    """
    if not sf_judge:
        return 0.0, 0.0
    with sf_lock:
        try:
            sf_judge.set_fen_position(fen_before)
            e_before = _parse_eval(sf_judge.get_evaluation())
            sf_judge.set_fen_position(fen_after)
            e_after = _parse_eval(sf_judge.get_evaluation())
            return e_before, e_after
        except Exception:
            return 0.0, 0.0

def get_move_annotation(eval_before, eval_after, turn):
    """
    Phân loại nước đi theo delta eval.
    Eval luôn theo góc White: dương = White có lợi.
    """
    delta = (eval_after - eval_before) if turn == chess.WHITE else (eval_before - eval_after)

    if delta >= 2.0:  return "!!"
    if delta >= 0.5:  return "!"
    if delta >= 0.2:  return "!?"
    if delta <= -3.0: return "??"
    if delta <= -1.5: return "?"
    if delta <= -0.5: return "?!"
    return None

def process_move_result(success, fen_before, fen_after, turn_before, san):
    """Tính annotation và broadcast sau khi nước đi thành công."""
    if not success:
        broadcast_board()
        return

    game_state['turn_count'] += 1

    if game_engine.is_checkmate():
        annotation = "!!"
    else:
        eval_before, eval_after = get_both_evals(fen_before, fen_after)
        annotation = get_move_annotation(eval_before, eval_after, turn_before)

    broadcast_board(last_move_san=san, move_annotation=annotation)

    if game_engine.is_game_over():
        process_game_over()
    elif game_state['is_running']:
        check_and_trigger_ai()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# --- SOCKET.IO EVENTS ---
@socketio.on('set_roles')
def handle_set_roles(data):
    game_state['white_role'] = data.get('white', 'human')
    game_state['black_role'] = data.get('black', 'dummy')
    check_and_trigger_ai()

@socketio.on('toggle_game')
def handle_toggle(data):
    game_state['is_running'] = data.get('running', False)
    if game_state['is_running']:
        check_and_trigger_ai()

@socketio.on('move')
def handle_move(data):
    move_uci = data.get('move')
    try:
        # Lấy SAN trước khi push
        san = game_engine.get_san(move_uci)
        # make_move trả về (success, fen_before, fen_after, turn_before) — atomic
        success, fen_before, fen_after, turn_before = game_engine.make_move(move_uci)
        process_move_result(success, fen_before, fen_after, turn_before, san)
    except Exception as e:
        print(f"⚠️ Lỗi handle_move: {e}")
        broadcast_board()

def check_and_trigger_ai():
    if not game_state['is_running'] or game_engine.is_game_over():
        return
    turn = game_engine.get_turn()
    current_role = game_state['white_role'] if turn == chess.WHITE else game_state['black_role']
    if current_role != 'human':
        socketio.start_background_task(trigger_ai_move, current_role)

def trigger_ai_move(algo):
    time.sleep(0.5)
    if not game_state['is_running'] or game_engine.is_game_over():
        return

    legal_moves = game_engine.get_legal_moves()
    import random
    move = random.choice(legal_moves) if legal_moves else None

    if move:
        try:
            san = game_engine.get_san(move.uci())
            success, fen_before, fen_after, turn_before = game_engine.make_move(move.uci())
            process_move_result(success, fen_before, fen_after, turn_before, san)
        except Exception as e:
            print(f"⚠️ Lỗi trigger_ai_move: {e}")

def broadcast_board(last_move_san=None, move_annotation=None):
    fen = game_engine.get_fen()
    eval_score = get_stockfish_eval(fen)
    socketio.emit('board_state', {
        'fen': fen,
        'last_move_san': last_move_san,
        'move_annotation': move_annotation,
        'turn_count': game_state['turn_count'],
        'evaluation': round(eval_score, 2)
    })

def process_game_over():
    result = game_engine.board.result()
    game_engine.save_log(result_text=result)
    socketio.emit('game_over', {'result': result})

@socketio.on('reset')
def handle_reset():
    game_engine.reset_game()
    game_state['turn_count'] = 0
    game_state['is_running'] = False
    broadcast_board()
    socketio.emit('game_state_sync', {'is_running': False})

if __name__ == '__main__':
    socketio.run(app, debug=True)