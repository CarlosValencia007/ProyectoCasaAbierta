"""
Smart Classroom AI - Enrollment API Router
Endpoints for student enrollment
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from app.core.schemas import BaseResponse, StudentEnrollRequest, StudentEnrollResponse
from app.services.enrollment_service import EnrollmentService
from app.core.logger import logger

router = APIRouter(prefix="/enrollment", tags=["Enrollment"])
enrollment_service = EnrollmentService()


@router.post(
    "/enroll",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll new student",
    description="Register a new student with facial biometric data"
)
async def enroll_student(request: StudentEnrollRequest):
    """
    Enroll a new student in the system
    
    - **student_id**: Unique identifier for the student
    - **name**: Full name of the student
    - **image_base64**: Base64 encoded image of the student's face
    - **email**: Optional email address
    - **metadata**: Optional additional information (JSON object)
    """
    try:
        result = await enrollment_service.enroll_student(
            student_id=request.student_id,
            name=request.name,
            image_base64=request.image_base64,
            email=request.email,
            metadata=request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return BaseResponse(
            success=True,
            message="Student enrolled successfully",
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrollment endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrollment failed: {str(e)}"
        )


@router.put(
    "/update-photo/{student_id}",
    response_model=BaseResponse,
    summary="Update student photo",
    description="Update facial biometric data for existing student"
)
async def update_student_photo(student_id: str, image_base64: str = Form(...)):
    """
    Update the facial photo of an existing student
    
    - **student_id**: The ID of the student to update
    - **image_base64**: New base64 encoded face image
    """
    try:
        result = await enrollment_service.update_student_photo(
            student_id=student_id,
            image_base64=image_base64
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result["message"] else status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return BaseResponse(
            success=True,
            message="Photo updated successfully",
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update photo error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Photo update failed: {str(e)}"
        )


@router.get(
    "/student/{student_id}",
    response_model=BaseResponse,
    summary="Get student information",
    description="Retrieve student details by ID"
)
async def get_student(student_id: str):
    """Get student information by ID"""
    try:
        from app.db.crud import StudentCRUD
        student_crud = StudentCRUD()
        
        student = await student_crud.find_by_id(student_id)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Remove embedding from response (too large)
        student_info = {k: v for k, v in student.items() if k != "face_embedding"}
        
        return BaseResponse(
            success=True,
            message="Student found",
            data=student_info
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get student error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/students",
    response_model=BaseResponse,
    summary="List all students",
    description="Get list of all enrolled students"
)
async def list_students(active_only: bool = True, limit: int = 100, offset: int = 0):
    """
    List all enrolled students
    
    - **active_only**: Filter only active students (default: True)
    - **limit**: Maximum number of results
    - **offset**: Pagination offset
    """
    try:
        from app.db.crud import StudentCRUD
        student_crud = StudentCRUD()
        
        students = await student_crud.list_all(active_only=active_only)
        
        # Pagination
        paginated_students = students[offset:offset + limit]
        
        # Remove embeddings
        students_info = [
            {k: v for k, v in s.items() if k != "face_embedding"}
            for s in paginated_students
        ]
        
        return BaseResponse(
            success=True,
            message=f"Found {len(students_info)} students",
            data={
                "total": len(students),
                "limit": limit,
                "offset": offset,
                "students": students_info
            }
        )
    
    except Exception as e:
        logger.error(f"List students error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
