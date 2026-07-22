# Ma trận là trái tim của AI — kịch bản tiếng Việt

Video dọc 1080×1920, 30fps, khoảng 120 giây.

## 01_hook (0:00–0:08)
**Narration:** Mỗi khi AI nhận diện khuôn mặt hay dịch một câu, nó chỉ làm một việc: nhân ma trận.

## 02_matrix_transform (0:08–0:22)
**Narration:** Ma trận không phải bảng số khô khan. Nó là phép biến hình không gian: xoay, kéo, nghiêng, phóng to.

## 03_cube_3d (0:22–0:36)
**Narration:** Hãy tưởng tượng một khối lập phương trong không gian ba chiều. Mỗi điểm có ba tọa độ: x, y, z.

## 04_basis (0:36–0:50)
**Narration:** Ba trục i, j, k là bộ cơ sở. Một ma trận ba ba nói cho ta biết mỗi trục sẽ đi đâu sau phép biến hình.

## 05_W1 (0:50–1:04)
**Narration:** Áp dụng ma trận W1: khối lập phương xoay và kéo. Các trục cơ sở cũng dịch chuyển theo đúng ba cột của W1.

## 06_W2 (1:04–1:17)
**Narration:** Tiếp theo, áp dụng W2. Không gian lại biến hình một lần nữa, tạo thành tích hợp mới.

## 07_composition (1:17–1:30)
**Narration:** Nhân W2 với W1 nghĩa là thực hiện cả hai trong một bước. Ma trận tích M cho kết quả y hệt.

## 08_why (1:30–1:42)
**Narration:** Mỗi cột của M chính là W2 tác động lên cột tương ứng của W1. Đó là lý do người ta định nghĩa phép nhân ma trận như vậy.

## 09_neural_net (1:42–1:55)
**Narration:** Mạng nơ-ron cũng chỉ làm điều này. Mỗi lớp là một ma trận. Dữ liệu đi qua chuỗi các phép biến hình để ra dự đoán.

## 10_forward_pass (1:55–2:08)
**Narration:** Đầu vào x, nhân W1, cộng bias, qua hàm kích hoạt ReLU, rồi W2, W3, cho đến khi ra kết quả.

## 11_recap_cta (2:08–2:20)
**Narration:** Vậy AI không hề ma thuật. Nó là hàng triệu phép nhân ma trận ghép lại. Theo dõi để xem thêm toán học đằng sau AI.
