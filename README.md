# Chess AI Duel: Alpha-Beta vs MCTS

Dự án xây dựng một môi trường chơi Cờ Vua tương tác, cho phép so sánh hiệu quả giữa hai thuật toán tìm kiếm phổ biến trong AI: **Alpha-Beta Pruning** và **Monte Carlo Tree Search (MCTS)**.

## Cài đặt (Installation)

1. Đảm bảo bạn có Python 3.11+ đã được cài đặt.
2. Clone repository: `git clone https://github.com/thienphucope/chessBot.git`
3. Di chuyển vào thư mục: `cd chessBot`

### Cài đặt Stockfish (Bắt buộc cho bot và evaluator)
Để sử dụng Stockfish bot và evaluator, bạn cần tải và cấu hình Stockfish engine:

1. Tải Stockfish từ: [https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows-x86-64-avx2.zip](https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows-x86-64-avx2.zip)
2. Giải nén file ZIP đã tải.
3. Sao chép đường dẫn đến file `stockfish.exe` (sau khi giải nén).
4. Mở file `config.py` và cập nhật biến `STOCKFISH_PATH` với đường dẫn đã sao chép. Ví dụ:
   ```python
   STOCKFISH_PATH = "C:\\path\\to\\stockfish.exe"
   ```
   Hoặc đặt `stockfish.exe` trực tiếp trong thư mục gốc của dự án để sử dụng cấu hình mặc định.

### Sử dụng uv (khuyến nghị):
4. Cài đặt uv nếu chưa có: `pip install uv`
5. Cài đặt dependencies: `uv sync`
6. Chạy server: `uv run python app.py`

### Hoặc sử dụng pip:
4. Cài đặt dependencies: `pip install -e .`
5. Chạy server: `python app.py`

7. Truy cập: `http://127.0.0.1:5000`

## Cách hoạt động của code (How the code works)

Ứng dụng sử dụng Flask server với SocketIO để quản lý trò chơi cờ vua thời gian thực. GameManager trong `engine/game_manager.py` quản lý trạng thái bàn cờ sử dụng thư viện `python-chess`. Frontend sử dụng Chessboard.js để hiển thị giao diện và đồng bộ với server qua SocketIO. Khi đến lượt AI, server gọi các thuật toán trong `algorithms/` để tính toán nước đi. Các bot nhận đối tượng `chess.Board` và trả về nước đi hợp lệ.

## Cách nhận state bàn cờ để implement bot ở algorithms/ (How to get board state for implementing bots in algorithms/)

### Sử dụng đối tượng chess.Board
Các bot trong thư mục `algorithms/` nhận một đối tượng `chess.Board` làm tham số đầu vào. Đối tượng này chứa toàn bộ trạng thái bàn cờ hiện tại và cung cấp các phương thức hữu ích:

#### Các phương thức quan trọng của chess.Board:

**Trạng thái bàn cờ:**
- `board.fen()`: Lấy FEN string của bàn cờ
- `board.epd()`: Lấy EPD string (Extended Position Description)
- `board.turn`: Lượt chơi hiện tại (chess.WHITE hoặc chess.BLACK)
- `board.fullmove_number`: Số nước đi đầy đủ
- `board.halfmove_clock`: Số nước đi không ăn quân hoặc di chuyển tốt
- `board.ply()`: Số ply (nửa nước đi) đã chơi

**Nước đi:**
- `board.legal_moves`: Generator các nước đi hợp lệ
- `board.pseudo_legal_moves`: Generator các nước đi pseudo-legal (không kiểm tra chiếu)
- `board.generate_legal_moves()`: Generator nước đi hợp lệ (tương tự legal_moves)
- `board.generate_pseudo_legal_moves()`: Generator nước đi pseudo-legal
- `board.is_legal(move)`: Kiểm tra nước đi có hợp lệ không
- `board.is_pseudo_legal(move)`: Kiểm tra nước đi pseudo-legal
- `board.parse_san(san)`: Parse nước đi từ Standard Algebraic Notation
- `board.parse_uci(uci)`: Parse nước đi từ UCI notation
- `board.san(move)`: Chuyển nước đi thành SAN string
- `board.uci(move)`: Chuyển nước đi thành UCI string
- `board.lan(move)`: Chuyển nước đi thành LAN string

