"""
Smart Classroom AI - Classes API Router
Endpoints for class session management
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from datetime import datetime
import pytz
from app.core.schemas import BaseResponse
from app.db.supabase_client import get_supabase
from app.core.logger import logger
from pydantic import BaseModel, Field

router = APIRouter(prefix="/classes", tags=["Classes"])

# Zona horaria de Ecuador (UTC-5)
ECUADOR_TZ = pytz.timezone('America/Guayaquil')

def get_ecuador_time():
    """Obtiene la hora actual en zona horaria de Ecuador (UTC-5)"""
    return datetime.now(ECUADOR_TZ)

def to_ecuador_time(dt: datetime):
    """Convierte un datetime a zona horaria de Ecuador"""
    if dt.tzinfo is None:
        # Si es naive, asumimos que es UTC
        dt = pytz.utc.localize(dt)
    return dt.astimezone(ECUADOR_TZ)


def parse_datetime(dt_string: str) -> Optional[datetime]:
    """
    Parse datetime string with various formats
    Handles ISO format with variable microsecond precision
    """
    if not dt_string:
        return None
    
    try:
        # Replace Z with +00:00 for ISO format
        dt_string = dt_string.replace('Z', '+00:00')
        
        # Try standard ISO format first
        try:
            return datetime.fromisoformat(dt_string)
        except ValueError:
            pass
        
        # Handle truncated microseconds (e.g., .02337 instead of .023370)
        # Find the decimal point and pad microseconds to 6 digits
        if '.' in dt_string:
            parts = dt_string.split('.')
            if len(parts) == 2:
                # Split timezone if present
                micro_and_tz = parts[1]
                if '+' in micro_and_tz:
                    micro, tz = micro_and_tz.split('+', 1)
                    micro = micro.ljust(6, '0')[:6]
                    dt_string = f"{parts[0]}.{micro}+{tz}"
                elif '-' in micro_and_tz and micro_and_tz.count('-') == 1:
                    micro, tz = micro_and_tz.rsplit('-', 1)
                    micro = micro.ljust(6, '0')[:6]
                    dt_string = f"{parts[0]}.{micro}-{tz}"
                else:
                    micro = micro_and_tz.ljust(6, '0')[:6]
                    dt_string = f"{parts[0]}.{micro}"
        
        return datetime.fromisoformat(dt_string)
        
    except Exception:
        # Last resort: use dateutil parser
        try:
            from dateutil import parser
            return parser.parse(dt_string)
        except Exception:
            return None


# ============================================================================
# SCHEMAS
# ============================================================================

class ClassCreateSimpleRequest(BaseModel):
    """Simplified request schema for creating a class session (for frontend)"""
    class_name: str = Field(..., min_length=1, max_length=100, description="Class name")
    session_date: str = Field(..., description="Session date (YYYY-MM-DD)")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM) - opcional, si no se pone la clase queda activa")
    instructor: Optional[str] = Field(None, max_length=100, description="Instructor name")
    room: Optional[str] = Field(None, max_length=50, description="Room number/name")
    teacher_id: Optional[str] = Field(None, description="ID del profesor")
    course_id: Optional[str] = Field(None, description="ID del curso/materia")


class ClassCreateRequest(BaseModel):
    """Request schema for creating a class session"""
    class_id: str = Field(..., min_length=1, max_length=100, description="Unique class identifier")
    class_name: str = Field(..., min_length=1, max_length=100, description="Class name")
    instructor: Optional[str] = Field(None, max_length=100, description="Instructor name")
    room: Optional[str] = Field(None, max_length=50, description="Room number/name")
    start_time: datetime = Field(..., description="Class start time")
    end_time: Optional[datetime] = Field(None, description="Class end time")
    metadata: Optional[dict] = Field(None, description="Additional metadata (JSON)")
    teacher_id: Optional[str] = Field(None, description="ID del profesor")
    course_id: Optional[str] = Field(None, description="ID del curso/materia")


class ClassUpdateRequest(BaseModel):
    """Request schema for updating a class session"""
    class_name: Optional[str] = Field(None, max_length=100)
    instructor: Optional[str] = Field(None, max_length=100)
    room: Optional[str] = Field(None, max_length=50)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Optional[dict] = None


class ClassResponse(BaseModel):
    """Response schema for class session"""
    id: int
    class_id: str
    class_name: str
    instructor: Optional[str]
    room: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    total_students: int
    present_count: int
    attendance_rate: float
    created_at: datetime
    metadata: Optional[dict]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create class session (simple)",
    description="Create a new class session with date and time fields"
)
async def create_class_simple(request: ClassCreateSimpleRequest):
    """
    Create a new class session with simplified date/time format
    
    - **class_name**: Name of the class (e.g., "Matemáticas 101")
    - **session_date**: Date in YYYY-MM-DD format (e.g., "2026-01-04")
    - **start_time**: Start time in HH:MM format (e.g., "10:00")
    - **end_time**: End time in HH:MM format (e.g., "12:00")
    - **instructor**: Teacher/instructor name (optional)
    - **room**: Classroom location (optional)
    """
    try:
        from datetime import datetime
        import uuid
        
        supabase = get_supabase()
        
        # Generate unique class_id
        class_id = f"CLASS-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear datetime strings directamente - NO convertir a UTC
        # Supabase/PostgreSQL manejará las zonas horarias
        start_datetime_str = f"{request.session_date}T{request.start_time}:00"
        end_datetime_str = None
        
        # Parsear para validaciones
        start_datetime = datetime.fromisoformat(start_datetime_str)
        end_datetime = None
        
        # end_time es opcional - si no se proporciona, la clase queda activa indefinidamente
        if request.end_time and request.end_time.strip():
            end_datetime_str = f"{request.session_date}T{request.end_time}:00"
            end_datetime = datetime.fromisoformat(end_datetime_str)
        
        # Obtener hora actual
        now = datetime.now()
        
        # Solo validar duración si hay hora de fin
        if end_datetime:
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
            if duration_hours <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La hora de fin debe ser posterior a la hora de inicio"
                )
            if duration_hours > 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La duración de la clase no puede exceder 8 horas (actual: {duration_hours:.1f}h)"
                )
        
        # Preparar metadata con teacher_id y course_id si existen
        metadata_dict = {}
        if request.teacher_id:
            metadata_dict['teacher_id'] = request.teacher_id
        if request.course_id:
            metadata_dict['course_id'] = request.course_id
        
        # Log para debugging
        logger.info(f"⏰ Creando clase:")
        logger.info(f"  - Hora actual: {now.isoformat()}")
        logger.info(f"  - Inicio: {start_datetime_str}")
        logger.info(f"  - Fin: {end_datetime_str or 'Sin definir (activa indefinidamente)'}")
        if end_datetime:
            logger.info(f"  - ¿Está activa? {start_datetime <= now < end_datetime}")
        else:
            logger.info(f"  - ¿Está activa? {start_datetime <= now}")
        
        # Create class session
        # La clase estará activa si aún no ha terminado (o si no tiene hora de fin)
        class_data = {
            "class_id": class_id,
            "class_name": request.class_name,
            "instructor": request.instructor or "No especificado",
            "room": request.room or "No especificada",
            "start_time": start_datetime_str,
            "end_time": end_datetime_str,
            "total_students": 0,
            "present_count": 0,
            "attendance_rate": 0.0,
            "metadata": metadata_dict if metadata_dict else None
        }
        
        result = supabase.table("class_sessions").insert(class_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create class session"
            )
        
        logger.info(f"Class session created: {class_id}")
        
        return {
            "class_id": result.data[0]["class_id"],
            "class_name": result.data[0]["class_name"],
            "session_date": request.session_date,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "instructor": result.data[0]["instructor"],
            "room": result.data[0]["room"],
            "created_at": result.data[0]["created_at"]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date/time format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating class session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/create",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new class session",
    description="Create a new class session with schedule and metadata"
)
async def create_class(request: ClassCreateRequest):
    """
    Create a new class session
    
    - **class_id**: Unique identifier for the class (e.g., "ALGORITMOS-2025-A")
    - **class_name**: Name of the class
    - **instructor**: Teacher/instructor name (optional)
    - **room**: Classroom location (optional)
    - **start_time**: Class start date/time
    - **end_time**: Class end date/time (optional)
    - **metadata**: Additional information as JSON object (optional)
    """
    try:
        supabase = get_supabase()
        
        # Check if class_id already exists
        existing = supabase.table("class_sessions").select("class_id").eq("class_id", request.class_id).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Class with ID '{request.class_id}' already exists"
            )
        
        # Create class session
        # Note: teacher_id and course_id can be stored in metadata if needed
        metadata = request.metadata or {}
        if request.teacher_id:
            metadata['teacher_id'] = request.teacher_id
        if request.course_id:
            metadata['course_id'] = request.course_id
        
        # Convertir tiempos a zona horaria de Ecuador si no tienen zona horaria
        start_time = request.start_time
        end_time = request.end_time
        
        if start_time.tzinfo is None:
            start_time = ECUADOR_TZ.localize(start_time)
        else:
            start_time = start_time.astimezone(ECUADOR_TZ)
        
        if end_time:
            if end_time.tzinfo is None:
                end_time = ECUADOR_TZ.localize(end_time)
            else:
                end_time = end_time.astimezone(ECUADOR_TZ)
            
            # Validate duration (max 8 hours)
            duration_hours = (end_time - start_time).total_seconds() / 3600
            if duration_hours > 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Class duration cannot exceed 8 hours (current: {duration_hours:.1f}h)"
                )
            if duration_hours <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End time cannot be before or equal to start time"
                )
        
        # La clase siempre se crea con su end_time programado
        # El estado (activa/finalizada) se determina dinámicamente según la hora actual
        class_data = {
            "class_id": request.class_id,
            "class_name": request.class_name,
            "instructor": request.instructor,
            "room": request.room,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat() if end_time else None,
            "total_students": 0,
            "present_count": 0,
            "attendance_rate": 0.0,
            "metadata": metadata if metadata else None
        }
        
        result = supabase.table("class_sessions").insert(class_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create class session"
            )
        
        logger.info(f"Class session created: {request.class_id}")
        
        return BaseResponse(
            success=True,
            message=f"Class session '{request.class_name}' created successfully",
            data=result.data[0]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating class session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating class: {str(e)}"
        )


@router.get(
    "/active",
    response_model=BaseResponse,
    summary="Get active class sessions",
    description="Get all class sessions that are currently active based on Ecuador time (UTC-5)"
)
async def get_active_classes():
    """
    Get all active class sessions (sessions where current time is between start_time and end_time)
    """
    try:
        supabase = get_supabase()
        
        # Obtener todas las clases
        result = supabase.table("class_sessions")\
            .select("*")\
            .order("start_time", desc=True)\
            .execute()
        
        # Filtrar clases activas basándose en la hora actual de Ecuador
        now_ecuador = get_ecuador_time()
        active_classes = []
        
        for class_session in result.data:
            try:
                start_time = parse_datetime(class_session['start_time'])
                end_time = parse_datetime(class_session['end_time']) if class_session.get('end_time') else None
                
                if start_time is None:
                    continue
                
                # Convertir a hora de Ecuador
                start_time_ecuador = to_ecuador_time(start_time)
                
                # Extraer course_id y teacher_id del metadata si existen
                metadata = class_session.get('metadata', {}) or {}
                if isinstance(metadata, dict):
                    if 'course_id' in metadata:
                        class_session['course_id'] = metadata['course_id']
                    if 'teacher_id' in metadata:
                        class_session['teacher_id'] = metadata['teacher_id']
                
                # Una clase está activa si:
                # 1. Ya comenzó (start_time <= now)
                # 2. No tiene end_time (indefinida) O aún no ha terminado (now < end_time)
                if end_time:
                    end_time_ecuador = to_ecuador_time(end_time)
                    if start_time_ecuador <= now_ecuador < end_time_ecuador:
                        active_classes.append(class_session)
                else:
                    # Sin end_time = clase activa indefinidamente hasta que se finalice
                    if start_time_ecuador <= now_ecuador:
                        active_classes.append(class_session)
            except Exception:
                # Skip invalid sessions
                continue
        
        return BaseResponse(
            success=True,
            message=f"Retrieved {len(active_classes)} active class sessions",
            data={
                "classes": active_classes,
                "count": len(active_classes),
                "current_time_ecuador": now_ecuador.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving active classes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving active classes: {str(e)}"
        )


@router.post(
    "/{class_id}/end",
    response_model=BaseResponse,
    summary="End a class session",
    description="Mark a class session as ended by setting the end_time to current Ecuador time"
)
async def end_class(class_id: str):
    """
    End an active class session by updating end_time to current time
    
    - **class_id**: The unique identifier of the class to end
    """
    try:
        from datetime import datetime
        supabase = get_supabase()
        
        # Check if class exists
        existing = supabase.table("class_sessions").select("*").eq("class_id", class_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID '{class_id}' not found"
            )
        
        class_data = existing.data[0]
        
        # Obtener hora actual (local)
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Verificar si la clase ya terminó según su end_time original
        original_end_time_str = class_data.get('end_time')
        if original_end_time_str:
            try:
                original_end_time = datetime.fromisoformat(original_end_time_str.replace('Z', '+00:00'))
                # Comparar sin zona horaria
                if original_end_time.replace(tzinfo=None) <= now:
                    return BaseResponse(
                        success=True,
                        message=f"Class session '{class_id}' was already ended",
                        data=class_data
                    )
            except:
                pass  # Si hay error parseando, continuar para actualizar
        
        # Actualizar end_time a la hora actual
        result = supabase.table("class_sessions")\
            .update({"end_time": now_str})\
            .eq("class_id", class_id)\
            .execute()
        
        logger.info(f"Class session manually ended at {now_str}: {class_id}")
        
        return BaseResponse(
            success=True,
            message=f"Class session '{class_id}' ended successfully",
            data=result.data[0] if result.data else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending class: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending class: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending class: {str(e)}"
        )


@router.get(
    "/{class_id}",
    response_model=BaseResponse,
    summary="Get class session by ID",
    description="Retrieve detailed information about a specific class session"
)
async def get_class(class_id: str):
    """
    Get class session details by class_id
    
    - **class_id**: The unique identifier of the class
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table("class_sessions").select("*").eq("class_id", class_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID '{class_id}' not found"
            )
        
        return BaseResponse(
            success=True,
            message="Class session retrieved successfully",
            data=result.data[0]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving class: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving class: {str(e)}"
        )


