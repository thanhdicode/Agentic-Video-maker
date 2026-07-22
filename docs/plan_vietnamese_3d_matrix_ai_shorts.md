# Kế hoạch video: "Ma trận là trái tim của AI" — Manim 3D Shorts tiếng Việt

## 1. Nghiên cứu tham khảo (top 10 video thể loại Manim math/AI Shorts)

| # | Video / kênh | Tại sao viral / điểm học được |
|---|---|---|
| 1 | **3Blue1Brown — "Where matrix multiplication comes from"** (TikTok/Shorts) | Mở đầu bằng câu hỏi trực quan, dùng `ApplyMatrix` liên tiếp, mỗi bước chỉ 1 ý, màu cột cố định. |
| 2 | **3Blue1Brown — "Don't let it fool you!" (Moser circle)** | Hook mạnh, tiết tấu nhanh, transition đơn giản, kết luận gây bất ngờ. |
| 3 | **3Blue1Brown — "What question is a Fourier Transform answering?"** | Hình ảnh phức tạp được chia nhỏ, dùng camera xoay 3D, nhạc nền lo-fi rất nhỏ. |
| 4 | **3Blue1Brown — "A nice way to visualize convolutions"** | Bắt đầu từ ví dụ cụ thể, dùng `ValueTracker` để kéo thả, người xem cảm nhận được sự thay đổi. |
| 5 | **@math.floyd** (TikTok, 780K followers) | Hiệu ứng nhanh, beat đồng bộ, mỗi video 1 công thức, tiêu đề to full màn hình. |
| 6 | **@tesseract_math** (TikTok, 26.7K followers) | Dùng Manim render chủ đề hình học/không gian, cube + axis rất đẹp, màu bão hòa cao. |
| 7 | **@reason4math — "Euler's Polyhedron Formula"** | Nội dung phức tạp được sống động hóa bằng hình khối, chuyển cảnh mượt, subtitle ngắn. |
| 8 | **@l0ve_math_** — các clip về hình học/phân số | Màu pastel, chữ to, tốc độ chậm vừa, phù hợp người xem mới. |
| 9 | **Fourier Series Manim Reels (Jhagas gist)** | Cấu hình 1080×1920, `Axes` dọc, plot từng sóng sin, công thức LaTeX hiện từng bước. |
| 10 | **"The Math Behind TikTok's Algorithm: Dot Product"** | Liên kết toán học với ứng dụng AI/social media, dùng vector 2D/3D, hook gắn với thực tế. |

### Bảng kiểm pattern viral đã rút ra
- **Hook trong 3 giây đầu**: câu hỏi hoặc phát ngôn gây tò mò, ví dụ "AI chỉ là nhân ma trận".
- **Một scene = một ý duy nhất**, không dồn nhiều công thức cùng lúc.
- **Màu cố định cho từng ý**: cột ma trận 1 = đỏ, 2 = xanh lá, 3 = vàng; cube = xanh cyan; AI = tím.
- **Camera 3D di chuyển chậm**, không để yên một góc quá lâu (`move_camera`, `begin_ambient_camera_rotation`).
- **Text/LaTeX lớn, nền đen mờ**, luôn nằm trong khu vực an toàn của màn hình dọc.
- **Transition mượt**: `TransformMatchingTex`, `ReplacementTransform`, `FadeIn/Out`, `Write` với `rate_func=smooth`.
- **Hiệu ứng nhấp nháy/đèn flash nhẹ** (`Flash`, `Indicate`, `Circumscribe`) đánh dấu phần đang giải thích.
- **Subtitle tiếng Việt**, câu ngắn, font to, viền đen, xuất hiện đúng lúc giọng đọc.
- **Nhạc nền lo-fi/chill-hop nhỏ**, BPM 70–90, không lời, mix ~12–15% so với voice.
- **Kết thúc CTA rõ ràng**: theo dõi / để lại câu hỏi.

---

## 2. Concept video

**Tiêu đề:** *Ma trận là trái tim của AI*  
**Thời lượng:** khoảng 120 giây  
**Tỷ lệ:** 9:16 (1080×1920)  
**Định dạng:** Manim `ThreeDScene`, 30fps, nền `#0A0A0A` (đen xám sâu, không phải đen tuyền)

