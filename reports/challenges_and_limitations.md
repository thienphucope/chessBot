# Thách thức & Hạn chế / Challenges & Limitations

## 1. Thách thức (Challenges)

### Thuật toán Alpha-Beta Pruning (AB)
- **Tối ưu hóa độ sâu:** Làm thế nào để tăng độ sâu tìm kiếm (depth) mà không gặp phải hiện tượng bùng nổ tổ hợp (combinatorial explosion) khi số lượng quân cờ trên bàn còn nhiều.
- **Xử lý dứt điểm trận đấu:** Thách thức trong việc điều chỉnh hàm đánh giá hoặc logic chọn nước đi để AI chủ động dứt điểm thay vì để xảy ra tình trạng lặp lại thế cờ (Draw by repetition) khi đang ở thế thắng tuyệt đối (như đã thấy trong ván 9).
- **Sắp xếp nước đi (Move Ordering):** Hiệu quả của việc cắt tỉa phụ thuộc cực lớn vào việc thử các nước đi tốt nhất trước tiên.

### Thuật toán Monte Carlo Tree Search (MCTS)
- **Cân bằng giữa Exploration và Exploitation:** Việc điều chỉnh tham số $C$ trong công thức UCB1 để AI vừa khám phá các nước đi mới vừa tập trung vào các nhánh triển vọng là một bài toán khó.
- **Vấn đề "Tactical Blindness":** Trong cờ vua, một sai lầm nhỏ có thể dẫn đến thua ngay lập tức. MCTS gặp thách thức lớn trong việc phát hiện các đòn phối hợp (tactics) ngắn hạn vì xác suất các lần mô phỏng ngẫu nhiên rơi đúng vào biến thế đó là rất thấp.
- **Độ hội tụ:** Cần một số lượng mô phỏng cực lớn để các giá trị xác định tại các nút đạt đến độ tin cậy cao.

## 2. Hạn chế (Limitations)

### Thuật toán Alpha-Beta Pruning (AB)
- **Tính "Cứng nhắc":** AB phụ thuộc hoàn toàn vào hàm đánh giá tĩnh (Static Evaluation). Nếu hàm này không bao quát được các yếu tố thế trận phức tạp (như cấu trúc tốt, sự linh động của quân), AI sẽ bỏ lỡ các nước đi chiến lược về dài hạn.
- **Giới hạn về thời gian:** Ở các độ sâu lớn, AB không thể đưa ra nước đi ngay lập tức nếu chưa hoàn thành toàn bộ cây tìm kiếm (trừ khi sử dụng Iterative Deepening).

### Thuật toán Monte Carlo Tree Search (MCTS)
- **Chi phí tài nguyên:** Tốn rất nhiều tài nguyên CPU cho các vòng lặp mô phỏng (Simulations). Thời gian suy nghĩ lâu hơn 3-4 lần so với AB nhưng hiệu quả thực tế trong cờ vua truyền thống lại thấp hơn.
- **Thiếu tri thức cờ vua (Domain Knowledge):** Nếu không có một Policy hoặc Value Network (như AlphaZero), MCTS thường đưa ra các nước đi khai cuộc thiếu tính bài bản (`h6`, `a6`, `f6`), dẫn đến mất ưu thế ngay từ đầu.
- **Hiệu ứng "Play-out":** Các ván đấu mô phỏng ngẫu nhiên đến hết trận thường không phản ánh đúng trình độ chơi cờ thực tế, dẫn đến các đánh giá sai lệch tại các nút lá.
