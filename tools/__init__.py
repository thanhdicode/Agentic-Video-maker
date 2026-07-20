"""Client wrappers and utilities for external AI services."""

from .audio_gen import f5_tts, foley, kokoro_tts, musicgen
from .character_consistency import build_character_sheet_prompt, lora_training_command
from .comfyui_client import get_workflow_names, queue_workflow
from .ffmpeg_tools import assemble_video, burn_subtitles, mix_audio
from .ltx_video import i2v as ltx_i2v
from .music_tools import generate_music, generate_sfx
from .pose_estimator import detect_face_mediapipe, detect_pose_mediapipe
from .rhubarb_lipsync import download_rhubarb, mouth_open_at, run_rhubarb, volume_based_mouth
from .tooncrafter import interpolate as tooncrafter_interpolate
from .upscale_tools import upscale_image, upscale_video
from .wan_video import i2v as wan_i2v, t2v as wan_t2v
from .whisper_tools import generate_subtitles, transcribe_audio

__all__ = [
    # ComfyUI / workflow
    "queue_workflow",
    "get_workflow_names",
    # FFmpeg
    "assemble_video",
    "burn_subtitles",
    "mix_audio",
    # CPU music/SFX
    "generate_music",
    "generate_sfx",
    # AI audio
    "f5_tts",
    "kokoro_tts",
    "musicgen",
    "foley",
    # AI video (GPU)
    "wan_i2v",
    "wan_t2v",
    "ltx_i2v",
    "tooncrafter_interpolate",
    # Character / pose
    "build_character_sheet_prompt",
    "lora_training_command",
    "detect_pose_mediapipe",
    "detect_face_mediapipe",
    # Lip sync
    "run_rhubarb",
    "mouth_open_at",
    "volume_based_mouth",
    "download_rhubarb",
    # Upscale / subtitles
    "upscale_image",
    "upscale_video",
    "generate_subtitles",
    "transcribe_audio",
]
