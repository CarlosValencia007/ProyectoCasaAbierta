"""
Smart Classroom AI - QR Code & Rotating Code Service
Generates QR codes and rotating verification codes for attendance
"""
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import base64
import io
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from app.core.logger import logger
from app.db.supabase_client import get_supabase

# Ecuador timezone (UTC-5)
ECUADOR_TZ = timezone(timedelta(hours=-5))

# Code rotation interval (in minutes)
CODE_ROTATION_MINUTES = 2


class RotatingCodeService:
    """Service for generating rotating verification codes"""
    
    def __init__(self):
        self.client = get_supabase()
    
    def _generate_code(self, class_id: str, time_slot: int) -> str:
        """
        Generate a deterministic 6-digit code based on class_id and time slot
        This ensures the same code is generated for the same time window
        """
        # Use a secret key + class_id + time_slot to generate code
        secret_key = "smart_classroom_2026"  # In production, use environment variable
        data = f"{secret_key}:{class_id}:{time_slot}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        # Take first 6 digits from hash (converted to numbers)
        code = str(int(hash_value[:8], 16) % 1000000).zfill(6)
        return code
    
    def _get_current_time_slot(self) -> int:
        """Get current time slot (changes every CODE_ROTATION_MINUTES)"""
        now = datetime.now(ECUADOR_TZ)
        # Calculate time slot: minutes since epoch / rotation interval
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        minutes_since_epoch = int((now - epoch).total_seconds() / 60)
        return minutes_since_epoch // CODE_ROTATION_MINUTES
    
    def get_current_code(self, class_id: str) -> Dict[str, Any]:
        """
        Get the current valid code for a class
        
        Returns:
            Dict with code, valid_until, and remaining seconds
        """
        now = datetime.now(ECUADOR_TZ)
        time_slot = self._get_current_time_slot()
        code = self._generate_code(class_id, time_slot)
        
        # Calculate when this code expires
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        next_slot_minutes = (time_slot + 1) * CODE_ROTATION_MINUTES
        valid_until = epoch + timedelta(minutes=next_slot_minutes)
        valid_until = valid_until.astimezone(ECUADOR_TZ)
        
        remaining_seconds = int((valid_until - now).total_seconds())
        
        return {
            "code": code,
            "valid_until": valid_until.isoformat(),
            "remaining_seconds": max(0, remaining_seconds),
            "rotation_minutes": CODE_ROTATION_MINUTES
        }
    
    def validate_code(self, class_id: str, submitted_code: str) -> Dict[str, Any]:
        """
        Validate a submitted code
        
        Accepts current code OR the previous code (for grace period)
        """
        time_slot = self._get_current_time_slot()
        
        # Current code
        current_code = self._generate_code(class_id, time_slot)
        
        # Previous code (grace period)
        previous_code = self._generate_code(class_id, time_slot - 1)
        
        if submitted_code == current_code:
            return {"valid": True, "message": "Código válido"}
        elif submitted_code == previous_code:
            return {"valid": True, "message": "Código válido (período de gracia)"}
        else:
            return {"valid": False, "message": "Código inválido o expirado"}


