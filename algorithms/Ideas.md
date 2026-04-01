# Tổng quan các thuật toán và chiến lược đánh giá

Tài liệu này tóm tắt các ý tưởng cốt lõi được triển khai trong hệ thống đánh giá và các thuật toán tìm kiếm nước đi.

## 1. Hệ thống đánh giá (Simple Evaluation - `engine/simple_eval.py`)

Hàm đánh giá đóng vai trò là **"đôi mắt"** của bot, giúp ước lượng khả năng chiến thắng tại một trạng thái bất kỳ mà không cần chờ đến khi kết thúc ván cờ (**Static Evaluation**). Kết quả trả về là một con số từ góc nhìn của quân Trắng (điểm dương là lợi thế cho Trắng).

*   **Vai trò cốt lõi:** Cung cấp "thước đo giá trị" cho các thuật toán tìm kiếm (Alpha-Beta, MCTS) để chúng biết nên ưu tiên đi theo nhánh nào khi không thể nhìn thấy nước chiếu hết.
*   **Thành phần điểm số:**
    *   **Giá trị quân cờ (Material):** Ước lượng sức mạnh dựa trên số lượng quân hiện có (Tốt: 100, Mã: 320, Tượng: 330, Xe: 500, Hậu: 900). Trọng số: **80%**.
    *   **Vị trí quân cờ (PST - Piece-Square Tables):** Đánh giá độ "đẹp" của vị trí đứng, khuyến khích quân cờ chiếm lĩnh trung tâm hoặc vị trí chiến lược. Trọng số: **10%**.
    *   **Kiểm soát không gian (Square Control):** Đếm số lượng ô mà các quân cờ đang kiểm soát, phản ánh độ cơ động của đội hình. Trọng số: **10%**.
*   **Trạng thái kết thúc:** Chiếu hết trả về giá trị tuyệt đối cực lớn (+/- 100,000), hòa trả về 0.

## 2. Thuật toán Alpha-Beta Pruning (`algorithms/template_alphabeta.py`)

Cải tiến thuật toán Minimax bằng cách cắt tỉa các nhánh không cần thiết.

*   **Sắp xếp nước đi (Move Ordering):** Rất quan trọng để tối ưu cắt tỉa.
    *   **MVV-LVA:** Ưu tiên quân giá trị thấp ăn quân giá trị cao.
    *   **Promotion:** Ưu tiên phong cấp.
    *   **Checks:** Ưu tiên các nước chiếu.
*   **Bảng chuyển đổi (Transposition Table):** Sử dụng Zobrist Hashing để lưu lại kết quả của các trạng thái bàn cờ đã tính toán, giúp tránh tính lại cùng một vị trí từ các thứ tự nước đi khác nhau.
*   **Tìm kiếm tĩnh (Quiescence Search):** Khi đạt đến độ sâu giới hạn, thuật toán không dừng lại ngay mà tiếp tục tìm kiếm các nước ăn quân (captures) để tránh sai số do "hiệu ứng chân trời" (ví dụ: dừng đúng lúc quân mình sắp bị ăn lại).

## 3. Monte Carlo Tree Search - MCTS (`algorithms/template_mcts.py`)

Thuật toán tìm kiếm dựa trên xác suất và mô phỏng.

*   **Cơ chế 4 bước:**
    1.  **Selection:** Sử dụng công thức **UCB1** để chọn node tiềm năng nhất, cân bằng giữa Khai thác (Exploitation - chọn nước tốt đã biết) và Khám phá (Exploration - thử nước mới).
    2.  **Expansion:** Mở rộng cây bằng cách thêm các nước đi hợp lệ mới.
    3.  **Simulation:** Thay vì chạy ngẫu nhiên hoàn toàn (pure rollout), bản triển khai này sử dụng **Quiescence Search** để đánh giá độ mạnh của node lá, giúp bot chơi ổn định hơn.
    4.  **Backpropagation:** Cập nhật tỷ lệ thắng và số lượt thăm ngược lên root.
*   **Xác suất hóa:** Chuyển đổi điểm số từ hàm `simple_eval` sang xác suất thắng [0, 1] thông qua hàm Sigmoid, phù hợp với bản chất thống kê của MCTS.
*   **Góc nhìn (Perspective):** Mỗi node lưu thống kê từ góc nhìn của quân đi trước đó (Parent).
