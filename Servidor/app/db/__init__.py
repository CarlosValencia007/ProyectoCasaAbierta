"""Database module - Supabase client and CRUD operations"""
from app.db.supabase_client import get_supabase, SupabaseClient
from app.db.crud import StudentCRUD, AttendanceCRUD, EmotionEventCRUD
from app.db.models import Student, Attendance, EmotionEvent, ClassSession

__all__ = [
    "get_supabase",
    "SupabaseClient",
    "StudentCRUD",
    "AttendanceCRUD",
    "EmotionEventCRUD",
    "Student",
    "Attendance",
    "EmotionEvent",
    "ClassSession"
]
