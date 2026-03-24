from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chess_secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    """
    Hiển thị giao diện chính của bàn cờ.
    """
    return render_template('index.html')

if __name__ == '__main__':
    # Chạy server tại địa chỉ http://127.0.0.1:5000
    print("Server đang chạy tại http://127.0.0.1:5000")
    socketio.run(app, debug=True)
