# Workflow Studio làm video YouTube giáo dục trẻ em bằng Google Flow (chuyên nghiệp, đồng nhất nhân vật, mượt chuyển cảnh)

> Tài liệu thiết kế đầy đủ trước khi sản xuất. Áp dụng cho video AumSum / Dr. Binocs / Smile and Learn: 2D cartoon, mascot thân thiện, phụ đề, nhạc nền, giọng đọc cố định.

---

## 1. Tại sao video vừa rồi chưa đạt?

| Vấn đề | Nguyên nhân | Cách khắc phục |
|--------|-------------|----------------|
| Nhân vật không đồng nhất | Mỗi clip sinh riêng bằng `Veo 3.1 Lite` mà không dùng **Character** hay **Ingredients**. AI tự vẽ lại mascot mỗi lần. | Tạo **Character** trong Flow, gán voice, mô tả tính cách, sinh character sheet, rồi gọi `@TênNhânVật` + đưa ảnh reference vào mỗi prompt. |
| Chuyển cảnh cắt ngang, không mượt | Ghép 22 clip 8 giây bằng cắt đơn, không có transition/extend. | Dùng **Extend** cho hành động dài trong 1 scene; dùng **Frames to Video** hoặc **camera movement prompt** để sinh clip chuyển cảnh 2-3 giây giữa các scene. |
| Giọng không cố định | Không gán voice riêng cho nhân vật. | Trong tab **Characters → Select a voice**, chọn 1 voice cố định. Hoặc sau này dùng F5-TTS clone voice mẫu để đọc tiếng Việt. |
| Prompt quá chung chung | Thiếu camera, style, negative, reference. | Dùng công thức prompt 7 phần dưới đây. |

---

## 2. Tổng quan workflow studio

```
KỊCH BẢN + STORYBOARD
        ↓
TẠO CHARACTERS + VOICE CAST + STYLE GUIDE
        ↓
SINH ASSETS: background, prop, character sheet (Nano Banana / Imagen)
        ↓
SINH TỪNG SCENE TRÊN FLOW (Veo 3.1 / Omni Flash)
   - Reference character/style/prop
   - Camera prompt
   - Extend hoặc Frames-to-Video
        ↓
SCENEBUILDER / GHÉP BẰNG PYTHON + FFmpeg
        ↓
POST: voiceover (TTS/F5-TTS), subtitle, music, SFX
        ↓
XUẤT FINAL 1080p/4K → YOUTUBE
```

---

## 3. Chuẩn bị trước khi vào Flow

### 3.1. Kịch bản theo công thức giáo dục trẻ em

Mỗi video 3-5 phút = **6-10 scene**, mỗi scene 20-40 giây, mỗi scene 1 ý chính.

| Phần | Thời lượng | Nội dung |
|------|------------|----------|
| Hook | 0-5s | Hỏi câu hỏi thú vị, mascot nhìn thẳng camera. |
| Giải thích 1 | 5-45s | Nguyên nhân chính (ví dụ: ánh sáng trắng gồm nhiều màu). |
| Giải thích 2 | 45-90s | Cơ chế (sóng ngắn xanh tán xạ nhiều hơn). |
| Ví dụ | 90-130s | Hoàng hôn, cầu vồng, vũ trụ. |
| Quiz/Recap | 130-170s | Hỏi lại + tóm tắt. |
| Outro CTA | 170-190s | Cảm ơn, subscribe, xem tiếp. |

### 3.2. Style guide cố định

- **Phong cách**: 2D vector cartoon, flat colors, viền đen đậm, màu sắc tươi sáng, nền đơn giản.
- **Mascot**: đầu tròn, mắt to, miệng rộng, tay/ngón tay ngắn, màu sắc rực rỡ (ví dụ: vàng cam / xanh dương).
- **Font/Text**: chữ to, dễ đọc, outline đen.
- **Âm thanh**: nhạc nền vui vẻ 120-130 BPM, SFX nhấn mạnh chuyển động.

---

