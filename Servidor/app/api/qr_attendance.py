"""
Smart Classroom AI - QR & Code-based Attendance API
Endpoints for QR and rotating code attendance verification
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from app.services.qr_service import QRService, ClassPeriodService, RotatingCodeService
from app.db.crud import StudentCRUD, AttendanceCRUD
from app.core.logger import logger
from app.core.schemas import BaseResponse
from app.db.supabase_client import get_supabase

router = APIRouter(prefix="/qr", tags=["QR Attendance"])

# Ecuador timezone
ECUADOR_TZ = timezone(timedelta(hours=-5))


# ============================================================================
# SCHEMAS
# ============================================================================

class QRGenerateRequest(BaseModel):
    """Request for generating QR code"""
    class_id: str = Field(..., description="Class session ID")
    period_number: int = Field(default=1, ge=1, description="Period/hour number")
    base_url: str = Field(default="http://localhost:5173", description="Frontend URL")


class CodeVerifyRequest(BaseModel):
    """Request for verifying attendance via rotating code (NO SELFIE)"""
    token: str = Field(..., description="QR token")
    cedula: str = Field(..., description="Student cédula")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


# ============================================================================
# ENDPOINTS - QR Generation (Teacher Side)
# ============================================================================

@router.post(
    "/generate",
    response_model=BaseResponse,
    summary="Generate QR for class",
    description="Generate a QR code with rotating verification code"
)
async def generate_qr(request: QRGenerateRequest):
    """
    Generate QR code for a class period
    
    Returns QR image + current rotating code (6 digits)
    """
    try:
        qr_service = QRService()
        result = await qr_service.generate_qr_for_class(
            class_id=request.class_id,
            period_number=request.period_number,
            base_url=request.base_url
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error generando QR')
            )
        
        return BaseResponse(
            success=True,
            message=f"QR generado para período {request.period_number}",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating QR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/code/{class_id}",
    response_model=BaseResponse,
    summary="Get current rotating code",
    description="Get the current 6-digit verification code for a class"
)
async def get_current_code(class_id: str):
    """
    Get current rotating code for attendance verification
    
    The code changes every 2 minutes
    """
    try:
        code_service = RotatingCodeService()
        code_info = code_service.get_current_code(class_id)
        
        return BaseResponse(
            success=True,
            message="Código actual obtenido",
            data=code_info
        )
        
    except Exception as e:
        logger.error(f"Error getting code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/class/{class_id}/periods",
    response_model=BaseResponse,
    summary="Get class periods",
    description="Get all periods/hours for a class"
)
async def get_class_periods(class_id: str):
    """Get calculated periods for a class"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("class_sessions")\
            .select("*")\
            .eq("class_id", class_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clase {class_id} no encontrada"
            )
        
        class_info = response.data[0]
        start_time = datetime.fromisoformat(class_info['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(class_info['end_time'].replace('Z', '+00:00'))
        
        period_service = ClassPeriodService()
        periods = period_service.calculate_periods(start_time, end_time)
        
        now = datetime.now(ECUADOR_TZ)
        current_period = period_service.get_current_period(start_time, end_time, now)
        
        return BaseResponse(
            success=True,
            message=f"Clase tiene {len(periods)} período(s)",
            data={
                "class_id": class_id,
                "class_name": class_info.get('class_name'),
                "total_periods": len(periods),
                "periods": periods,
                "current_period": current_period,
                "current_time": now.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting periods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# ENDPOINTS - Public Verification (Student Side - No Auth Required)
# ============================================================================

@router.get(
    "/validate/{token}",
    summary="Validate QR token",
    description="Validate a QR token and get class info (public)"
)
async def validate_token(token: str):
    """Validate QR token (public endpoint)"""
    try:
        qr_service = QRService()
        result = await qr_service.validate_token(token)
        
        if not result.get('valid'):
            error_message = result.get('message', 'Token inválido')
            logger.warning(f"Token validation failed: {token} - {error_message}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "message": error_message
                }
            )
        
        # Get current code info
        code_service = RotatingCodeService()
        code_info = code_service.get_current_code(result['class_id'])
        
        return {
            "success": True,
            "valid": True,
            "class_id": result.get('class_id'),
            "period_number": result.get('period_number'),
            "class_name": result.get('class_info', {}).get('class_name', 'N/A') if result.get('class_info') else 'N/A',
            "expires_at": result.get('expires_at'),
            "code_remaining_seconds": code_info["remaining_seconds"]
        }
        
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)}
        )


