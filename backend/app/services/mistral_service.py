"""
Mistral AI API Service for Tourism Chatbot
Fallback LLM provider with Mistral AI models
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    logging.warning("Mistral AI library not installed. Mistral features will be disabled.")

from backend.app.core.config import settings
from backend.app.services.cache_service import cached

logger = logging.getLogger(__name__)


class MistralService:
    """Mistral AI API service for LLM-powered responses"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        
        if MISTRAL_AVAILABLE and settings.MISTRAL_API_KEY:
            try:
                # Initialize Mistral client
                self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
                self.enabled = True
                logger.info(f"Mistral service initialized successfully with model: {settings.MISTRAL_MODEL}")
                
            except Exception as e:
                logger.error(f"Failed to initialize Mistral service: {e}")
                self.enabled = False
        else:
            if not MISTRAL_AVAILABLE:
                logger.info("Mistral library not available")
            elif not settings.MISTRAL_API_KEY:
                logger.info("Mistral API key not configured")
    
    async def is_available(self) -> bool:
        """Check if Mistral service is available"""
        return self.enabled
    
    @cached(ttl=300, prefix="mistral:response")
    async def get_response(
        self,
        message: str,
        language: str = "en",
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
        tourism_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get response from Mistral API with tourism context
        
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
            raise Exception("Mistral service is not enabled or configured")
        
        try:
            # Build messages for chat completion
            messages = self._build_messages(
                message=message,
                language=language,
                context=context,
                conversation_history=conversation_history,
                tourism_context=tourism_context
            )
            
            # Call Mistral API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.complete(
                    model=settings.MISTRAL_MODEL,
                    messages=messages,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                    top_p=settings.LLM_TOP_P
                )
            )
            
            # Extract response
            if response and response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                
                # Extract sources
                sources = self._extract_sources(response_text, tourism_context)
                
                return {
                    "text": response_text,
                    "intent": "mistral_generated",
                    "confidence": 0.92,  # Mistral responses are high confidence
                    "entities": [],
                    "sources": sources,
                    "model": settings.MISTRAL_MODEL,
                    "provider": "mistral"
                }
            else:
                logger.warning("Empty response from Mistral API")
                return {
                    "text": "I apologize, but I couldn't generate a proper response. Please try rephrasing your question.",
                    "intent": "error",
                    "confidence": 0.5,
                    "entities": [],
                    "sources": [],
                    "model": settings.MISTRAL_MODEL,
                    "provider": "mistral"
                }
                
        except Exception as e:
            logger.error(f"Mistral API error: {e}", exc_info=True)
            raise
    
    def _build_messages(
        self,
        message: str,
        language: str,
        context: Optional[Dict],
        conversation_history: Optional[List[Dict]],
        tourism_context: Optional[str]
    ) -> List[Dict[str, str]]:
        """Build message array for Mistral chat completion"""
        messages = []
        
        # System message
        system_prompt = """You are an expert tourism assistant for Sri Lanka, providing accurate, helpful, and engaging travel information.

Your expertise includes:
- Attractions (beaches, historical sites, wildlife, temples, cultural sites)
- Accommodations (hotels, guesthouses, resorts)
- Transportation (trains, buses, taxis, tuk-tuks)
- Cuisine (restaurants, local dishes, dining experiences)
- Events and festivals
- Safety and emergency information
- Cultural customs and etiquette

Guidelines:
- Provide specific, actionable information
- Be conversational and warm
- Prioritize traveler safety
- Respect cultural sensitivities
- Suggest alternatives when needed
- Keep responses concise (2-4 sentences typically)
- If uncertain, acknowledge limitations honestly
"""
        
        # Add tourism context to system message if available
        if tourism_context:
            system_prompt += f"\n\nRelevant Tourism Information:\n{tourism_context[:2000]}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if conversation_history and len(conversation_history) > 0:
            for msg in conversation_history[-5:]:  # Last 5 messages
                sender = msg.get("sender", "user")
                content = msg.get("content", msg.get("text", ""))
                
                if sender in ["user", "USER"]:
                    messages.append({"role": "user", "content": content})
                else:
                    messages.append({"role": "assistant", "content": content})
        
        # Add user context if available
        context_note = ""
        if context:
            context_parts = []
            if context.get("user_location"):
                context_parts.append(f"Location: {context['user_location']}")
            if context.get("user_preferences"):
                context_parts.append(f"Preferences: {context['user_preferences']}")
            if context.get("travel_dates"):
                context_parts.append(f"Travel dates: {context['travel_dates']}")
            
            if context_parts:
                context_note = "[Traveler context: " + "; ".join(context_parts) + "]\n\n"
        
        # Add current message
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
        
        user_message = f"{context_note}{message}\n\n[Please respond in {lang_name}]"
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _extract_sources(self, response_text: str, tourism_context: Optional[str]) -> List[str]:
        """Extract source snippets mentioned in response"""
        sources = []
        
        if tourism_context:
            keywords = ["Attraction:", "Hotel:", "Restaurant:", "Event:", "Transport:"]
            
            for keyword in keywords:
                if keyword in tourism_context:
                    lines = tourism_context.split("\n")
                    for i, line in enumerate(lines):
                        if keyword in line:
                            snippet = line
                            if i + 1 < len(lines):
                                snippet += " " + lines[i + 1]
                            sources.append(snippet[:200])
                            if len(sources) >= 3:
                                break
                    if len(sources) >= 3:
                        break
        
        return sources


# Singleton instance
mistral_service = None


def get_mistral_service() -> MistralService:
    """Get or create Mistral service singleton"""
    global mistral_service
    if mistral_service is None:
        mistral_service = MistralService()
    return mistral_service




