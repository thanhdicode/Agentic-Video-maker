"""Client wrappers and utilities for external AI services."""

from .comfyui_client import queue_workflow
from .ffmpeg_tools import assemble_video, burn_subtitles, mix_audio
from .music_tools import generate_music, generate_sfx
from .upscale_tools import upscale_image, upscale_video
from .whisper_tools import generate_subtitles, transcribe_audio

__all__ = [
    "queue_workflow",
    "assemble_video",
    "burn_subtitles",
    "mix_audio",
    "generate_music",
    "generate_sfx",
    "upscale_image",
    "upscale_video",
    "generate_subtitles",
    "transcribe_audio",
]
