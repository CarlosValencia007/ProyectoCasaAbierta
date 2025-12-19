"""Core module - Configuration, logging, and utilities"""
from app.core.config import settings, get_settings
from app.core.logger import logger, setup_logger
from app.core.constants import (
    EmotionType,
    AttendanceStatus,
    FaceRecognitionModel,
    FaceDetectorBackend
)

__all__ = [
    "settings",
    "get_settings",
    "logger",
    "setup_logger",
    "EmotionType",
    "AttendanceStatus",
    "FaceRecognitionModel",
    "FaceDetectorBackend"
]