## 4. Tạo nhân vật đồng nhất trong Flow

### 4.1. Tạo Character chính

1. Vào tab **Characters**.
2. Chọn **New character**.
3. Prompt character tối thiểu phải bao gồm:
   - Kiểu dáng (2D cartoon mascot).
   - Màu sắc (ví dụ: orange-yellow star-shaped body).
   - Đặc điểm khuôn mặt (big round eyes, black pupils, wide smile).
   - Trang phục/phụ kiện (none / white gloves).
   - Phong cách nghệ thuật (AumSum style, vector illustration, flat colors, bold black outlines, white background).

**Ví dụ prompt tạo Character:**

```text
A friendly star-shaped 2D cartoon mascot for a kids science YouTube channel. Round oversized head, big expressive eyes with black pupils, small orange nose, wide happy smile, short stubby arms and legs, bright yellow-orange body with subtle gradient, white gloves, bold black outlines, flat vector colors, AumSum / Dr. Binocs educational style, full body front view, standing pose, white background.
```

4. Sau khi sinh ảnh, nhấn **Create Body** để có phiên bản toàn thân.
5. Đặt tên: `@AumSum`.
6. Chọn **Select a voice** → chọn 1 voice cố định, ví dụ `Achird (Male, friendly, mid pitch)` cho tiếng Anh.
7. Điền **Character Info** (tính cách để agent viết prompt đúng):

```text
AumSum is curious, cheerful, and energetic. He waves at the camera, points at objects with his right hand, shows surprise with wide eyes, and gives thumbs-up. He explains science in a friendly, simple way for kids aged 5-10.
```

### 4.2. Sinh Character Sheet (Ingredients)

Sinh 4-6 ảnh reference từ Nano Banana / Imagen:

1. **Front view** — đã có từ bước trên.
2. **3/4 view** — `@AumSum standing in 3/4 angle`.
3. **Pointing pose** — `@AumSum pointing finger up`.
4. **Surprised pose** — `@AumSum with surprised expression, big eyes`.
5. **Thumbs-up pose** — `@AumSum giving thumbs-up`.
6. **Waving pose** — `@AumSum waving hand`.

Upload tất cả vào **Ingredients** của project (hoặc **Collections**) để dùng lại.

### 4.3. Tạo nhân vật phụ (nếu cần)

Ví dụ: Một cô bé đặt câu hỏi, một chú mặt trời biết nói.

- Tạo character riêng, tên riêng, voice riêng (ví dụ `@Sunny` voice `Autonoe (Female, bright, mid pitch)`).
- Mỗi nhân vật có voice duy nhất, không trùng.

---

## 5. Công thức prompt 7 phần (dùng cho mọi scene)

```
[SHOT] + [CHARACTER] + [ACTION] + [CONTEXT] + [CAMERA] + [AUDIO/SFX] + [STYLE] + [NEGATIVE]
```

| Phần | Mô tả | Ví dụ |
|------|-------|-------|
| `[SHOT]` | Loại cảnh (wide, medium, close-up, extreme close-up). | `Wide shot` |
| `[CHARACTER]` | `@TênNhânVật` + mô tả trạng thái. | `@AumSum stands on the left` |
| `[ACTION]` | Hành động chính, cử chỉ, biểu cảm. | `points at a large glowing sun with his right hand, smiling` |
| `[CONTEXT]` | Bối cảnh, props, vị trí. | `bright blue sky with a few white clouds, green hills below` |
| `[CAMERA]` | Chuyển động camera. | `slow dolly-in, slight pan right, 24fps` |
| `[AUDIO/SFX]` | Âm thanh, giọng nói, hiệu ứng. | `cheerful upbeat music, soft whoosh as the sun glows` |
| `[STYLE]` | Phong cách, chất lượng, tỷ lệ. | `2D vector cartoon, AumSum kids educational style, flat bold colors, black outlines, 16:9` |
| `[NEGATIVE]` | Loại trừ. | `no photorealism, no 3D render, no blurry face, no extra limbs, no watermark` |