@router.get(
    "",
    response_model=BaseResponse,
    summary="List all class sessions",
    description="Get list of all class sessions with optional filtering and status classification"
)
async def list_classes(
    limit: int = 50,
    offset: int = 0,
    instructor: Optional[str] = None,
    status_filter: Optional[str] = None  # "active", "finished", or None for all
):
    """
    List all class sessions with dynamic status based on Ecuador time
    
    - **limit**: Maximum number of results (default: 50)
    - **offset**: Number of results to skip (default: 0)
    - **instructor**: Filter by instructor name (optional)
    - **status_filter**: Filter by status - "active" or "finished" (optional)
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table("class_sessions").select("*")
        
        if instructor:
            query = query.eq("instructor", instructor)
        
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        
        result = query.execute()
        
        # Clasificar clases por estado basándose en la hora actual de Ecuador
        now_ecuador = get_ecuador_time()
        active_classes = []
        finished_classes = []
        
        for class_session in result.data:
            try:
                start_time = parse_datetime(class_session['start_time'])
                end_time = parse_datetime(class_session['end_time']) if class_session.get('end_time') else None
                
                if start_time is None:
                    class_session['is_active'] = False
                    class_session['status'] = 'finished'
                    finished_classes.append(class_session)
                    continue
                
                start_time_ecuador = to_ecuador_time(start_time)
                
                # Extraer course_id y teacher_id del metadata si existen
                metadata = class_session.get('metadata', {}) or {}
                if isinstance(metadata, dict):
                    if 'course_id' in metadata:
                        class_session['course_id'] = metadata['course_id']
                    if 'teacher_id' in metadata:
                        class_session['teacher_id'] = metadata['teacher_id']
                
                # Agregar campo de estado dinámico
                # Si no tiene end_time, la clase está activa hasta que se finalice manualmente
                if end_time:
                    end_time_ecuador = to_ecuador_time(end_time)
                    if start_time_ecuador <= now_ecuador < end_time_ecuador:
                        class_session['is_active'] = True
                        class_session['status'] = 'active'
                        active_classes.append(class_session)
                    else:
                        class_session['is_active'] = False
                        class_session['status'] = 'finished'
                        finished_classes.append(class_session)
                else:
                    # Sin end_time = clase activa indefinidamente hasta finalizar manualmente
                    if start_time_ecuador <= now_ecuador:
                        class_session['is_active'] = True
                        class_session['status'] = 'active'
                        active_classes.append(class_session)
                    else:
                        # Aún no ha comenzado
                        class_session['is_active'] = False
                        class_session['status'] = 'pending'
                        finished_classes.append(class_session)
            except Exception:
                # Si hay error, asumir que está finalizada
                class_session['is_active'] = False
                class_session['status'] = 'finished'
                finished_classes.append(class_session)
        
        # Aplicar filtro de estado si se especific\u00f3
        if status_filter == "active":
            filtered_classes = active_classes
        elif status_filter == "finished":
            filtered_classes = finished_classes
        else:
            filtered_classes = result.data
        
        return BaseResponse(
            success=True,
            message=f"Retrieved {len(filtered_classes)} class sessions",
            data={
                "classes": filtered_classes,
                "count": len(filtered_classes),
                "active_count": len(active_classes),
                "finished_count": len(finished_classes),
                "limit": limit,
                "offset": offset,
                "current_time_ecuador": now_ecuador.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing classes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing classes: {str(e)}"
        )


@router.put(
    "/{class_id}",
    response_model=BaseResponse,
    summary="Update class session",
    description="Update information of an existing class session"
)
async def update_class(class_id: str, request: ClassUpdateRequest):
    """
    Update class session information
    
    - **class_id**: The unique identifier of the class to update
    - Only provided fields will be updated
    """
    try:
        supabase = get_supabase()
        
        # Check if class exists
        existing = supabase.table("class_sessions").select("id").eq("class_id", class_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID '{class_id}' not found"
            )
        
        # Build update data (only include provided fields)
        update_data = {}
        if request.class_name is not None:
            update_data["class_name"] = request.class_name
        if request.instructor is not None:
            update_data["instructor"] = request.instructor
        if request.room is not None:
            update_data["room"] = request.room
        if request.start_time is not None:
            update_data["start_time"] = request.start_time.isoformat()
        if request.end_time is not None:
            update_data["end_time"] = request.end_time.isoformat()
        if request.metadata is not None:
            update_data["metadata"] = request.metadata
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        result = supabase.table("class_sessions").update(update_data).eq("class_id", class_id).execute()
        
        logger.info(f"Class session updated: {class_id}")
        
        return BaseResponse(
            success=True,
            message=f"Class session '{class_id}' updated successfully",
            data=result.data[0] if result.data else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating class: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating class: {str(e)}"
        )


@router.delete(
    "/{class_id}",
    response_model=BaseResponse,
    summary="Delete class session",
    description="Delete a class session and all related records"
)
async def delete_class(class_id: str):
    """
    Delete a class session
    
    - **class_id**: The unique identifier of the class to delete
    - ⚠️ WARNING: This will also delete all attendance and emotion records for this class
    """
    try:
        supabase = get_supabase()
        
        # Check if class exists
        existing = supabase.table("class_sessions").select("id").eq("class_id", class_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID '{class_id}' not found"
            )
        
        # Delete related records first (if you want cascade delete)
        # Note: If you have ON DELETE CASCADE in DB, this is automatic
        supabase.table("attendance").delete().eq("class_id", class_id).execute()
        supabase.table("emotion_events").delete().eq("class_id", class_id).execute()
        
        # Delete class session
        result = supabase.table("class_sessions").delete().eq("class_id", class_id).execute()
        
        logger.info(f"Class session deleted: {class_id}")
        
        return BaseResponse(
            success=True,
            message=f"Class session '{class_id}' deleted successfully",
            data={"class_id": class_id, "deleted": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting class: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting class: {str(e)}"
        )


@router.get(
    "/{class_id}/stats",
    response_model=BaseResponse,
    summary="Get class statistics",
    description="Get attendance and emotion statistics for a class"
)
async def get_class_stats(class_id: str):
    """
    Get statistics for a class session
    
    - **class_id**: The unique identifier of the class
    - Returns attendance rate, emotion analysis, and engagement metrics
    """
    try:
        supabase = get_supabase()
        
        # Get class info
        class_result = supabase.table("class_sessions").select("*").eq("class_id", class_id).execute()
        
        if not class_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID '{class_id}' not found"
            )
        
        class_data = class_result.data[0]
        
        # Get attendance records
        attendance_result = supabase.table("attendance").select("*").eq("class_id", class_id).execute()
        attendance_count = len(attendance_result.data)
        
        # Get emotion events
        emotions_result = supabase.table("emotion_events").select("dominant_emotion, confidence").eq("class_id", class_id).execute()
        emotions_count = len(emotions_result.data)
        
        # Calculate emotion distribution
        emotion_distribution = {}
        if emotions_result.data:
            for event in emotions_result.data:
                emotion = event["dominant_emotion"]
                emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        # Calculate engagement score (% of positive emotions)
        positive_emotions = ["happy", "surprise"]
        positive_count = sum(emotion_distribution.get(e, 0) for e in positive_emotions)
        engagement_score = (positive_count / emotions_count * 100) if emotions_count > 0 else 0
        
        stats = {
            "class_info": class_data,
            "attendance": {
                "total_records": attendance_count,
                "unique_students": len(set(r["student_id"] for r in attendance_result.data)),
                "attendance_rate": class_data.get("attendance_rate", 0.0)
            },
            "emotions": {
                "total_events": emotions_count,
                "distribution": emotion_distribution,
                "engagement_score": round(engagement_score, 2)
            }
        }
        
        return BaseResponse(
            success=True,
            message="Class statistics retrieved successfully",
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting class statistics: {str(e)}"
        )
