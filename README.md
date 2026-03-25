# Chess AI Duel: Alpha-Beta vs MCTS

Dự án xây dựng một môi trường chơi Cờ Vua tương tác, cho phép so sánh hiệu quả giữa hai thuật toán tìm kiếm phổ biến trong AI: **Alpha-Beta Pruning** và **Monte Carlo Tree Search (MCTS)**.

## Cài đặt (Installation)

1. Đảm bảo bạn có Python 3.11+ đã được cài đặt.
2. Clone repository: `git clone https://github.com/thienphucope/chessBot.git`
3. Di chuyển vào thư mục: `cd chessBot`

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

Các bot trong thư mục `algorithms/` nhận một đối tượng `chess.Board` làm tham số đầu vào. Đối tượng này chứa toàn bộ trạng thái bàn cờ hiện tại. Bạn có thể sử dụng các phương thức như:

- `board.fen()`: Lấy FEN string của bàn cờ
- `board.legal_moves`: Danh sách các nước đi hợp lệ
- `board.turn`: Lượt chơi hiện tại (chess.WHITE hoặc chess.BLACK)
- `board.is_check()`: Kiểm tra chiếu
- `board.is_checkmate()`: Kiểm tra chiếu hết
- `board.is_stalemate()`: Kiểm tra hòa do hết nước đi

Hàm bot phải trả về một `chess.Move` hoặc None nếu không có nước đi hợp lệ.

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
- [ ] **Alpha-Beta Engine:**
    - [ ] Cài đặt hàm `evaluate()` với Piece-Square Tables.
    - [ ] Cài đặt Minimax + Alpha-Beta Pruning.
    - [ ] Tối ưu hóa: Move Ordering.
- [ ] **MCTS Engine:**
    - [ ] Xây dựng cấu trúc cây (Selection, Expansion, Simulation, Backprop).
    - [ ] Cài đặt công thức UCB1.

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
