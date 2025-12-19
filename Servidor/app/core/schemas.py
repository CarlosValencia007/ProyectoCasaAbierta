"""
Smart Classroom AI - Pydantic Schemas
Request/Response models for API validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.constants import EmotionType, AttendanceStatus


# ---- Base Response Schema ----

class BaseResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---- Student Schemas ----

class StudentEnrollRequest(BaseModel):
    """Request schema for student enrollment"""
    student_id: str = Field(..., min_length=1, max_length=50, description="Unique student identifier")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    image_base64: str = Field(..., description="Base64 encoded image of student's face")
    email: Optional[str] = Field(None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v):
        if not v.strip():
            raise ValueError("Student ID cannot be empty")
        return v.strip()


class StudentEnrollResponse(BaseModel):
    """Response schema for student enrollment"""
    student_id: str
    name: str
    embedding_saved: bool
    created_at: datetime


class StudentInfo(BaseModel):
    """Student information schema"""
    id: int
    student_id: str
    name: str
    email: Optional[str]
    embedding_dimension: int
    enrolled_at: datetime
    is_active: bool = True


# ---- Face Recognition Schemas ----

class FaceEmbedding(BaseModel):
    """Face embedding vector schema"""
    embedding: List[float] = Field(..., min_length=128, max_length=512)
    model: str = Field(default="Facenet")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class FaceDetectionResult(BaseModel):
    """Face detection result"""
    face_detected: bool
    face_count: int
    bounding_box: Optional[Dict[str, int]] = None
    confidence: Optional[float] = None


# ---- Emotion Analysis Schemas ----

class EmotionScore(BaseModel):
    """Individual emotion score"""
    emotion: EmotionType
    confidence: float = Field(..., ge=0.0, le=100.0)


class EmotionAnalysisResult(BaseModel):
    """Emotion analysis result"""
    dominant_emotion: EmotionType
    emotions: List[EmotionScore]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---- Attendance Schemas ----

class AttendanceVerifyRequest(BaseModel):
    """Request schema for attendance verification"""
    class_id: str = Field(..., description="Unique class session identifier")
    timestamp: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "class_id": "CS101-2024-01-15",
                "timestamp": "2024-01-15T09:00:00"
            }
        }


class AttendanceRecord(BaseModel):
    """Attendance record schema"""
    id: int
    student_id: str
    student_name: str
    class_id: str
    status: AttendanceStatus
    timestamp: datetime
    confidence: float


class AttendanceResponse(BaseModel):
    """Response for attendance verification"""
    student_id: str
    student_name: str
    status: AttendanceStatus
    confidence: float
    match_distance: float
    timestamp: datetime


# ---- Batch Processing Schemas ----

class BatchAttendanceRequest(BaseModel):
    """Request for batch attendance processing"""
    class_id: str
    images: List[str] = Field(..., description="List of base64 encoded images")
    timestamp: Optional[datetime] = None


class BatchAttendanceResponse(BaseModel):
    """Response for batch attendance"""
    class_id: str
    total_processed: int
    students_present: List[AttendanceResponse]
    unidentified_faces: int
    processing_time: float


# ---- Report Schemas ----

class ClassSessionReport(BaseModel):
    """Class session summary report"""
    class_id: str
    start_time: datetime
    end_time: datetime
    total_students: int
    present_count: int
    attendance_rate: float
    dominant_emotion: EmotionType
    emotion_breakdown: Dict[str, float]
    average_engagement: float


# ---- Health Check Schema ----

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, bool] = {
        "api": True,
        "database": False,
        "deepface": False
    }
