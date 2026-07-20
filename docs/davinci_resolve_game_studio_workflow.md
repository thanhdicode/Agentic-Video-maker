# Workflow DaVinci Resolve chỉn chu cho Studio Game

> Mục tiêu: xây dựng trailer / devlog / cinematic bằng DaVinci Resolve theo quy trình post-production của studio game chuyên nghiệp — từ ingest, edit, VFX, color, audio đến delivery — và tự động hóa bằng Python API.

---

## 1. Tại sao Resolve là lựa chọn cho studio game?

* **All-in-one**: Media, Cut, Edit, Fusion, Color, Fairlight, Deliver trong một app.
* **Miễn phí mạnh mẽ** cho indie / solo (DaVinci Resolve).
* **Studio** bắt buộc nếu muốn điều khiển từ Python bên ngoài.
* **Color & audio chuyên nghiệp**: dễ dàng đạt look cinematic và mix âm thanh chuẩn LUFS.
* **Fusion**: title, lower third, end card, particle, glow, screen replacement, comp 2D/3D.

---

## 2. Thiết lập dự án (làm trước khi edit)

### 2.1 Xác định spec đích ngay từ đầu

| Thông số | Gợi ý trailer game |
| --- | --- |
| Resolution | 1920×1080 (YouTube/Steam) hoặc 2560×1440/3840×2160 (master) |
| Frame rate | 30 hoặc 60 fps — **giữ nguyên trong toàn bộ dự án** |
| Audio | 48 kHz, 24-bit |
| Color science | `davinciYRGBColorManagedv2` |
| Deliver master | QuickTime `ProRes 422 HQ` hoặc `ProRes 4444 XQ` |
| Deliver web | MP4 `H.264` / `H.265` |

> **Cảnh báo**: đổi frame rate giữa chừng sẽ gây lệch âm thanh và render sai. Thống nhất từ ngày đầu.

### 2.2 Quy tắc đặt tên project

```text
GameName_Trailer_v01
GameName_Devlog_Ep03_v02
CharacterTeaser_Demo_v01
```

### 2.3 Thiết lập Project Settings

Vào `File > Project Settings` hoặc dùng API:

```python
project.SetSetting("colorScienceMode", "davinciYRGBColorManagedv2")
project.SetSetting("timelineResolutionWidth", "1920")
project.SetSetting("timelineResolutionHeight", "1080")
project.SetSetting("timelineFrameRate", "60")
```

---

## 3. Tổ chức Media Pool theo studio

Tạo bins trước khi import bất kỳ clip nào:

* `Gameplay_Raw`
* `Captures_Broll`
* `Audio_Music`
* `Audio_SFX`
* `VO` (Voice Over)
* `Brand_Assets` (logo, end card, watermark)
* `Exports` (draft / final renders)

Dùng API:

```python
media_pool = project.GetMediaPool()
root = media_pool.GetRootFolder()
for name in ["Gameplay_Raw", "Audio_Music", ...]:
    media_pool.AddSubFolder(root, name)
```

---

## 4. Cấu trúc trailer / devlog chuyên nghiệp

Dùng template 5 phần sau để giữ pacing rõ ràng:

| Phần | Thời gian | Nội dung |
| --- | --- | --- |
| **Hook** | 0–5s | Hình ảnh mạnh nhất hoặc gameplay action gay cấn nhất |
| **Core Loop** | 5–20s | Người chơi làm gì lặp đi lặp lại — combat, craft, platform... |
| **Variety** | 20–40s | Nhiều môi trường, enemy, progression, feature khác nhau |
| **Payoff** | 40–55s | Boss fight, high-tension moment, reveal lớn nhất |
| **CTA** | Cuối 5s | Tên game, nền tảng, Wishlist / Release date |

**Mẹo pro**: tắt âm thanh, xem timeline ở **1.5× speed**. Nếu câu chuyện vẫn hiểu được, cấu trúc edit đã tốt. Chỉ bắt đầu color grading sau khi pacing ổn.

---

## 5. Workflow theo từng Page

### 5.1 Media Page — Ingest & Proxy

* Import gameplay capture, screen recordings, VO, music, SFX.
* Tạo proxy nếu source là 4K/6K để edit mượt.
* Kiểm tra metadata: frame rate, resolution, audio channels.

### 5.2 Cut Page — Rough Assembly nhanh

* Dùng Cut page để chọn moment tốt nhất từ raw footage.
* Tạo một timeline `Selects` chứa highlight theo thứ tự impact, không theo thời gian.
* Xóa dead time: mỗi shot nên đẩy story hoặc mechanic đi một bước.

### 5.3 Edit Page — Refine

* Build timeline `Final` từ `Selects`.
* Đặt VO trước, sau đó chèn gameplay theo VO.
* Music temp trước, sau đó thay music final ở Fairlight.
* Tránh transitions flashy che gameplay; dùng cut sạch và J/L cuts.

### 5.4 Fusion Page — VFX & Motion Graphics

* **Title card / end card**: `Text+` kết hợp background blur + glow.
* **Lower third**: tên kênh / platform / release date.
* **Screen replacement**: theo dõi gameplay UI vào màn hình mockup.
* **Particles / embers / muzzle flash**: dùng Fusion particle system.
* **Light bloom / lens dirt**: tạo cinematic look cho cinematic shots.

