# ♟️ Chess AI Duel: Alpha-Beta vs MCTS

Dự án xây dựng một môi trường chơi Cờ Vua tương tác, cho phép so sánh hiệu quả giữa hai thuật toán tìm kiếm phổ biến trong AI: **Alpha-Beta Pruning** và **Monte Carlo Tree Search (MCTS)**.

## 🌟 Tính năng chính
- **Giao diện hiện đại:** Sử dụng **Chessground** (engine bàn cờ của Lichess) cho trải nghiệm mượt mà, hỗ trợ kéo thả và hiệu ứng di chuyển.
- **Hai "não bộ" AI:**
    - **Alpha-Beta Bot:** Tối ưu hóa thuật toán Minimax với hàm lượng giá (Heuristic) dựa trên vị trí và giá trị quân cờ.
    - **MCTS Bot:** Thuật toán tìm kiếm cây Monte Carlo dựa trên mô phỏng ngẫu nhiên (Rollouts).
- **Chế độ chơi đa dạng:** 
    - Người vs AI (Chọn 1 trong 2 thuật toán).
    - AI vs AI (Alpha-Beta đấu với MCTS).
- **Bảng so sánh thời gian thực:** Hiển thị thời gian suy nghĩ, số lượng Node đã duyệt và điểm số đánh giá bàn cờ.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)

### Backend (AI & Logic)
- **Ngôn ngữ:** Python 3.x
- **Thư viện Logic:** `python-chess` (Xử lý luật chơi, FEN, PGN).
- **Server:** `Flask` + `Flask-SocketIO` (Giao tiếp thời gian thực giữa Python và Web).

### Frontend (Giao diện)
- **Engine bàn cờ:** `Chessground` (JavaScript/TypeScript).
- **Logic Client:** `chess.js` (Đảm bảo đồng bộ trạng thái bàn cờ với Backend).
- **Styling:** CSS3 (Lichess theme).

---

## 🏗️ Kiến trúc hệ thống
```text
[ Người dùng (Browser) ] <--- Socket.io ---> [ Flask Server (Python) ]
         |                                          |
   (Chessground UI)                          (python-chess logic)
         |                                          |
   (chess.js sync)                          (Alpha-Beta / MCTS)
```

---

## 📅 Lộ trình thực hiện (Roadmap)

### Giai đoạn 1: Core AI & Logic (Backend)
- [ ] Thiết lập môi trường Python và cài đặt `python-chess`.
- [ ] **Alpha-Beta Engine:**
    - Cài đặt hàm `evaluate()` với Piece-Square Tables.
    - Cài đặt Minimax + Alpha-Beta Pruning.
    - Tối ưu hóa: Move Ordering (ưu tiên các nước ăn quân).
- [ ] **MCTS Engine:**
    - Xây dựng cấu trúc cây (Selection, Expansion, Simulation, Backprop).
    - Cài đặt công thức UCB1.

### Giai đoạn 2: Giao tiếp & Web API
- [ ] Xây dựng Flask Server với các Endpoint/Socket nhận nước đi.
- [ ] Viết hàm chuyển đổi dữ liệu giữa `python-chess` và `chess.js`.

### Giai đoạn 3: Frontend (GUI)
- [ ] Tích hợp `Chessground` vào trang web.
- [ ] Xử lý sự kiện kéo thả (OnMove) để gửi dữ liệu về Backend.
- [ ] Hiển thị danh sách nước đi (Move History) và bảng thông số so sánh.

### Giai đoạn 4: Thử nghiệm & Báo cáo (10/10)
- [ ] Chạy thử nghiệm 20 ván đấu AI vs AI.
- [ ] Thu thập dữ liệu: Tỉ lệ thắng, Thời gian trung bình, Độ sâu tìm kiếm.
- [ ] Hoàn thiện tài liệu Documentation và so sánh.

---

## 🚀 Hướng dẫn cài đặt (Sơ bộ)
1. **Clone project:**
   ```bash
   git clone https://github.com/your-username/chess-ai-duel.git
   cd chess-ai-duel
   ```
2. **Cài đặt thư viện Python:**
   ```bash
   pip install flask flask-socketio python-chess
   ```
3. **Chạy Server:**
   ```bash
   python app.py
   ```
4. **Truy cập:** Mở trình duyệt tại `http://127.0.0.1:5000`

---

## 📊 Tiêu chí so sánh (Comparison)
Dự án sẽ thực hiện đánh giá dựa trên:
1. **Chiến thuật (Strategy):** Khả năng phối hợp quân và bảo vệ Vua.
2. **Hiệu suất (Performance):** Số Node/giây và thời gian phản hồi.
3. **Độ ổn định:** MCTS có bị đi "ngáo" ở tàn cuộc không? Alpha-Beta có bị quá tải ở trung cuộc không?

---

## 📜 Quy tắc viết code (Coding Standards)
Để đảm bảo dự án đạt chất lượng cao nhất (10/10), toàn bộ mã nguồn phải tuân thủ các quy tắc sau:

### 1. Chú thích đầy đủ (Serious Docstrings)
Tất cả các hàm và class phải có chú thích rõ ràng bằng `"""Docstring"""` ngay sau dòng khai báo. Chú thích cần bao gồm:
- Mô tả chức năng của hàm.
- Giải thích các tham số đầu vào (Args).
- Mô tả giá trị trả về (Returns).
- Các ngoại lệ có thể xảy ra (Raises - nếu có).

*Ví dụ:*
```python
def get_best_move(board, depth):
    """
    Tìm kiếm nước đi tốt nhất sử dụng thuật toán Minimax kết hợp Alpha-Beta Pruning.

    Args:
        board (chess.Board): Trạng thái hiện tại của bàn cờ.
        depth (int): Độ sâu tìm kiếm tối đa.

    Returns:
        chess.Move: Nước đi tối ưu được tìm thấy.
    """
    # Logic code...
```

### 2. Code Clean & Modular
- **Tính đóng gói:** Chia nhỏ mã nguồn thành các module riêng biệt (ví dụ: `engine/`, `algorithms/`, `utils/`).
- **DRY (Don't Repeat Yourself):** Không lặp lại code, sử dụng các hàm helper cho các tác vụ lặp đi lặp lại.
- **Single Responsibility:** Mỗi hàm/class chỉ nên thực hiện một nhiệm vụ duy nhất và rõ ràng.
- **Kiểu dữ liệu:** Sử dụng Type Hinting (ví dụ: `def func(a: int) -> str:`) để code dễ đọc và debug.
