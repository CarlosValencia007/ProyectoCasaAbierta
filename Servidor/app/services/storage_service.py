"""
Smart Classroom AI - Storage Service
Handle image uploads to Supabase Storage
"""
import base64
import uuid
from typing import Optional
from io import BytesIO
from PIL import Image
from app.db.supabase_client import get_supabase
from app.core.config import settings
from app.core.logger import logger


class StorageService:
    """Service for managing image uploads to Supabase Storage"""
    
    def __init__(self):
        self.client = get_supabase()
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
    
    def upload_student_photo(
        self,
        student_id: str,
        image_base64: str,
        file_extension: str = "jpg"
    ) -> Optional[str]:
        """
        Upload student photo to Supabase Storage
        
        Args:
            student_id: Student identifier
            image_base64: Base64 encoded image
            file_extension: File extension (jpg, png, etc.)
        
        Returns:
            Public URL of uploaded image or None if failed
        """
        try:
            # Remove data URI prefix if present (e.g., "data:image/png;base64,")
            if "," in image_base64 and image_base64.startswith("data:"):
                image_base64 = image_base64.split(",", 1)[1]
            
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            
            # Generate unique filename
            filename = f"{student_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
            file_path = f"students/{filename}"
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket).upload(
                path=file_path,
                file=image_data,
                file_options={"content-type": f"image/{file_extension}"}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket).get_public_url(file_path)
            
            logger.info(f"✅ Photo uploaded for {student_id}: {public_url}")
            return public_url
        
        except Exception as e:
            logger.error(f"❌ Failed to upload photo for {student_id}: {str(e)}")
            return None
    
    def delete_student_photo(self, photo_url: str) -> bool:
        """
        Delete student photo from storage
        
        Args:
            photo_url: Full URL of the photo
        
        Returns:
            True if deleted successfully
        """
        try:
            # Extract file path from URL
            # URL format: https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}
            path_parts = photo_url.split(f"/{self.bucket}/")
            if len(path_parts) < 2:
                logger.error(f"Invalid photo URL format: {photo_url}")
                return False
            
            file_path = path_parts[1]
            
            # Delete from storage
            self.client.storage.from_(self.bucket).remove([file_path])
            
            logger.info(f"✅ Photo deleted: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete photo: {str(e)}")
            return False
    
    def update_student_photo(
        self,
        student_id: str,
        old_photo_url: Optional[str],
        new_image_base64: str,
        file_extension: str = "jpg"
    ) -> Optional[str]:
        """
        Update student photo (delete old, upload new)
        
        Args:
            student_id: Student identifier
            old_photo_url: URL of existing photo (will be deleted)
            new_image_base64: New base64 encoded image
            file_extension: File extension
        
        Returns:
            Public URL of new image or None if failed
        """
        try:
            # Delete old photo if exists
            if old_photo_url:
                self.delete_student_photo(old_photo_url)
            
            # Upload new photo
            return self.upload_student_photo(student_id, new_image_base64, file_extension)
        
        except Exception as e:
            logger.error(f"❌ Failed to update photo for {student_id}: {str(e)}")
            return None
