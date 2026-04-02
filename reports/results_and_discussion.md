# Kết quả & Phân tích / Results & Discussion

## 1. Tóm tắt kết quả (Summary of Results)
Dựa trên 10 ván đấu (logs/) thử nghiệm giữa thuật toán **Alpha-Beta Pruning (White)** và **MCTS (Black)**:
- **Alpha-Beta thắng:** 9 ván.
- **MCTS thắng:** 0 ván.
- **Hòa:** 1 ván (do lặp lại thế cờ khi Alpha-Beta đang ở thế thắng tuyệt đối +100).
- **Tỉ lệ thắng của Alpha-Beta:** 95%.

## 2. Phân tích hiệu năng (Performance Analysis)

### Thời gian phản hồi (Response Time)
- **Alpha-Beta:** Rất nhanh, trung bình dao động từ **0.5s đến 4.4s** mỗi nước đi. Thuật toán này cho thấy sự ổn định cao về tốc độ nhờ vào việc cắt tỉa hiệu quả.
- **MCTS:** Chậm hơn đáng kể, trung bình từ **7s đến 14s** mỗi nước đi. Mặc dù dành nhiều thời gian hơn để mô phỏng, nhưng chất lượng nước đi không tương xứng với thời gian bỏ ra.

### Chất lượng nước đi (Move Quality)
- **Khai cuộc:** MCTS thường xuyên mắc sai lầm ngay từ đầu với các nước đi yếu như `h6`, `f6`, `a6`, tạo điều kiện cho Alpha-Beta chiếm ưu thế không gian và phát triển quân nhanh chóng.
- **Trung cuộc:** Alpha-Beta thể hiện khả năng tính toán chiến thuật (tactics) cực kỳ chính xác. Trong nhiều ván (ví dụ ván 1, 3), Alpha-Beta đã tìm ra các đòn phối hợp chiếu hết chỉ sau 6-7 nước đi khi MCTS để lộ sơ hở lớn.

### Đánh giá chất lượng từ Stockfish (Move Quality Assessment)
Các ván đấu được phân tích bởi **Stockfish** để đưa ra cái nhìn khách quan về chất lượng nước đi của hai thuật toán:
- **Alpha-Beta (White):** Điểm đánh giá trung bình từ Stockfish luôn duy trì ở mức dương rất cao (từ **+14.0 đến +44.0**). Điều này xác nhận rằng các nước đi của Alpha-Beta có độ chính xác rất cao theo tiêu chuẩn của engine hàng đầu thế giới.
- **MCTS (Black):** Stockfish đánh giá các nước đi của MCTS ở mức âm sâu (từ **-15.0 đến -49.0**). Điều này phản ánh việc MCTS thường xuyên chọn các nước đi yếu hoặc mắc sai lầm chiến thuật nghiêm trọng, dẫn đến thế trận bị Stockfish đánh giá là sụp đổ nhanh chóng.