### 5.1. Prompt mẫu hoàn chỉnh

```text
Wide shot, @AumSum stands on the left, points with his right hand at a large friendly cartoon sun on the right, smiling and looking at the camera. Bright blue sky with fluffy white clouds, green hills in the distance. Slow dolly-in toward the sun, subtle lens glow. Cheerful background music, soft whoosh SFX. 2D vector cartoon, AumSum kids educational style, flat bold colors, bold black outlines, bright and clean, 16:9, 24fps. Negative: photorealistic, 3D render, blurry, deformed hands, extra fingers, watermark, dark mood.
```

### 5.2. Lưu ý khi dùng `@CharacterName`

- Nhập đúng tên đã lưu trong tab **Characters**.
- Kết hợp với **Ingredients**: chọn ảnh character sheet trong panel `+` hoặc `Ingredients` khi sinh video.
- Nếu Flow chưa nhận `@`, mô tả lại ngắn gọn nhân vật ở cuối prompt.

---

## 6. Chiến lược chuyển cảnh mượt mà

### 6.1. Giữ nguyên nhân vật trong 1 scene (Extend)

- Mỗi scene = 1 clip gốc 8s (Veo 3.1) hoặc 10s (Omni Flash).
- Dùng **Extend** 2-3 lần để đạt 24-32s liên tục.
- Khi extend, prompt chỉ mô tả **tiếp theo** hành động, không thay đổi nhân vật/bối cảnh.
- Giới hạn: sau 3-5 lần extend có thể bị **drift** (nhân vật biến dạng). Nên cắt scene trước khi drift.

**Ví dụ Extend prompt:**

```text
Continue from the last frame: @AumSum keeps pointing at the sun, the sun rays slowly pulse outward, his expression stays cheerful. Same blue sky, same 2D vector style. Smooth motion, 24fps.
```

### 6.2. Chuyển scene (Add Scene / Transition clip)

Các cách:

| Kỹ thuật | Khi nào dùng | Cách làm |
|----------|--------------|----------|
| **Cut đơn** | Chuyển ý lớn, thay đổi bối cảnh | Thêm scene mới. |
| **Match cut** | Cùng một hình dạng/đối tượng ở 2 scene | Sinh clip với prompt: `camera zooms into the sun, then dissolves to a blue light wave` bằng **Frames to Video**. |
| **Camera movement** | Giữ liên tục không gian | Prompt: `slow pan right from the sun to @AumSum holding a prism`. |
| **Whip pan / Dolly** | Tăng năng lượng | Prompt: `fast whip pan to a new blue sky scene, motion blur, 24fps`. |
| **Fade / Crossfade** | Nối 2 scene khác tone | Làm trong post bằng FFmpeg/CapCut. |

### 6.3. Frames to Video cho transition

- Sinh **end frame** của scene N (Ảnh PNG từ clip hoặc Nano Banana).
- Sinh **start frame** của scene N+1.
- Vào **Frames to Video**, upload 2 ảnh, prompt:

```text
Smooth cinematic transition from [end frame scene N] to [start frame scene N+1], camera moves right, motion blur, same 2D cartoon style, 2 seconds.
```

---

## 7. Giọng nói cố định & đa nhân vật

### 7.1. Trong Flow UI

- Tab **Characters → Select a voice** chọn voice cho từng character.
- Khi prompt có dialogue: `@AumSum says, "Why is the sky blue?"`.
- Omni Flash hỗ trợ audio reference và voice tốt hơn Veo 3.1.

### 7.2. Nếu làm tiếng Việt

- Flow voice chủ yếu là tiếng Anh.
- Cách 1: Sinh video **silent**, sau đó dùng **F5-TTS / Kokoro / edge-tts** để đọc tiếng Việt.
- Cách 2: Tìm 1 voice tiếng Việt mẫu, clone bằng **F5-TTS** hoặc **CosyVoice**, rồi áp dụng cho cả video.
- Cách 3: Thuê voice actor lồng tiếng (tốt nhất cho kênh chuyên nghiệp).

