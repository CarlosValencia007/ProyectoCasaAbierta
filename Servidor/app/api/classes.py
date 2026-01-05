"""
Smart Classroom AI - Classes API Router
Endpoints for class session management
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from datetime import datetime
from app.core.schemas import BaseResponse
from app.db.supabase_client import get_supabase
from app.core.logger import logger
from pydantic import BaseModel, Field

router = APIRouter(prefix="/classes", tags=["Classes"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ClassCreateSimpleRequest(BaseModel):
    """Simplified request schema for creating a class session (for frontend)"""
    class_name: str = Field(..., min_length=1, max_length=100, description="Class name")
    session_date: str = Field(..., description="Session date (YYYY-MM-DD)")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    instructor: Optional[str] = Field(None, max_length=100, description="Instructor name")
    room: Optional[str] = Field(None, max_length=50, description="Room number/name")


class ClassCreateRequest(BaseModel):
    """Request schema for creating a class session"""
    class_id: str = Field(..., min_length=1, max_length=100, description="Unique class identifier")
    class_name: str = Field(..., min_length=1, max_length=100, description="Class name")
    instructor: Optional[str] = Field(None, max_length=100, description="Instructor name")
    room: Optional[str] = Field(None, max_length=50, description="Room number/name")
    start_time: datetime = Field(..., description="Class start time")
    end_time: Optional[datetime] = Field(None, description="Class end time")
    metadata: Optional[dict] = Field(None, description="Additional metadata (JSON)")


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
        
        # Combine date and time strings into datetime objects
        start_datetime = datetime.fromisoformat(f"{request.session_date}T{request.start_time}:00")
        end_datetime = datetime.fromisoformat(f"{request.session_date}T{request.end_time}:00")
        
        # Create class session
        class_data = {
            "class_id": class_id,
            "class_name": request.class_name,
            "instructor": request.instructor or "No especificado",
            "room": request.room or "No especificada",
            "start_time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "total_students": 0,
            "present_count": 0,
            "attendance_rate": 0.0,
            "metadata": None
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
        class_data = {
            "class_id": request.class_id,
            "class_name": request.class_name,
            "instructor": request.instructor,
            "room": request.room,
            "start_time": request.start_time.isoformat(),
            "end_time": request.end_time.isoformat() if request.end_time else None,
            "total_students": 0,
            "present_count": 0,
            "attendance_rate": 0.0,
            "metadata": request.metadata
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
    description="Get list of all class sessions with optional filtering"
)
async def list_classes(
    limit: int = 50,
    offset: int = 0,
    instructor: Optional[str] = None
):
    """
    List all class sessions
    
    - **limit**: Maximum number of results (default: 50)
    - **offset**: Number of results to skip (default: 0)
    - **instructor**: Filter by instructor name (optional)
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table("class_sessions").select("*")
        
        if instructor:
            query = query.eq("instructor", instructor)
        
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        
        result = query.execute()
        
        return BaseResponse(
            success=True,
            message=f"Retrieved {len(result.data)} class sessions",
            data={
                "classes": result.data,
                "count": len(result.data),
                "limit": limit,
                "offset": offset
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
