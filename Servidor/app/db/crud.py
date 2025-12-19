"""
Smart Classroom AI - Database CRUD Operations
Abstraction layer for database interactions with pgvector
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json
import numpy as np
from supabase import Client
from app.db.supabase_client import get_supabase
from app.core.logger import logger
from app.core.exceptions import (
    StudentNotFoundException,
    DuplicateStudentException,
    DatabaseConnectionException
)


class StudentCRUD:
    """CRUD operations for Student entity"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()
    
    async def create(
        self,
        student_id: str,
        name: str,
        face_embedding: List[float],
        email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create new student with facial embedding
        
        Args:
            student_id: Unique student identifier
            name: Full name
            face_embedding: 128-dimensional facial embedding vector
            email: Optional email address
            metadata: Optional additional data
        
        Returns:
            Created student record
        
        Raises:
            DuplicateStudentException: If student_id already exists
        """
        try:
            # Check if student already exists
            existing = self.client.table("students").select("id").eq("student_id", student_id).execute()
            if existing.data:
                raise DuplicateStudentException(student_id)
            
            # Prepare data
            data = {
                "student_id": student_id,
                "name": name,
                "face_embedding": face_embedding,
                "email": email,
                "metadata": json.dumps(metadata) if metadata else None,
                "enrolled_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            # Insert
            response = self.client.table("students").insert(data).execute()
            logger.info(f"Student {student_id} enrolled successfully")
            return response.data[0]
        
        except DuplicateStudentException:
            raise
        except Exception as e:
            logger.error(f"Failed to create student {student_id}: {str(e)}")
            raise DatabaseConnectionException(f"Student creation failed: {str(e)}")
    
    async def find_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Find student by student_id"""
        try:
            response = self.client.table("students").select("*").eq("student_id", student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to find student {student_id}: {str(e)}")
            return None
    
    async def find_by_embedding(
        self,
        embedding: List[float],
        threshold: float = 0.6,
        limit: int = 1
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find students by facial embedding similarity using pgvector
        
        Args:
            embedding: Query embedding vector
            threshold: Maximum distance threshold
            limit: Maximum number of results
        
        Returns:
            List of (student_record, distance) tuples
        """
        try:
            # Using pgvector's <-> operator for Euclidean distance
            # Note: Supabase Python client might need RPC call for this
            rpc_result = self.client.rpc(
                'match_students_by_embedding',
                {
                    'query_embedding': embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            # Returns list of {student, distance}
            results = []
            for item in rpc_result.data:
                results.append((item['student'], item['distance']))
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to search by embedding: {str(e)}")
            return []
    
    async def list_all(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all students"""
        try:
            query = self.client.table("students").select("*")
            if active_only:
                query = query.eq("is_active", True)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to list students: {str(e)}")
            return []
    
    async def update(self, student_id: str, **kwargs) -> Dict[str, Any]:
        """Update student record"""
        try:
            response = self.client.table("students").update(kwargs).eq("student_id", student_id).execute()
            if not response.data:
                raise StudentNotFoundException(student_id)
            return response.data[0]
        except StudentNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to update student {student_id}: {str(e)}")
            raise DatabaseConnectionException(f"Update failed: {str(e)}")
    
    async def delete(self, student_id: str) -> bool:
        """Soft delete student (set is_active=False)"""
        try:
            await self.update(student_id, is_active=False)
            logger.info(f"Student {student_id} deactivated")
            return True
        except Exception as e:
            logger.error(f"Failed to delete student {student_id}: {str(e)}")
            return False


class AttendanceCRUD:
    """CRUD operations for Attendance records"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()
    
    async def mark_attendance(
        self,
        student_id: str,
        class_id: str,
        status: str = "present",
        confidence: Optional[float] = None,
        match_distance: Optional[float] = None
    ) -> Dict[str, Any]:
        """Mark attendance for a student"""
        try:
            data = {
                "student_id": student_id,
                "class_id": class_id,
                "status": status,
                "confidence": confidence,
                "match_distance": match_distance,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("attendance").insert(data).execute()
            logger.info(f"Attendance marked for {student_id} in {class_id}")
            return response.data[0]
        
        except Exception as e:
            logger.error(f"Failed to mark attendance: {str(e)}")
            raise DatabaseConnectionException(f"Attendance marking failed: {str(e)}")
    
    async def get_class_attendance(self, class_id: str) -> List[Dict[str, Any]]:
        """Get all attendance records for a class"""
        try:
            response = self.client.table("attendance").select("*").eq("class_id", class_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get attendance for {class_id}: {str(e)}")
            return []


class EmotionEventCRUD:
    """CRUD operations for Emotion events"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()
    
    async def record_emotion(
        self,
        student_id: str,
        class_id: str,
        dominant_emotion: str,
        confidence: float,
        emotion_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Record emotion detection event"""
        try:
            data = {
                "student_id": student_id,
                "class_id": class_id,
                "dominant_emotion": dominant_emotion,
                "confidence": confidence,
                "emotion_scores": json.dumps(emotion_scores) if emotion_scores else None,
                "detected_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("emotion_events").insert(data).execute()
            return response.data[0]
        
        except Exception as e:
            logger.error(f"Failed to record emotion: {str(e)}")
            raise DatabaseConnectionException(f"Emotion recording failed: {str(e)}")
    
    async def get_class_emotions(
        self,
        class_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get emotion events for a class session"""
        try:
            query = self.client.table("emotion_events").select("*").eq("class_id", class_id)
            
            if start_time:
                query = query.gte("detected_at", start_time.isoformat())
            if end_time:
                query = query.lte("detected_at", end_time.isoformat())
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get emotions for {class_id}: {str(e)}")
            return []
