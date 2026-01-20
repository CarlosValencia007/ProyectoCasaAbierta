"""
Smart Classroom AI - Attendance API Router
Endpoints for attendance verification and reporting
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from app.core.schemas import BaseResponse, AttendanceVerifyRequest, BatchAttendanceRequest
from app.services.attendance_service import AttendanceService
from app.core.logger import logger
from app.core.config import get_settings
import httpx
import asyncio
from app.db.supabase_client import get_supabase
router = APIRouter(prefix="/attendance", tags=["Attendance"])
attendance_service = AttendanceService()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def enviar_notificacion_asistencia():
    """Llama a la Edge Function para enviar notificaciones de nuevas asistencias (fire-and-forget)"""
    try:
        settings = get_settings()
        url = f"{settings.SUPABASE_URL}/functions/v1/student-notifications"
        
        logger.info(f"🔔 Llamando Edge Function (asíncrono): {url}")
        
        # Fire-and-forget: no esperamos respuesta para evitar timeouts
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Usamos asyncio.create_task para ejecutar sin bloquear
            try:
                response = await client.post(
                    url,
                    params={"accion": "nuevas_asistencias"},
                    headers={"Authorization": f"Bearer {settings.SUPABASE_KEY}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Notificaciones procesadas: {data.get('notificaciones_enviadas', 0)} enviadas, {data.get('errores', 0)} errores")
                else:
                    logger.warning(f"⚠️ Edge Function respondió con código {response.status_code}: {response.text}")
            except httpx.ReadTimeout:
                logger.info(f"⏱️ Edge Function está procesando (timeout esperado con muchas notificaciones)")
            except httpx.RequestError as e:
                logger.warning(f"⚠️ Error de conexión con Edge Function: {str(e)}")
                
    except Exception as e:
        logger.error(f"❌ Error iniciando notificación: {str(e)}")


@router.post(
    "/verify",
    response_model=BaseResponse,
    summary="Verify attendance",
    description="Verify single student attendance from image"
)
async def verify_attendance(
    class_id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Verify student attendance using facial recognition
    
    - **class_id**: Unique identifier for the class session
    - **image**: Image file containing student's face
    """
    try:
        # Read image file and convert to base64
        import base64
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        result = await attendance_service.verify_attendance(
            image_base64=image_base64,
            class_id=class_id
        )
        
        if not result["success"]:
            return BaseResponse(
                success=False,
                message=result["message"],
                data=result
            )
        
        # Llamar Edge Function para enviar notificación (sin esperar)
        asyncio.create_task(enviar_notificacion_asistencia())
        
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
    "/class/{class_id}",
    response_model=BaseResponse,
    summary="Get class attendance records",
    description="Retrieve all attendance records for a specific class session"
)
async def get_class_attendance(class_id: str):
    """
    Get all attendance records for a class session
    
    - **class_id**: The class session identifier
    """
    try:
        from app.db.supabase_client import get_supabase
        
        client = get_supabase()
        
        # Get attendance records with student info (using select with foreign key)
        response = client.table("attendance")\
            .select("*, students(student_id, name, email)")\
            .eq("class_id", class_id)\
            .order("timestamp", desc=True)\
            .execute()
        
        # Format records to include student name at top level
        formatted_records = []
        for record in response.data:
            student_info = record.pop('students', None)
            if student_info:
                record['student_name'] = student_info['name']
                record['student_email'] = student_info.get('email')
            formatted_records.append(record)
        
        return BaseResponse(
            success=True,
            message=f"Found {len(formatted_records)} attendance records",
            data={
                "class_id": class_id,
                "total": len(formatted_records),
                "records": formatted_records
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving class attendance: {str(e)}")
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


from pydantic import BaseModel

class ManualAttendanceRequest(BaseModel):
    class_id: str
    student_id: str
    status: str  # 'present', 'late', 'absent'
    period: int = 1


@router.post(
    "/manual",
    response_model=BaseResponse,
    summary="Register manual attendance",
    description="Manually register attendance for a student with a specific status"
)
async def register_manual_attendance(request: ManualAttendanceRequest):
    """
    Register manual attendance for a student
    
    - **class_id**: Class session identifier
    - **student_id**: Student identifier (cédula)
    - **status**: Attendance status ('present', 'late', 'absent')
    - **period**: Class period/hour number (1, 2, 3, etc.)
    """
    try:
        from datetime import datetime
        
        client = get_supabase()
        
        # Validate status
        valid_statuses = ['present', 'late', 'absent']
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        # Verify student exists
        student_response = client.table("students")\
            .select("student_id, name")\
            .eq("student_id", request.student_id)\
            .execute()
        
        if not student_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {request.student_id} not found"
            )
        
        student_name = student_response.data[0]['name']
        
        # Check if attendance already exists for this student and class
        existing = client.table("attendance")\
            .select("id")\
            .eq("class_id", request.class_id)\
            .eq("student_id", request.student_id)\
            .execute()
        
        now = datetime.now().isoformat()
        
        if existing.data:
            # Update existing record - only update status field which we know exists
            update_data = {"status": request.status}
            
            update_response = client.table("attendance")\
                .update(update_data)\
                .eq("id", existing.data[0]['id'])\
                .execute()
            
            logger.info(f"Updated manual attendance: {request.student_id} -> {request.status}")
            
            return BaseResponse(
                success=True,
                message=f"Attendance updated for {student_name}",
                data={
                    "student_id": request.student_id,
                    "student_name": student_name,
                    "status": request.status,
                    "period": request.period,
                    "action": "updated"
                }
            )
        else:
            # Insert new record with only basic fields that we know exist
            insert_data = {
                "class_id": request.class_id,
                "student_id": request.student_id,
                "status": request.status,
                "timestamp": now,
                "confidence": 1.0
            }
            
            insert_response = client.table("attendance")\
                .insert(insert_data)\
                .execute()
            
            logger.info(f"Registered manual attendance: {request.student_id} -> {request.status}")
            
            # Trigger notification (async, non-blocking)
            asyncio.create_task(enviar_notificacion_asistencia())
            
            return BaseResponse(
                success=True,
                message=f"Attendance registered for {student_name}",
                data={
                    "student_id": request.student_id,
                    "student_name": student_name,
                    "status": request.status,
                    "period": request.period,
                    "action": "created"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual attendance error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
