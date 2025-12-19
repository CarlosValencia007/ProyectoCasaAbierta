"""
Smart Classroom AI - DeepFace Service
Wrapper for facial recognition and emotion analysis using DeepFace
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import io
import base64
from deepface import DeepFace
from app.core.config import settings
from app.core.logger import logger
from app.core.constants import EmotionType, FaceRecognitionModel
from app.core.exceptions import (
    FaceNotDetectedException,
    MultipleFacesDetectedException,
    FaceRecognitionFailedException,
    InvalidImageException
)


class FaceRecognitionService:
    """Service for facial recognition using DeepFace"""
    
    def __init__(self):
        self.model = settings.FACE_RECOGNITION_MODEL
        self.detector = settings.FACE_DETECTOR_BACKEND
        self.distance_metric = settings.DISTANCE_METRIC
        self.logger = logger
    
    def generate_embedding(self, image: np.ndarray) -> List[float]:
        """
        Generate facial embedding from image
        
        Args:
            image: Input image as numpy array (BGR format)
        
        Returns:
            128-dimensional embedding vector (for Facenet)
        
        Raises:
            FaceNotDetectedException: If no face found
            MultipleFacesDetectedException: If multiple faces found
            FaceRecognitionFailedException: If embedding generation fails
        """
        try:
            # Use DeepFace.represent to get embedding
            embeddings = DeepFace.represent(
                img_path=image,
                model_name=self.model,
                detector_backend=self.detector,
                enforce_detection=True,
                align=True
            )
            
            # Check face count
            if not embeddings:
                raise FaceNotDetectedException()
            
            if len(embeddings) > 1 and not settings.ENABLE_MULTI_FACE_DETECTION:
                raise MultipleFacesDetectedException()
            
            # Return first face embedding
            embedding = embeddings[0]["embedding"]
            
            self.logger.debug(f"Generated embedding with dimension: {len(embedding)}")
            return embedding
        
        except FaceNotDetectedException:
            raise
        except MultipleFacesDetectedException:
            raise
        except ValueError as e:
            if "Face could not be detected" in str(e):
                raise FaceNotDetectedException()
            raise FaceRecognitionFailedException(str(e))
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {str(e)}")
            raise FaceRecognitionFailedException(str(e))
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect all faces in image
        
        Args:
            image: Input image as numpy array
        
        Returns:
            List of face detections with bounding boxes
        """
        try:
            faces = DeepFace.extract_faces(
                img_path=image,
                detector_backend=self.detector,
                enforce_detection=False,
                align=True
            )
            
            results = []
            for face in faces:
                results.append({
                    "confidence": face.get("confidence", 0.0),
                    "bounding_box": face.get("facial_area", {}),
                    "face_pixels": face.get("face")
                })
            
            self.logger.info(f"Detected {len(results)} face(s) in image")
            return results
        
        except Exception as e:
            self.logger.error(f"Face detection failed: {str(e)}")
            return []
    
    def compare_faces(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate distance between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Distance score (lower = more similar)
        """
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)
        
        if self.distance_metric == "euclidean":
            distance = np.linalg.norm(arr1 - arr2)
        elif self.distance_metric == "cosine":
            distance = 1 - np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
        else:
            distance = np.linalg.norm(arr1 - arr2)  # Default to euclidean
        
        return float(distance)
    
    def is_match(self, distance: float) -> bool:
        """Check if distance indicates a match"""
        return distance < settings.FACE_MATCH_THRESHOLD
    
    async def batch_generate_embeddings(
        self,
        images: List[np.ndarray]
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple images
        
        Args:
            images: List of input images
        
        Returns:
            List of embeddings (None for failed images)
        """
        embeddings = []
        for idx, image in enumerate(images):
            try:
                embedding = self.generate_embedding(image)
                embeddings.append(embedding)
            except Exception as e:
                self.logger.warning(f"Failed to process image {idx}: {str(e)}")
                embeddings.append(None)
        
        return embeddings


class EmotionAnalysisService:
    """Service for emotion detection using DeepFace"""
    
    def __init__(self):
        self.logger = logger
        self.detector = settings.FACE_DETECTOR_BACKEND
        self.confidence_threshold = settings.EMOTION_CONFIDENCE_THRESHOLD
    
    def analyze_emotion(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze emotions in image
        
        Args:
            image: Input image as numpy array
        
        Returns:
            Dict with dominant emotion and all scores
        """
        try:
            # DeepFace.analyze for emotion detection
            analysis = DeepFace.analyze(
                img_path=image,
                actions=["emotion"],
                detector_backend=self.detector,
                enforce_detection=True,
                silent=True
            )
            
            # Handle single or multiple faces
            if isinstance(analysis, list):
                analysis = analysis[0]
            
            emotions = analysis["emotion"]
            dominant_emotion = analysis["dominant_emotion"]
            
            # Map to our custom emotion types if needed
            mapped_emotion = self._map_emotion(dominant_emotion)
            
            result = {
                "dominant_emotion": mapped_emotion,
                "confidence": emotions[dominant_emotion],
                "all_emotions": emotions
            }
            
            self.logger.debug(f"Detected emotion: {mapped_emotion} ({emotions[dominant_emotion]:.2f}%)")
            return result
        
        except ValueError as e:
            if "Face could not be detected" in str(e):
                raise FaceNotDetectedException()
            raise
        except Exception as e:
            self.logger.error(f"Emotion analysis failed: {str(e)}")
            raise FaceRecognitionFailedException(f"Emotion analysis error: {str(e)}")
    
    def _map_emotion(self, deepface_emotion: str) -> str:
        """
        Map DeepFace emotion to our custom classroom emotions
        
        DeepFace emotions: angry, disgust, fear, happy, sad, surprise, neutral
        Our emotions: happy, sad, angry, fear, surprise, neutral, bored, sleepy, attentive
        """
        emotion_mapping = {
            "happy": EmotionType.HAPPY.value,
            "sad": EmotionType.SAD.value,
            "angry": EmotionType.ANGRY.value,
            "fear": EmotionType.FEAR.value,
            "surprise": EmotionType.SURPRISE.value,
            "neutral": EmotionType.NEUTRAL.value,
            "disgust": EmotionType.DISGUST.value
        }
        
        return emotion_mapping.get(deepface_emotion.lower(), EmotionType.NEUTRAL.value)
    
    async def batch_analyze_emotions(
        self,
        images: List[np.ndarray]
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Analyze emotions for multiple images
        
        Args:
            images: List of input images
        
        Returns:
            List of emotion analysis results
        """
        results = []
        for idx, image in enumerate(images):
            try:
                emotion = self.analyze_emotion(image)
                results.append(emotion)
            except Exception as e:
                self.logger.warning(f"Failed to analyze emotion for image {idx}: {str(e)}")
                results.append(None)
        
        return results


class ImageProcessingService:
    """Utility service for image processing"""
    
    @staticmethod
    def base64_to_image(base64_string: str) -> np.ndarray:
        """
        Convert base64 string to numpy array (OpenCV format)
        
        Args:
            base64_string: Base64 encoded image
        
        Returns:
            Image as numpy array in BGR format
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to numpy array (RGB)
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_array
        
        except Exception as e:
            logger.error(f"Failed to convert base64 to image: {str(e)}")
            raise InvalidImageException(f"Invalid base64 image: {str(e)}")
    
    @staticmethod
    def validate_image(image: np.ndarray) -> bool:
        """Validate image format and size"""
        try:
            if image is None or image.size == 0:
                return False
            
            height, width = image.shape[:2]
            
            # Check minimum size
            if min(height, width) < settings.MIN_FACE_SIZE:
                logger.warning(f"Image too small: {width}x{height}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return False
    
    @staticmethod
    def resize_image(image: np.ndarray, max_dimension: int = 1024) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        if max(height, width) <= max_dimension:
            return image
        
        if height > width:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        else:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized
