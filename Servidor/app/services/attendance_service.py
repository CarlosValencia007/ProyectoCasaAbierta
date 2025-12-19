"""
Smart Classroom AI - Attendance Service
Business logic for attendance verification and management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from app.services.face_service import FaceRecognitionService, ImageProcessingService
from app.db.crud import StudentCRUD, AttendanceCRUD
from app.core.logger import logger
from app.core.exceptions import StudentNotFoundException, FaceNotDetectedException
from app.core.constants import AttendanceStatus


class AttendanceService:
    """Service for managing attendance verification"""
    
    def __init__(self):
        self.face_service = FaceRecognitionService()
        self.image_service = ImageProcessingService()
        self.student_crud = StudentCRUD()
        self.attendance_crud = AttendanceCRUD()
    
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
            
            # Search for matching student
            matches = await self.student_crud.find_by_embedding(
                embedding=embedding,
                threshold=0.6,
                limit=1
            )
            
            if not matches:
                logger.warning("No matching student found")
                return {
                    "success": False,
                    "message": "Student not recognized",
                    "confidence": 0.0
                }
            
            # Get best match
            student_record, distance = matches[0]
            confidence = 1.0 - (distance / 1.0)  # Convert distance to confidence
            
            # Mark attendance
            attendance_record = await self.attendance_crud.mark_attendance(
                student_id=student_record["student_id"],
                class_id=class_id,
                status=AttendanceStatus.PRESENT.value,
                confidence=confidence,
                match_distance=distance
            )
            
            logger.info(f"Attendance verified for {student_record['student_id']} (confidence: {confidence:.2f})")
            
            return {
                "success": True,
                "student_id": student_record["student_id"],
                "student_name": student_record["name"],
                "status": AttendanceStatus.PRESENT.value,
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