**Ý chính:**  
Mỗi khi AI hoạt động, ở bên trong nó chỉ làm một việc: nhân ma trận. Ma trận chính là cách biến hình không gian 3D — xoay, kéo, nghiêng, phóng to. Khi ghép nhiều ma trận lại với nhau, ta có một mạng nơ-ron. Video sẽ đi từ khái niệm ma trận → phép biến hình 3D → tích ma trận → mạng nơ-ron.

---

## 3. Thiết lập kỹ thuật

### Voice AI
- **Engine:** `edge-tts` (Microsoft Edge neural TTS, miễn phí, không cần API key).
- **Voice tiếng Việt:**
  - `vi-VN-HoaiMyNeural` (nữ, nhẹ nhàng, phù hợp giải thích toán) — **đề xuất chính**.
  - `vi-VN-NamMinhNeural` (nam, trầm ấm) — phương án thay thế.
- **Tốc độ:** mặc định `+0%`, có thể điều chỉnh `rate="-10%"` nếu cần chậm hơn.
- **Chất lượng:** `audio-24khz-48kbitrate-mono-mp3`.

### Nhạc nền
- **Thể loại đang viral:** lo-fi / chill-hop / study beats, không lời, BPM ~75–90.
- **Track đề xuất:** *Soft Vibes* của Vital trên Bensound (cdn2.bensound.com/bensound-softvibes.mp3).
  - Miễn phí sử dụng với ghi công `Music: Soft Vibes by Vital from Bensound` trong mô tả video.
  - Nếu kênh monetized, nên mua license ($34) hoặc chọn track khác từ Uppbeat/Epidemic Sound.
- **Xử lý:** dùng `ffmpeg` loop + crossfade để kéo dài đủ 120 giây, mix ở 12–15% volume.

### Subtitle
- Tiếng Việt, font Arial, size 36–38, màu trắng `#FFFFFF`, viền đen `#000000` 3px.
- `WrapStyle: 0`, mỗi dòng tối đa 4–5 từ, cách đáy 100 px.
- Đối chiếu từng cụm với thời gian voice.

### Màu sắc & phong cách
- Nền: `#0A0A0A`
- Cube: `#2DD4BF` (cyan)
- Trục x/y/z: đỏ / xanh lá / vàng nhạt
- `i-hat` = đỏ, `j-hat` = xanh lá, `k-hat` = vàng
- Ma trận W1 = xanh dương, W2 = tím, M = vàng
- Mạng nơ-ron: lớp ẩn màu xanh dương, lớp ra màu cam

---

## 4. Storyboard từng scene

### Scene 0 — Hook (0:00 → 0:08, ~8 giây)
**Narration:**  
"Mỗi khi AI nhận diện khuôn mặt hay dịch một câu, nó chỉ làm một việc: nhân ma trận."

**Visuals:**
- Màn hình đen, chữ "AI" lớn màu trắng ở giữa.
- Nhanh chóng: một dãy ma trận và vector nhỏ chạy từ trái qua phải quanh chữ AI (dùng `VGroup` di chuyển nhanh với `rate_func=linear`).
- Dòng chữ phụ "Nhân ma trận" xuất hiện dưới chữ AI.

**Camera/transition:**
- `FadeIn` từng từ với `lag_ratio`, `Flash` quanh chữ AI khi nói "nhân ma trận".
- Zoom camera nhẹ từ 0.9 → 1.0 trong 1 giây đầu.

**Audio notes:**
- Voice bắt đầu ngay, nhạc fade in 2 giây.

---

### Scene 1 — Ma trận = phép biến hình (0:08 → 0:22, ~14 giây)
**Narration:**  
"Ma trận không phải là bảng số khô khan. Nó chính là phép biến hình không gian: xoay, kéo, nghiêng, phóng to."

**Visuals:**
- Một ma trận 2×2 hoặc 3×3 `Matrix` xuất hiện ở giữa màn hình.
- Các từ "xoay", "kéo", "nghiêng", "phóng to" lần lượt xuất hiện xung quanh ma trận.
- Mũi tên cong chỉ các hướng biến hình (dùng `Arc` và `Arrow`).

**Camera/transition:**
- `Transform` từ chữ AI trong hook thành ma trận.
- `Indicate` từng cột của ma trận khi nói các từ khác nhau.
- `Flash` màu xanh cyan ở vị trí ma trận khi nói "biến hình không gian".