**Kết thúc ván cờ:**
- `board.is_check()`: Kiểm tra chiếu
- `board.is_checkmate()`: Kiểm tra chiếu hết
- `board.is_stalemate()`: Kiểm tra hết nước đi
- `board.is_insufficient_material()`: Kiểm tra thiếu quân
- `board.is_game_over()`: Kiểm tra ván cờ kết thúc
- `board.is_fifty_moves()`: Kiểm tra quy tắc 50 nước
- `board.is_repetition()`: Kiểm tra lặp lại vị trí
- `board.outcome()`: Kết quả ván cờ (chess.Outcome object)
- `board.result()`: Kết quả ván cờ string ('1-0', '0-1', '1/2-1/2', '*')
- `board.can_claim_draw()`: Có thể đòi hòa không
- `board.can_claim_fifty_moves()`: Có thể đòi hòa 50 nước
- `board.can_claim_threefold_repetition()`: Có thể đòi hòa lặp lại

**Quân cờ và vị trí:**
- `board.piece_at(square)`: Quân cờ tại ô (chess.Piece hoặc None)
- `board.piece_type_at(square)`: Loại quân tại ô (chess.PAWN, chess.KNIGHT, v.v.)
- `board.color_at(square)`: Màu quân tại ô (chess.WHITE, chess.BLACK, hoặc None)
- `board.piece_map()`: Dict của tất cả quân trên bàn {square: piece}
- `board.pieces(piece_type, color)`: Set các ô chứa quân chỉ định
- `board.king(color)`: Vị trí vua của màu chỉ định

**Thực hiện nước đi:**
- `board.push(move)`: Thực hiện nước đi
- `board.pop()`: Hoàn tác nước đi cuối
- `board.peek()`: Xem nước đi cuối mà không pop
- `board.push_san(san)`: Thực hiện nước đi từ SAN
- `board.push_uci(uci)`: Thực hiện nước đi từ UCI
- `board.san_and_push(move)`: Thực hiện nước đi và trả về SAN
- `board.copy()`: Sao chép bàn cờ

**Thông tin nước đi:**
- `board.is_capture(move)`: Nước đi có ăn quân không
- `board.is_en_passant(move)`: Nước đi bắt tốt qua đường
- `board.is_castling(move)`: Nước đi nhập thành
- `board.is_promotion(move)`: Nước đi phong cấp
- `board.is_kingside_castling(move)`: Nước đi nhập thành cánh vua
- `board.is_queenside_castling(move)`: Nước đi nhập thành cánh hậu
- `board.promoted_to(move)`: Quân được phong cấp thành gì
- `board.gives_check(move)`: Nước đi có chiếu không
- `board.is_into_check(move)`: Nước đi có tự đưa vào chiếu không
- `board.was_into_check()`: Nước đi cuối có đưa vào chiếu không

**Quyền đặc biệt:**
- `board.has_kingside_castling_rights(color)`: Quyền nhập thành cánh vua
- `board.has_queenside_castling_rights(color)`: Quyền nhập thành cánh hậu
- `board.has_castling_rights(color)`: Có quyền nhập thành không
- `board.clean_castling_rights()`: Xóa quyền nhập thành không hợp lệ
- `board.has_legal_en_passant()`: Có nước bắt tốt qua đường hợp lệ
- `board.has_pseudo_legal_en_passant()`: Có nước bắt tốt qua đường pseudo-legal

**Kiểm tra tấn công:**
- `board.is_attacked_by(color, square)`: Ô có bị tấn công bởi màu không
- `board.attackers(color, square)`: Set các ô tấn công square
- `board.attacks(square)`: Set các ô bị tấn công từ square
- `board.is_pinned(color, square)`: Quân có bị ghim không
- `board.pin(color, square)`: Quân ghim tại square (nếu có)
- `board.checkers()`: Set các quân đang chiếu vua

