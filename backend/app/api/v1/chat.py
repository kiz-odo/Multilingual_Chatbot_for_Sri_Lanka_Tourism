"""
Chat and AI API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio

from backend.app.models.user import User
from backend.app.models.conversation import (
    Conversation, ConversationCreate, ConversationResponse, 
    MessageCreate, Message, MessageType, MessageSender
)
from backend.app.core.auth import get_current_active_user
from backend.app.services.chat_service import ChatService
from backend.app.services.hybrid_chat_service import HybridChatService
from backend.app.services.translation_service import TranslationService
from backend.app.services.speech_service import SpeechService

router = APIRouter()


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="Message cannot be empty")
    message_type: MessageType = MessageType.TEXT
    language: Optional[str] = None
    session_id: Optional[str] = None
    
    @field_validator('message')
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """Validate message is not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or contain only whitespace")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    response_type: MessageType = MessageType.TEXT
    confidence: Optional[float] = None
    intent: Optional[str] = None
    entities: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    language: str = "en"
    session_id: str
    conversation_id: str
    metadata: Optional[Dict[str, Any]] = None


class VoiceMessage(BaseModel):
    session_id: Optional[str] = None
    language: Optional[str] = None


class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    supported: bool


class LanguageDetectionRequest(BaseModel):
    text: str = Field(..., description="Text to detect language for")
    message: Optional[str] = Field(None, description="Alternative field name for text")


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    current_user: Optional[User] = Depends(lambda: None)  # Allow anonymous users
):
    """Send a text message to the chatbot"""
    try:
        chat_service = ChatService()
        hybrid_chat_service = HybridChatService()
        translation_service = TranslationService()
        
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Detect language if not provided
        detected_language = chat_message.language
        if not detected_language:
            detected_language = await translation_service.detect_language(chat_message.message)
        
        # Get or create conversation
        conversation = await chat_service.get_or_create_conversation(
            user_id=str(current_user.id) if current_user else None,
            session_id=session_id,
            language=detected_language
        )
        
        # Add user message to conversation
        conversation.add_message(
            sender=MessageSender.USER,
            content=chat_message.message,
            message_type=chat_message.message_type,
            detected_language=detected_language
        )
        
        # Prepare conversation history for hybrid service
        conversation_history = [
            {
                "sender": msg.sender.value if hasattr(msg.sender, 'value') else str(msg.sender),
                "content": msg.content,
                "text": msg.content
            }
            for msg in conversation.messages[-10:]  # Last 10 messages
        ]
        
        # Get response from Hybrid Chat Service (LLM or Rasa)
        hybrid_response = await hybrid_chat_service.get_response(
            message=chat_message.message,
            sender_id=session_id,
            language=detected_language,
            conversation_history=conversation_history
        )
        
        # Process response
        bot_response = hybrid_response.get("text", "I'm sorry, I didn't understand that.")
        
        # Extract intent name properly (handle both string and dict formats)
        intent_data = hybrid_response.get("intent", "unknown")
        if isinstance(intent_data, dict):
            intent = intent_data.get("name", "unknown")
            confidence = intent_data.get("confidence", hybrid_response.get("confidence", 0.0))
        else:
            intent = intent_data if intent_data else "unknown"
            confidence = hybrid_response.get("confidence", 0.0)
        
        entities = hybrid_response.get("entities", [])
        model_used = hybrid_response.get("model", "unknown")
        
        # Add bot response to conversation
        conversation.add_message(
            sender=MessageSender.BOT,
            content=bot_response,
            message_type=MessageType.TEXT,
            intent=intent,
            intent_confidence=confidence,
            entities=entities,
            metadata={"model": model_used}  # Track which model was used
        )
        
        # Save conversation
        await conversation.save()
        
        # Get suggestions based on intent
        suggestions = await chat_service.get_suggestions(intent, detected_language)
        
        return ChatResponse(
            response=bot_response,
            confidence=confidence,
            intent=intent,
            entities=entities,
            suggestions=suggestions,
            language=detected_language,
            session_id=session_id,
            conversation_id=str(conversation.id)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/voice", response_model=ChatResponse)
async def send_voice_message(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = None,
    language: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Send a voice message to the chatbot"""
    try:
        speech_service = SpeechService()
        
        # Read audio file
        audio_content = await audio_file.read()
        
        # Convert speech to text
        text = await speech_service.speech_to_text(audio_content, language)
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not transcribe audio"
            )
        
        # Process as text message
        chat_message = ChatMessage(
            message=text,
            message_type=MessageType.AUDIO,
            language=language,
            session_id=session_id
        )
        
        return await send_message(chat_message, current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing voice message: {str(e)}"
        )


@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """Detect the language of a message"""
    try:
        translation_service = TranslationService()
        
        # Support both 'text' and 'message' field names for backward compatibility
        text_to_detect = request.text or request.message or ""
        if not text_to_detect:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either 'text' or 'message' field is required"
            )
        
        detected_lang, confidence = await translation_service.detect_language_with_confidence(text_to_detect)
        
        from backend.app.core.config import settings
        supported = detected_lang in settings.SUPPORTED_LANGUAGES
        
        return LanguageDetectionResponse(
            detected_language=detected_lang,
            confidence=confidence,
            supported=supported
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting language: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's conversations"""
    try:
        chat_service = ChatService()
        conversations = await chat_service.get_user_conversations(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset
        )
        
        return [ConversationResponse(**conv.dict()) for conv in conversations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific conversation"""
    try:
        chat_service = ChatService()
        conversation = await chat_service.get_conversation(conversation_id, str(current_user.id))
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return ConversationResponse(**conversation.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a conversation"""
    try:
        chat_service = ChatService()
        success = await chat_service.delete_conversation(conversation_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.get("/suggestions")
async def get_suggestions(
    intent: Optional[str] = None,
    language: str = "en"
):
    """Get conversation suggestions"""
    try:
        chat_service = ChatService()
        suggestions = await chat_service.get_suggestions(intent, language)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting suggestions: {str(e)}"
        )


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages"""
    from backend.app.core.config import settings
    
    language_names = {
        "si": "Sinhala (සිංහල)",
        "ta": "Tamil (தமிழ்)",
        "en": "English",
        "de": "German (Deutsch)",
        "fr": "French (Français)",
        "zh": "Chinese (中文)",
        "ja": "Japanese (日本語)"
    }
    
    supported_languages = [
        {
            "code": lang,
            "name": language_names.get(lang, lang),
            "native_name": language_names.get(lang, lang)
        }
        for lang in settings.SUPPORTED_LANGUAGES
    ]
    
    return {
        "supported_languages": supported_languages,
        "default_language": settings.DEFAULT_LANGUAGE
    }


# ============ ADDITIONAL CHAT ENDPOINTS PER ARCHITECTURE ============

@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    chat_message: ChatMessage,
    current_user: Optional[User] = Depends(lambda: None)
):
    """
    Send message to AI chatbot (main endpoint)
    
    Alias for /message endpoint
    """
    return await send_message(chat_message, current_user)


@router.get("/language/detect", response_model=LanguageDetectionResponse)
async def detect_language_get(
    message: str = Query(..., description="Message to detect language for")
):
    """
    Language detection endpoint (GET)
    
    - Detects language of input message
    - Returns detected language and confidence
    """
    request = LanguageDetectionRequest(text=message)
    return await detect_language(request)


@router.get("/history", response_model=List[ConversationResponse])
async def get_chat_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get conversation history
    
    - Returns user's conversation history
    - Alias for /conversations endpoint
    """
    return await get_conversations(limit=limit, offset=offset, current_user=current_user)


@router.delete("/history", status_code=status.HTTP_200_OK)
async def clear_chat_history(
    current_user: User = Depends(get_current_active_user)
):
    """
    Clear conversation history
    
    - Deletes all user's conversations
    """
    try:
        chat_service = ChatService()
        success = await chat_service.delete_all_user_conversations(str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear conversation history"
            )
        
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing conversation history: {str(e)}"
        )


class ChatFeedbackRequest(BaseModel):
    """Chat feedback request"""
    conversation_id: str
    message_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback: Optional[str] = Field(None, max_length=500)
    helpful: Optional[bool] = None


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_chat_feedback(
    feedback_data: ChatFeedbackRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Submit feedback on chat responses
    
    - Allows users to rate and provide feedback on AI responses
    """
    try:
        from backend.app.models.feedback import Feedback, FeedbackCategory, FeedbackType
        
        feedback = Feedback(
            title="Chat Feedback",
            description=feedback_data.feedback or "User feedback on chat response",
            feedback_type=FeedbackType.GENERAL_FEEDBACK,
            user_id=str(current_user.id) if current_user else None,
            category=FeedbackCategory.CHAT,
            rating=feedback_data.rating,
            conversation_id=feedback_data.conversation_id,
            metadata={
                "conversation_id": feedback_data.conversation_id,
                "message_id": feedback_data.message_id,
                "helpful": feedback_data.helpful,
                "comment": feedback_data.feedback
            }
        )
        
        await feedback.save()
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": str(feedback.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


class ConversationContextUpdate(BaseModel):
    """Update conversation context"""
    session_id: str
    context: Dict[str, Any] = Field(..., description="Context data to update")


@router.post("/context", status_code=status.HTTP_200_OK)
async def update_conversation_context(
    context_update: ConversationContextUpdate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update conversation context
    
    - Updates conversation context/metadata
    - Used for maintaining state across conversation
    """
    try:
        chat_service = ChatService()
        
        conversation = await chat_service.get_or_create_conversation(
            user_id=str(current_user.id) if current_user else None,
            session_id=context_update.session_id,
            language="en"
        )
        
        # Update context
        if not conversation.context:
            from backend.app.models.conversation import ConversationContext
            conversation.context = ConversationContext()
        
        # Merge context data
        if conversation.context.metadata:
            conversation.context.metadata.update(context_update.context)
        else:
            conversation.context.metadata = context_update.context
        
        await conversation.save()
        
        return {
            "message": "Context updated successfully",
            "session_id": context_update.session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating context: {str(e)}"
        )


@router.post("/upload-image", response_model=ChatResponse)
async def upload_image_for_chat(
    image_file: UploadFile = File(...),
    message: Optional[str] = None,
    session_id: Optional[str] = None,
    language: Optional[str] = None,
    current_user: Optional[User] = Depends(lambda: None)
):
    """
    Upload image for analysis
    
    - Uploads image for visual analysis
    - Can include optional text message
    - Returns AI response about the image
    """
    try:
        from backend.app.services.landmark_recognition_service import LandmarkRecognitionService
        
        # Read image file
        image_content = await image_file.read()
        
        # Validate file type
        if image_file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format. Supported: JPEG, PNG, GIF"
            )
        
        # Recognize landmark/analyze image
        landmark_service = LandmarkRecognitionService()
        recognition_result = await landmark_service.recognize_landmark(image_content, language or "en")
        
        # Create message from recognition result
        image_message = message or f"I see an image. {recognition_result.get('description', '')}"
        
        # Process as text message
        chat_message = ChatMessage(
            message=image_message,
            message_type=MessageType.IMAGE,
            language=language,
            session_id=session_id
        )
        
        response = await send_message(chat_message, current_user)
        
        # Add image analysis to response
        response.metadata = {
            "image_analysis": recognition_result,
            "image_url": None  # In production, upload to storage and return URL
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )


@router.post("/upload-audio", response_model=ChatResponse)
async def upload_audio_for_chat(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = None,
    language: Optional[str] = None,
    current_user: Optional[User] = Depends(lambda: None)
):
    """
    Upload audio for voice chat
    
    - Uploads audio file for voice chat
    - Converts speech to text
    - Returns AI response
    """
    return await send_voice_message(
        audio_file=audio_file,
        session_id=session_id,
        language=language,
        current_user=current_user
    )