**Audio notes:**
- Nhạc nền duy trì ổn định, voice rõ ràng.

---

### Scene 2 — Khối lập phương 3D (0:22 → 0:36, ~14 giây)
**Narration:**  
"Hãy tưởng tượng một khối lập phương trong không gian ba chiều. Mỗi điểm của nó có ba tọa độ: x, y, z."

**Visuals:**
- `ThreeDAxes` màu xám nhạt fade in.
- `Cube` cyan trong suốt (`fill_opacity=0.15`, `stroke_width=2`) xoay nhẹ ở trung tâm.
- Ba trục `x`, `y`, `z` được gắn nhãn `MathTex` gần đầu mũi tên.
- Tọa độ `(x, y, z)` hiện góc trên bên trái.

**Camera/transition:**
- `set_camera_orientation(phi=70°, theta=-55°, zoom=0.85)`.
- `move_camera(phi=65°, theta=-45°, run_time=3, rate_func=smooth)` khi cube xoay nhẹ.
- `begin_ambient_camera_rotation(rate=0.08)` trong suốt scene.

**Audio notes:**
- Nhạc nền nhỏ, tạo cảm giác "khám phá".

---

### Scene 3 — Bộ cơ sở i, j, k (0:36 → 0:50, ~14 giây)
**Narration:**  
"Ba trục i, j, k là bộ cơ sở. Một ma trận 3×3 nói cho ta biết mỗi trục này sẽ đi đâu sau phép biến hình."

**Visuals:**
- `Vector` đỏ `(1,0,0)`, xanh lá `(0,1,0)`, vàng `(0,0,1)` mọc ra từ gốc tọa độ.
- Nhãn `\hat i`, `\hat j`, `\hat k` dính theo đầu vector, có nền đen mờ.
- Ma trận `M` 3×3 xuất hiện bên phải, ba cột được tô màu đỏ/xanh lá/vàng.

**Camera/transition:**
- `GrowArrow` cho từng vector, mỗi vector cách nhau 0.6 giây.
- `Circumscribe` quanh ma trận khi nói "ma trận 3×3".
- Cột 1 của ma trận nhấp nháy cùng lúc vector i xuất hiện (đồng bộ màu).

**Audio notes:**
- Voice chậm vừa, nhấn vào "bộ cơ sở".

---

### Scene 4 — W1 biến hình lần 1 (0:50 → 1:05, ~15 giây)
**Narration:**  
"Áp dụng ma trận W1: khối lập phương xoay và kéo. Các trục cơ sở cũng dịch chuyển đúng theo ba cột của W1."

**Visuals:**
- `ApplyMatrix(W1, cube)` và `ApplyMatrix(W1, i_vec/j_vec/k_vec)` chạy đồng thời.
- Ma trận `W1` hiện ở góc trên bên phải, cột 1/2/3 có màu tương ứng.
- `TracedPath` để lại vệt mờ cho đầu vector khi di chuyển (cảm giác chuyển động).

**Camera/transition:**
- `move_camera(phi=60°, theta=-30°, zoom=0.9, run_time=2, rate_func=smooth)`.
- Sau `ApplyMatrix`, `Indicate` từng cột của `W1` và vector tương ứng.
- `begin_ambient_camera_rotation(rate=0.05)` nhẹ để người xem thấy độ sâu 3D.

**Audio notes:**
- Voice nhấn "xoay và kéo" đúng lúc animation chạy.

---

### Scene 5 — W2 biến hình lần 2 (1:05 → 1:17, ~12 giây)
**Narration:**  
"Tiếp theo, áp dụng W2. Không gian lại biến hình một lần nữa, tạo thành tích hợp mới."

**Visuals:**
- `ApplyMatrix(W2, cube)` và `ApplyMatrix(W2, i/j/k vectors)`.
- Ma trận `W2` hiện kế bên `W1` ở góc phải.
- Dấu nhân `\times` hoặc `\cdot` xuất hiện giữa `W2` và `W1`.

**Camera/transition:**
- `move_camera(phi=55°, theta=-70°, zoom=0.95, run_time=2)` — xoay góc nhìn sang bên trái để thấy rõ sự biến dạng thứ hai.
- `TransformMatchingTex` để dấu nhân xuất hiện mượt.