### 7.3. Casting voice mẫu

| Nhân vật | Voice Flow (tiếng Anh) | Ghi chú |
|----------|------------------------|---------|
| @AumSum | `Achird` (Male, friendly, mid pitch) | Giọng bạn thân, dễ nghe. |
| @Sunny (mặt trời) | `Autonoe` (Female, bright, mid pitch) | Vui tươi, năng động. |
| @Luna (mặt trăng) | `Aoede` (Female, breezy, mid pitch) | Dịu dàng. |
| Narrator | `Algieba` (Male, easy-going, mid-low pitch) | Trầm, rõ ràng. |

---

## 8. Workflow chi tiết từng bước trên Flow UI

### Bước 1: Tạo project mới

- Vào `labs.google/fx/tools/flow`.
- Click **New project**.
- Mở **Settings** (biểu tượng tune):
  - **Confirm before generating**: chọn `Never` nếu chạy batch tự động, hoặc `Always` nếu muốn kiểm soát credits.
  - **Video generation default**: chọn model phù hợp:
    - `Veo 3.1 Lite` — rẻ, nhanh, 8s, phù hợp test.
    - `Veo 3.1 Fast` — cân bằng.
    - `Veo 3.1 Quality` — đẹp nhất, 8s, tốn credits.
    - `Omni Flash` — tốt cho character consistency + voice/audio, 10s.
  - **Aspect ratio**: `16:9`.
  - **Scaling**: `1x` (hoặc `x2` rồi upscale sau).

### Bước 2: Tạo Characters & Ingredients

- Tab **Characters**: tạo `@AumSum`, `@Sunny`, v.v.
- Tab **All Media → Upload** hoặc **+ → Upload media**: upload character sheet, background PNG, prop PNG.
- Tạo **Collections** theo scene (ví dụ `Scene 05 - Scattering`) để quản lý.

### Bước 3: Sinh từng scene

- Gõ prompt theo công thức 7 phần.
- Thêm reference:
  - Click nút **+ / Add Media** hoặc chọn từ **Ingredients**.
  - Chọn ảnh `@AumSum front`, `@AumSum pointing`, background, prop.
- Click **arrow_forward → Create**.
- Approve (hoặc để `Never` để tự động).
- Sau khi có clip:
  - Nếu scene cần dài hơn → click clip → **Extend**.
  - Nếu cần chuyển cảnh → **Frames to Video** hoặc tạo scene mới.

### Bước 4: Dùng Scenebuilder

- Tab **Scenes**.
- Kéo các clip đã sinh vào timeline theo đúng thứ tự storyboard.
- Trim phần thừa ở đầu/cuối mỗi clip.
- Sắp xếp thứ tự, thêm transition clip ở giữa.
- Preview toàn bộ.
- Export scene-by-scene hoặc export toàn project.

### Bước 5: Post-production

- **Voiceover**: nếu Flow voice chưa đủ, dùng F5-TTS/Kokoro/edge-tts.
- **Subtitle**: burn captions bằng MoviePy/FFmpeg với font lớn, outline đen.
- **Music**: sinh nhạc nền bằng AudioCraft / Udio / Suno hoặc thư viện miễn phí (YouTube Audio Library).
- **SFX**: thêm whoosh, pop, chime theo hành động.
- **Upscale**: dùng Flow upscale 1080p (miễn phí cho Pro/Ultra) hoặc Topaz Video AI nếu cần 4K.
- **Final check**: độ dài 3-5 phút, âm thanh rõ, phụ đề đúng, không bị lỗi frame.

---

## 9. Ví dụ toàn bộ prompt cho "Why is the sky blue?"

Giả sử đã tạo `@AumSum` (mascot) và `@Sunny` (mặt trời).

### Scene 1 — Hook (8-10s)

