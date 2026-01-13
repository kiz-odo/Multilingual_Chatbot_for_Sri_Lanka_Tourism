"""
Speech API endpoints for voice interactions
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from backend.app.services.speech_service import SpeechService
from backend.app.core.auth import get_current_user
from backend.app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()
speech_service = SpeechService()


@router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, WEBM, etc.)"),
    language: Optional[str] = Form(None, description="Language code (en, si, ta, etc.)"),
    current_user: User = Depends(get_current_user)
):
    """
    Convert speech audio to text
    
    **Parameters:**
    - **audio**: Audio file upload
    - **language**: Optional language code (defaults to 'en')
    
    **Returns:**
    - Text transcription from audio
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Validate audio
        is_valid = await speech_service.validate_audio_format(audio_data)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid audio format or file too small"
            )
        
        # Convert speech to text
        transcript = await speech_service.speech_to_text(audio_data, language)
        
        if not transcript:
            raise HTTPException(
                status_code=422,
                detail="Could not transcribe audio. Please try again with clearer audio."
            )
        
        logger.info(f"Speech-to-text successful for user {current_user.email}")
        
        return {
            "success": True,
            "text": transcript,
            "language": language or "en",
            "filename": audio.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Speech-to-text processing failed"
        )


@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(..., description="Text to convert to speech"),
    language: str = Form("en", description="Language code (en, si, ta, etc.)"),
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech audio
    
    **Parameters:**
    - **text**: Text to convert
    - **language**: Language code (defaults to 'en')
    
    **Returns:**
    - MP3 audio file
    """
    try:
        # Validate text length
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        if len(text) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Text is too long (maximum 5000 characters)"
            )
        
        # Convert text to speech
        audio_data = await speech_service.text_to_speech(text, language)
        
        if not audio_data:
            raise HTTPException(
                status_code=500,
                detail="Text-to-speech conversion failed"
            )
        
        logger.info(f"Text-to-speech successful for user {current_user.email}")
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=speech_{language}.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Text-to-speech processing failed"
        )


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for speech services
    
    **Returns:**
    - Dictionary of supported language codes and names
    """
    try:
        languages = speech_service.get_supported_languages()
        
        return {
            "success": True,
            "languages": languages
        }
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve supported languages"
        )


@router.post("/analyze-sentiment")
async def analyze_audio_sentiment(
    audio: UploadFile = File(..., description="Audio file to analyze"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment from audio (experimental feature)
    
    **Parameters:**
    - **audio**: Audio file upload
    
    **Returns:**
    - Sentiment analysis results
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Validate audio
        is_valid = await speech_service.validate_audio_format(audio_data)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid audio format"
            )
        
        # Analyze sentiment
        sentiment = await speech_service.analyze_audio_sentiment(audio_data)
        
        return {
            "success": True,
            "sentiment": sentiment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Sentiment analysis failed"
        )