**Audio notes:**
- Nhạc nền thêm 1 chút beat, voice nhấn "tích hợp mới".

---

### Scene 6 — Tích M = W2 × W1 (1:17 → 1:30, ~13 giây)
**Narration:**  
"Nhân hai ma trận W2 với W1 nghĩa là thực hiện cả hai phép biến hình chỉ trong một bước. Ma trận tích M cho kết quả cuối cùng y hệt."

**Visuals:**
- Cube và vector reset về vị ban đầu (fade out/in nhanh).
- `ApplyMatrix(M, cube)` và `ApplyMatrix(M, i/j/k vectors)` chạy một lượt.
- Khi chạy xong, một khung wireframe màu xanh lá (`Cube` với `stroke_color=GREEN`, `fill_opacity=0`) hiện lên chồng khớp lên cube cuối cùng, chứng minh kết quả giống nhau.
- Ma trận `M = W_2 \cdot W_1` hiện ở góc phải, cột có màu.

**Camera/transition:**
- `move_camera(phi=50°, theta=-40°, zoom=1.0)` — zoom cận vào cube khi nó biến hình.
- `Flash` xung quanh wireframe khi hai hình khớp nhau.
- `TransformMatchingTex` từ `W2 × W1` thành `M`.

**Audio notes:**
- Voice nói "một bước" đúng lúc `ApplyMatrix(M,...)` bắt đầu.

---

### Scene 7 — Tại sao lại định nghĩa như vậy? (1:30 → 1:42, ~12 giây)
**Narration:**  
"Mỗi cột của M, chính là W2 tác động lên cột tương ứng của W1. Đó là lý do người ta định nghĩa phép nhân ma trận như vậy."

**Visuals:**
- Phóng to cột 1 của `W1` (đỏ), sau đó `W2` tác động lên nó, tạo thành cột 1 của `M` (vàng).
- Lặp lại cho cột 2 và 3 với tốc độ nhanh hơn.
- Công thức `M_{:,j} = W_2 \cdot W_{1,:,j}` hiện ở giữa.

**Camera/transition:**
- `FocusOn` hoặc `Indicate` từng cột.
- `Transform` cột W1 thành cột M (morph số).
- `Circumscribe` công thức khi nói "định nghĩa".

**Audio notes:**
- Voice chậm, rõ ràng, nhấn từng từ.

---

### Scene 8 — Từ ma trận đến mạng nơ-ron (1:42 → 1:55, ~13 giây)
**Narration:**  
"Mạng nơ-ron cũng chỉ làm điều này. Mỗi lớp là một ma trận. Dữ liệu đi qua chuỗi các phép biến hình để ra dự đoán."

**Visuals:**
- Camera rút lui, toàn bộ khối cube mờ dần.
- Một mô hình mạng nơ-ron 2D dạng vertical stack hiện lên: các hình chữ nhật `x`, `W_1`, `ReLU`, `W_2`, `...`, `W_n`, `y`.
- Các mũi tên nối từ trên xuống, mũi tên đang chạy dần (`ShowPassingFlashWithThinningStrokeWidth`).

**Camera/transition:**
- `FadeOut` toàn bộ mô hình 3D, `FadeIn` mô hình neural net.
- `set_camera_orientation` reset về 2D (phi=0, theta=-90) nhưng vẫn dùng `ThreeDScene`.
- `Indicate` lần lượt từng lớp khi voice đọc đến.

**Audio notes:**
- Nhạc nền hơi tăng nhịp nhẹ khi chuyển sang AI.

---

### Scene 9 — Forward pass trực quan (1:55 → 2:08, ~13 giây)
**Narration:**  
"Đầu vào x, nhân W1, cộng bias, qua hàm kích hoạt ReLU, rồi W2, W3, ... cho đến khi ra kết quả."

**Visuals:**
- Một vector `x` màu trắng ở trên cùng.
- Nó di chuyển xuống qua từng lớp, mỗi lớp là một ma trận `Matrix` mở rộng ra.
- Biểu đồ ReLU (`max(0, z)`) hiện cạnh lớp 1 bằng `Axes` + `plot`.
- Vector đầu ra `y` hiện ở dưới cùng với màu cam.

**Camera/transition:**
- `MoveAlongPath` hoặc `Transform` vector qua các lớp.
- Mỗi lớp `Flash` khi vector đi qua.
- `Write` công thức `y = W_n \cdots W_2 \cdot ReLU(W_1 x + b)` ở trên cùng.

**Audio notes:**
- Voice đọc đúng nhịp với mỗi lớp vector đi qua.

---

### Scene 10 — Recap + CTA (2:08 → 2:20, ~12 giây)
**Narration:**  
"Vậy AI không hề ma thuật. Nó là hàng triệu phép nhân ma trận ghép lại, biến hình dữ liệu từng chút cho đến khi ra câu trả lời."

**Visuals:**
- Màn hình trở lại với ma trận `M` ở giữa, xung quanh là các vector `x`, `W1`, `W2`, `...`, `y` nhỏ xoay quanh.
- Chữ "AI = tích các ma trận" lớn ở giữa.
- Dòng "Theo dõi để xem thêm toán học đằng sau AI" hiện dưới cùng.

**Camera/transition:**
- `FadeIn` các yếu tố, `begin_ambient_camera_rotation(rate=0.1)`.
- `Flash` quanh dòng chữ chính.
- Kết thúc bằng `FadeOut` nhẹ hoặc zoom vào chữ CTA.

**Audio notes:**
- Voice kết thúc chắc chắn, nhạc fade out 2 giây cuối.

---

## 5. Timeline tổng hợp

| Scene | Thời gian | Nội dung chính | Hiệu ứng nổi bật |
|---|---|---|---|
| 0 | 0–8s | Hook: AI = nhân ma trận | Text chạy, Flash AI |
| 1 | 8–22s | Ma trận = biến hình | Matrix + mũi tên xoay/kéo |
| 2 | 22–36s | Khối lập phương 3D | Camera 3D xoay nhẹ |
| 3 | 36–50s | Bộ cơ sở i,j,k | GrowArrow, cột ma trận đồng bộ màu |
| 4 | 50–65s | W1 biến hình | ApplyMatrix, TracedPath, camera di chuyển |
| 5 | 65–77s | W2 biến hình tiếp | ApplyMatrix, dấu nhân xuất hiện |
| 6 | 77–90s | M = W2 × W1 | Reset + ApplyMatrix M, wireframe chồng khớp |
| 7 | 90–102s | Tại sao định nghĩa như vậy | Morph cột W1 → cột M, công thức |
| 8 | 102–115s | Từ ma trận đến neural net | Chuyển sang diagram 2D, mũi tên chạy |
| 9 | 115–128s | Forward pass | Vector di chuyển qua các lớp, ReLU plot |
| 10 | 128–140s | Recap + CTA | Text tổng kết, camera xoay, fade out nhạc |

*Lưu ý: tổng thời lượng đích là ~120 giây. Bảng trên là phân bổ sơ bộ; khi viết kịch bản cuối em sẽ cắt gọn câu văn và chỉnh thời gian chờ để đạt đúng 2 phút.*

---

## 6. Quy trình thực hiện sau khi anh duyệt

1. Viết `script.md` tiếng Việt đầy đủ (đoạn voice chuẩn chính tả).
2. Sinh TTS bằng `edge-tts` với `vi-VN-HoaiMyNeural`, đo duration từng segment.
3. Chuẩn bị nhạc nền: loop `bensound-softvibes.mp3` đến 120s, mix 12–15%.
4. Viết `matrix_ai_3d.py` Manim `ThreeDScene` theo storyboard.
5. Render 1080×1920 30fps, burn-in subtitle tiếng Việt bằng ASS.
6. Kiểm tra frame tại các mốc 5s, 20s, 50s, 80s, 110s để đảm bảo không đè chữ, camera rõ, hiệu ứng đúng.
7. Xuất file MP4 cuối và gửi anh.

---

## 7. Cần anh quyết định

1. **Giọng AI:** đề xuất `vi-VN-HoaiMyNeural` (nữ). Có muốn đổi sang `vi-VN-NamMinhNeural` (nam) không?
2. **Nhạc nền:** đề xuất `Soft Vibes` (Bensound, free, cần ghi công). Nếu muốn track khác hoặc mua license, anh cho em biết.
3. **Chủ đề:** đề xuất như trên. Anh có muốn đổi sang chủ đề khác (ví dụ: gradient descent, attention, hình học fractal) không?
