# Google Flow / Veo 3.1 / Gemini Omni Flash — Research làm video 4-5 phút cho kênh giáo dục trẻ em

> Tài liệu tổng hợp cách dùng **Google Flow** (`flow.google.com` / `labs.google/fx/tools/flow`) và API tương đương (`Gemini API` cho `Veo 3.1` và `Gemini Omni Flash`) để làm video hoạt hình 2D giáo dục dài 4-5 phút, phù hợp với phong cách AumSum / Dr. Binocs / Smile and Learn.

---

## 1. Google Flow là gì?

Google Flow là **AI creative studio** của Google, tích hợp:

- **Veo 3.1** (`Lite`, `Fast`, `Quality`): text-to-video, image-to-video, extend, first/last frame, reference images, native audio.
- **Gemini Omni Flash**: multimodal video generation & conversational editing (3-10s, 720p), hỗ trợ reference ảnh, video, giọng nói, audio.
- **Nano Banana / Imagen 4**: sinh ảnh characters, background, props.
- **Scenebuilder**: timeline ghép nhiều clip, trim, preview, export.
- **Flow Agent**: chat agent giúp brainstorm, viết prompt, chọn model, generate theo lô.

Giao diện chính: [flow.google.com](https://flow.google.com) hoặc [labs.google/fx/tools/flow](https://labs.google/fx/tools/flow). Yêu cầu tài khoản Google, 18+, ở khu vực được hỗ trợ (VPN **không** mở được vùng không hỗ trợ).

---

## 2. Yêu cầu & chi phí

### 2.1. Gói Flow / Google AI

| Gói | Giá / tháng | Flow credits / tháng | Ghi chú |
|-----|-------------|----------------------|---------|
| Free | $0 | 50/ngày + 100 starter | Chỉ đủ thử nghiệm, **không đủ** làm 4-5 phút |
| Google AI Plus | ~$4.99 | 200 | Ít cho video dài |
| Google AI Pro | $19.99 ($9.99 6 tháng đầu) | 1,000 | Đủ vài video ngắn/tháng |
| Google AI Ultra $99 | $99.99 | 10,000 | Nhiều video 4-5 phút |
| Google AI Ultra $200 | $199.99 | 25,000 | Sản xuất hàng loạt |

Nguồn: [Google Flow Help – Manage credits](https://support.google.com/flow/answer/16526234), [Google AI plans](https://one.google.com/about/google-ai-plans/).

### 2.2. Credits mỗi generation trên Flow UI

| Model | Clip | Non-Ultra | Ultra |
|-------|------|-----------|-------|
| Veo 3.1 Lite | 4/6/8s | 10 | 5 |
| Veo 3.1 Fast | 4/6/8s | 20 | 10 |
| Veo 3.1 Quality | 8s | 100 | 100 |
| Gemini Omni Flash | 4s/6s/8s/10s | 15/20/25/30 | 15/20/25/30 |
| Upscale 1080p | – | 0 (cần gói trả phí) | 0 |
| Upscale 4K | – | không có | 50 |

Nguồn: [Manage your Google Flow credits](https://support.google.com/flow/answer/16526234?co=GENIE.Platform%3DAndroid&hl=en).

### 2.3. Gemini API (trả theo giây, không cần gói Flow)

| Model | 720p | 1080p | 4K | Ghi chú |
|-------|------|-------|----|---------|
| Veo 3.1 Standard | $0.40/s | $0.40/s | $0.60/s | Chất lượng cao nhất |
| Veo 3.1 Fast | $0.10/s | $0.12/s | $0.30/s | Cân bằng |
| Veo 3.1 Lite | $0.05/s | $0.08/s | không | Rẻ, nhanh, ít VRAM/cloud cost |
| Gemini Omni Flash | ~$0.10/s | 720p only | – | Tốt cho character & audio, tối đa 10s |

Nguồn: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

---

## 3. Giới hạn độ dài & cách đạt 4-5 phút

### 3.1. Giới hạn từng clip

- **Veo 3.1**: 4s, 6s, 8s (Quality chỉ 8s). 24fps. Aspect `16:9` hoặc `9:16`.
- **Gemini Omni Flash**: 3s-10s, 720p, 24fps.
- **Extend**: mỗi lần thêm ~7-8s, tối đa khoảng **148s** qua API, hoặc 60s+ trong Flow Scenebuilder.
- Chất lượng extend bắt đầu **drift** sau **3-5 lần extend** (nhân vật, ánh sáng, vật thể biến đổi).

### 3.2. Chiến lược làm 4-5 phút (240-300s)

Flow không sinh 1 video dài 5 phút một lúc. Bạn phải **chia nhỏ rồi ghép**:

1. **Storyboard 25-40 scene**, mỗi scene 1 câu/c ý tưởng, 8-15s.
2. **Mỗi scene** = 1-2 clip gốc (8-10s) có thể extend thêm 1-3 lần để đạt 20-40s.
3. **Dùng Scenebuilder** (hoặc export ra rồi dùng FFmpeg/CapCut) để nối các scene.
4. **Thêm voiceover, nhạc nền, SFX, subtitle** ở bước post.

Ví dụ phân bổ:

- 6 scene × 45s = 4m30s
- 10 scene × 30s = 5m
- 30 clip 10s = 5m (dùng Gemini Omni Flash API)

---

## 4. Workflow chi tiết trên Google Flow UI

### Bước 1: Kịch bản & storyboard

Viết kịch bản theo công thức AumSum:

- Hook 3s đầu.
- 1 ý/1 prop/1 hành động mỗi scene.
- Nhân vật phản ứng (ngạc nhiên, chỉ tay, thumbs-up).
- Recap + CTA ở cuối.

### Bước 2: Tạo Characters

1. Vào **Characters** trong Flow.
2. Dán mô tả hoặc upload character sheet (front/back/profile).
3. Đặt tên, gán **Voice** (`@Tên` và `@Voice: Tên`).
4. Lưu để tái dùng trong mọi scene.

Ví dụ prompt character:

```text
A friendly 2D cartoon mascot for kids educational channel, round head, big expressive eyes, simple nose, bright flat colors, bold black outlines, smiling, waving hand, AumSum style, white background, vector illustration.
```

### Bước 3: Chuẩn bị Ingredients

- **Style reference**: 1-2 ảnh minh họa phong cách 2D cartoon.
- **Backgrounds**: mỗi scene 1 background sáng màu, đơn giản.
- **Props**: mặt trời, bong bóng, ngôi sao, cây cối, v.v.

Tip: ảnh reference nên có **nền trắng/plain hoặc segmented** để Flow ghép tốt hơn.

### Bước 4: Sinh video từng scene

1. Chọn model:
   - **Gemini Omni Flash** nếu cần character + giọng nói + nhiều reference.
   - **Veo 3.1 Quality/Fast** nếu cần chuyển động cinematic, physics, 1080p/4K.
2. Cài đặt: aspect `16:9`, duration 8s (hoặc 10s Omni), resolution `720p`/`1080p`.
3. Thêm **Ingredients** (character, background, props) bằng `@Tên`.
4. (Tùy chọn) thêm **Start frame / End frame** để kiểm soát đầu/cuối.
5. Prompt theo công thức 5 phần:

```text
[SHOT] Wide shot, [SUBJECT] a friendly orange mascot points at a bright sun, [ACTION] smiling and explaining, [CONTEXT] in a blue sky with fluffy clouds, [STYLE] 2D vector cartoon, flat colors, bold outlines, AumSum kids educational style, smooth animation, 24fps.
```

### Bước 5: Extend hoặc Add Scene

- **Extend**: dùng khi muốn tiếp tục hành động trong cùng 1 shot (ít cut).
- **Add Scene (Jump To)**: dùng khi chuyển góc máy, bối cảnh, hoặc nhân vật xuất hiện khác.

### Bước 6: Scenebuilder

- Kéo các clip vào timeline.
- Trim đầu/cuối.
- Preview toàn bộ.
- Export từng scene hoặc cả project.

Lưu ý: Scenebuilder **chưa lưu state khi rời khỏi** (đang cập nhật), nên export ngay khi xong.

### Bước 7: Post-production

- **Voiceover tiếng Việt**: Flow voice chủ yếu là tiếng Anh. Nên export video, sau đó dùng TTS tiếng Việt (F5-TTS / Kokoro / edge-tts) và ghép trong CapCut / DaVinci / MoviePy.
- **Subtitle**: tự động burn captions.
- **Music/SFX**: thêm nhạc nền vui, SFX nhấn mạnh chuyển cảnh.

---

## 5. Tự động hóa bằng AI Agent / API

### 5.1. Google Flow UI không có API chính thức

Bạn không thể gọi trực tiếp Flow UI bằng REST chính chủ. Có 2 hướng tự động:

1. **Gemini API** (`google-genai`) – dùng `Veo 3.1` hoặc `Gemini Omni Flash`.
2. **useapi.net** – wrapper third-party REST cho Flow UI (cần token riêng, $15/tháng + credits Flow).

### 5.2. Ví dụ Python: Gemini API + Veo 3.1

```bash
pip install -U "google-genai>=2.9.0"
```

```python
import os, time
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Wide shot, a friendly 2D cartoon mascot with round head and big eyes explains why the sky is blue, pointing at the sky, bright flat colors, bold black outlines, kids educational style, 16:9, 24fps.",
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="1080p",
        duration_seconds=8,
        negative_prompt="realistic, photorealistic, 3D render, blurry, low quality",
    ),
)

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
client.files.download(file=video)
print(video.uri)
```

### 5.3. Ví dụ Python: Gemini Omni Flash

```python
import base64, os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

interaction = client.interactions.create(
    model="gemini-omni-flash-preview",
    input="A friendly 2D cartoon mascot waves and smiles in a bright classroom, kids educational show style, 16:9, smooth animation.",
    response_format={"type": "video", "aspect_ratio": "16:9"},
)

with open("scene.mp4", "wb") as f:
    f.write(base64.b64decode(interaction.output_video.data))
```

### 5.4. Ghép nhiều clip thành 4-5 phút bằng FFmpeg

```bash
# Tạo list.txt chứa đường dẫn các clip
printf "file 'scene_01.mp4'\nfile 'scene_02.mp4'\n" > list.txt

ffmpeg -f concat -i list.txt -c copy -r 24 final.mp4
```

---

## 6. Ước tính chi phí cho video 4-5 phút (300s)

Giả sử chia thành 30 clip × 10s hoặc 38 clip × 8s.

| Phương án | 4 phút (240s) | 5 phút (300s) | Ghi chú |
|-----------|---------------|---------------|---------|
| Omni Flash API 720p | ~$24 | ~$30 | ~$0.10/s, clip 10s |
| Veo 3.1 Lite API 720p | ~$12 | ~$15 | $0.05/s |
| Veo 3.1 Lite API 1080p | ~$19 | ~$24 | $0.08/s |
| Veo 3.1 Fast API 1080p | ~$29 | ~$36 | $0.12/s |
| Veo 3.1 Standard 1080p | ~$96 | ~$120 | $0.40/s |
| Flow UI Ultra ($199/mo, 25,000 cr) Veo 3.1 Lite | ~190 cr | ~380 cr | Rất rẻ với Ultra |
| Flow UI Ultra Veo 3.1 Quality | ~3,000 cr | ~3,800 cr | Vẫn còn dư credits |

Chưa tính retries, sinh reference images, upscale 4K, hoặc TTS nhạc ngoài.

---

## 7. Lưu ý & rủi ro quan trọng

1. **Phong cách 2D cartoon không dễ**: Veo 3.1 nghiêng về **realism/cinematic**. Omni Flash linh hoạt hơn nhưng giới hạn 720p. Cần **reference images mạnh**, nhiều lần retry, và prompt rõ ràng.
2. **Extend drift**: sau 3-5 lần extend nhân vật có thể biến dạng. Nên giữ mỗi scene ngắn (~20-40s) rồi ghép.
3. **Watermark**: video sinh từ Flow/UI trên Free/Plus/Pro có watermark hiển thị; Ultra có thể không watermark tùy quy định địa phương. **SynthID watermark vô hình** luôn có.
4. **Giọng nói tiếng Việt**: Flow voice chủ yếu tiếng Anh. Nên làm video silent hoặc dùng TTS tiếng Việt riêng.
5. **An toàn trẻ em**: Flow có guardrail. Không nên tạo hình ảnh trẻ em chân thực; nhân vật cartoon là ổn. Tuân thủ COPPA/YouTube Kids policies.
6. **Region lock**: Flow chưa mở ở mọi quốc gia. Kiểm tra danh sách supported regions trước khi mua gói.
7. **Không có API chính thức của Flow UI**: nếu muốn agent tự động hoàn toàn, dùng Gemini API là ổn định nhất.

---

## 8. Khuyến nghị cho anh

| Mục tiêu | Cách làm tốt nhất |
|----------|-------------------|
| Nhanh, ít code, dùng web | **Flow UI + Google AI Ultra ($199/mo)** → Agent mode + Scenebuilder |
| Agent tự động 100% | **Gemini API (`Veo 3.1` hoặc `Omni Flash`) + Python + FFmpeg** |
| Chất lượng 2D cartoon cao nhất | Kết hợp **FLUX + LoRA character sheet** (Nano Banana) + **Omni Flash** cho video + **F5-TTS** cho tiếng Việt |
| Tiết kiệm nhất | **Veo 3.1 Lite** 720p hoặc **Omni Flash** API |

Nếu anh muốn, em có thể:

1. Viết **script Python tự động** nhận kịch bản, gọi Gemini API/Omni Flash sinh từng scene, extend, rồi ghép thành video 4-5 phút.
2. Tích hợp vào repo `Agentic-Video-maker` làm backend thay cho Pollinations/MoviePy.
3. So sánh thêm **Kling 3.0 / LTX / Wan** nếu Flow chưa đủ 2D cartoon.

---

## 9. Nguồn tham khảo

- [Google Flow](https://flow.google.com) / [labs.google/fx/tools/flow](https://labs.google/fx/tools/flow)
- [Flow Help – Create videos](https://support.google.com/flow/answer/16353334)
- [Flow Help – Edit & build scenes](https://support.google.com/flow/answer/16935718)
- [Flow Help – Manage credits](https://support.google.com/flow/answer/16526234)
- [Flow models & supported features](https://support.google.com/labs/answer/16352836)
- [Gemini API – Veo 3.1](https://ai.google.dev/gemini-api/docs/models/veo-3.1-generate-preview)
- [Gemini API – Omni Flash](https://ai.google.dev/gemini-api/docs/omni)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Google AI plans](https://one.google.com/about/google-ai-plans/)
- [useapi.net Google Flow API (third-party)](https://useapi.net/docs/api-google-flow-v1)
- [Google Developers Blog – Veo 3.1](https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/)
