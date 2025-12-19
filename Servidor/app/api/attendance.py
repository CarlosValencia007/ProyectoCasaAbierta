"""
Smart Classroom AI - Attendance API Router
Endpoints for attendance verification and reporting
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.core.schemas import BaseResponse, AttendanceVerifyRequest, BatchAttendanceRequest
from app.services.attendance_service import AttendanceService
from app.core.logger import logger

router = APIRouter(prefix="/attendance", tags=["Attendance"])
attendance_service = AttendanceService()


@router.post(
    "/verify",
    response_model=BaseResponse,
    summary="Verify attendance",
    description="Verify single student attendance from image"
)
async def verify_attendance(request: AttendanceVerifyRequest, image_base64: str):
    """
    Verify student attendance using facial recognition
    
    - **class_id**: Unique identifier for the class session
    - **image_base64**: Base64 encoded image containing student's face
    - **timestamp**: Optional timestamp (defaults to current time)
    """
    try:
        result = await attendance_service.verify_attendance(
            image_base64=image_base64,
            class_id=request.class_id
        )
        
        if not result["success"]:
            return BaseResponse(
                success=False,
                message=result["message"],
                data=result
            )
        
        return BaseResponse(
            success=True,
            message="Attendance verified successfully",
            data=result
        )
    
    except Exception as e:
        logger.error(f"Attendance verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.post(
    "/batch-verify",
    response_model=BaseResponse,
    summary="Batch verify attendance",
    description="Verify multiple students from multiple images"
)
async def batch_verify_attendance(request: BatchAttendanceRequest):
    """
    Batch attendance verification for multiple students
    
    - **class_id**: Class session identifier
    - **images**: List of base64 encoded images
    - **timestamp**: Optional timestamp
    """
    try:
        if not request.images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No images provided"
            )
        
        if len(request.images) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 images per batch"
            )
        
        result = await attendance_service.batch_verify_attendance(
            images_base64=request.images,
            class_id=request.class_id
        )
        
        return BaseResponse(
            success=True,
            message=f"Processed {result['total_images']} images",
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/report/{class_id}",
    response_model=BaseResponse,
    summary="Get attendance report",
    description="Generate attendance report for a class session"
)
async def get_attendance_report(class_id: str):
    """
    Get detailed attendance report for a class session
    
    - **class_id**: The class session identifier
    """
    try:
        report = await attendance_service.get_class_attendance_report(class_id)
        
        return BaseResponse(
            success=True,
            message="Attendance report generated",
            data=report
        )
    
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/history/{student_id}",
    response_model=BaseResponse,
    summary="Get student attendance history",
    description="Retrieve attendance history for a specific student"
)
async def get_student_attendance_history(
    student_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get attendance history for a student
    
    - **student_id**: Student identifier
    - **limit**: Maximum number of records
    - **offset**: Pagination offset
    """
    try:
        from app.db.supabase_client import get_supabase
        
        client = get_supabase()
        response = client.table("attendance")\
            .select("*")\
            .eq("student_id", student_id)\
            .order("timestamp", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return BaseResponse(
            success=True,
            message=f"Found {len(response.data)} attendance records",
            data={
                "student_id": student_id,
                "total": len(response.data),
                "records": response.data
            }
        )
    
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/record/{record_id}",
    response_model=BaseResponse,
    summary="Delete attendance record",
    description="Remove an attendance record (admin only)"
)
async def delete_attendance_record(record_id: int):
    """
    Delete an attendance record
    
    - **record_id**: The ID of the attendance record to delete
    """
    try:
        from app.db.supabase_client import get_supabase
        
        client = get_supabase()
        response = client.table("attendance").delete().eq("id", record_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance record {record_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Attendance record deleted",
            data={"record_id": record_id}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete record error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
