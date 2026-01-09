"""
Google Gemini API Service for Tourism Chatbot
Provides natural language understanding and generation using Google's Gemini Pro model
Uses the new google-genai SDK (replacing deprecated google-generativeai)
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google GenAI library not installed. Gemini features will be disabled.")

from backend.app.core.config import settings
from backend.app.services.cache_service import cached

logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini API service for LLM-powered responses"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.chat_session = None
        
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                # Configure Gemini API with new SDK
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                # Store generation config
                self.generation_config = types.GenerateContentConfig(
                    temperature=settings.LLM_TEMPERATURE,
                    top_p=settings.LLM_TOP_P,
                    top_k=40,
                    max_output_tokens=settings.LLM_MAX_TOKENS,
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_MEDIUM_AND_ABOVE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE"
                        ),
                    ]
                )
                
                self.enabled = True
                logger.info(f"Gemini service initialized successfully with model: {settings.GEMINI_MODEL}")
                
            except Exception as e:
                logger.error(f"Failed to initialize Gemini service: {e}")
                self.enabled = False
        else:
            if not GEMINI_AVAILABLE:
                logger.info("Gemini library not available")
            elif not settings.GEMINI_API_KEY:
                logger.info("Gemini API key not configured")
    
    async def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.enabled
    
    @cached(ttl=300, prefix="gemini:response")
    async def get_response(
        self,
        message: str,
        language: str = "en",
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
        tourism_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get response from Gemini API with tourism context
        
        Args:
            message: User message
            language: Response language
            context: Additional context (user location, preferences)
            conversation_history: Previous conversation messages
            tourism_context: Retrieved tourism information for RAG
        
        Returns:
            Response dictionary with text, confidence, model info
        """
        if not self.enabled:
            raise Exception("Gemini service is not enabled or configured")
        
        try:
            # Build prompt with tourism context
            prompt = self._build_prompt(
                message=message,
                language=language,
                context=context,
                conversation_history=conversation_history,
                tourism_context=tourism_context
            )
            
            # Generate response using new SDK
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=self.generation_config
                )
            )
            
            # Extract response text
            if response and response.text:
                response_text = response.text.strip()
                
                # Extract any sources mentioned
                sources = self._extract_sources(response_text, tourism_context)
                
                return {
                    "text": response_text,
                    "intent": "gemini_generated",
                    "confidence": 0.95,  # Gemini responses are generally high confidence
                    "entities": [],
                    "sources": sources,
                    "model": f"gemini-{settings.GEMINI_MODEL}",
                    "provider": "google"
                }
            else:
                logger.warning("Empty response from Gemini API")
                return {
                    "text": "I apologize, but I couldn't generate a proper response. Please try rephrasing your question.",
                    "intent": "error",
                    "confidence": 0.5,
                    "entities": [],
                    "sources": [],
                    "model": f"gemini-{settings.GEMINI_MODEL}",
                    "provider": "google"
                }
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise
    
    async def get_response_with_images(
        self,
        message: str,
        images: List[bytes],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get response from Gemini with image understanding (Gemini Pro Vision)
        
        Args:
            message: User message/question about images
            images: List of image bytes
            language: Response language
        
        Returns:
            Response dictionary
        """
        if not self.enabled:
            raise Exception("Gemini service is not enabled or configured")
        
        try:
            # Use Gemini model with vision capability for image understanding
            # Prepare content parts
            content_parts = [message]
            
            # Add images (Gemini can handle multiple images)
            for image_bytes in images[:5]:  # Limit to 5 images
                content_parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
            
            # Generate response using new SDK
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model="gemini-2.0-flash",  # Use flash model for vision
                    contents=content_parts,
                    config=self.generation_config
                )
            )
            
            if response and response.text:
                return {
                    "text": response.text.strip(),
                    "intent": "gemini_vision",
                    "confidence": 0.95,
                    "entities": [],
                    "sources": [],
                    "model": "gemini-2.0-flash",
                    "provider": "google"
                }
            else:
                logger.warning("Empty response from Gemini Vision API")
                return {
                    "text": "I couldn't analyze the image. Please try again.",
                    "intent": "error",
                    "confidence": 0.5,
                    "entities": [],
                    "sources": [],
                    "model": "gemini-2.0-flash",
                    "provider": "google"
                }
                
        except Exception as e:
            logger.error(f"Gemini Vision API error: {e}", exc_info=True)
            raise
    
    def _build_prompt(
        self,
        message: str,
        language: str,
        context: Optional[Dict],
        conversation_history: Optional[List[Dict]],
        tourism_context: Optional[str]
    ) -> str:
        """Build comprehensive prompt for Gemini"""
        prompt_parts = []
        
        # System instruction
        prompt_parts.append("""You are a helpful, knowledgeable, and friendly tourism assistant for Sri Lanka.
Your role is to provide accurate, engaging, and informative responses about Sri Lankan tourism.

Guidelines:
- Provide specific, actionable information when possible
- Be conversational and warm in tone
- If you don't know something, be honest about it
- Prioritize traveler safety and well-being
- Respect cultural sensitivities
- Suggest alternatives when appropriate
- Keep responses concise but informative (2-4 sentences)
""")
        
        # Add tourism context (RAG)
        if tourism_context:
            prompt_parts.append("\n--- Tourism Information ---")
            prompt_parts.append(tourism_context)
            prompt_parts.append("--- End of Tourism Information ---\n")
        
        # Add conversation history
        if conversation_history and len(conversation_history) > 0:
            prompt_parts.append("\n--- Conversation History ---")
            for msg in conversation_history[-5:]:  # Last 5 messages
                sender = msg.get("sender", "user")
                content = msg.get("content", msg.get("text", ""))
                role = "Traveler" if sender in ["user", "USER"] else "Assistant"
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("--- End of Conversation History ---\n")
        
        # Add user context
        if context:
            context_info = []
            if context.get("user_location"):
                context_info.append(f"Traveler's location: {context['user_location']}")
            if context.get("user_preferences"):
                context_info.append(f"Preferences: {context['user_preferences']}")
            if context.get("travel_dates"):
                context_info.append(f"Travel dates: {context['travel_dates']}")
            
            if context_info:
                prompt_parts.append("\n--- Traveler Context ---")
                prompt_parts.extend(context_info)
                prompt_parts.append("--- End of Traveler Context ---\n")
        
        # Add current message
        prompt_parts.append(f"\nTraveler's Question: {message}")
        
        # Language instruction
        language_map = {
            "en": "English",
            "si": "Sinhala (සිංහල)",
            "ta": "Tamil (தமிழ்)",
            "de": "German",
            "fr": "French",
            "zh": "Chinese",
            "ja": "Japanese"
        }
        lang_name = language_map.get(language, "English")
        prompt_parts.append(f"\nPlease respond in {lang_name}. Be helpful, informative, and conversational.")
        
        return "\n".join(prompt_parts)
    
    def _extract_sources(self, response_text: str, tourism_context: Optional[str]) -> List[str]:
        """Extract source snippets mentioned in response"""
        sources = []
        
        if tourism_context:
            # Basic extraction - look for place names, hotels, etc.
            # This is a simple implementation; could be enhanced
            keywords = ["Attraction:", "Hotel:", "Restaurant:", "Event:", "Transport:"]
            
            for keyword in keywords:
                if keyword in tourism_context:
                    # Extract snippets
                    lines = tourism_context.split("\n")
                    for i, line in enumerate(lines):
                        if keyword in line and i < len(lines) - 1:
                            snippet = line + " " + lines[i+1] if i+1 < len(lines) else line
                            sources.append(snippet[:200])  # Limit length
                            if len(sources) >= 3:  # Max 3 sources
                                break
                    if len(sources) >= 3:
                        break
        
        return sources
    
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            if self.client:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.client.models.count_tokens(
                        model=settings.GEMINI_MODEL,
                        contents=text
                    )
                )
                return result.total_tokens
            return 0
        except Exception as e:
            logger.warning(f"Error counting tokens: {e}")
            return int(len(text.split()) * 1.3)  # Rough estimate


# Singleton instance
gemini_service = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiService()
    return gemini_service
