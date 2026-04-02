# Kết luận & Hướng phát triển trong tương lai / Conclusion

## 1. Tổng kết (Summary)

Sự vượt trội hoàn toàn của **Alpha-Beta Pruning** so với **MCTS** trong thử nghiệm này có thể được giải thích qua sự tương tác giữa thuật toán tìm kiếm và hàm đánh giá (`engine/simple_eval.py`):

- **Sự chính xác của Alpha-Beta trong giới hạn Depth:** Mặc dù chỉ sử dụng một hàm đánh giá tương đối đơn giản (dựa trên giá trị quân cờ, vị trí và kiểm soát ô cờ), Alpha-Beta vẫn thể hiện sự ổn định tuyệt đối. Thuật toán này tuân thủ chặt chẽ các quy tắc về giá trị vật chất (material value) và kiểm soát không gian, cho phép nó chọn ra nước đi chính xác nhất trong phạm vi chiều sâu tính toán của mình, loại bỏ hoàn toàn các biến số ngẫu nhiên.

- **Vấn đề hội tụ của MCTS với hàm đánh giá hiện tại:** Hàm `simple_eval.py` không cung cấp một "tín hiệu" đủ mạnh và chi tiết để MCTS có thể hội tụ (converge) nhanh chóng vào một nước đi tối ưu. Trong cờ vua, các thay đổi nhỏ về thế trận thường mang tính quyết định, nhưng mô phỏng của MCTS (vốn dựa nhiều vào xác suất) dễ bị nhiễu bởi các đánh giá chưa đủ sâu sắc, dẫn đến việc chọn các nước đi thiếu bài bản ở khai cuộc và bỏ lỡ các đòn phối hợp ở trung cuộc.

**Kết luận chung:** Trong một môi trường có luật chơi chặt chẽ và yêu cầu tính toán chính xác cao như cờ vua, Alpha-Beta Pruning vẫn là lựa chọn tối ưu khi đi kèm với các hàm Heuristic truyền thống. MCTS đòi hỏi một hàm đánh giá hoặc mạng nơ-ron mạnh mẽ hơn nhiều để có thể phát huy hiệu quả tương xứng.

## 2. Hướng phát triển tương lai

### Cải thiện MCTS
- **Tích hợp Mạng Nơ-ron (Deep Learning):** Áp dụng mô hình giống AlphaZero, sử dụng Policy Network để thu hẹp phạm vi tìm kiếm và Value Network để đánh giá thế cờ thay vì mô phỏng ngẫu nhiên đến hết ván.
- **Heuristic Bias:** Sử dụng tri thức cờ vua để ưu tiên các nước đi chiếm trung tâm, phát triển quân trong giai đoạn Selection của MCTS.

### Tối ưu hóa Alpha-Beta
- **Bảng chuyển đổi (Transposition Table):** Lưu trữ các thế cờ đã tính toán để tránh tính lại, giúp tăng độ sâu tìm kiếm.
- **Sắp xếp nước đi (Move Ordering):** Cải thiện thứ tự thử các nước đi (ưu tiên ăn quân, chiếu vua) để tối đa hóa khả năng cắt tỉa của Alpha-Beta.

### Mở rộng quy mô
- Phát triển giao diện người dùng trực quan hơn để theo dõi quá trình suy nghĩ của AI theo thời gian thực (hiển thị các biến thể tốt nhất mà AI đang cân nhắc).
