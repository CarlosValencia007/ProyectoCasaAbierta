"""
Smart Classroom AI - Database Models
SQLAlchemy ORM models with pgvector support
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()


class Student(Base):
    """Student entity with facial embedding"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    
    # Facial embedding (128-dimensional for Facenet, 512 for Facenet512)
    face_embedding = Column(Vector(128), nullable=False)
    
    # Metadata
    enrolled_at = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Relationships
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    emotion_events = relationship("EmotionEvent", back_populates="student", cascade="all, delete-orphan")
    
    # Index for vector similarity search
    __table_args__ = (
        Index('ix_students_face_embedding', 'face_embedding', postgresql_using='ivfflat'),
    )


class Attendance(Base):
    """Attendance records for class sessions"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False)
    class_id = Column(String(100), nullable=False, index=True)
    
    # Attendance details
    status = Column(String(20), nullable=False, default="present")  # present, absent, late, excused
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Recognition confidence
    confidence = Column(Float, nullable=True)
    match_distance = Column(Float, nullable=True)  # Euclidean distance from reference embedding
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    
    __table_args__ = (
        Index('ix_attendance_class_timestamp', 'class_id', 'timestamp'),
        Index('ix_attendance_student_class', 'student_id', 'class_id'),
    )


class EmotionEvent(Base):
    """Emotion detection events during class"""
    __tablename__ = "emotion_events"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False)
    class_id = Column(String(100), nullable=False, index=True)
    
    # Emotion details
    dominant_emotion = Column(String(20), nullable=False)  # happy, sad, angry, etc.
    confidence = Column(Float, nullable=False)
    
    # All emotion scores (JSON string: {"happy": 85.2, "sad": 10.3, ...})
    emotion_scores = Column(Text, nullable=True)
    
    # Timestamp
    detected_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    student = relationship("Student", back_populates="emotion_events")
    
    __table_args__ = (
        Index('ix_emotion_class_timestamp', 'class_id', 'detected_at'),
        Index('ix_emotion_student_class', 'student_id', 'class_id'),
    )


class ClassSession(Base):
    """Class session metadata"""
    __tablename__ = "class_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Session details
    class_name = Column(String(100), nullable=False)
    instructor = Column(String(100), nullable=True)
    room = Column(String(50), nullable=True)
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    # Statistics (calculated periodically)
    total_students = Column(Integer, default=0)
    present_count = Column(Integer, default=0)
    attendance_rate = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    extra_data = Column(Text, nullable=True)
