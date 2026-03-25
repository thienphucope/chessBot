import time
import threading
import chess
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

try:
    from config import Config
except (ImportError, SyntaxError, AttributeError) as e:
    print(f"Warning: Error loading config.py ({e}). Using default config.")
    class Config:
        SECRET_KEY = 'fallback_secret'
        ASYNC_MODE = 'threading'
        DEBUG = True
        AI_THINKING_DELAY = 1.0

from engine.game_manager import game_engine
from engine.evaluator import evaluator
from algorithms import get_random_move, get_stockfish_move, get_alphabeta_move, get_mcts_move

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=Config.ASYNC_MODE)
ai_task_lock = threading.Lock()
ai_task_scheduled = False
ai_task_generation = 0
runtime_settings_lock = threading.Lock()
ai_thinking_delay = float(getattr(Config, 'AI_THINKING_DELAY', 0.5))

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# --- CORE LOGIC ---
def build_board_state(last_san=None, last_move_uci=None, annotation=None, evaluation=None, move_time=None, total_time=None, white_total_time=None, black_total_time=None):
    fen = game_engine.board.fen()
    if evaluation is None:
        evaluation = evaluator.get_eval(fen)

    if move_time is None:
        move_time = 0.0

    if total_time is None:
        total_time = game_engine.total_move_time

    if white_total_time is None:
        white_total_time = game_engine.white_total_time

    if black_total_time is None:
        black_total_time = game_engine.black_total_time

    return {
        'fen': fen,
        'last_move_san': last_san,
        'last_move_uci': last_move_uci,
        'move_annotation': annotation,
        'turn_count': game_engine.turn_count,
        'evaluation': round(evaluation, 2),
        'move_time': round(move_time, 2),
        'total_time': round(total_time, 2),
        'white_total_time': round(white_total_time, 2),
        'black_total_time': round(black_total_time, 2)
    }

def sync_board(last_san=None, last_move_uci=None, annotation=None, evaluation=None, move_time=None, total_time=None, white_total_time=None, black_total_time=None):
    socketio.emit('board_state', build_board_state(
        last_san=last_san,
        last_move_uci=last_move_uci,
        annotation=annotation,
        evaluation=evaluation,
        move_time=move_time,
        total_time=total_time,
        white_total_time=white_total_time,
        black_total_time=black_total_time
    ))

def get_ai_thinking_delay():
    with runtime_settings_lock:
        return ai_thinking_delay

def set_ai_thinking_delay(delay):
    global ai_thinking_delay
    with runtime_settings_lock:
        ai_thinking_delay = delay

def sync_runtime_settings():
    socketio.emit('ai_settings_sync', {
        'thinking_delay': round(get_ai_thinking_delay(), 2)
    })

def schedule_ai_turn():
    global ai_task_scheduled
    if not game_engine.is_ai_turn():
        return

    with ai_task_lock:
        if ai_task_scheduled:
            return
        ai_task_scheduled = True
        generation = ai_task_generation

    socketio.start_background_task(run_ai, generation)

def invalidate_ai_tasks():
    global ai_task_scheduled, ai_task_generation
    with ai_task_lock:
        ai_task_generation += 1
        ai_task_scheduled = False

def perform_turn(move_uci, schedule_next_ai=True, move_time=0.0):
    fen_before = game_engine.board.fen()
    eval_before = evaluator.get_eval(fen_before)

    success, san, turn = game_engine.apply_move(move_uci)
    if not success:
        return sync_board()

    eval_after = evaluator.get_eval(game_engine.board.fen())
    is_white_turn = (turn == chess.WHITE)
    total_time, white_total_time, black_total_time = game_engine.record_move_time(move_time, is_white_turn)
    game_engine.last_move_timestamp = time.perf_counter()

    if game_engine.board.is_checkmate():
        annotation = "!!"
    else:
        annotation = evaluator.get_annotation(eval_before, eval_after, turn)

    sync_board(
        last_san=san,
        last_move_uci=move_uci,
        annotation=annotation,
        evaluation=eval_after,
        move_time=move_time,
        total_time=total_time,
        white_total_time=white_total_time,
        black_total_time=black_total_time
    )

    if game_engine.board.is_game_over():
        res = game_engine.save_log()
        socketio.emit('game_over', {'result': res})
    elif schedule_next_ai and game_engine.is_ai_turn():
        schedule_ai_turn()

def run_ai(task_generation):
    global ai_task_scheduled

    try:
        while True:
            with ai_task_lock:
                if task_generation != ai_task_generation:
                    return

            if not game_engine.is_ai_turn():
                return

            time.sleep(get_ai_thinking_delay())

            with ai_task_lock:
                if task_generation != ai_task_generation:
                    return

            if not game_engine.is_ai_turn():
                return

            move_started_at = time.perf_counter()
            algo = game_engine.get_current_ai_algo()
            move_uci = None

            if algo == 'stockfish':
                move = get_stockfish_move(game_engine.board)
                if move:
                    move_uci = move.uci()
            elif algo == 'alphabeta':
                move = get_alphabeta_move(game_engine.board)
                if move:
                    move_uci = move.uci()
            elif algo == 'mcts':
                move = get_mcts_move(game_engine.board)
                if move:
                    move_uci = move.uci()
            else:  # dummy/random
                move = get_random_move(game_engine.board)
                if move:
                    move_uci = move.uci()

            move_time = time.perf_counter() - move_started_at

            if not move_uci:
                return

            perform_turn(
                move_uci,
                schedule_next_ai=False,
                move_time=move_time
            )
    finally:
        with ai_task_lock:
            if task_generation == ai_task_generation:
                ai_task_scheduled = False

@socketio.on('move')
def handle_player_move(data):
    if not game_engine.is_ai_turn():
        move_time = time.perf_counter() - game_engine.last_move_timestamp
        perform_turn(data.get('move'), move_time=move_time)

@socketio.on('connect')
def handle_connect():
    emit('board_state', build_board_state())
    emit('game_state_sync', {'is_running': game_engine.is_running})
    emit('ai_settings_sync', {'thinking_delay': round(get_ai_thinking_delay(), 2)})

@socketio.on('set_roles')
def handle_settings(data):
    game_engine.update_settings(white=data.get('white'), black=data.get('black'))

@socketio.on('toggle_game')
def handle_toggle(data):
    game_engine.update_settings(running=data.get('running'))
    if game_engine.is_ai_turn():
        schedule_ai_turn()

@socketio.on('reset')
def handle_reset():
    invalidate_ai_tasks()
    game_engine.reset()
    sync_board()
    socketio.emit('game_state_sync', {'is_running': False})

@socketio.on('set_ai_delay')
def handle_set_ai_delay(data):
    try:
        delay = float(data.get('delay'))
    except (TypeError, ValueError):
        emit('ai_settings_error', {'message': 'AI thinking delay khong hop le.'})
        return

    if delay < 0 or delay > 10:
        emit('ai_settings_error', {'message': 'AI thinking delay phai nam trong khoang 0-10 giay.'})
        return

    set_ai_thinking_delay(delay)
    sync_runtime_settings()

if __name__ == '__main__':
    socketio.run(app, debug=True)
