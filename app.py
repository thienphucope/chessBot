import time
import chess
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from engine.game_manager import game_engine
from algorithms.random_bot import get_random_move

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chess_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Lưu trạng thái vai trò của từng bên
game_state = {
    'white_role': 'human', # human, dummy, alpha_beta, mcts
    'black_role': 'dummy'
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('set_roles')
def handle_set_roles(data):
    game_state['white_role'] = data.get('white', 'human')
    game_state['black_role'] = data.get('black', 'dummy')
    print(f"Vai trò mới: Trắng={game_state['white_role']}, Đen={game_state['black_role']}")
    
    # Kiểm tra xem có cần Bot đi ngay không
    check_and_trigger_ai()

@socketio.on('move')
def handle_move(data):
    move_uci = data.get('move')
    if game_engine.make_move(move_uci):
        emit('board_state', {'fen': game_engine.get_fen()}, broadcast=True)
        if game_engine.is_game_over():
            process_game_over()
        else:
            check_and_trigger_ai()
    else:
        emit('board_state', {'fen': game_engine.get_fen()}, broadcast=False)

def check_and_trigger_ai():
    if game_engine.is_game_over():
        return

    turn = game_engine.board.turn # True: Trắng, False: Đen
    
    current_role = game_state['white_role'] if turn == chess.WHITE else game_state['black_role']
    
    if current_role != 'human':
        # Chạy AI trong background task
        socketio.start_background_task(target=trigger_ai_move, algo=current_role)

def trigger_ai_move(algo):
    """Gọi thuật toán AI dựa trên vai trò hiện tại."""
    time.sleep(0.6)
    board = game_engine.board
    
    move = None
    if algo == 'dummy':
        move = get_random_move(board)
    elif algo == 'alpha_beta':
        # move = get_alpha_beta_move(board)
        move = get_random_move(board) # Tạm thời
    elif algo == 'mcts':
        # move = get_mcts_move(board)
        move = get_random_move(board) # Tạm thời
        
    if move:
        move_uci = move.uci()
        if game_engine.make_move(move_uci):
            socketio.emit('board_state', {'fen': game_engine.get_fen()})
            print(f"Bot ({algo}) đi: {move_uci}")
            
            if game_engine.is_game_over():
                process_game_over()
            else:
                # Kiểm tra tiếp (trong trường hợp Bot đấu Bot)
                check_and_trigger_ai()

def process_game_over():
    result = game_engine.board.result()
    log_path = game_engine.save_log(result_text=result)
    socketio.emit('game_over', {'result': result, 'log': log_path})

@socketio.on('reset')
def handle_reset():
    game_engine.reset_game()
    emit('board_state', {'fen': game_engine.get_fen()}, broadcast=True)
    check_and_trigger_ai()

if __name__ == '__main__':
    socketio.run(app, debug=True)