**Chuyển đổi và thao tác bàn cờ:**
- `board.mirror()`: Lật bàn cờ (trắng thành đen và ngược lại)
- `board.transform(transform)`: Áp dụng phép biến đổi
- `board.apply_transform(transform)`: Áp dụng và trả về bàn cờ mới
- `board.clear()`: Xóa toàn bộ bàn cờ
- `board.reset()`: Đặt lại về vị trí bắt đầu
- `board.set_fen(fen)`: Đặt bàn cờ từ FEN
- `board.set_piece_at(square, piece)`: Đặt quân tại ô
- `board.remove_piece_at(square)`: Gỡ quân tại ô

**Thông tin bàn cờ:**
- `board.status()`: Trạng thái bàn cờ (chess.Status)
- `board.ep_square`: Ô en passant (hoặc None)
- `board.castling_rights`: Bitmask quyền nhập thành
- `board.is_valid()`: Bàn cờ có hợp lệ không
- `board.unicode()`: Biểu diễn bàn cờ bằng Unicode

#### Làm việc với FEN:
FEN là chuỗi ký tự mô tả đầy đủ trạng thái bàn cờ. Ví dụ: `"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"`

- **Vị trí quân cờ**: Phần đầu tiên, dùng ký tự để đại diện quân (r=Rook, n=Knight, b=Bishop, q=Queen, k=King, p=Pawn)
- **Lượt chơi**: `w` (trắng) hoặc `b` (đen)
- **Quyền nhập thành**: KQkq (King và Queen side cho cả hai màu)
- **Nước đi en passant**: `-` hoặc ô đích
- **Halfmove clock**: Số nước đi không ăn quân hoặc di chuyển tốt
- **Fullmove number**: Số nước đi đầy đủ

#### Ví dụ lập trình bot đơn giản:
```python
import chess
import random

def get_my_bot_move(board: chess.Board):
    """
    Bot đơn giản: Ưu tiên ăn quân, nếu không thì đi ngẫu nhiên.
    
    Args:
        board (chess.Board): Trạng thái bàn cờ hiện tại
        
    Returns:
        chess.Move: Nước đi được chọn
    """
    # Lấy FEN để log hoặc debug
    current_fen = board.fen()
    print(f"Current position: {current_fen}")
    
    # Tìm nước đi ăn quân
    for move in board.legal_moves:
        if board.is_capture(move):
            return move
    
    # Nếu không có nước ăn, đi ngẫu nhiên
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves) if legal_moves else None
```

#### Sử dụng evaluator để đánh giá vị trí:
```python
from engine.evaluator import evaluator

def get_evaluated_move(board: chess.Board):
    """Bot sử dụng Stockfish để đánh giá."""
    best_eval = -float('inf')
    best_move = None
    
    for move in board.legal_moves:
        board.push(move)
        eval_score = evaluator.get_eval(board.fen())
        board.pop()
        
        if eval_score > best_eval:
            best_eval = eval_score
            best_move = move
    
    return best_move
```

Hàm bot phải trả về một `chess.Move` hoặc None nếu không có nước đi hợp lệ.

## Hướng dẫn hiện thực thuật toán đánh giá (Evaluation Algorithm)

Thuật toán đánh giá (evaluation function) là hàm quan trọng nhất trong các thuật toán tìm kiếm như Alpha-Beta hay MCTS. Nó đánh giá mức độ tốt của một vị trí bàn cờ từ góc nhìn của một bên chơi.

### Cấu trúc hàm đánh giá

Hàm đánh giá trong `engine/simple_eval.py` bao gồm:
1. **Giá trị quân cờ (Material values)**: Định giá tương đối cho từng loại quân
2. **Bảng vị trí quân cờ (Piece-Square Tables)**: Thưởng/phạt dựa trên vị trí của từng quân

### Các thành phần chính

```python
# Giá trị quân cờ (centipawns)
_PIECE_VAL = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:     0,
}

# Bảng vị trí (ví dụ cho tốt) - index 0=a8, 63=h1
_PST = {
    chess.PAWN: [
         0,  0,  0,  0,  0,  0,  0,  0,  # a8-h8
        50, 50, 50, 50, 50, 50, 50, 50,  # a7-h7
        # ... (các hàng khác)
    ],
    # Tương tự cho các quân khác
}
```

### Hàm đánh giá chính

