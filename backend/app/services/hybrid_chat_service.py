"""
Hybrid Chat Service - Intelligent routing between Rasa (NLU) and LLM APIs
Architecture: Rasa for structured intents + Gemini for complex queries
"""

from typing import Dict, Any, Optional, List
import logging

from backend.app.services.llm_service import get_llm_service
from backend.app.services.rasa_service import RasaService
from backend.app.services.tavily_search_service import get_tavily_search_service
from backend.app.services.crewai_service import get_crewai_service
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class HybridChatService:
    """
    Intelligent routing between Rasa NLU and LLM APIs
    
    Architecture:
    1. Rasa: Handles structured intents (bookings, specific queries, etc.)
    2. Gemini: Handles complex, open-ended questions
    3. RAG: Provides tourism context to LLMs
    """
    
    def __init__(self):
        self.llm_service = get_llm_service()
        self.rasa_service = RasaService()
        self.tavily_search_service = get_tavily_search_service()
        self.crewai_service = get_crewai_service()
        
        # CrewAI configuration
        self.USE_CREWAI = getattr(settings, 'USE_CREWAI', False)
        
        # Define structured intents that Rasa handles well
        self.STRUCTURED_INTENTS = [
            "ask_attractions_by_category",
            "ask_attraction_details",
            "ask_restaurants",
            "ask_restaurant_details",
            "ask_hotels",
            "ask_hotel_details",
            "ask_transport",
            "ask_transport_details",
            "ask_events",
            "ask_event_details",
            "ask_emergency",
            "ask_currency",
            "ask_weather",
            "change_language",
            "affirm",
            "deny",
            "goodbye",
            "greet",
            "thank",
            "bot_challenge",
            "book_hotel",
            "book_restaurant",
            "book_transport"
        ]
        
        # Confidence thresholds for Rasa (matching architecture spec)
        self.RASA_HIGH_CONFIDENCE_THRESHOLD = 0.7  # Updated from 0.85
        self.RASA_MEDIUM_CONFIDENCE_THRESHOLD = 0.4  # Updated from 0.6
        self.RASA_LOW_CONFIDENCE_THRESHOLD = 0.4  # Below this triggers Google Search fallback
        
        logger.info("Hybrid Chat Service initialized with Rasa + LLM + Google Search architecture")
    
    async def get_response(
        self,
        message: str,
        sender_id: str,
        language: str = "en",
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Route to Rasa, LLM, or Google Search based on query complexity and Rasa NLU confidence
        
        Decision Flow (matching architecture spec):
        1. Language Detection (automatic)
        2. Rasa NLU Intent Classification
        3. Confidence Check:
           - High (>0.7): Rasa response + optional LLM enhancement
           - Medium (0.4-0.7): LLM reasoning
           - Low (<0.4): LLM + Google Search fallback
        4. Response Generation (multilingual)
        5. Return to User
        
        Args:
            message: User message
            sender_id: Unique sender identifier
            language: Response language
            conversation_history: Previous conversation messages
        
        Returns:
            Response dictionary with text, intent, confidence, entities, etc.
        """
        try:
            # Step 0: Check if query is complex enough for CrewAI multi-agent processing
            is_complex_query = self._is_complex_query(message)
            
            # Step 0.5: Use CrewAI for complex queries if enabled
            if self.USE_CREWAI and is_complex_query and await self.crewai_service.is_available():
                logger.info("Routing to CrewAI for complex multi-agent processing")
                try:
                    crewai_response = await self.crewai_service.process_query(
                        query=message,
                        language=language,
                        context=self._prepare_llm_context([]),
                        agent_type=None  # Auto-select agents
                    )
                    # Add Rasa intent info if available
                    try:
                        rasa_nlu_result = await self.rasa_service.parse_message(message, language)
                        intent = rasa_nlu_result.get("intent", {}).get("name", "unknown")
                        confidence = rasa_nlu_result.get("intent", {}).get("confidence", 0.0)
                        crewai_response["rasa_intent"] = intent
                        crewai_response["rasa_confidence"] = confidence
                    except:
                        pass
                    return crewai_response
                except Exception as e:
                    logger.warning(f"CrewAI processing failed: {e}, falling back to standard routing")
                    # Continue with normal routing
            
            # Step 1: Get intent and confidence from Rasa NLU
            rasa_nlu_result = await self.rasa_service.parse_message(message, language)
            intent = rasa_nlu_result.get("intent", {}).get("name", "unknown")
            confidence = rasa_nlu_result.get("intent", {}).get("confidence", 0.0)
            entities = rasa_nlu_result.get("entities", [])
            
            logger.info(f"Rasa NLU: intent={intent}, confidence={confidence:.2f}")
            
            # Step 2: Decide routing
            use_rasa = self._should_use_rasa(intent, confidence, message)
            
            # Step 3A: Route to Rasa for structured intents
            if use_rasa:
                logger.info(f"Routing to Rasa for structured intent: {intent} (confidence: {confidence:.2f})")
                
                try:
                    rasa_response = await self.rasa_service.get_response(
                        message=message,
                        sender_id=sender_id,
                        language=language
                    )
                    
                    intent_name = intent.get('name') if isinstance(intent, dict) else intent
                    return self._format_rasa_response(rasa_response, intent_name, confidence, entities)
                    
                except Exception as e:
                    logger.error(f"Rasa service error: {e}, falling back to LLM")
                    # Fallback to LLM if Rasa fails
                    use_rasa = False
            
            # Step 3B: Route to LLM for complex queries or medium confidence
            if not use_rasa:
                # Check confidence level for routing decision
                is_low_confidence = confidence < self.RASA_LOW_CONFIDENCE_THRESHOLD
                
                # Check if LLM is available
                await self.llm_service.ensure_initialized()
                
                if self.llm_service.enabled:
                    logger.info(f"Routing to LLM for query (Rasa confidence: {confidence:.2f}, low_confidence: {is_low_confidence})")
                    
                    try:
                        # Prepare context for LLM
                        context = self._prepare_llm_context(entities)
                        
                        # Get response from LLM (will use Gemini → Qwen → Mistral fallback chain)
                        llm_response = await self.llm_service.get_response(
                            message=message,
                            language=language,
                            context=context,
                            conversation_history=conversation_history
                        )
                        
                        # Step 3C: If low confidence (<0.4), add Tavily Search fallback
                        if is_low_confidence and await self.tavily_search_service.is_available():
                            logger.info(f"Low confidence ({confidence:.2f}), adding Tavily Search fallback")
                            try:
                                search_response = await self.tavily_search_service.get_fallback_response(
                                    query=message,
                                    language=language
                                )
                                
                                # Enhance LLM response with search results
                                if search_response.get("sources"):
                                    llm_response["text"] += f"\n\n[Additional sources: {', '.join(search_response['sources'][:2])}]"
                                    llm_response["sources"] = search_response.get("sources", [])
                                    llm_response["search_enabled"] = True
                            except Exception as search_error:
                                logger.warning(f"Tavily Search fallback failed: {search_error}")
                        
                        # Add Rasa intent info to LLM response
                        # Extract intent name if it's a dict
                        intent_name = intent.get('name') if isinstance(intent, dict) else intent
                        llm_response["rasa_intent"] = intent_name
                        llm_response["rasa_confidence"] = confidence
                        llm_response["rasa_entities"] = entities
                        
                        return llm_response
                        
                    except Exception as e:
                        logger.error(f"LLM service error: {e}, trying Tavily Search fallback")
                        
                        # Step 4: Try Tavily Search as fallback when all LLMs fail
                        try:
                            if await self.tavily_search_service.is_available():
                                logger.info("All LLMs failed, using Tavily Search fallback")
                                search_response = await self.tavily_search_service.get_fallback_response(
                                    query=message,
                                    language=language
                                )
                                
                                if search_response.get("sources") or search_response.get("search_results"):
                                    intent_name = intent.get('name') if isinstance(intent, dict) else intent
                                    search_response["rasa_intent"] = intent_name
                                    search_response["rasa_confidence"] = confidence
                                    search_response["rasa_entities"] = entities
                                    search_response["fallback_reason"] = "all_llms_failed"
                                    return search_response
                        except Exception as search_error:
                            logger.warning(f"Tavily Search fallback also failed: {search_error}")
                        
                        # Step 5: Final fallback to Rasa
                        logger.warning("All LLMs and Tavily Search failed, falling back to Rasa")
                        intent_name = intent.get('name') if isinstance(intent, dict) else intent
                        rasa_response = await self.rasa_service.get_response(
                            message=message,
                            sender_id=sender_id,
                            language=language
                        )
                        return self._format_rasa_response(rasa_response, intent_name, confidence, entities)
                
                else:
                    # LLM not available, try Tavily Search first before Rasa
                    logger.warning("LLM not available, trying Tavily Search")
                    
                    try:
                        if await self.tavily_search_service.is_available():
                            search_response = await self.tavily_search_service.get_fallback_response(
                                query=message,
                                language=language
                            )
                            
                            if search_response.get("sources") or search_response.get("search_results"):
                                intent_name = intent.get('name') if isinstance(intent, dict) else intent
                                search_response["rasa_intent"] = intent_name
                                search_response["rasa_confidence"] = confidence
                                search_response["rasa_entities"] = entities
                                search_response["fallback_reason"] = "llm_not_available"
                                return search_response
                    except Exception as search_error:
                        logger.warning(f"Tavily Search fallback failed: {search_error}")
                    
                    # Final fallback to Rasa
                    logger.warning("Tavily Search failed, using Rasa fallback")
                    intent_name = intent.get('name') if isinstance(intent, dict) else intent
                    rasa_response = await self.rasa_service.get_response(
                        message=message,
                        sender_id=sender_id,
                        language=language
                    )
                    return self._format_rasa_response(rasa_response, intent_name, confidence, entities)
        
        except Exception as e:
            logger.error(f"Error in hybrid chat service: {e}", exc_info=True)
            
            # Ultimate fallback chain: Tavily Search → Rasa → Static message
            try:
                # First try Tavily Search
                if await self.tavily_search_service.is_available():
                    logger.info("Critical error, attempting Tavily Search as ultimate fallback")
                    search_response = await self.tavily_search_service.get_fallback_response(
                        query=message,
                        language=language
                    )
                    if search_response.get("sources") or search_response.get("search_results"):
                        search_response["fallback_reason"] = "critical_error_tavily_search"
                        return search_response
            except Exception as search_error:
                logger.warning(f"Ultimate Tavily Search fallback failed: {search_error}")
            
            # Then try Rasa
            try:
                rasa_response = await self.rasa_service.get_response(
                    message=message,
                    sender_id=sender_id,
                    language=language
                )
                return self._format_rasa_response(rasa_response, "error", 0.5, [])
                
            except Exception as fallback_error:
                logger.error(f"All fallbacks failed: {fallback_error}")
                return {
                    "text": "I'm sorry, I'm having trouble understanding right now. Please try again.",
                    "intent": "error",
                    "confidence": 0.0,
                    "entities": [],
                    "suggestions": [],
                    "model": "error",
                    "provider": "error"
                }
    
    def _should_use_rasa(self, intent: str, confidence: float, message: str) -> bool:
        """
        Determine if query should be handled by Rasa or LLM
        
        Decision Logic:
        1. High confidence structured intent -> Rasa
        2. Very low confidence -> LLM (Rasa doesn't understand)
        3. Complex query indicators -> LLM
        4. Medium confidence structured intent -> Rasa
        
        Returns:
            True if Rasa should handle it, False if LLM should handle it
        """
        # High confidence structured intent -> Use Rasa
        if intent in self.STRUCTURED_INTENTS and confidence >= self.RASA_HIGH_CONFIDENCE_THRESHOLD:
            return True
        
        # Very low confidence (<0.4) -> Use LLM + Google Search (Rasa doesn't understand)
        if confidence < self.RASA_LOW_CONFIDENCE_THRESHOLD:
            return False
        
        # Check if query is complex enough for LLM
        is_complex = self._is_complex_query(message)
        
        if is_complex:
            return False  # Use LLM for complex queries
        
        # Medium confidence structured intent -> Use Rasa
        if intent in self.STRUCTURED_INTENTS and confidence >= self.RASA_MEDIUM_CONFIDENCE_THRESHOLD:
            return True
        
        # Default: Use Rasa for medium+ confidence, LLM for low confidence
        return confidence >= self.RASA_MEDIUM_CONFIDENCE_THRESHOLD
    
    def _is_complex_query(self, message: str) -> bool:
        """
        Determine if query is complex/open-ended enough for LLM
        
        Complex queries include:
        - Why/how questions
        - Comparisons
        - Planning requests
        - Long messages
        - Multiple questions
        
        Returns:
            True if query is complex and should use LLM
        """
        complex_indicators = [
            # Question types
            "why", "how", "explain", "tell me about",
            "what is", "describe", "compare", "difference",
            "recommend", "suggest", "plan my trip",
            "what are", "what do", "can you explain",
            "help me understand", "what makes", "why is",
            # Planning
            "itinerary", "schedule", "plan", "trip",
            # Comparisons
            "better", "best", "versus", "vs", "or",
            # Explanations
            "because", "reason", "details", "more about"
        ]
        
        message_lower = message.lower()
        
        # Check length (longer messages often benefit from LLM)
        if len(message) > 70:
            return True
        
        # Check for complex question words
        if any(indicator in message_lower for indicator in complex_indicators):
            return True
        
        # Check for multiple questions
        if message.count("?") > 1:
            return True
        
        # Check for comparison requests
        if " vs " in message_lower or " versus " in message_lower:
            return True
        
        return False
    
    def _prepare_llm_context(self, entities: List[Dict]) -> Dict[str, Any]:
        """Prepare context from Rasa entities for LLM"""
        context = {}
        
        for entity in entities:
            entity_type = entity.get("entity", "")
            entity_value = entity.get("value", "")
            
            if entity_type == "location":
                context["user_location"] = entity_value
            elif entity_type == "date":
                if "travel_dates" not in context:
                    context["travel_dates"] = []
                context["travel_dates"].append(entity_value)
            elif entity_type in ["attraction_category", "cuisine", "hotel_type"]:
                if "user_preferences" not in context:
                    context["user_preferences"] = []
                context["user_preferences"].append(entity_value)
        
        return context
    
    def _format_rasa_response(
        self,
        rasa_response: Any,
        intent: str,
        confidence: float,
        entities: List[Dict]
    ) -> Dict[str, Any]:
        """Format Rasa response to standard response format"""
        
        if isinstance(rasa_response, dict):
            if "text" in rasa_response:
                return {
                    "text": rasa_response.get("text", ""),
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "suggestions": rasa_response.get("suggestions", []),
                    "model": "rasa",
                    "provider": "rasa"
                }
            else:
                return {
                    "text": rasa_response.get("message", str(rasa_response)),
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "suggestions": [],
                    "model": "rasa",
                    "provider": "rasa"
                }
        else:
            return {
                "text": str(rasa_response),
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "suggestions": [],
                "model": "rasa",
                "provider": "rasa"
            }
    
    async def get_llm_status(self) -> Dict[str, Any]:
        """Get status of all LLM providers"""
        await self.llm_service.ensure_initialized()
        
        status = settings.get_llm_provider_status()
        status["rasa_available"] = True  # Rasa is always available (has fallback)
        
        return status


# Singleton instance
hybrid_chat_service = None


def get_hybrid_chat_service() -> HybridChatService:
    """Get or create hybrid chat service singleton"""
    global hybrid_chat_service
    if hybrid_chat_service is None:
        hybrid_chat_service = HybridChatService()
    return hybrid_chat_service
