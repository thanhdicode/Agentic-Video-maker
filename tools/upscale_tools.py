"""Real-ESRGAN and frame interpolation helpers."""

from __future__ import annotations

import os
import subprocess


def upscale_image(input_path: str, output_path: str, scale: int = 2, model: str = "RealESRGAN_x4plus") -> str:
    """Upscale an image using Real-ESRGAN."""
    # Assumes real-esrgan installed and `realesrgan-ncnn-vulkan` or Python package available
    try:
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
    except ImportError as exc:
        raise ImportError("Real-ESRGAN Python package not installed") from exc

    model_path = f"models/upscale/{model}.pth"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Upscale model not found: {model_path}")

    upsampler = RealESRGANer(scale=scale, model_path=model_path, model=RRDBNet())
    upsampler.enhance(input_path, output=output_path)
    return output_path


def upscale_video(input_video: str, output_video: str, scale: int = 2) -> str:
    """Extract frames, upscale, and re-encode video."""
    tmp_dir = output_video + "_frames"
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_video, f"{tmp_dir}/frame_%04d.png"],
            check=True,
            capture_output=True,
            text=True,
        )
        for fn in sorted(os.listdir(tmp_dir)):
            upscale_image(os.path.join(tmp_dir, fn), os.path.join(tmp_dir, fn), scale)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                f"{tmp_dir}/frame_%04d.png",
                "-c:v",
                "libx265",
                "-pix_fmt",
                "yuv420p",
                output_video,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)
    return output_video


def interpolate_video(input_video: str, output_video: str, target_fps: int = 60) -> str:
    """Interpolate frames using RIFE."""
    raise NotImplementedError("RIFE integration is a stub; wrap a RIFE CLI or Python API.")