```python
def simple_eval(board: chess.Board) -> float:
    """
    Đánh giá vị trí từ góc nhìn trắng (centipawns).
    Dương = trắng tốt hơn, Âm = đen tốt hơn.
    """
    if board.is_checkmate():
        return -100_000 if board.turn == chess.WHITE else 100_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    score = 0
    for sq, piece in board.piece_map().items():
        # PST index: 63 - sq để chuyển từ a1→63 sang a8→0
        pst_index = 63 - sq
        if piece.color == chess.WHITE:
            score += _PIECE_VAL[piece.piece_type] + _PST[piece.piece_type][pst_index]
        else:
            # Đen lật ngược bàn cờ
            mirrored = chess.square_mirror(sq)
            pst_index = 63 - mirrored
            score -= _PIECE_VAL[piece.piece_type] + _PST[piece.piece_type][pst_index]

    return float(score)
```

### Giải thích

1. **Xử lý kết thúc ván**: Chiếu hết = ±100,000, hòa = 0
2. **Tính điểm**: Duyệt qua tất cả quân, cộng/trừ giá trị + vị trí
3. **Piece-Square Tables**: Sử dụng `63 - sq` để map square sang index PST
4. **Đối xứng**: Đen sử dụng `chess.square_mirror()` để lật bàn cờ

Xem `engine/simple_eval.py` để có bảng PST đầy đủ cho tất cả quân cờ.

## Các API và lớp bổ sung trong python-chess

Ngoài các phương thức của `chess.Board`, thư viện còn cung cấp các lớp và hàm tiện ích quan trọng:

### Lớp Move (chess.Move)
```python
# Tạo nước đi
move = chess.Move.from_uci("e2e4")  # Từ UCI string
move = chess.Move(chess.E2, chess.E4)  # Từ ô nguồn và đích

# Thuộc tính của Move
move.from_square    # Ô nguồn (0-63)
move.to_square      # Ô đích (0-63)
move.promotion      # Quân phong cấp (None hoặc piece_type)
move.drop           # Quân thả (cho variant)

# Chuyển đổi
move.uci()          # "e2e4"
move.xboard()       # Chuyển sang xboard notation
```

### Lớp Piece (chess.Piece)
```python
# Tạo quân cờ
piece = chess.Piece(chess.PAWN, chess.WHITE)
piece = chess.Piece.from_symbol("P")  # Từ ký hiệu

# Thuộc tính
piece.piece_type    # Loại quân (PAWN, KNIGHT, v.v.)
piece.color         # Màu (WHITE, BLACK)

# Chuyển đổi
piece.symbol()      # "P", "p", "N", "n", v.v.
piece.unicode_symbol()  # ♟, ♞, v.v.
```

### Hằng số quan trọng
```python
# Màu sắc
chess.WHITE         # True
chess.BLACK         # False
chess.COLORS        # [False, True]

# Loại quân
chess.PAWN          # 1
chess.KNIGHT        # 2
chess.BISHOP        # 3
chess.ROOK          # 4
chess.QUEEN         # 5
chess.KING          # 6
chess.PIECE_TYPES   # [1, 2, 3, 4, 5, 6]

# Ô cờ
chess.A1, chess.H1, chess.A8, chess.H8  # 0, 7, 56, 63
chess.SQUARES       # range(0, 64)
chess.SQUARE_NAMES  # ["a1", "b1", ..., "h8"]
```

### Hàm tiện ích
```python
# Chuyển đổi ô
chess.parse_square("e4")  # 28
chess.square_name(28)     # "e4"
chess.square(4, 3)        # e4 (file=4, rank=3)

# Ký hiệu quân cờ
chess.piece_symbol(chess.PAWN)    # "p"
chess.piece_name(chess.QUEEN)     # "queen"

# Thao tác bitboard
chess.lsb(bb)        # Least significant bit
chess.msb(bb)        # Most significant bit
chess.popcount(bb)   # Đếm số bit 1

# Ray và attack
chess.ray(chess.E4, chess.E8)     # Các ô trên đường thẳng
chess.between(chess.E4, chess.E8) # Các ô giữa hai ô
```