@router.post(
    "/verify-code",
    summary="Verify attendance via code (NO SELFIE)",
    description="Public endpoint - verify attendance using cédula + 6-digit code"
)
async def verify_attendance_by_code(request: CodeVerifyRequest):
    """
    Verify student attendance via rotating code
    
    NO SELFIE REQUIRED - Just cédula + current 6-digit code
    
    - **token**: QR token from scanned code
    - **cedula**: Student's cédula
    - **code**: Current 6-digit code shown on teacher's screen
    """
    try:
        # 1. Validate token
        qr_service = QRService()
        token_result = await qr_service.validate_token(request.token)
        
        if not token_result.get('valid'):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "message": token_result.get('message', 'Código QR inválido o expirado')
                }
            )
        
        class_id = token_result['class_id']
        period_number = token_result.get('period_number', 1)
        class_info = token_result.get('class_info', {})
        
        # 2. Validate rotating code
        code_service = RotatingCodeService()
        code_result = code_service.validate_code(class_id, request.code)
        
        if not code_result.get('valid'):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "message": "❌ Código incorrecto o expirado. Verifica el código en la pantalla del profesor."
                }
            )
        
        # 3. Find student by cédula
        student_crud = StudentCRUD()
        student = await student_crud.find_by_id(request.cedula)
        
        if not student:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "message": f"❌ No se encontró estudiante con cédula {request.cedula}. ¿Estás registrado en el sistema?"
                }
            )
        
        # 4. Determine attendance status
        now = datetime.now(ECUADOR_TZ)
        start_time = datetime.fromisoformat(class_info['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(class_info['end_time'].replace('Z', '+00:00'))
        
        period_service = ClassPeriodService()
        status_info = period_service.determine_attendance_status(
            start_time, end_time, now
        )
        
        attendance_status = status_info.get('status', 'present')
        actual_period = status_info.get('period_number', 1)
        
        # Get numeric ID for attendance (compatible with frontend queries)
        numeric_class_id = str(class_info.get('id', class_id))
        
        # 5. Check if already registered
        attendance_crud = AttendanceCRUD()
        
        existing = await attendance_crud.check_attendance_exists(
            student_id=request.cedula,
            class_id=numeric_class_id
        )
        
        if existing:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "already_registered": True,
                    "message": f"⚠️ Ya tienes asistencia registrada para esta clase",
                    "student_name": student.get('name'),
                    "status": existing.get('status'),
                    "timestamp": existing.get('timestamp'),
                    "period_number": actual_period
                }
            )
        
        # 6. Mark attendance (using numeric ID for compatibility)
        attendance_record = await attendance_crud.mark_attendance(
            student_id=request.cedula,
            class_id=numeric_class_id,
            status=attendance_status,
            confidence=1.0,  # Code-based verification = 100% confidence
            match_distance=0.0
        )
        
        status_emoji = "✅" if attendance_status == "present" else "⚠️"
        status_text = "Presente" if attendance_status == "present" else "Atrasado"
        
        logger.info(f"Attendance marked via CODE: {request.cedula} in class {numeric_class_id} - {status_text}")
        
        return {
            "success": True,
            "already_registered": False,
            "message": f"{status_emoji} ¡Asistencia registrada! Estado: {status_text}",
            "student_id": request.cedula,
            "student_name": student.get('name'),
            "status": attendance_status,
            "period_number": actual_period,
            "timestamp": attendance_record.get('timestamp'),
            "class_name": class_info.get('class_name', 'N/A') if class_info else 'N/A'
        }
        
    except Exception as e:
        logger.error(f"Error in code verification: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Error en verificación: {str(e)}"
            }
        )


@router.get(
    "/attendance/{class_id}/by-period",
    response_model=BaseResponse,
    summary="Get attendance by period",
    description="Get attendance records grouped by period"
)
async def get_attendance_by_period(class_id: str):
    """Get attendance records grouped by period"""
    try:
        supabase = get_supabase()
        
        class_response = supabase.table("class_sessions")\
            .select("*")\
            .eq("class_id", class_id)\
            .execute()
        
        if not class_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clase {class_id} no encontrada"
            )
        
        class_info = class_response.data[0]
        start_time = datetime.fromisoformat(class_info['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(class_info['end_time'].replace('Z', '+00:00'))
        
        period_service = ClassPeriodService()
        periods = period_service.calculate_periods(start_time, end_time)
        
        result_periods = []
        for period in periods:
            period_class_id = f"{class_id}_P{period['period_number']}"
            
            attendance_response = supabase.table("attendance")\
                .select("*")\
                .eq("class_id", period_class_id)\
                .execute()
            
            records = attendance_response.data if attendance_response.data else []
            
            present_count = len([r for r in records if r['status'] == 'present'])
            late_count = len([r for r in records if r['status'] == 'late'])
            
            result_periods.append({
                **period,
                "attendance_records": records,
                "present_count": present_count,
                "late_count": late_count,
                "total_registered": len(records)
            })
        
        return BaseResponse(
            success=True,
            message=f"Asistencia por período para {class_info.get('class_name')}",
            data={
                "class_id": class_id,
                "class_name": class_info.get('class_name'),
                "periods": result_periods,
                "total_periods": len(periods)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance by period: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
