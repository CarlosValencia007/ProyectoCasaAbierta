"""
Smart Classroom AI - Emotion Analysis API Router
Endpoints for emotion detection and classroom engagement analysis
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.core.schemas import BaseResponse
from app.services.face_service import EmotionAnalysisService, ImageProcessingService
from app.db.crud import EmotionEventCRUD
from app.core.logger import logger

router = APIRouter(prefix="/emotions", tags=["Emotion Analysis"])
emotion_service = EmotionAnalysisService()
image_service = ImageProcessingService()
emotion_crud = EmotionEventCRUD()


@router.post(
    "/analyze",
    response_model=BaseResponse,
    summary="Analyze emotion",
    description="Detect emotion from a single face image"
)
async def analyze_emotion(image_base64: str, student_id: Optional[str] = None, class_id: Optional[str] = None):
    """
    Analyze emotion from face image
    
    - **image_base64**: Base64 encoded face image
    - **student_id**: Optional student identifier
    - **class_id**: Optional class session identifier
    """
    try:
        # Convert image
        image = image_service.base64_to_image(image_base64)
        
        # Validate
        if not image_service.validate_image(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image"
            )
        
        # Analyze emotion
        emotion_result = emotion_service.analyze_emotion(image)
        
        # Save to database if student and class provided
        if student_id and class_id:
            await emotion_crud.record_emotion(
                student_id=student_id,
                class_id=class_id,
                dominant_emotion=emotion_result["dominant_emotion"],
                confidence=emotion_result["confidence"],
                emotion_scores=emotion_result["all_emotions"]
            )
        
        return BaseResponse(
            success=True,
            message="Emotion analyzed successfully",
            data=emotion_result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emotion analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/batch-analyze",
    response_model=BaseResponse,
    summary="Batch analyze emotions",
    description="Analyze emotions from multiple images"
)
async def batch_analyze_emotions(images_base64: List[str], class_id: str):
    """
    Batch emotion analysis for classroom monitoring
    
    - **images_base64**: List of base64 encoded images
    - **class_id**: Class session identifier
    """
    try:
        if not images_base64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No images provided"
            )
        
        # Convert images
        images = [image_service.base64_to_image(img) for img in images_base64]
        
        # Analyze emotions
        results = await emotion_service.batch_analyze_emotions(images)
        
        # Calculate statistics
        successful = [r for r in results if r is not None]
        emotion_counts = {}
        for result in successful:
            emotion = result["dominant_emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return BaseResponse(
            success=True,
            message=f"Analyzed {len(successful)}/{len(images_base64)} images",
            data={
                "class_id": class_id,
                "total_analyzed": len(successful),
                "emotion_distribution": emotion_counts,
                "results": results
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch emotion analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/class-summary/{class_id}",
    response_model=BaseResponse,
    summary="Get class emotion summary",
    description="Get emotion distribution and engagement metrics for a class"
)
async def get_class_emotion_summary(
    class_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """
    Get emotion summary for a class session
    
    - **class_id**: Class session identifier
    - **start_time**: Optional start time filter
    - **end_time**: Optional end time filter
    """
    try:
        # Get emotion events
        emotions = await emotion_crud.get_class_emotions(
            class_id=class_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not emotions:
            return BaseResponse(
                success=True,
                message="No emotion data found",
                data={"class_id": class_id, "total_events": 0}
            )
        
        # Calculate statistics
        emotion_counts = {}
        total_confidence = 0.0
        
        for event in emotions:
            emotion = event["dominant_emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_confidence += event["confidence"]
        
        # Calculate percentages
        total_events = len(emotions)
        emotion_percentages = {
            emotion: (count / total_events) * 100
            for emotion, count in emotion_counts.items()
        }
        
        # Calculate engagement score (simplified)
        positive_emotions = ["happy", "surprise", "attentive", "neutral"]
        negative_emotions = ["sad", "bored", "sleepy", "angry"]
        
        positive_count = sum(emotion_counts.get(e, 0) for e in positive_emotions)
        negative_count = sum(emotion_counts.get(e, 0) for e in negative_emotions)
        
        engagement_score = (positive_count / total_events) * 100 if total_events > 0 else 0
        
        return BaseResponse(
            success=True,
            message="Emotion summary generated",
            data={
                "class_id": class_id,
                "total_events": total_events,
                "emotion_distribution": emotion_counts,
                "emotion_percentages": emotion_percentages,
                "engagement_score": round(engagement_score, 2),
                "average_confidence": round(total_confidence / total_events, 2),
                "dominant_emotion": max(emotion_counts.items(), key=lambda x: x[1])[0]
            }
        )
    
    except Exception as e:
        logger.error(f"Class emotion summary error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/student-timeline/{student_id}",
    response_model=BaseResponse,
    summary="Get student emotion timeline",
    description="Get emotion timeline for a specific student in a class"
)
async def get_student_emotion_timeline(
    student_id: str,
    class_id: str,
    limit: int = 100
):
    """
    Get emotion timeline for a student during a class
    
    - **student_id**: Student identifier
    - **class_id**: Class session identifier
    - **limit**: Maximum number of events
    """
    try:
        from app.db.supabase_client import get_supabase
        
        client = get_supabase()
        response = client.table("emotion_events")\
            .select("*")\
            .eq("student_id", student_id)\
            .eq("class_id", class_id)\
            .order("detected_at", desc=False)\
            .limit(limit)\
            .execute()
        
        return BaseResponse(
            success=True,
            message=f"Found {len(response.data)} emotion events",
            data={
                "student_id": student_id,
                "class_id": class_id,
                "timeline": response.data
            }
        )
    
    except Exception as e:
        logger.error(f"Student emotion timeline error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
