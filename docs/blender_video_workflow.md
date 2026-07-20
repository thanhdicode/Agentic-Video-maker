# Workflow edit video bằng Blender VSE (Video Sequence Editor)

> Blender không chỉ là 3D/VFX — nó còn có **Video Sequence Editor (VSE)** mạnh, có API Python đầy đủ, chạy headless (`blender -b`), không bắt buộc GPU, render bằng CPU. Đây là nền tảng edit video lý tưởng cho pipeline tự động / agentic khi DaVinci Resolve không chạy được (ví dụ máy ảo không có GPU).

---

## 1. Tại sao Blender VSE?

* **Không cần GPU** để edit & render cơ bản (render CPU).
* **Chạy headless**: `blender -b -P script.py` — không cần màn hình.
* **Python API đầy đủ** (`bpy`): thêm strip, text, audio, modifier, transition, render.
* **Có sẵn VFX/Compositor**: có thể xử lý màu, glow, blur, mask, 3D text, particles.
* **Cộng đồng lớn**, miễn phí, đa nền tảng (Windows/macOS/Linux).
* Phù hợp cho **game trailer/devlog** ở mức indie: cắt clip, thêm nhạc/narration, title card, color correction, export H.264.

---

## 2. Cài đặt Blender

### Windows

1. Tải **Portable .zip** từ [blender.org/download](https://www.blender.org/download/lts/4-2/).
2. Giải nén, ví dụ `C:\Program Files\Blender Foundation\Blender 4.2\`.
3. (Tùy chọn) set env `BLENDER_EXECUTABLE` trỏ đến `blender.exe`.

### macOS / Linux

```bash
# macOS (Homebrew)
brew install --cask blender

# Ubuntu/Debian
sudo apt update && sudo apt install blender

# Hoặc tải tarball từ blender.org
```

---

## 3. Kiểm tra Blender chạy headless

```bash
blender -b --python-expr "import bpy; print(bpy.app.version)"
# Output kỳ vọng: Blender 4.2.x, (4, 2, x)
```

---

## 4. Workflow Blender VSE cho game trailer

### 4.1 Chuẩn bị trước edit

| Thông số | Gợi ý |
| --- | --- |
| Resolution | 1920×1080 (YouTube/Steam) hoặc 1080×1920 (Shorts) |
| FPS | 30 hoặc 60, giữ nguyên toàn dự án |
| Audio | 48 kHz, AAC 192 kbps |
| Output | H.264 MP4 |

### 4.2 Cấu trúc timeline

Tương tự Resolve / bất kỳ editor nào:

* **Hook** 0–5s
* **Core Loop** 5–20s
* **Variety** 20–40s
* **Payoff** 40–55s
* **CTA** cuối 5s

### 4.3 Kênh VSE gợi ý

* **Kênh 1/2**: video clips (luân phiên để làm crossfade).
* **Kênh 3**: text overlay / title card.
* **Kênh 5/6/7**: narration, music, SFX.
* **Kênh 8**: hiệu ứng `GAMMA_CROSS` (crossfade).

VSE xếp kênh từ dưới lên — kênh cao hơn nằm trên.

### 4.4 Các thao tác chính qua Python

```python
import bpy

scene = bpy.context.scene
if not scene.sequence_editor:
    scene.sequence_editor_create()
sequences = scene.sequence_editor.sequences

# Thêm video strip
strip = sequences.new_movie(
    name="Clip_A",
    filepath="C:/Renders/clip_a.mp4",
    channel=1,
    frame_start=1,
)

# Trim in/out (tính bằng frame)
strip.frame_offset_start = 30   # bỏ 1 giây đầu ở 30fps
strip.frame_offset_end = 30     # bỏ 1 giây cuối

# Crossfade với clip trước
cross = sequences.new_effect(
    name="Cross", type="GAMMA_CROSS", channel=8,
    frame_start=strip.frame_start,
    frame_end=strip.frame_start + 12,
    seq1=prev_strip, seq2=strip,
)

# Text overlay
text = sequences.new_effect(
    name="Title", type="TEXT", channel=3,
    frame_start=1, frame_end=60,
)
text.text = "GAME TITLE"
text.font_size = 80
text.color = (1.0, 1.0, 1.0, 1.0)
text.location = (0.5, 0.85)
text.align_x = "CENTER"
text.use_shadow = True

# Audio strip + volume
audio = sequences.new_sound(
    name="Music", filepath="C:/Audio/music.mp3",
    channel=5, frame_start=1,
)
audio.volume = 0.3
audio.keyframe_insert(data_path="volume", frame=1)

# Color correction modifier
bc = strip.modifiers.new(name="BC", type="BRIGHT_CONTRAST")
bc.bright = 0.05
bc.contrast = 0.1

cb = strip.modifiers.new(name="CB", type="COLOR_BALANCE")
cb.color_balance.lift = (0.95, 0.95, 1.0)
cb.color_balance.gain = (1.1, 1.05, 0.95)

# Render settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.audio_codec = "AAC"
scene.render.ffmpeg.audio_bitrate = 192
scene.render.filepath = "C:/Renders/trailer.mp4"

# Auto frame range
scene.frame_start = 1
scene.frame_end = max(s.frame_final_end for s in sequences)

bpy.ops.render.render(animation=True)
```

---

## 5. Dùng wrapper `tools/blender_edit.py`

Repo đã có `BlenderVideoEditor` — tự động sinh script + JSON config rồi gọi Blender headless.

```python
from tools.blender_edit import BlenderVideoEditor

editor = BlenderVideoEditor()  # auto tìm Blender hoặc set BLENDER_EXECUTABLE

output = editor.assemble(
    video_paths=["clip_01.mp4", "clip_02.mp4", "clip_03.mp4"],
    output="C:/Renders/final_trailer.mp4",
    resolution=(1920, 1080),
    fps=30,
    transition_frames=12,
    audio_clips=[
        {"path": "narration.wav", "volume": 1.0},
        {"path": "music.mp3", "volume": 0.3, "fit_to_timeline": True},
    ],
    text_overlays=[
        {"text": "My Game", "start_sec": 0, "duration_sec": 2, "font_size": 80},
    ],
)
print("Rendered:", output)
```

### Tích hợp pipeline

```cmd
set AI_VIDEO_USE_BLENDER=1
python -m agents.orchestrator --idea "Epic game launch trailer"
```

Hoặc dùng biến tổng quát:

```cmd
set AI_VIDEO_EDIT_ENGINE=blender
python -m agents.orchestrator --idea "Game devlog episode 1"
```

---

## 6. Cấu hình `config/settings.yaml`

```yaml
blender:
  enabled: false
  executable: ""              # để trống = tự tìm Blender
  resolution: "1920x1080"
  fps: 30
  transition_frames: 12       # crossfade giữa các clip
  music_volume: 0.3             # nhạc nền duck dưới narration
  narration_volume: 1.0
  text_overlay_enabled: true
  text_overlay_font_size: 80
  text_overlay_duration_sec: 2.0
  text_overlay_location: [0.5, 0.85]
  text_overlay_color: [1.0, 1.0, 1.0, 1.0]
```

---

## 7. Ưu/nhược điểm so với DaVinci Resolve

| Tiêu chí | Blender VSE | DaVinci Resolve Studio |
| --- | --- | --- |
| GPU | Không bắt buộc | Bắt buộc OpenCL/CUDA |
| Color grading | Cơ bản (modifiers, Compositor) | Chuyên nghiệp (nodes, HDR, DRT) |
| Audio mix | Cơ bản (volume, keyframe) | Chuyên nghiệp (Fairlight, LUFS, EQ) |
| VFX/Motion Graphics | Rất mạnh (Compositor, Geometry Nodes) | Rất mạnh (Fusion) |
| Scripting | Python API, chạy headless | Python API (cần Studio) |
| Chi phí | Miễn phí | Studio trả phí cho external scripting |
| Phù hợp | Agentic/automated edit, headless, CPU | Final mastering màu/sound chuẩn broadcast |

---

## 8. Tips

* **Render ảnh sequence trước** nếu edit dài (> vài phút): tránh lỗi crash giữa chừng, sau đó gộp bằng FFmpeg.
* **Dùng Compositor** để color grade nâng cao: add `Color Balance`, `RGB Curves`, `Glare`, `Lens Distortion`.
* **Proxy / Preview**: khi edit bằng UI, tạo proxy 25% để mượt; script headless thì không cần.
* **Subtitles**: tạo text strips từ file SRT bằng cách parse SRT trong Python rồi gọi `sequences.new_effect(type='TEXT')` cho từng dòng.
* **Performance**: render CPU, tận dụng `-t` để giới hạn threads nếu cần.

---

## 9. Kiểm tra nhanh

```cmd
blender -b --python-expr "import bpy; print(bpy.app.version)"
set AI_VIDEO_USE_BLENDER=1
python -m agents.orchestrator --idea "Blender VSE demo"
```