### Lớp SquareSet (chess.SquareSet)
```python
# Tạo SquareSet
squares = chess.SquareSet()
squares.add(chess.E4)
squares.add(chess.E5)

# Thao tác
squares.remove(chess.E4)
chess.E4 in squares        # True/False
len(squares)               # Số ô
list(squares)              # List các ô

# Phép toán tập hợp
squares1 | squares2        # Hợp
squares1 & squares2        # Giao
squares1 - squares2        # Hiệu
```

### Lớp Outcome (chess.Outcome)
```python
# Kết quả ván cờ
outcome = board.outcome()
if outcome:
    outcome.winner      # chess.WHITE, chess.BLACK, hoặc None
    outcome.termination # Lý do kết thúc
```

### Các hàm biến đổi bàn cờ
```python
# Lật bàn cờ
board.mirror()              # Lật theo chiều ngang
chess.flip_vertical(bb)     # Lật bitboard theo chiều dọc
chess.flip_horizontal(bb)   # Lật bitboard theo chiều ngang
chess.flip_diagonal(bb)     # Lật theo đường chéo chính
```

## Hướng dẫn hiện thực thuật toán xây dựng cây tìm kiếm (Search Tree Building Algorithm)

Thuật toán MCTS (Monte Carlo Tree Search) xây dựng cây tìm kiếm động gồm 4 giai đoạn: Selection, Expansion, Simulation, Backpropagation.

### Lớp MCTSNode

```python
class MCTSNode:
    __slots__ = ('board', 'parent', 'move', 'children', 'visits', 'value', 'untried_moves')

    def __init__(self, board: chess.Board, parent=None, move=None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.children: list['MCTSNode'] = []
        self.visits: int = 0
        self.value: float = 0.0
        self.untried_moves = list(board.legal_moves)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def uct_score(self, c_param: float = 1.4) -> float:
        if self.visits == 0:
            return float('inf')
        exploitation = self.value / self.visits
        exploration = c_param * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def best_child(self, c_param: float = 1.4) -> 'MCTSNode':
        return max(self.children, key=lambda c: c.uct_score(c_param))

    def expand(self) -> 'MCTSNode':
        move = self.untried_moves.pop()
        new_board = self.board.copy()
        new_board.push(move)
        child = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child)
        return child
```

### Hàm mô phỏng (Simulation)

```python
def _simulate(board: chess.Board, max_moves: int = 50) -> float:
    sim = board.copy()
    for _ in range(max_moves):
        if sim.is_game_over():
            break
        sim.push(random.choice(list(sim.legal_moves)))

    if sim.is_game_over():
        result = sim.result()
        if result == '1-0':
            return 1.0
        elif result == '0-1':
            return -1.0
        return 0.0

    return math.tanh(simple_eval(sim) / 5.0)
```

### Một vòng lặp MCTS

```python
def _mcts_iteration(root: MCTSNode) -> None:
    # Selection
    node = root
    while node.is_fully_expanded() and node.children:
        node = node.best_child()

    # Expansion
    if not node.is_fully_expanded() and not node.board.is_game_over():
        node = node.expand()

    # Simulation
    white_score = _simulate(node.board)

    # Backpropagation
    current = node
    while current is not None:
        current.visits += 1
        if current.parent is not None:
            if current.parent.board.turn == chess.WHITE:
                current.value += white_score
            else:
                current.value += -white_score
        current = current.parent
```

### Hàm tìm kiếm chính

```python
def mcts_search(root: MCTSNode, iterations: int = 800) -> None:
    for _ in range(iterations):
        _mcts_iteration(root)

def get_mcts_move(board: chess.Board, iterations: int = 800) -> chess.Move | None:
    if board.is_game_over():
        return None

    root = MCTSNode(board)
    legal = list(root.untried_moves)
    if not legal:
        return None
    if len(legal) == 1:
        return legal[0]

    mcts_search(root, iterations)

    if not root.children:
        return random.choice(legal)

    return root.best_child(c_param=0).move
```

### Giải thích

1. **MCTSNode**: Lưu trạng thái bàn cờ và thống kê (visits, value)
2. **Selection**: Chọn đường đi tốt nhất bằng UCB1
3. **Expansion**: Mở rộng node mới khi cần
4. **Simulation**: Chơi ngẫu nhiên và đánh giá kết quả
5. **Backpropagation**: Lan truyền kết quả lên trên

