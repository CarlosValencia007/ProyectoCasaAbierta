"""
Smart Classroom AI - Attendance Service
Business logic for attendance verification and management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import numpy as np
from app.services.face_service import FaceRecognitionService, ImageProcessingService
from app.db.crud import StudentCRUD, AttendanceCRUD
from app.core.logger import logger
from app.core.exceptions import StudentNotFoundException, FaceNotDetectedException
from app.core.constants import AttendanceStatus

# Zona horaria de Ecuador (UTC-5)
ECUADOR_TZ = timezone(timedelta(hours=-5))

# Tiempo de tolerancia en minutos antes de marcar como "late"
LATE_THRESHOLD_MINUTES = 15


class AttendanceService:
    """Service for managing attendance verification"""
    
    def __init__(self):
        self.face_service = FaceRecognitionService()
        self.image_service = ImageProcessingService()
        self.student_crud = StudentCRUD()
        self.attendance_crud = AttendanceCRUD()
    
    async def _get_class_start_time(self, class_id: str) -> Optional[datetime]:
        """
        Get the start time of a class session
        
        Args:
            class_id: Class session identifier
        
        Returns:
            Start time as datetime or None if not found
        """
        try:
            from app.db.supabase_client import get_supabase
            client = get_supabase()
            
            response = client.table("class_sessions")\
                .select("start_time")\
                .eq("class_id", class_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                start_time_str = response.data[0].get("start_time")
                if start_time_str:
                    # Parse ISO format datetime
                    return datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            return None
        except Exception as e:
            logger.error(f"Error getting class start time: {str(e)}")
            return None
    
    def _determine_attendance_status(self, class_start_time: Optional[datetime]) -> str:
        """
        Determine if attendance should be marked as 'present' or 'late'
        based on the class start time and current time in Ecuador timezone
        
        Args:
            class_start_time: When the class started
        
        Returns:
            'present' if within tolerance, 'late' if past tolerance
        """
        if class_start_time is None:
            # If we can't determine start time, default to present
            return AttendanceStatus.PRESENT.value
        
        # Current time in Ecuador timezone
        now_ecuador = datetime.now(ECUADOR_TZ)
        
        # Ensure class_start_time is timezone-aware
        if class_start_time.tzinfo is None:
            # Assume class start time is in Ecuador timezone
            class_start_time = class_start_time.replace(tzinfo=ECUADOR_TZ)
        
        # Calculate time difference
        time_diff = now_ecuador - class_start_time
        minutes_late = time_diff.total_seconds() / 60
        
        logger.info(f"⏰ Hora actual (Ecuador): {now_ecuador.strftime('%H:%M:%S')}")
        logger.info(f"⏰ Hora inicio clase: {class_start_time.strftime('%H:%M:%S')}")
        logger.info(f"⏰ Minutos desde inicio: {minutes_late:.1f}")
        
        if minutes_late > LATE_THRESHOLD_MINUTES:
            logger.info(f"⚠️ Estudiante llegó TARDE ({minutes_late:.0f} min > {LATE_THRESHOLD_MINUTES} min)")
            return AttendanceStatus.LATE.value
        else:
            logger.info(f"✅ Estudiante llegó A TIEMPO ({minutes_late:.0f} min <= {LATE_THRESHOLD_MINUTES} min)")
            return AttendanceStatus.PRESENT.value
    
    async def verify_attendance(
        self,
        image_base64: str,
        class_id: str
    ) -> Dict[str, Any]:
        """
        Verify single student attendance from image
        
        Args:
            image_base64: Base64 encoded image
            class_id: Class session identifier
        
        Returns:
            Dict with student info, status, and confidence
        """
        try:
            # Convert image
            image = self.image_service.base64_to_image(image_base64)
            
            # Validate
            if not self.image_service.validate_image(image):
                raise FaceNotDetectedException("Invalid or too small image")
            
            # Generate embedding
            embedding = self.face_service.generate_embedding(image)
            
            # Search for matching student with LOWER threshold to debug
            logger.warning(f"🔍 Searching for match with threshold 0.8...")
            matches = await self.student_crud.find_by_embedding(
                embedding=embedding,
                threshold=0.8,  # TEMPORARY: Lower threshold for debugging
                limit=5  # Get top 5 matches to see distances
            )
            
            logger.warning(f"🔍 Found {len(matches)} potential matches")
            for i, (student, distance) in enumerate(matches[:3]):
                confidence = 1.0 - (distance / 1.0)
                logger.warning(f"  Match #{i+1}: Student {student['student_id']} - Distance: {distance:.4f} - Confidence: {confidence:.2%}")
            
            if not matches:
                logger.warning("❌ No matching student found (threshold=0.8)")
                return {
                    "success": False,
                    "message": "Student not recognized",
                    "confidence": 0.0
                }
            
            # Get best match
            student_record, distance = matches[0]
            confidence = 1.0 - (distance / 1.0)  # Convert distance to confidence
            
            # Get class start time and determine if late
            class_start_time = await self._get_class_start_time(class_id)
            attendance_status = self._determine_attendance_status(class_start_time)
            
            # Mark attendance (will check for duplicates automatically)
            attendance_record = await self.attendance_crud.mark_attendance(
                student_id=student_record["student_id"],
                class_id=class_id,
                status=attendance_status,
                confidence=confidence,
                match_distance=distance
            )
            
            # Check if attendance was already registered
            already_registered = attendance_record.get("already_registered", False)
            
            if already_registered:
                logger.info(f"Attendance already registered for {student_record['student_id']} in {class_id}")
                return {
                    "success": True,
                    "already_registered": True,
                    "student_id": student_record["student_id"],
                    "student_name": student_record["name"],
                    "status": attendance_record.get("status", AttendanceStatus.PRESENT.value),
                    "confidence": confidence,
                    "match_distance": distance,
                    "timestamp": attendance_record["timestamp"],
                    "message": f"⚠️ El estudiante {student_record['name']} ya tiene asistencia registrada en esta clase"
                }
            
            # Build status message based on attendance status
            status_msg = "✅ Presente" if attendance_status == AttendanceStatus.PRESENT.value else "⚠️ Atrasado"
            logger.info(f"Attendance verified for {student_record['student_id']} - {status_msg} (confidence: {confidence:.2f})")
            
            return {
                "success": True,
                "already_registered": False,
                "student_id": student_record["student_id"],
                "student_name": student_record["name"],
                "status": attendance_status,
                "confidence": confidence,
                "match_distance": distance,
                "timestamp": attendance_record["timestamp"]
            }
        
        except FaceNotDetectedException as e:
            logger.warning(f"Face not detected: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "confidence": 0.0
            }
        except Exception as e:
            logger.error(f"Attendance verification failed: {str(e)}")
            return {
                "success": False,
                "message": f"Verification error: {str(e)}",
                "confidence": 0.0
            }
    
    async def batch_verify_attendance(
        self,
        images_base64: List[str],
        class_id: str
    ) -> Dict[str, Any]:
        """
        Verify multiple students from multiple images
        
        Args:
            images_base64: List of base64 encoded images
            class_id: Class session identifier
        
        Returns:
            Dict with results for all images
        """
        start_time = datetime.utcnow()
        
        results = {
            "class_id": class_id,
            "total_images": len(images_base64),
            "students_identified": [],
            "unidentified_count": 0,
            "processing_time": 0.0
        }
        
        for idx, image_b64 in enumerate(images_base64):
            try:
                verification = await self.verify_attendance(image_b64, class_id)
                
                if verification["success"]:
                    results["students_identified"].append(verification)
                else:
                    results["unidentified_count"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to process image {idx}: {str(e)}")
                results["unidentified_count"] += 1
        
        # Calculate processing time
        end_time = datetime.utcnow()
        results["processing_time"] = (end_time - start_time).total_seconds()
        
        logger.info(f"Batch attendance: {len(results['students_identified'])}/{len(images_base64)} identified")
        
        return results
    
    async def get_class_attendance_report(self, class_id: str) -> Dict[str, Any]:
        """
        Get attendance report for a class session
        
        Args:
            class_id: Class session identifier
        
        Returns:
            Dict with attendance statistics
        """
        try:
            # Get all attendance records
            records = await self.attendance_crud.get_class_attendance(class_id)
            
            # Calculate statistics
            total_records = len(records)
            present_count = len([r for r in records if r["status"] == AttendanceStatus.PRESENT.value])
            late_count = len([r for r in records if r["status"] == AttendanceStatus.LATE.value])
            
            # Average confidence
            confidences = [r["confidence"] for r in records if r["confidence"] is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "class_id": class_id,
                "total_records": total_records,
                "present_count": present_count,
                "late_count": late_count,
                "attendance_rate": (present_count / total_records * 100) if total_records > 0 else 0.0,
                "average_confidence": avg_confidence,
                "records": records
            }
        
        except Exception as e:
            logger.error(f"Failed to generate attendance report: {str(e)}")
            raise
