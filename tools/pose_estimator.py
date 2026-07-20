"""Pose estimation helpers for character animation control.

Supported backends:
- MediaPipe Pose: CPU, 33 landmarks, good for 2D puppet mocap.
- DWPose: GPU/ONNX, better whole-body estimation, used with ControlNet.
- OpenPose: classic 2D keypoints.

Repos:
- https://github.com/google-ai-edge/mediapipe
- https://github.com/IDEA-Research/DWPose
- https://github.com/CMU-Perceptual-Computing-Lab/openpose
"""

from __future__ import annotations

from pathlib import Path


def _try_mediapipe():
    try:
        import mediapipe as mp
        return mp
    except ImportError:
        return None


def detect_pose_mediapipe(image_path: str | Path) -> list[dict] | None:
    """Return 33 MediaPipe pose landmarks as {x, y, z, visibility}."""
    mp = _try_mediapipe()
    if not mp:
        return None
    import cv2

    image = cv2.imread(str(image_path))
    if image is None:
        return None
    with mp.Pose(static_image_mode=True, model_complexity=1) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return []
        return [
            {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
            for lm in results.pose_landmarks.landmark
        ]


def detect_face_mediapipe(image_path: str | Path) -> list[dict] | None:
    """Return face detection bounding boxes. Useful for placing mouth/eye overlays."""
    mp = _try_mediapipe()
    if not mp:
        return None
    import cv2

    image = cv2.imread(str(image_path))
    if image is None:
        return None
    h, w = image.shape[:2]
    with mp.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face:
        results = face.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.detections:
            return []
        return [
            {
                "x": d.location_data.relative_bounding_box.xmin * w,
                "y": d.location_data.relative_bounding_box.ymin * h,
                "w": d.location_data.relative_bounding_box.width * w,
                "h": d.location_data.relative_bounding_box.height * h,
            }
            for d in results.detections
        ]