class QRService:
    """Service for QR code generation and token management"""
    
    def __init__(self):
        self.client = get_supabase()
        self.code_service = RotatingCodeService()
    
    def _generate_token(self, class_id: str, period_number: int) -> str:
        """Generate a unique token for a class period"""
        random_bytes = secrets.token_bytes(16)
        timestamp = datetime.now(ECUADOR_TZ).isoformat()
        data = f"{class_id}:{period_number}:{timestamp}:{random_bytes.hex()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    async def generate_qr_for_class(
        self,
        class_id: str,
        period_number: int = 1,
        base_url: str = "http://localhost:5173"
    ) -> Dict[str, Any]:
        """
        Generate QR code for a class session/period
        """
        try:
            # Get class info
            class_info = await self._get_class_info(class_id)
            if not class_info:
                return {
                    "success": False,
                    "message": f"Clase {class_id} no encontrada"
                }
            
            # Generate unique token
            token = self._generate_token(class_id, period_number)
            
            # Get current rotating code
            code_info = self.code_service.get_current_code(class_id)
            
            # Calculate expiry time (24 hours for testing, or class end time, whichever is later)
            end_time = datetime.fromisoformat(class_info['end_time'].replace('Z', '+00:00'))
            now = datetime.now(ECUADOR_TZ)
            expires_at = max(end_time, now + timedelta(hours=24))  # At least 24 hours validity
            
            # Store token
            await self._store_token(
                token=token,
                class_id=class_id,
                period_number=period_number,
                expires_at=expires_at
            )
            
            # Generate QR code URL (simplified - just needs token)
            qr_url = f"{base_url}/verificar-asistencia?token={token}"
            
            # Generate QR image
            qr_image_base64 = self._generate_qr_image(qr_url)
            
            logger.info(f"QR generated for class {class_id}, period {period_number}")
            
            return {
                "success": True,
                "token": token,
                "class_id": class_id,
                "period_number": period_number,
                "qr_url": qr_url,
                "attendance_url": qr_url,  # Alias for frontend compatibility
                "qr_image": qr_image_base64,
                "expires_at": end_time.isoformat(),
                "class_name": class_info.get('class_name', 'N/A'),
                # Rotating code info
                "current_code": code_info["code"],
                "code_valid_until": code_info["valid_until"],
                "code_remaining_seconds": code_info["remaining_seconds"]
            }
            
        except Exception as e:
            logger.error(f"Error generating QR: {str(e)}")
            return {
                "success": False,
                "message": f"Error generando QR: {str(e)}"
            }
    
    def _generate_qr_image(self, data: str) -> str:
        """Generate QR code image as base64"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    
    async def _get_class_info(self, class_id: str) -> Optional[Dict[str, Any]]:
        """Get class session info"""
        try:
            response = self.client.table("class_sessions")\
                .select("*")\
                .eq("class_id", class_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting class info: {str(e)}")
            return None
    
    async def _store_token(
        self,
        token: str,
        class_id: str,
        period_number: int,
        expires_at: datetime
    ) -> bool:
        """Store QR token in database"""
        try:
            data = {
                "token": token,
                "class_id": class_id,
                "period_number": period_number,
                "expires_at": expires_at.isoformat(),
                "is_active": True,
                "created_at": datetime.now(ECUADOR_TZ).isoformat()
            }
            
            self.client.table("qr_tokens").upsert(
                data,
                on_conflict="token"
            ).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error storing token: {str(e)}")
            return False
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a QR token"""
        try:
            response = self.client.table("qr_tokens")\
                .select("*")\
                .eq("token", token)\
                .eq("is_active", True)\
                .execute()
            
            if not response.data:
                return {
                    "valid": False,
                    "message": "Token inválido o expirado"
                }
            
            token_data = response.data[0]
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
            now = datetime.now(ECUADOR_TZ)
            
            if now > expires_at:
                return {
                    "valid": False,
                    "message": "El código QR ha expirado"
                }
            
            # Get class info
            class_info = await self._get_class_info(token_data['class_id'])
            
            return {
                "valid": True,
                "class_id": token_data['class_id'],
                "period_number": token_data['period_number'],
                "class_info": class_info,
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return {
                "valid": False,
                "message": f"Error validando token: {str(e)}"
            }


class ClassPeriodService:
    """Service for managing class periods/hours"""
    
    def __init__(self):
        self.client = get_supabase()
    
    def calculate_periods(
        self,
        start_time: datetime,
        end_time: datetime,
        period_duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Calculate class periods based on start/end time"""
        periods = []
        current_start = start_time
        period_number = 1
        
        while current_start < end_time:
            period_end = min(
                current_start + timedelta(minutes=period_duration_minutes),
                end_time
            )
            
            late_threshold = current_start + timedelta(minutes=15)
            
            periods.append({
                "period_number": period_number,
                "start_time": current_start.isoformat(),
                "end_time": period_end.isoformat(),
                "late_threshold": late_threshold.isoformat(),
                "duration_minutes": (period_end - current_start).total_seconds() / 60
            })
            
            current_start = period_end
            period_number += 1
        
        return periods
    
    def get_current_period(
        self,
        start_time: datetime,
        end_time: datetime,
        current_time: Optional[datetime] = None,
        period_duration_minutes: int = 60
    ) -> Optional[Dict[str, Any]]:
        """Get the current period based on current time"""
        if current_time is None:
            current_time = datetime.now(ECUADOR_TZ)
        
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=ECUADOR_TZ)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=ECUADOR_TZ)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=ECUADOR_TZ)
        
        if current_time < start_time or current_time >= end_time:
            return None
        
        periods = self.calculate_periods(start_time, end_time, period_duration_minutes)
        
        for period in periods:
            period_start = datetime.fromisoformat(period['start_time'])
            period_end = datetime.fromisoformat(period['end_time'])
            
            if period_start <= current_time < period_end:
                late_threshold = datetime.fromisoformat(period['late_threshold'])
                
                if current_time <= late_threshold:
                    period['status_if_now'] = 'present'
                else:
                    period['status_if_now'] = 'late'
                
                return period
        
        return None
    
    def determine_attendance_status(
        self,
        class_start_time: datetime,
        class_end_time: datetime,
        attendance_time: datetime,
        period_duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """Determine attendance status for a given time"""
        current_period = self.get_current_period(
            class_start_time,
            class_end_time,
            attendance_time,
            period_duration_minutes
        )
        
        if current_period is None:
            return {
                "period_number": None,
                "status": "absent",
                "message": "Fuera del horario de clase"
            }
        
        return {
            "period_number": current_period['period_number'],
            "status": current_period['status_if_now'],
            "period_start": current_period['start_time'],
            "period_end": current_period['end_time']
        }