```text
Medium shot, @AumSum stands center, waves his right hand and smiles at camera, then points up at a bright blue sky. Big white cloud floats by. Slow dolly-in. Cheerful kids music starts. 2D vector cartoon, AumSum educational style, flat bold colors, black outlines, bright blue sky, 16:9, 24fps.
Negative: photorealistic, 3D, blurry, dark, watermark, extra limbs.
```

### Scene 2 — Sunlight is white (8-10s)

```text
Wide shot, @AumSum stands on the left, points at a large friendly cartoon sun on the right. The sun has a smiling face and emits white rays that split into a rainbow arc. Blue sky background. Slow pan right following the rainbow. Soft chime SFX. 2D vector cartoon, AumSum kids educational style, flat colors, bold black outlines, 16:9, 24fps.
Negative: photorealism, 3D render, muddy colors, watermark, distorted face.
```

### Scene 3 — Blue light scatters (8-10s)

```text
Close-up, @AumSum holds a magnifying glass over tiny glowing blue spheres representing air molecules. Blue light waves bounce off the spheres in slow motion, spreading in all directions. @AumSum looks excited. Soft sparkle SFX. 2D vector cartoon, AumSum style, bright colors, black outlines, 16:9, 24fps.
Negative: realistic, 3D, dark background, blurry, watermark.
```

### Scene 4 — Red/Orange passes through (8-10s)

```text
Medium shot, @AumSum watches as red and orange light beams travel straight past the air molecules without bouncing. Red beams continue toward the right side of screen. Blue sky background. Slow tracking shot following the beams. 2D vector cartoon, AumSum style, flat colors, bold black outlines, 16:9, 24fps.
Negative: photorealistic, 3D, deformed hands, watermark.
```

### Scene 5 — Day vs sunset (8-10s)

```text
Wide shot split screen: left half bright blue daytime sky, right half orange sunset sky. @AumSum stands in the center, gestures left then right with a confused-then-happy expression. Slow zoom out. Warm to cool lighting transition. 2D vector cartoon, AumSum style, flat colors, bold black outlines, 16:9, 24fps.
Negative: photorealism, 3D, dark, watermark.
```

### Scene 6 — Recap + CTA (8-10s)

```text
Medium shot, @AumSum gives two thumbs up, a simple equation `Sun + Air + Scattering = Blue Sky` appears above his head in bold white text with black outline. Confetti pops. Cheerful music swells. 2D vector cartoon, AumSum style, flat colors, bold black outlines, 16:9, 24fps.
Negative: photorealistic, 3D, watermark, blurry text.
```

---

## 10. Tự động hóa bằng AI Agent

### 10.1. Đầu vào: `project.yaml`

```yaml
project: why-is-the-sky-blue
language: en
target_duration: 240  # seconds
characters:
  - name: AumSum
    description: "A friendly star-shaped 2D cartoon mascot..."
    voice: Achird
    style: "2D vector cartoon, AumSum style, flat bold colors, black outlines"
    references:
      - assets/aumsum_front.png
      - assets/aumsum_pointing.png

scenes:
  - id: 01
    title: Hook
    narration: "Hi friends! Let's learn why the sky is blue."
    duration: 10
    prompt: "Medium shot, @AumSum stands center, waves his right hand..."
    extend: 2
    transition: cut
  - id: 02
    title: Sunlight is white
    narration: "The sun sends white light made of many colors."
    duration: 10
    prompt: "Wide shot, @AumSum points at a large friendly cartoon sun..."
    extend: 2
    transition: pan_right
```

### 10.2. Agent steps

1. **Pre-prod**: đọc YAML → sinh storyboard JSON.
2. **Login Flow** qua Playwright hoặc gọi Gemini API.
3. **Create project** → setting model/aspect ratio.
4. **Create characters**: upload prompt + reference → save character IDs.
5. **Generate assets**: background/prop bằng Nano Banana.
6. **Generate scenes**: gửi prompt, approve, poll video URL, download.
7. **Extend**: nếu YAML yêu cầu, gọi Extend và poll.
8. **Transition clips**: sinh Frames-to-Video giữa scene.
9. **Assemble**: FFmpeg/MoviePy nối clip, thêm TTS, subtitle, music.
10. **QA**: kiểm tra duration, độ phân giải, lỗi drift.

