"""
Smart Classroom AI - Enrollment API Router
Endpoints for student enrollment
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from app.core.schemas import (
    BaseResponse, 
    StudentEnrollRequest, 
    StudentEnrollResponse,
    EnrollmentRequest,
    EnrollmentResponse
)
from app.services.enrollment_service import EnrollmentService
from app.services.face_service import get_face_embedding
from app.db.supabase_client import get_supabase
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
async def enroll_student(
    student_id: str = Form(...),
    name: str = Form(...),
    email: Optional[str] = Form(None),
    image: UploadFile = File(...),
    course_id: Optional[str] = Form(None),
    teacher_id: Optional[str] = Form(None)
):
    """
    Enroll a new student in the system
    
    - **student_id**: Unique identifier for the student
    - **name**: Full name of the student
    - **image**: Image file of the student's face
    - **email**: Optional email address
    - **course_id**: Optional course ID
    - **teacher_id**: Optional teacher ID
    """
    try:
        # Read image file and convert to base64
        import base64
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        result = await enrollment_service.enroll_student(
            student_id=student_id,
            name=name,
            image_base64=image_base64,
            email=email,
            metadata=None,
            teacher_id=teacher_id,
            course_id=course_id
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
        
        # Remove embeddings but add a flag to indicate if it exists
        students_info = []
        for s in paginated_students:
            student_info = {k: v for k, v in s.items() if k != "face_embedding"}
            student_info["has_embedding"] = bool(s.get("face_embedding"))
            students_info.append(student_info)
        
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


# ============================================================================
# ENDPOINT OPTIMIZADO - Usa las funciones nuevas de face_service.py
# ============================================================================

@router.post(
    "/enroll-v2",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll student (Optimized)",
    description="Versión optimizada del endpoint de enrollment que usa las funciones directas de face_service"
)
async def enroll_student_optimized(payload: EnrollmentRequest):
    """
    Registra un nuevo estudiante (Versión Optimizada):
    1. Recibe la foto en Base64.
    2. Genera el vector facial (Embedding) usando DeepFace.
    3. Guarda ID, Nombre y Vector en Supabase.
    
    Esta versión usa las funciones optimizadas de face_service.py
    y mapea correctamente a tu esquema de BD.
    """
    try:
        logger.info(f"📝 Iniciando registro para: {payload.full_name} ({payload.student_id})")

        # PASO 1: Obtener el vector facial (Lógica de IA)
        # Esto llama a tu función creada anteriormente en face_service.py
        # Nota: El modelo ya está en RAM gracias al lifespan, no hay cold start
        vector_embedding = await get_face_embedding(payload.image_base64)
        
        logger.info(f"✅ Vector generado. Dimensiones: {len(vector_embedding)}")

        # PASO 2: Guardar en Supabase (Lógica de Base de Datos)
        # --- CORRECCIÓN CRÍTICA: Mapeamos los datos para que coincidan EXACTAMENTE con tu tabla 'students' ---
        supabase = get_supabase()
        
        student_data = {
            "student_id": payload.student_id,           # VARCHAR (UNIQUE, NOT NULL)
            "name": payload.full_name,                  # Tu tabla usa 'name', no 'full_name'
            "email": f"{payload.student_id}@tu-universidad.edu.ec",  # Opcional (puede ser None)
            "face_embedding": vector_embedding,         # USER-DEFINED (vector(512) o vector(128))
            "is_active": True,                          # BOOLEAN (default true)
            # "metadata": None,                         # JSONB (opcional)
            # "enrolled_at" se genera automáticamente con DEFAULT now()
        }

        logger.info(f"📤 Insertando en tabla 'students': {student_data['student_id']} - {student_data['name']}")

        # Insertamos en la tabla 'students'
        response = supabase.table("students").insert(student_data).execute()

        # Verificar si hubo error en la inserción
        if not response.data:
            raise Exception("Error al insertar en base de datos (posible ID duplicado o error de constraint).")

        logger.info(f"✅ Estudiante {payload.student_id} registrado exitosamente en BD")
        logger.info(f"📊 Registro guardado: {response.data[0].get('id', 'N/A')} - {response.data[0].get('name', 'N/A')}")

        return EnrollmentResponse(
            status="success", 
            message="Estudiante registrado exitosamente en el sistema biométrico.",
            student_id=payload.student_id
        )

    except ValueError as ve:
        # Errores de validación (ej. no se detectó cara)
        logger.warning(f"⚠️ Error de validación: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        # Errores inesperados (DB desconectada, error de DeepFace, ID duplicado)
        error_message = str(e)
        logger.error(f"❌ Error crítico en enrollment: {error_message}")
        
        # Detectar error de ID duplicado
        if "duplicate key" in error_message.lower() or "unique constraint" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El estudiante {payload.student_id} ya está registrado en el sistema."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error interno del servidor: {error_message}"
        )


@router.delete(
    "/students/{student_id}",
    response_model=BaseResponse,
    summary="Delete a student",
    description="Delete a student from the system by student_id"
)
async def delete_student(student_id: str):
    """
    Delete a student from the system
    
    - **student_id**: The student_id of the student to delete (e.g., "2020411")
    """
    try:
        from app.db.supabase_client import get_supabase
        
        client = get_supabase()
        
        # Check if student exists
        existing = client.table("students").select("id").eq("student_id", student_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{student_id}' not found"
            )
        
        # Delete student
        result = client.table("students").delete().eq("student_id", student_id).execute()
        
        logger.info(f"Student {student_id} deleted successfully")
        
        return BaseResponse(
            success=True,
            message=f"Student {student_id} deleted successfully",
            data={"student_id": student_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting student: {str(e)}"
        )
