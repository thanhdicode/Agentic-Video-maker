"""DaVinci Resolve Studio automation wrapper.

This module provides a Python controller around the DaVinci Resolve scripting
API. It is designed to be importable even when Resolve is not installed: the
Resolve-specific imports happen lazily inside :meth:`ResolveController.connect`.

Notes:
    - External Python scripting requires DaVinci Resolve *Studio* (paid).
      The free version only runs scripts from the built-in Console/Fusion page.
    - Resolve must already be running (or launched with ``-nogui``) before any
      script can connect.
    - This wrapper targets game-studio trailer / devlog pipelines: organised
      bins, timeline assembly, LUT/CDL colour, and render-queue automation.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


class ResolveError(Exception):
    """Base exception for Resolve automation problems."""

    pass


class ResolveNotInstalledError(ResolveError):
    """Raised when the DaVinciResolveScript module cannot be found."""

    pass


class ResolveConnectionError(ResolveError):
    """Raised when Resolve is not running or does not respond."""

    pass


class ResolveAPIError(ResolveError):
    """Raised for errors returned by the Resolve API."""

    pass


@dataclass
class ClipInfo:
    """Placement instruction for a media-pool item on a timeline."""

    media_pool_item: Any
    start_frame: int = 1
    end_frame: int = 0
    media_type: int = 1
    track_index: int = 1
    record_frame: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "mediaPoolItem": self.media_pool_item,
            "startFrame": self.start_frame,
            "endFrame": self.end_frame,
            "mediaType": self.media_type,
            "trackIndex": self.track_index,
            "recordFrame": self.record_frame,
        }


class ResolveController:
    """High-level controller for automating a Resolve project."""

    def __init__(
        self,
        project_name: Optional[str] = None,
        connect_timeout: float = 10.0,
    ) -> None:
        self.project_name = project_name
        self.connect_timeout = connect_timeout

        self._resolve: Any = None
        self._project_manager: Any = None
        self._project: Any = None
        self._media_pool: Any = None
        self._media_storage: Any = None
        self._clips: dict[str, Any] = {}

    # ------------------------------------------------------------------ #
    # Environment / connection
    # ------------------------------------------------------------------ #
    @staticmethod
    def _script_api_path() -> str:
        if sys.platform == "win32":
            return os.path.join(
                os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                "Blackmagic Design",
                "DaVinci Resolve",
                "Support",
                "Developer",
                "Scripting",
            )
        if sys.platform == "darwin":
            return "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
        return "/opt/resolve/Developer/Scripting/"

    @staticmethod
    def _script_lib_path() -> str:
        if sys.platform == "win32":
            return os.path.join(
                os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                "Blackmagic Design",
                "DaVinci Resolve",
                "fusionscript.dll",
            )
        if sys.platform == "darwin":
            return "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
        return "/opt/resolve/libs/Fusion/fusionscript.so"

    def _setup_environment(self) -> None:
        api_path = self._script_api_path()
        lib_path = self._script_lib_path()
        os.environ.setdefault("RESOLVE_SCRIPT_API", api_path)
        os.environ.setdefault("RESOLVE_SCRIPT_LIB", lib_path)
        modules_path = os.path.join(os.environ["RESOLVE_SCRIPT_API"], "Modules")
        if modules_path not in sys.path:
            sys.path.insert(0, modules_path)

    def connect(self) -> Any:
        """Connect to a running Resolve instance.

        Returns the low-level Resolve object. Raises ResolveNotInstalledError
        if the scripting module is missing, or ResolveConnectionError if Resolve
        is not running / not responding.
        """
        self._setup_environment()
        try:
            import DaVinciResolveScript as dvr_script
        except ImportError as exc:
            raise ResolveNotInstalledError(
                "DaVinciResolveScript module not found. "
                "Install DaVinci Resolve Studio and verify the scripting paths."
            ) from exc

        result: list[Any] = [None]
        error: list[Optional[BaseException]] = [None]

        def _connect() -> None:
            try:
                result[0] = dvr_script.scriptapp("Resolve")
            except Exception as exc:
                error[0] = exc

        thread = threading.Thread(target=_connect, daemon=True)
        thread.start()
        thread.join(timeout=self.connect_timeout)

        if thread.is_alive():
            raise ResolveConnectionError(
                f"Timed out after {self.connect_timeout}s waiting for Resolve. "
                "Is DaVinci Resolve Studio running?"
            )
        if error[0]:
            raise ResolveConnectionError(f"Resolve connection failed: {error[0]}")

        resolve = result[0]
        if resolve is None:
            raise ResolveConnectionError(
                "Could not connect to Resolve. "
                "Ensure DaVinci Resolve Studio is running and external scripting is enabled."
            )

        self._resolve = resolve
        self._project_manager = resolve.GetProjectManager()
        self._media_storage = resolve.GetMediaStorage()
        return resolve

    def __enter__(self) -> "ResolveController":
        self.connect()
        if self.project_name:
            self.get_or_create_project(self.project_name)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        try:
            self.save_project()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Project
    # ------------------------------------------------------------------ #
    def get_or_create_project(self, name: Optional[str] = None) -> Any:
        """Load an existing project or create a new one in the current database."""
        name = name or self.project_name
        if not name:
            raise ResolveAPIError("Project name is required.")
        if self._project_manager is None:
            raise ResolveConnectionError("Not connected to Resolve.")

        self._project_manager.GotoRootFolder()
        project = self._project_manager.LoadProject(name)
        if not project:
            project = self._project_manager.CreateProject(name)
        if not project:
            raise ResolveAPIError(f"Failed to load or create project '{name}'")

        self._project = project
        self._media_pool = project.GetMediaPool()
        self.project_name = name
        return project

    def configure_project(
        self,
        width: int = 1920,
        height: int = 1080,
        frame_rate: str = "30",
        color_science: str = "davinciYRGBColorManagedv2",
    ) -> None:
        """Set base timeline resolution, frame rate and colour science."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")

        # Color science must be configured first or later settings may not stick.
        self._project.SetSetting("colorScienceMode", color_science)
        self._project.SetSetting("timelineResolutionWidth", str(width))
        self._project.SetSetting("timelineResolutionHeight", str(height))
        self._project.SetSetting("timelineFrameRate", str(frame_rate))

    def save_project(self) -> None:
        if self._project_manager is None:
            raise ResolveConnectionError("Not connected to Resolve.")
        if not self._project_manager.SaveProject():
            raise ResolveAPIError("Failed to save project")

    def open_page(self, page: str) -> None:
        """Switch Resolve page: media, cut, edit, fusion, color, fairlight, deliver."""
        if self._resolve is None:
            raise ResolveConnectionError("Not connected to Resolve.")
        self._resolve.OpenPage(page)

    # ------------------------------------------------------------------ #
    # Media organisation
    # ------------------------------------------------------------------ #
    def create_bins(self, bin_names: list[str]) -> None:
        """Create media-pool bins under the root folder."""
        if self._media_pool is None:
            raise ResolveConnectionError("No active project.")
        root = self._media_pool.GetRootFolder()
        for name in bin_names:
            self._media_pool.AddSubFolder(root, name)

    def import_media(self, paths: list[str | Path]) -> list[Any]:
        """Import one or more files/folders into the current media-pool folder.

        Returns a list of MediaPoolItem objects. The paths are also indexed by
        absolute POSIX path and filename for later lookup.
        """
        if self._media_storage is None:
            raise ResolveConnectionError("Not connected to Resolve.")

        abs_paths = [str(Path(p).resolve().as_posix()) for p in paths if p]
        missing = [p for p in abs_paths if not Path(p).exists()]
        if missing:
            raise ResolveAPIError(f"Media not found: {missing}")

        clips = self._media_storage.AddItemListToMediaPool(abs_paths)
        if not clips:
            raise ResolveAPIError(f"Failed to import media into Resolve: {abs_paths}")

        for clip in clips:
            props = clip.GetClipProperty() or {}
            file_path = props.get("File Path") or props.get("File Name") or ""
            file_path = str(file_path).replace("\\", "/")
            self._clips[file_path] = clip
            self._clips[Path(file_path).name] = clip

        return clips

    def _resolve_media_item(self, item: Any) -> Any:
        """Look up an imported MediaPoolItem from a path string or return the object."""
        if not isinstance(item, (str, Path)):
            return item
        path = str(Path(item).resolve().as_posix())
        if path in self._clips:
            return self._clips[path]
        name = Path(path).name
        if name in self._clips:
            return self._clips[name]
        raise ResolveAPIError(f"Media not imported: {item}")

    # ------------------------------------------------------------------ #
    # Timeline assembly
    # ------------------------------------------------------------------ #
    def create_timeline(
        self,
        name: str,
        clip_infos: Optional[list[ClipInfo]] = None,
    ) -> Any:
        """Create a new timeline. If clip_infos is supplied, auto-populate it."""
        if self._media_pool is None:
            raise ResolveConnectionError("No active project.")

        if clip_infos:
            clip_dicts = [c.to_dict() for c in clip_infos]
            timeline = self._media_pool.CreateTimelineFromClips(name, clip_dicts)
        else:
            timeline = self._media_pool.CreateEmptyTimeline(name)

        if not timeline:
            raise ResolveAPIError(f"Failed to create timeline '{name}'")

        self.set_current_timeline(timeline)
        return timeline

    def append_clips(self, timeline: Any, clip_infos: list[ClipInfo]) -> list[Any]:
        """Append clips to an existing timeline."""
        if self._media_pool is None or self._project is None:
            raise ResolveConnectionError("No active project.")

        self.set_current_timeline(timeline)
        items = self._media_pool.AppendToTimeline([c.to_dict() for c in clip_infos])
        if not items:
            raise ResolveAPIError("Failed to append clips to timeline")
        return items

    def set_current_timeline(self, timeline: Any) -> None:
        if self._project is None:
            raise ResolveConnectionError("No active project.")
        if not self._project.SetCurrentTimeline(timeline):
            raise ResolveAPIError("Failed to set current timeline")

    def get_timeline_items(
        self,
        track_type: str = "video",
        track_index: int = 1,
        timeline: Optional[Any] = None,
    ) -> list[Any]:
        """Return timeline items for a given track type and index."""
        tl = timeline or self._project.GetCurrentTimeline()
        if tl is None:
            raise ResolveAPIError("No current timeline")
        return tl.GetItemListInTrack(track_type, track_index) or []

    # ------------------------------------------------------------------ #
    # Colour
    # ------------------------------------------------------------------ #
    def apply_lut(self, timeline_item: Any, lut_path: str, node_index: int = 1) -> None:
        """Apply a .cube LUT to a timeline item's colour node."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")

        lut_path = str(Path(lut_path).resolve().as_posix())
        if not Path(lut_path).exists():
            raise ResolveAPIError(f"LUT not found: {lut_path}")

        self._project.RefreshLUTList()
        if not timeline_item.SetLUT(node_index, lut_path):
            raise ResolveAPIError(f"Failed to apply LUT {lut_path}")

    def apply_cdl(self, timeline_item: Any, cdl: dict[str, Any]) -> None:
        """Apply a CDL to a timeline item's colour node."""
        cdl = dict(cdl)
        if "NodeIndex" in cdl:
            cdl["NodeIndex"] = str(cdl["NodeIndex"])
        if not timeline_item.SetCDL(cdl):
            raise ResolveAPIError(f"Failed to apply CDL {cdl}")

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def list_render_formats(self) -> dict[str, str]:
        """Return available render formats (description -> extension)."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")
        return self._project.GetRenderFormats() or {}

    def list_render_codecs(self, format_name: str) -> dict[str, str]:
        """Return available codecs for a render format (description -> codec name)."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")
        return self._project.GetRenderCodecs(format_name) or {}

    @staticmethod
    def _match_name(target: str, options: dict[str, str]) -> Optional[str]:
        """Match a user-friendly name against a dict of Resolve option names."""
        target = target.lower().replace(" ", "").replace(".", "")
        for key in options:
            key_norm = key.lower().replace(" ", "").replace(".", "")
            if target == key_norm or target in key_norm:
                return key
        for key, value in options.items():
            val_norm = value.lower().replace(" ", "").replace(".", "")
            if target == val_norm or target in val_norm:
                return key
        return None

    def set_render_format_codec(self, format_name: str, codec_name: str) -> None:
        """Set the render container and codec, tolerating common aliases."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")

        formats = self.list_render_formats()
        format_key = self._match_name(format_name, formats)
        if format_key is None:
            raise ResolveAPIError(
                f"Render format '{format_name}' not available. "
                f"Available: {sorted(formats.keys())}"
            )

        codecs = self.list_render_codecs(format_key)
        codec_key = self._match_name(codec_name, codecs)
        if codec_key is None:
            raise ResolveAPIError(
                f"Codec '{codec_name}' not available for {format_key}. "
                f"Available: {sorted(codecs.keys())}"
            )

        if not self._project.SetCurrentRenderFormatAndCodec(format_key, codecs[codec_key]):
            raise ResolveAPIError("Failed to set render format/codec")

    def set_render_job_settings(
        self,
        target_dir: str,
        custom_name: str = "final",
        select_all_frames: bool = True,
        mark_in: Optional[int] = None,
        mark_out: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        frame_rate: Optional[float] = None,
        audio_codec: str = "aac",
        audio_sample_rate: int = 48000,
        export_video: bool = True,
        export_audio: bool = True,
    ) -> None:
        """Configure the render job that will be added next."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")

        settings: dict[str, Any] = {
            "TargetDir": str(Path(target_dir).resolve().as_posix()),
            "CustomName": custom_name,
            "ExportVideo": export_video,
            "ExportAudio": export_audio,
            "AudioCodec": audio_codec,
            "AudioSampleRate": audio_sample_rate,
            "SelectAllFrames": select_all_frames,
        }
        if not select_all_frames:
            if mark_in is None or mark_out is None:
                raise ResolveAPIError(
                    "mark_in and mark_out are required when select_all_frames=False"
                )
            settings["MarkIn"] = mark_in
            settings["MarkOut"] = mark_out
        if width:
            settings["FormatWidth"] = width
        if height:
            settings["FormatHeight"] = height
        if frame_rate:
            settings["FrameRate"] = frame_rate

        if not self._project.SetRenderSettings(settings):
            raise ResolveAPIError("Failed to set render settings")

    def add_render_job(self) -> Optional[str]:
        """Add the configured render job to the queue.

        Returns a job id when Resolve provides one, otherwise True/None.
        """
        if self._project is None:
            raise ResolveConnectionError("No active project.")
        result = self._project.AddRenderJob()
        if not result:
            raise ResolveAPIError("Failed to add render job")
        return result if isinstance(result, str) else None

    def start_rendering(self, interactive: bool = False) -> None:
        """Start rendering all jobs in the render queue."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")
        if not self._project.StartRendering(interactive):
            raise ResolveAPIError("Failed to start rendering")

    def wait_for_render(
        self,
        job_id: Optional[str] = None,
        poll_interval: float = 1.0,
        timeout: Optional[float] = None,
    ) -> Optional[dict[str, Any]]:
        """Block until Resolve reports that rendering has finished."""
        if self._project is None:
            raise ResolveConnectionError("No active project.")

        start = time.time()
        while self._project.IsRenderingInProgress():
            if timeout and (time.time() - start) > timeout:
                raise ResolveAPIError("Render timeout")
            time.sleep(poll_interval)

        if job_id:
            return self._project.GetRenderJobStatus(job_id)
        return None
