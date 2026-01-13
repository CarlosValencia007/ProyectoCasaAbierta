"""
Smart Classroom AI - Enrollments API Router
Endpoints for managing student enrollments in courses
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.schemas import BaseResponse
from app.db.supabase_client import get_supabase
from app.core.logger import logger

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# ============================================================================
# SCHEMAS
# ============================================================================

class EnrollStudentRequest(BaseModel):
    """Request to enroll a student in a course"""
    student_id: str = Field(..., description="Cédula del estudiante")
    course_id: str = Field(..., description="ID del curso (UUID)")


class EnrollmentResponse(BaseModel):
    """Response for enrollment operations"""
    id: Optional[int] = None
    student_id: str
    course_id: str
    enrolled_at: Optional[str] = None
    student_name: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscribir estudiante en un curso",
    description="Añade un estudiante existente a un curso/materia"
)
async def enroll_student_in_course(request: EnrollStudentRequest):
    """
    Inscribir un estudiante en un curso
    
    - **student_id**: Cédula del estudiante (debe estar registrado previamente)
    - **course_id**: ID del curso (UUID)
    """
    try:
        supabase = get_supabase()
        
        # Verify student exists
        student_response = supabase.table("students")\
            .select("student_id, name")\
            .eq("student_id", request.student_id)\
            .execute()
        
        if not student_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con cédula '{request.student_id}' no está registrado en el sistema"
            )
        
        student = student_response.data[0]
        
        # Check if already enrolled
        existing = supabase.table("enrollments")\
            .select("id")\
            .eq("student_id", request.student_id)\
            .eq("course_id", request.course_id)\
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El estudiante {student['name']} ya está inscrito en este curso"
            )
        
        # Create enrollment
        enrollment_data = {
            "student_id": request.student_id,
            "course_id": request.course_id,
            "enrolled_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("enrollments").insert(enrollment_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al inscribir estudiante"
            )
        
        logger.info(f"✅ Estudiante {request.student_id} inscrito en curso {request.course_id}")
        
        return BaseResponse(
            success=True,
            message=f"Estudiante {student['name']} inscrito exitosamente",
            data={
                **result.data[0],
                "student_name": student['name']
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inscribir estudiante: {str(e)}"
        )


@router.delete(
    "/{course_id}/{student_id}",
    response_model=BaseResponse,
    summary="Desinscribir estudiante de un curso",
    description="Elimina la inscripción de un estudiante en un curso"
)
async def unenroll_student_from_course(course_id: str, student_id: str):
    """
    Desinscribir un estudiante de un curso
    
    - **course_id**: ID del curso (UUID)
    - **student_id**: Cédula del estudiante
    """
    try:
        supabase = get_supabase()
        
        # Check if enrollment exists
        existing = supabase.table("enrollments")\
            .select("id")\
            .eq("student_id", student_id)\
            .eq("course_id", course_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El estudiante no está inscrito en este curso"
            )
        
        # Delete enrollment
        supabase.table("enrollments")\
            .delete()\
            .eq("student_id", student_id)\
            .eq("course_id", course_id)\
            .execute()
        
        logger.info(f"✅ Estudiante {student_id} desinscrito del curso {course_id}")
        
        return BaseResponse(
            success=True,
            message="Estudiante desinscrito exitosamente",
            data={"student_id": student_id, "course_id": course_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unenrolling student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desinscribir estudiante: {str(e)}"
        )


@router.get(
    "/course/{course_id}",
    response_model=BaseResponse,
    summary="Listar estudiantes de un curso",
    description="Obtiene todos los estudiantes inscritos en un curso específico"
)
async def get_course_students(course_id: str):
    """
    Obtener todos los estudiantes inscritos en un curso
    
    - **course_id**: ID del curso (UUID)
    """
    try:
        supabase = get_supabase()
        
        # Get enrollments with student data
        response = supabase.table("enrollments")\
            .select("*, students(student_id, name, email, photo_url, is_active)")\
            .eq("course_id", course_id)\
            .execute()
        
        # Format response
        students = []
        for enrollment in response.data or []:
            student_data = enrollment.get("students", {})
            if student_data:
                students.append({
                    "enrollment_id": enrollment.get("id"),
                    "student_id": student_data.get("student_id"),
                    "name": student_data.get("name"),
                    "email": student_data.get("email"),
                    "photo_url": student_data.get("photo_url"),
                    "is_active": student_data.get("is_active"),
                    "enrolled_at": enrollment.get("enrolled_at")
                })
        
        return BaseResponse(
            success=True,
            message=f"Se encontraron {len(students)} estudiantes",
            data={
                "course_id": course_id,
                "total": len(students),
                "students": students
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting course students: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes: {str(e)}"
        )


@router.get(
    "/student/{student_id}",
    response_model=BaseResponse,
    summary="Listar cursos de un estudiante",
    description="Obtiene todos los cursos en los que está inscrito un estudiante"
)
async def get_student_courses(student_id: str):
    """
    Obtener todos los cursos de un estudiante
    
    - **student_id**: Cédula del estudiante
    """
    try:
        supabase = get_supabase()
        
        # Get enrollments with course data
        response = supabase.table("enrollments")\
            .select("*, courses(id, course_name, course_code, description)")\
            .eq("student_id", student_id)\
            .execute()
        
        # Format response
        courses = []
        for enrollment in response.data or []:
            course_data = enrollment.get("courses", {})
            if course_data:
                courses.append({
                    "enrollment_id": enrollment.get("id"),
                    "course_id": course_data.get("id"),
                    "course_name": course_data.get("course_name"),
                    "course_code": course_data.get("course_code"),
                    "description": course_data.get("description"),
                    "enrolled_at": enrollment.get("enrolled_at")
                })
        
        return BaseResponse(
            success=True,
            message=f"El estudiante está inscrito en {len(courses)} cursos",
            data={
                "student_id": student_id,
                "total": len(courses),
                "courses": courses
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting student courses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cursos: {str(e)}"
        )


@router.get(
    "/available/{course_id}",
    response_model=BaseResponse,
    summary="Listar estudiantes disponibles para inscribir",
    description="Obtiene los estudiantes que NO están inscritos en un curso"
)
async def get_available_students(course_id: str):
    """
    Obtener estudiantes que pueden ser inscritos en un curso
    (todos los estudiantes menos los ya inscritos)
    
    - **course_id**: ID del curso (UUID)
    """
    try:
        supabase = get_supabase()
        
        # Get all students
        all_students_response = supabase.table("students")\
            .select("student_id, name, email, photo_url")\
            .eq("is_active", True)\
            .execute()
        
        all_students = {s["student_id"]: s for s in (all_students_response.data or [])}
        
        # Get enrolled students
        enrolled_response = supabase.table("enrollments")\
            .select("student_id")\
            .eq("course_id", course_id)\
            .execute()
        
        enrolled_ids = {e["student_id"] for e in (enrolled_response.data or [])}
        
        # Filter available students
        available_students = [
            student for student_id, student in all_students.items()
            if student_id not in enrolled_ids
        ]
        
        return BaseResponse(
            success=True,
            message=f"Hay {len(available_students)} estudiantes disponibles para inscribir",
            data={
                "course_id": course_id,
                "total": len(available_students),
                "students": available_students
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting available students: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes disponibles: {str(e)}"
        )
