"""
Smart Classroom AI - Enrollment Service
Business logic for student enrollment with facial biometrics
"""
from typing import Dict, Any
from app.services.face_service import (
    FaceRecognitionService, 
    ImageProcessingService,
    get_face_embedding,  # Nueva función optimizada
    load_image_from_base64
)
from app.services.storage_service import StorageService
from app.db.crud import StudentCRUD
from app.core.logger import logger
from app.core.exceptions import DuplicateStudentException, FaceNotDetectedException


class EnrollmentService:
    """Service for student enrollment"""
    
    def __init__(self):
        self.face_service = FaceRecognitionService()
        self.image_service = ImageProcessingService()
        self.storage_service = StorageService()
        self.student_crud = StudentCRUD()
    
    async def enroll_student(
        self,
        student_id: str,
        name: str,
        image_base64: str,
        email: str = None,
        metadata: Dict[str, Any] = None,
        teacher_id: str = None,
        course_id: str = None
    ) -> Dict[str, Any]:
        """
        Enroll a new student with facial biometric
        
        Args:
            student_id: Unique student identifier
            name: Full name
            image_base64: Base64 encoded face image
            email: Optional email address
            metadata: Optional additional data
        
        Returns:
            Dict with enrollment result
        
        Raises:
            DuplicateStudentException: If student already enrolled
            FaceNotDetectedException: If no face in image
        """
        try:
            logger.info(f"Starting enrollment for student: {student_id}")
            
            # Convert image
            image = self.image_service.base64_to_image(image_base64)
            
            # Validate image
            if not self.image_service.validate_image(image):
                raise FaceNotDetectedException("Image is invalid or too small")
            
            # Upload photo to Supabase Storage
            photo_url = self.storage_service.upload_student_photo(
                student_id=student_id,
                image_base64=image_base64
            )
            
            if not photo_url:
                logger.warning(f"Failed to upload photo for {student_id}, continuing without URL")
            
            # Generate embedding
            embedding = self.face_service.generate_embedding(image)
            
            # Save to database
            student_record = await self.student_crud.create(
                student_id=student_id,
                name=name,
                face_embedding=embedding,
                email=email,
                metadata=metadata,
                photo_url=photo_url,
                teacher_id=teacher_id,
                course_id=course_id
            )
            
            logger.info(f"Student {student_id} enrolled successfully")
            
            return {
                "success": True,
                "message": "Student enrolled successfully",
                "student_id": student_id,
                "name": name,
                "photo_url": photo_url,
                "embedding_dimension": len(embedding),
                "enrolled_at": student_record["enrolled_at"]
            }
        
        except DuplicateStudentException as e:
            logger.warning(f"Duplicate enrollment attempt: {student_id}")
            return {
                "success": False,
                "message": str(e),
                "student_id": student_id
            }
        
        except FaceNotDetectedException as e:
            logger.warning(f"Face not detected for {student_id}")
            return {
                "success": False,
                "message": str(e),
                "student_id": student_id
            }
        
        except Exception as e:
            logger.error(f"Enrollment failed for {student_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Enrollment error: {str(e)}",
                "student_id": student_id
            }
    
    async def update_student_photo(
        self,
        student_id: str,
        image_base64: str
    ) -> Dict[str, Any]:
        """
        Update student's facial biometric
        
        Args:
            student_id: Student identifier
            image_base64: New face image
        
        Returns:
            Dict with update result
        """
        try:
            # Find student
            student = await self.student_crud.find_by_id(student_id)
            if not student:
                return {
                    "success": False,
                    "message": f"Student {student_id} not found"
                }
            
            # Process new image
            image = self.image_service.base64_to_image(image_base64)
            if not self.image_service.validate_image(image):
                raise FaceNotDetectedException("Invalid image")
            
            # Generate new embedding
            new_embedding = self.face_service.generate_embedding(image)
            
            # Update database
            await self.student_crud.update(
                student_id=student_id,
                face_embedding=new_embedding
            )
            
            logger.info(f"Updated photo for student {student_id}")
            
            return {
                "success": True,
                "message": "Photo updated successfully",
                "student_id": student_id
            }
        
        except Exception as e:
            logger.error(f"Failed to update photo for {student_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Update error: {str(e)}"
            }
    
    async def enroll_student_optimized(
        self,
        student_id: str,
        full_name: str,
        image_base64: str
    ) -> Dict[str, Any]:
        """
        Versión optimizada del enrollment usando las nuevas funciones de face_service.
        
        Esta función usa get_face_embedding() directamente, que es más rápida
        porque el modelo ya está pre-cargado en memoria.
        
        Args:
            student_id: ID único del estudiante
            full_name: Nombre completo
            image_base64: Imagen en Base64 (con o sin header)
        
        Returns:
            Dict con resultado del enrollment
        """
        try:
            logger.info(f"📝 Enrollment optimizado para: {full_name} ({student_id})")
            
            # Generar embedding usando la función optimizada
            # Esta función ya maneja la conversión de base64 internamente
            embedding = await get_face_embedding(image_base64)
            
            logger.info(f"✅ Embedding generado: {len(embedding)} dimensiones")
            
            # Guardar en base de datos
            student_record = await self.student_crud.create(
                student_id=student_id,
                name=full_name,
                face_embedding=embedding,
                email=None,
                metadata=None
            )
            
            logger.info(f"✅ Estudiante {student_id} registrado exitosamente")
            
            return {
                "success": True,
                "message": "Estudiante registrado exitosamente",
                "student_id": student_id,
                "name": full_name,
                "embedding_dimension": len(embedding),
                "enrolled_at": student_record.get("enrolled_at", "N/A")
            }
        
        except FaceNotDetectedException as e:
            logger.warning(f"⚠️ No se detectó cara para {student_id}: {str(e)}")
            return {
                "success": False,
                "message": f"No se detectó ningún rostro en la imagen: {str(e)}",
                "student_id": student_id
            }
        
        except DuplicateStudentException as e:
            logger.warning(f"⚠️ ID duplicado: {student_id}")
            return {
                "success": False,
                "message": f"El estudiante {student_id} ya está registrado",
                "student_id": student_id
            }
        
        except Exception as e:
            logger.error(f"❌ Error crítico en enrollment: {str(e)}")
            return {
                "success": False,
                "message": f"Error al registrar estudiante: {str(e)}",
                "student_id": student_id
            }