Xem `algorithms/template_mcts.py` để có hiện thực đầy đủ.

## Tính năng đã hoàn thành
- **Giao diện Chess.com Style:** Cho phép chọn vai trò (Người hoặc Bot với các thuật toán khác nhau) riêng biệt cho cả quân Trắng và quân Đen.
- **Chạy Offline 100%:** Toàn bộ thư viện (JQuery, Chessboard.js, Chess.js) và bộ ảnh quân cờ đã được tích hợp nội bộ, không phụ thuộc internet khi demo.
- **Hệ thống Logging chuyên nghiệp:** Tự động xuất file lịch sử ván cờ định dạng `.pgn` vào thư mục `logs/` sau mỗi trận đấu.
- **Đồng bộ thời gian thực:** Sử dụng Socket.io để truyền nhận nước đi giữa trình duyệt và server Python.
- **Dummy Bot:** Bot ngẫu nhiên để kiểm tra luồng xử lý và kết nối.

---

## Công nghệ sử dụng (Tech Stack)

### Backend (AI & Logic)
- **Ngôn ngữ:** Python 3.11+ (Quản lý bởi `uv`).
- **Thư viện Logic:** `python-chess` (Xử lý luật chơi, PGN).
- **Server:** `Flask` + `Flask-SocketIO` + `eventlet`.

### Frontend (Giao diện)
- **Engine bàn cờ:** `Chessboard.js` (Bản ổn định cao).
- **Logic Client:** `chess.js` (Đảm bảo đồng bộ trạng thái bàn cờ).
- **Styling:** CSS3 tối giản theo phong cách Lichess/Chess.com.

---

## Kiến trúc hệ thống
```text
[ Trình duyệt (Frontend) ] <--- Socket.io ---> [ Flask Server (app.py) ]
          |                                             |
   (Chessboard.js UI)                          (engine/game_manager.py)
          |                                             |
   (chess.js sync)                             (algorithms/*.py)
          |                                             |
          |                                      (engine/evaluator.py)
          |                                             |
          +------------------------------------> [ Stockfish Engine ]
```

---

## Lộ trình thực hiện (Roadmap)

### Giai đoạn 1: Cơ sở hạ tầng (Done)
- [x] Khởi tạo dự án với `uv` và cấu trúc modular.
- [x] Xây dựng Flask Server và kết nối Socket.io.
- [x] Tích hợp bàn cờ Offline với đầy đủ quân cờ.
- [x] Triển khai `GameManager` để quản lý logic và lưu Log PGN.
- [x] Dummy Bot (Random) hoàn thành.

### Giai đoạn 2: Phát triển AI (Đang thực hiện)
- [x] **Stockfish Integration:**
    - [x] Tích hợp Stockfish engine qua python-stockfish.
    - [x] Xây dựng evaluator với khả năng đánh giá vị trí và tìm nước đi tốt nhất.
    - [x] Triển khai Stockfish bot sử dụng FEN để giao tiếp.
- [x] **Alpha-Beta Engine:**
    - [x] Cài đặt hàm `evaluate()` với Piece-Square Tables.
    - [x] Cài đặt Minimax + Alpha-Beta Pruning.
    - [x] Tối ưu hóa: Move Ordering, Transposition Table, Quiescence Search.
- [x] **MCTS Engine:**
    - [x] Xây dựng cấu trúc cây (Selection, Expansion, Simulation, Backprop).
    - [x] Cài đặt công thức UCB1.

### Giai đoạn 3: Hoàn thiện & Báo cáo
- [ ] Chạy ván đấu AI vs AI để thu thập dữ liệu so sánh.
- [ ] Viết báo cáo chi tiết về hiệu suất và chiến thuật.

---

## Quy tắc viết code (Coding Standards)
- **Chú thích:** Tất cả các hàm phải có `"""Docstring"""` mô tả Args và Returns.
- **Modular:** AI nằm trong `algorithms/`, Logic nằm trong `engine/`.

---

## Hướng dẫn chạy nhanh
1. **Cài đặt uv (nếu chưa có):** `pip install uv`
2. **Chạy server:** `uv run python app.py`
3. **Truy cập:** `http://127.0.0.1:5000`
