"""API module - FastAPI routers"""
from app.api import enrollment, attendance, emotions, health

__all__ = [
    "enrollment",
    "attendance",
    "emotions",
    "health"
]
