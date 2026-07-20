"""Rhubarb Lip Sync wrapper.

Rhubarb is a CPU tool that converts speech audio into timed 2D mouth shapes
(A-F + X). It is the standard for open-source 2D cartoon lip-sync.

Repo: https://github.com/DanielSWolf/rhubarb-lip-sync
Windows binary: https://github.com/DanielSWolf/rhubarb-lip-sync/releases
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import requests
from pydub import AudioSegment


RHUBARB_RELEASE = "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Windows.zip"
MOUTH_OPEN_MAP = {
    "X": 0.0,
    "A": 0.15,
    "B": 0.30,
    "C": 0.45,
    "D": 0.70,
    "E": 0.85,
    "F": 0.90,
    "G": 0.55,
    "H": 0.40,
}


def _find_rhubarb(tool_dir: Path) -> Path | None:
    candidates = [
        tool_dir / "rhubarb.exe",
        tool_dir / "rhubarb",
        Path("tools/rhubarb/rhubarb.exe"),
        Path("tools/rhubarb/rhubarb"),
        Path("rhubarb.exe"),
        Path("rhubarb"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return shutil.which("rhubarb")


def download_rhubarb(tool_dir: Path = Path("tools/rhubarb")) -> Path:
    """Download and extract the Windows Rhubarb binary."""
    tool_dir.mkdir(parents=True, exist_ok=True)
    exe = tool_dir / "rhubarb.exe"
    if exe.exists():
        return exe
    zip_path = tool_dir / "rhubarb.zip"
    if not zip_path.exists():
        r = requests.get(RHUBARB_RELEASE, timeout=120)
        r.raise_for_status()
        zip_path.write_bytes(r.content)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(tool_dir)
    zip_path.unlink(missing_ok=True)
    return exe


def run_rhubarb(audio_path: str | Path, tool_dir: Path = Path("tools/rhubarb")) -> list[dict]:
    """Return list of {start, end, mouth} from a wav/mp3 audio file."""
    audio_path = Path(audio_path)
    rhubarb = _find_rhubarb(tool_dir)
    if not rhubarb:
        rhubarb = download_rhubarb(tool_dir)

    # Rhubarb only accepts WAV/OGG (mono or stereo).
    wav_path = audio_path.with_suffix(".wav")
    if not wav_path.exists():
        seg = AudioSegment.from_file(str(audio_path))
        seg = seg.set_channels(1).set_frame_rate(22050)
        seg.export(str(wav_path), format="wav")

    cmd = [str(rhubarb), "-o", "json", str(wav_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    cues = []
    for cue in data.get("mouthCues", []):
        cues.append({
            "start": float(cue["start"]),
            "end": float(cue["end"]),
            "mouth": str(cue["value"]),
        })
    return cues


def mouth_open_at(t: float, cues: list[dict]) -> float:
    """Get mouth openness (0..1) at time t from Rhubarb cues or volume values."""
    for cue in cues:
        if cue["start"] <= t < cue["end"]:
            v = cue["mouth"]
            if isinstance(v, (int, float)):
                return float(v)
            return MOUTH_OPEN_MAP.get(v, 0.0)
    return 0.0


def volume_based_mouth(audio_path: str | Path, fps: float = 30.0) -> list[float]:
    """Fallback when Rhubarb is unavailable: derive mouth openness from RMS volume."""
    seg = AudioSegment.from_file(str(audio_path))
    seg = seg.set_channels(1)
    frame_ms = 1000.0 / fps
    values = []
    for i in range(int(math.ceil(len(seg) / frame_ms))):
        chunk = seg[int(i * frame_ms):int((i + 1) * frame_ms)]
        rms = chunk.rms or 1
        db = 20 * math.log10(rms) if rms > 0 else -60
        # Map -60..-20 dB to 0..1
        openness = (db + 60) / 40
        openness = max(0.0, min(1.0, openness))
        values.append(openness)
    return values
