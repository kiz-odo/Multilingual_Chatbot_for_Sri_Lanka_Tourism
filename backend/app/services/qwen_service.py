"""
Qwen AI Service for Tourism Chatbot
Alibaba Cloud's Qwen (通义千问) - FREE multilingual LLM
"""

import logging
from typing import Optional, Dict, Any, List
from backend.app.core.config import settings
from backend.app.core.cache_decorator import cached

logger = logging.getLogger(__name__)

# Lazy import for Qwen to avoid startup issues
QWEN_AVAILABLE = False
OpenAI = None  # Qwen uses OpenAI-compatible API

def _load_qwen():
    """Lazy load OpenAI library for Qwen API"""
    global QWEN_AVAILABLE, OpenAI
    if OpenAI is not None:
        return QWEN_AVAILABLE
    try:
        from openai import OpenAI as _OpenAI
        OpenAI = _OpenAI
        QWEN_AVAILABLE = True
    except ImportError as e:
        QWEN_AVAILABLE = False
        logging.warning(f"OpenAI library not available for Qwen: {e}")
    return QWEN_AVAILABLE


# System prompts for tourism context
TOURISM_SYSTEM_PROMPT = """You are a helpful tourism assistant for Sri Lanka. 
Your role is to provide accurate, friendly, and culturally appropriate information about:
- Tourist attractions, hotels, restaurants, and activities
- Sri Lankan culture, history, and traditions
- Travel tips, safety, and practical advice
- Multilingual support (Sinhala, Tamil, English)

Keep responses concise, informative, and tourist-friendly."""


class QwenService:
    """Qwen AI service using OpenAI-compatible API"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        
        # Lazy load Qwen library
        if _load_qwen() and settings.QWEN_API_KEY:
            try:
                # Initialize Qwen client with OpenAI-compatible endpoint
                self.client = OpenAI(
                    api_key=settings.QWEN_API_KEY,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
                self.enabled = True
                logger.info(f"Qwen service initialized successfully with model: {settings.QWEN_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Qwen service: {e}")
                self.enabled = False
        else:
            if not QWEN_AVAILABLE:
                logger.info("OpenAI library not available for Qwen")
            elif not settings.QWEN_API_KEY:
                logger.info("Qwen API key not configured")
    
    async def is_available(self) -> bool:
        """Check if Qwen service is available"""
        return self.enabled
    
    @cached(ttl=300, prefix="qwen:response")
    async def get_response(
        self,
        message: str,
        language: str = "en",
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tourism_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get response from Qwen AI with tourism context
        
        Args:
            message: User's message
            language: Response language (en, si, ta, etc.)
            context: Additional context for the query
            conversation_history: Previous conversation messages
            tourism_context: Tourism-specific context (attractions, hotels, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Dict with response text and metadata
        """
        if not self.enabled:
            raise Exception("Qwen service is not enabled or configured")
        
        # Build messages array
        messages = self._build_messages(
            message=message,
            language=language,
            context=context,
            conversation_history=conversation_history,
            tourism_context=tourism_context
        )
        
        try:
            # Call Qwen API (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=settings.QWEN_MODEL,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                top_p=settings.LLM_TOP_P
            )
            
            # Extract response
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content
                
                return {
                    "text": response_text,
                    "language": language,
                    "intent": "qwen_generated",
                    "confidence": 0.92,  # Qwen responses are high confidence
                    "entities": [],
                    "sources": [],
                    "model": settings.QWEN_MODEL,
                    "provider": "qwen",
                    "metadata": {
                        "tokens_used": response.usage.total_tokens if response.usage else None
                    }
                }
            else:
                logger.warning("Empty response from Qwen API")
                return {
                    "text": "I apologize, but I couldn't generate a response. Please try again.",
                    "language": language,
                    "intent": "error",
                    "confidence": 0.5,
                    "entities": [],
                    "sources": [],
                    "model": settings.QWEN_MODEL,
                    "provider": "qwen"
                }
                
        except Exception as e:
            logger.error(f"Qwen API error: {e}", exc_info=True)
            raise
    
    def _build_messages(
        self,
        message: str,
        language: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tourism_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Build message array for Qwen chat completion"""
        messages = []
        
        # System prompt with tourism context
        system_content = TOURISM_SYSTEM_PROMPT
        
        # Add language instruction
        language_names = {
            "en": "English",
            "si": "Sinhala (සිංහල)",
            "ta": "Tamil (தமிழ்)",
            "de": "German",
            "fr": "French",
            "zh": "Chinese",
            "ja": "Japanese"
        }
        lang_name = language_names.get(language, "English")
        system_content += f"\n\nIMPORTANT: Respond in {lang_name}."
        
        # Add tourism context if provided
        if tourism_context:
            if "attractions" in tourism_context:
                system_content += f"\n\nRelevant Attractions: {tourism_context['attractions']}"
            if "hotels" in tourism_context:
                system_content += f"\nRelevant Hotels: {tourism_context['hotels']}"
            if "restaurants" in tourism_context:
                system_content += f"\nRelevant Restaurants: {tourism_context['restaurants']}"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"] and content:
                    messages.append({
                        "role": role,
                        "content": content
                    })
        
        # Add current message with context
        user_message = message
        if context:
            user_message = f"Context: {context}\n\nQuestion: {message}"
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages


# Singleton instance
qwen_service = None


def get_qwen_service() -> QwenService:
    """Get or create Qwen service singleton"""
    global qwen_service
    if qwen_service is None:
        qwen_service = QwenService()
    return qwen_service