### 5.5 Color Page — Cinematic Look

1. **Color Management**: set `davinciYRGBColorManagedv2`, chọn input/output color space.
2. **Node tree gợi ý**:
   * Node 1: `Color Space Transform` hoặc `Input LUT`.
   * Node 2: Primaries / balance (lift, gamma, gain).
   * Node 3: Look LUT (`.cube`) hoặc `FilmConvert`.
   * Node 4: Vignette / grain / bloom.
3. **LUT/CDL qua API**:

```python
project.RefreshLUTList()
item.SetLUT(1, "/path/to/look.cube")
item.SetCDL({
    "NodeIndex": "1",
    "Slope": "1.1 1.05 1.0",
    "Offset": "0.0 0.0 0.0",
    "Power": "0.95 1.0 1.05",
    "Saturation": "1.1",
})
```

4. **HDR/SDR**: nếu target YouTube HDR, dùng `Rec.2100 ST2084` và export metadata đúng.

### 5.6 Fairlight Page — Audio Mix chuẩn studio

* **Dialog**: noise reduction, EQ, compression, de-esser.
* **Music**: side-chain để VO nổi; music duck khi VO phát.
* **SFX**: đảm bảo mỗi impact gameplay được nghe rõ.
* **Loudness target**:
  * YouTube: **-14 LUFS** integrated.
  * Game trailer / cinema: **-24 LUFS** hoặc **-23 LUFS** (ATSC).
* Xuất stems nếu cần localization sau này.

### 5.7 Deliver Page — Render & Platform Specs

| Platform | Cài đặt gợi ý |
| --- | --- |
| Master archive | `QuickTime` `ProRes 4444 XQ` hoặc `ProRes 422 HQ` |
| YouTube / Steam | `MP4` `H.264`, 15–25 Mbps 1080p, 30–50 Mbps 4K |
| TikTok / Shorts | 1080×1920, 60 fps, bitrate 8–16 Mbps |
| Press kit | `ProRes 422` + `H.264` thấp để xem trước |

---

## 6. Tự động hóa bằng Python API

### 6.1 Yêu cầu

* **DaVinci Resolve Studio** (bản Free chỉ chạy script trong Console/Fusion, không chạy từ command line).
* Resolve đang chạy, hoặc khởi động với flag `-nogui`.
* Bật external scripting: `Preferences > General > External scripting using > Local`.

### 6.2 Biến môi trường (Resolve tự động setup trong `tools/davinci_resolve.py`)

Windows:

```cmd
set RESOLVE_SCRIPT_API=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
set PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\
```

### 6.3 Ví dụ dùng `tools/davinci_resolve.py`

```python
from tools.davinci_resolve import ResolveController, ClipInfo

with ResolveController(project_name="MyGame_Trailer") as resolve:
    resolve.configure_project(1920, 1080, "60")
    resolve.create_bins(["Gameplay_Raw", "Audio_Music", "Exports"])

    clips = resolve.import_media(["clip1.mp4", "clip2.mp4"])
    infos = [ClipInfo(media_pool_item=c) for c in clips]
    timeline = resolve.create_timeline("Final", clip_infos=infos)

    # Grade first clip
    items = resolve.get_timeline_items("video", 1)
    if items:
        resolve.apply_lut(items[0], "looks/cinematic.cube")

    # Render
    resolve.set_render_format_codec("mp4", "H264")
    resolve.set_render_job_settings(
        target_dir="C:/Renders",
        custom_name="MyGame_Trailer_v01",
    )
    resolve.add_render_job()
    resolve.start_rendering()
    resolve.wait_for_render()
```

### 6.4 Tích hợp pipeline

Set biến môi trường để `edit_node` dùng Resolve thay vì FFmpeg:

```cmd
set AI_VIDEO_USE_RESOLVE=1
python -m agents.orchestrator --idea "Epic game launch trailer"
```

Hoặc chỉnh `config/settings.yaml`:

```yaml
resolve:
  enabled: true
  resolution: "1920x1080"
  fps: 60
  color_science: "davinciYRGBColorManagedv2"
  render_format: "mp4"
  render_codec: "H264"
  audio_codec: "aac"
  render_name: "final_resolve"
  lut_path: "assets/luts/game_look.cube"
```

---

## 7. Lỗi thường gặp cần tránh

* Edit trước khi tổ chức bins.
* Trộn nhiều frame rate mà không có kế hoạch.
* Dùng transition quá nhiều che mất gameplay.
* Để music át voice-over và SFX quan trọng.
* Không test compression sau render — xem lại file export trên thiết bị thực.
* Color grading quá sớm trước khi pacing hoàn thiện.

---

## 8. QC Checklist trước khi xuất

* [ ] Xem lại ở 1.5×, tắt âm thanh.
* [ ] Hook đủ mạnh trong 5 giây đầu.
* [ ] Core loop rõ ràng: người xem hiểu cách chơi.
* [ ] Âm thanh không clipping, music duck khi có VO.
* [ ] LUT/grade đồng nhất toàn bộ.
* [ ] End card có tên game, platform, CTA.
* [ ] Render master `ProRes` lưu trữ trước khi nén web.
* [ ] Test file web trên YouTube/TikTok/Steam preview.
