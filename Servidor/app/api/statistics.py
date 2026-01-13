"""
Smart Classroom AI - Statistics API Router
Endpoints for system-wide statistics and analytics
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from app.core.schemas import BaseResponse
from app.db.supabase_client import SupabaseClient
from app.core.logger import logger

router = APIRouter(prefix="/statistics", tags=["Statistics"])

# Zona horaria de Ecuador (UTC-5)
ECUADOR_TZ_OFFSET = -5


@router.get(
    "/dashboard",
    response_model=BaseResponse,
    summary="Get dashboard statistics",
    description="Get overall system statistics for the dashboard"
)
async def get_dashboard_statistics():
    """
    Get general statistics for the dashboard:
    - Average attendance across all classes
    - Average engagement based on emotions
    - Total students and classes
    """
    try:
        supabase = SupabaseClient.get_client()
        
        # Get all attendance records
        attendance_response = supabase.table("attendance").select("*").execute()
        attendance_records = attendance_response.data if attendance_response.data else []
        
        # Get all class sessions
        classes_response = supabase.table("class_sessions").select("*").execute()
        classes = classes_response.data if classes_response.data else []
        
        # Get all students
        students_response = supabase.table("students").select("*").execute()
        students = students_response.data if students_response.data else []
        
        # Get all emotion events
        emotions_response = supabase.table("emotion_events").select("*").execute()
        emotions = emotions_response.data if emotions_response.data else []
        
        # Calculate average attendance (capped at 100%)
        avg_attendance = 0
        if classes and students:
            total_students = len(students)
            total_classes = len(classes)
            total_possible_attendances = total_students * total_classes
            
            if total_possible_attendances > 0:
                # Count unique student-class combinations to avoid duplicates
                unique_attendances = set()
                for record in attendance_records:
                    key = f"{record.get('student_id')}_{record.get('class_id')}"
                    unique_attendances.add(key)
                
                total_unique_attendances = len(unique_attendances)
                avg_attendance = round((total_unique_attendances / total_possible_attendances) * 100, 1)
                # Cap at 100%
                avg_attendance = min(avg_attendance, 100.0)
        
        # Calculate engagement based on emotions
        avg_engagement = 0
        if emotions:
            # Define positive emotions (DeepFace emotions)
            positive_emotions = ['happy', 'neutral', 'surprise']
            negative_emotions = ['sad', 'angry', 'fear', 'disgust']
            
            # Use 'dominant_emotion' field (correct field name in database)
            positive_count = sum(1 for e in emotions if e.get('dominant_emotion') in positive_emotions)
            total_emotions = len(emotions)
            
            if total_emotions > 0:
                avg_engagement = round((positive_count / total_emotions) * 100, 1)
        
        # Active classes (those without end_time)
        active_classes = sum(1 for c in classes if not c.get('end_time'))
        
        return BaseResponse(
            success=True,
            message="Dashboard statistics retrieved successfully",
            data={
                "totalStudents": len(students),
                "activeClasses": active_classes,
                "avgAttendance": avg_attendance,
                "avgEngagement": avg_engagement,
                "totalClasses": len(classes),
                "totalAttendances": len(attendance_records),
                "totalEmotions": len(emotions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dashboard statistics: {str(e)}"
        )


@router.get(
    "/course/{course_id}",
    response_model=BaseResponse,
    summary="Get course statistics",
    description="Get statistics for a specific course"
)
async def get_course_statistics(course_id: str):
    """
    Get statistics for a specific course:
    - Average attendance for this course
    - Average engagement for this course
    - Number of classes and students
    """
    try:
        supabase = SupabaseClient.get_client()
        
        # Get classes for this course
        classes_response = supabase.table("class_sessions").select("*").eq("course_id", course_id).execute()
        classes = classes_response.data if classes_response.data else []
        
        if not classes:
            return BaseResponse(
                success=True,
                message="No classes found for this course",
                data={
                    "avgAttendance": 0,
                    "avgEngagement": 0,
                    "totalClasses": 0,
                    "totalAttendances": 0
                }
            )
        
        # Get class_ids
        class_ids = [c['class_id'] for c in classes]
        
        # Get attendance for these classes
        attendance_records = []
        for class_id in class_ids:
            att_response = supabase.table("attendance").select("*").eq("class_id", class_id).execute()
            if att_response.data:
                attendance_records.extend(att_response.data)
        
        # Get emotions for these classes
        emotion_records = []
        for class_id in class_ids:
            emo_response = supabase.table("emotion_events").select("*").eq("class_id", class_id).execute()
            if emo_response.data:
                emotion_records.extend(emo_response.data)
        
        # Get total students enrolled in the course
        enrollment_response = supabase.table("enrollments").select("*").eq("course_id", course_id).execute()
        enrolled_students = len(enrollment_response.data) if enrollment_response.data else 0
        
        # Calculate average attendance
        avg_attendance = 0
        if enrolled_students > 0 and classes:
            total_possible = enrolled_students * len(classes)
            if total_possible > 0:
                avg_attendance = round((len(attendance_records) / total_possible) * 100, 1)
        
        # Calculate engagement (using correct field 'dominant_emotion')
        avg_engagement = 0
        if emotion_records:
            positive_emotions = ['happy', 'neutral', 'surprise']
            positive_count = sum(1 for e in emotion_records if e.get('dominant_emotion') in positive_emotions)
            avg_engagement = round((positive_count / len(emotion_records)) * 100, 1)
        
        return BaseResponse(
            success=True,
            message="Course statistics retrieved successfully",
            data={
                "avgAttendance": avg_attendance,
                "avgEngagement": avg_engagement,
                "totalClasses": len(classes),
                "totalAttendances": len(attendance_records),
                "totalEmotions": len(emotion_records),
                "enrolledStudents": enrolled_students
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting course statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting course statistics: {str(e)}"
        )
