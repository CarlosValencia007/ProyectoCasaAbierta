"""
Smart Classroom AI - Constants
Global constants and enumerations
"""
from enum import Enum


# ---- Emotion Categories ----
class EmotionType(str, Enum):
    """Supported emotion types"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"
    DISGUST = "disgust"
    
    # Custom classroom-specific emotions
    BORED = "bored"          # Mapped from sad/neutral combination
    SLEEPY = "sleepy"        # Mapped from low energy signals
    ATTENTIVE = "attentive"  # Mapped from neutral/positive


# ---- Attendance Status ----
class AttendanceStatus(str, Enum):
    """Attendance record status"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


# ---- Face Recognition Models ----
class FaceRecognitionModel(str, Enum):
    """Supported DeepFace models"""
    VGG_FACE = "VGG-Face"
    FACENET = "Facenet"
    FACENET512 = "Facenet512"
    OPENFACE = "OpenFace"
    DEEPFACE = "DeepFace"
    DEEPID = "DeepID"
    ARCFACE = "ArcFace"
    DLIB = "Dlib"
    SFACE = "SFace"


# ---- Face Detector Backends ----
class FaceDetectorBackend(str, Enum):
    """Supported face detection backends"""
    OPENCV = "opencv"
    SSD = "ssd"
    MTCNN = "mtcnn"
    RETINAFACE = "retinaface"
    MEDIAPIPE = "mediapipe"
    YOLOV8 = "yolov8"


# ---- Distance Metrics ----
class DistanceMetric(str, Enum):
    """Distance metrics for vector comparison"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    EUCLIDEAN_L2 = "euclidean_l2"


# ---- API Response Codes ----
class ResponseCode(str, Enum):
    """Standard API response codes"""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


# ---- HTTP Status Messages ----
HTTP_STATUS_MESSAGES = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    422: "Unprocessable Entity",
    500: "Internal Server Error",
    503: "Service Unavailable"
}


# ---- DeepFace Action Types ----
class DeepFaceAction(str, Enum):
    """DeepFace analysis actions"""
    EMOTION = "emotion"
    AGE = "age"
    GENDER = "gender"
    RACE = "race"


# ---- File Upload Limits ----
MAX_IMAGE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/bmp"}


# ---- Vector Dimensions (FaceNet) ----
FACENET_EMBEDDING_SIZE = 128
FACENET512_EMBEDDING_SIZE = 512


# ---- Classroom Event Types ----
class ClassroomEventType(str, Enum):
    """Types of classroom events"""
    CLASS_START = "class_start"
    CLASS_END = "class_end"
    BREAK_START = "break_start"
    BREAK_END = "break_end"
    EMOTION_DETECTED = "emotion_detected"
    ATTENDANCE_MARKED = "attendance_marked"
