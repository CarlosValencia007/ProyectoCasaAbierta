"""
Smart Classroom AI - Custom Exceptions
Define domain-specific exceptions for better error handling
"""


class SmartClassroomException(Exception):
    """Base exception for Smart Classroom AI"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ---- Face Processing Exceptions ----

class FaceNotDetectedException(SmartClassroomException):
    """Raised when no face is detected in the image"""
    def __init__(self, message: str = "No face detected in the provided image"):
        super().__init__(message, code="FACE_NOT_DETECTED")


class MultipleFacesDetectedException(SmartClassroomException):
    """Raised when multiple faces detected but single expected"""
    def __init__(self, message: str = "Multiple faces detected, expected single face"):
        super().__init__(message, code="MULTIPLE_FACES")


class FaceRecognitionFailedException(SmartClassroomException):
    """Raised when face recognition process fails"""
    def __init__(self, message: str = "Face recognition process failed"):
        super().__init__(message, code="RECOGNITION_FAILED")


# ---- Database Exceptions ----

class StudentNotFoundException(SmartClassroomException):
    """Raised when student not found in database"""
    def __init__(self, student_id: str):
        super().__init__(
            f"Student with ID '{student_id}' not found",
            code="STUDENT_NOT_FOUND"
        )


class DuplicateStudentException(SmartClassroomException):
    """Raised when attempting to enroll duplicate student"""
    def __init__(self, student_id: str):
        super().__init__(
            f"Student with ID '{student_id}' already enrolled",
            code="DUPLICATE_STUDENT"
        )


class DatabaseConnectionException(SmartClassroomException):
    """Raised when database connection fails"""
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message, code="DB_CONNECTION_ERROR")


# ---- Validation Exceptions ----

class InvalidImageException(SmartClassroomException):
    """Raised when image format or content is invalid"""
    def __init__(self, message: str = "Invalid image format or corrupted file"):
        super().__init__(message, code="INVALID_IMAGE")


class ImageTooLargeException(SmartClassroomException):
    """Raised when uploaded image exceeds size limit"""
    def __init__(self, size: int, max_size: int):
        super().__init__(
            f"Image size {size} bytes exceeds maximum {max_size} bytes",
            code="IMAGE_TOO_LARGE"
        )


# ---- API Exceptions ----

class UnauthorizedException(SmartClassroomException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, code="UNAUTHORIZED")


class RateLimitExceededException(SmartClassroomException):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded, try again later"):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED")