### 10.3. Code mẫu (Python + Playwright)

Xem `tools/google_flow/flow_studio_agent.py` (nếu đã viết) hoặc viết từ các hàm:

- `create_flow_project()`
- `create_character(name, prompt, voice, references)`
- `set_project_settings(model, aspect, confirm=False)`
- `generate_scene(project, prompt, references, timeout=120)`
- `extend_clip(clip_id, prompt)`
- `frames_to_video(start_img, end_img, prompt)`
- `download_clip(url, path)`
- `assemble_video(scenes, output)`

---

## 11. Chi phí ước tính (video 4 phút, 240 giây)

Giả sử chia thành **8 scene × 30 giây**. Mỗi scene = 1 clip gốc 8s + 3 extend = 32s.

| Model | Clip gốc | Extend | Tổng clip | Credits Flow UI | Gemini API |
|-------|----------|--------|-----------|-----------------|------------|
| Veo 3.1 Lite | 8s × 8 = 64s | 7s × 24 = 168s | 232s | 8×10 + 24×10 = **320 cr** | ~$12 |
| Veo 3.1 Fast | 8s × 8 = 64s | 7s × 24 = 168s | 232s | 8×20 + 24×20 = **640 cr** | ~$28 |
| Omni Flash 10s | 10s × 8 = 80s | 10s × 16 = 160s | 240s | 8×30 + 16×30 = **720 cr** | ~$24 |

Chưa tính sinh reference images, upscale, retries.

---

## 12. Checklist trước khi render lần sau

- [ ] Đã tạo `@AumSum` và gán voice.
- [ ] Đã sinh ít nhất 4 ảnh reference (front, 3/4, pointing, thumbs-up).
- [ ] Mỗi prompt có `[SHOT] + [CHARACTER] + [ACTION] + [CONTEXT] + [CAMERA] + [AUDIO] + [STYLE] + [NEGATIVE]`.
- [ ] Đã chọn model phù hợp (Omni Flash nếu cần character + voice; Veo Fast nếu cần chuyển động cinematic).
- [ ] Mỗi scene không dài quá 40s trước khi cắt.
- [ ] Có transition clip hoặc camera movement giữa các scene.
- [ ] Đã chuẩn bị sẵn voiceover/script và music.
- [ ] Có kế hoạch retry nếu scene bị lỗi.

---

## 13. Rủi ro & cách tránh

| Rủi ro | Ảnh hưởng | Giải pháp |
|--------|-----------|-----------|
| Drift sau extend | Nhân vật biến dạng | Giới hạn 3 extend/scene, dùng reference ảnh mạnh. |
| Veo không đủ 2D cartoon | Ra phong cách 3D/realistic | Omni Flash + reference + negative prompt rõ ràng. |
| Giọng Flow không tiếng Việt | Không đọc đúng | Dùng F5-TTS/edge-tts tiếng Việt, burn subtitle. |
| Scenebuilder chưa lưu | Mất timeline | Export từng scene thường xuyên. |
| Credits hết | Dừng giữa chừng | Tính toán trước, mua Ultra nếu sản xuất nhiều. |
| Flow region lock | Không truy cập | Kiểm tra vùng hỗ trợ trước. |

---

## 14. Đề xuất tiếp theo

1. Anh duyệt workflow này.
2. Em sẽ tạo 1 project mới trên Flow, thiết lập Character + Voice + Ingredients theo đúng workflow.
3. Sinh lại toàn bộ `Why is the sky blue?` với 8 scene × 30s, nhân vật đồng nhất, transition mượt, voice cố định.
4. Post bằng MoviePy/FFmpeg: TTS tiếng Anh (hoặc tiếng Việt nếu anh muốn), subtitle, music.
5. Xuất final 1080p/4K và đẩy lên YouTube.
