"""
LLM Service - Orchestrates API-based LLMs (Gemini, Qwen, Mistral)
Uses RAG (Retrieval Augmented Generation) with tourism database
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    try:
        # Fallback to older import path
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        EMBEDDINGS_AVAILABLE = True
    except ImportError:
        EMBEDDINGS_AVAILABLE = False
        logging.warning("LangChain embeddings not available. RAG features will be limited.")

from backend.app.core.config import settings
from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.event import Event
from backend.app.models.transport import Transport
from backend.app.services.cache_service import cached
from backend.app.services.gemini_service import get_gemini_service
from backend.app.services.mistral_service import get_mistral_service
from backend.app.services.qwen_service import get_qwen_service

logger = logging.getLogger(__name__)


class LLMService:
    """
    Orchestrates API-based LLM providers with RAG for tourism chatbot
    Multi-LLM fallback chain (100% FREE): Gemini → Qwen → Mistral
    Implements circuit breaker pattern to prevent cascading failures
    """
    
    def __init__(self):
        # Initialize all FREE LLM providers
        self.gemini_service = get_gemini_service()
        self.qwen_service = get_qwen_service()
        self.mistral_service = get_mistral_service()
        
        self.embeddings = None
        self.vector_store = None
        self.enabled = False
        self._initialization_task = None
        
        # Circuit breaker: Track failures per provider
        self.provider_failures = {
            "gemini": 0,
            "qwen": 0,
            "mistral": 0
        }
        self.provider_last_failure = {
            "gemini": None,
            "mistral": None,
            "qwen": None
        }
        self.CIRCUIT_BREAKER_THRESHOLD = 3  # Fail after 3 consecutive failures
        self.CIRCUIT_BREAKER_RESET_TIME = 300  # Reset after 5 minutes
        
        # Determine primary model name
        if settings.LLM_PROVIDER == "gemini":
            self.model_name = settings.GEMINI_MODEL
        elif settings.LLM_PROVIDER == "mistral":
            self.model_name = settings.MISTRAL_MODEL
        elif settings.LLM_PROVIDER == "openai":
            self.model_name = settings.OPENAI_MODEL
        else:
            self.model_name = settings.GEMINI_MODEL
        
        # Check if any LLM provider is available
        if settings.LLM_ENABLED:
            logger.info("LLM service will initialize on first use")
            logger.info(f"Fallback chain: {settings.LLM_PROVIDER} → {settings.LLM_FALLBACK_PROVIDER_1} → {settings.LLM_FALLBACK_PROVIDER_2}")
        else:
            logger.info("LLM service disabled in configuration")
    
    async def ensure_initialized(self) -> bool:
        """Ensure LLM service is initialized with embeddings"""
        if self.enabled:
            return True
        
        if not settings.LLM_ENABLED:
            return False
        
        # Check if any provider is available
        gemini_available = await self.gemini_service.is_available()
        qwen_available = await self.qwen_service.is_available()
        mistral_available = await self.mistral_service.is_available()
        
        if not (gemini_available or qwen_available or mistral_available):
            logger.warning("No FREE LLM providers available")
            return False
        
        if self._initialization_task is None:
            self._initialization_task = asyncio.create_task(self._initialize_embeddings())
        
        try:
            await self._initialization_task
            return self.enabled
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            return False
    
    async def _initialize_embeddings(self):
        """Initialize embeddings and build knowledge base"""
        try:
            if not EMBEDDINGS_AVAILABLE:
                logger.warning("Embeddings not available, running without RAG")
                self.enabled = True
                return
            
            logger.info("Initializing embeddings for RAG...")
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def load_embeddings():
                return HuggingFaceEmbeddings(
                    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    model_kwargs={'device': 'cpu'}
                )
            
            self.embeddings = await loop.run_in_executor(None, load_embeddings)
            
            # Build knowledge base
            await self._build_knowledge_base()
            
            self.enabled = True
            logger.info("LLM service with RAG initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}", exc_info=True)
            logger.info("LLM service will work without RAG")
            self.enabled = True  # Still enable service without RAG
    
    async def _build_knowledge_base(self):
        """Build vector store from tourism database"""
        try:
            logger.info("Building knowledge base from tourism database...")
            
            # Fetch all tourism content
            attractions = await Attraction.find({"is_active": True}).to_list()
            hotels = await Hotel.find({"is_active": True}).to_list()
            restaurants = await Restaurant.find({"is_active": True}).to_list()
            events = await Event.find({"status": "published"}).to_list()
            transport_options = await Transport.find({"is_active": True}).to_list()
            
            # Create documents for RAG
            documents = []
            
            # Process attractions
            for attr in attractions:
                for lang in settings.SUPPORTED_LANGUAGES:
                    name = attr.name.get(lang, attr.name.get("en", ""))
                    desc = attr.description.get(lang, attr.description.get("en", ""))
                    short_desc = attr.short_description.get(lang, attr.short_description.get("en", ""))
                    
                    doc = f"""
Attraction: {name}
Category: {attr.category.value}
Location: {attr.location.city}, {attr.location.province}
Description: {short_desc}
Full Description: {desc}
Tags: {', '.join(attr.tags)}
Activities: {', '.join(attr.amenities) if attr.amenities else 'N/A'}
Opening Hours: {self._format_opening_hours(attr.opening_hours)}
Pricing: {'Free' if attr.is_free else 'Paid'}
Rating: {attr.average_rating}/5.0 ({attr.total_reviews} reviews)
"""
                    documents.append(doc)
            
            # Process hotels
            for hotel in hotels:
                for lang in settings.SUPPORTED_LANGUAGES:
                    name = hotel.name.get(lang, hotel.name.get("en", ""))
                    desc = hotel.description.get(lang, hotel.description.get("en", ""))
                    short_desc = hotel.short_description.get(lang, hotel.short_description.get("en", ""))
                    
                    price_range = hotel.get_price_range()
                    
                    doc = f"""
Hotel: {name}
Category: {hotel.category.value}
Star Rating: {hotel.star_rating.value}
Location: {hotel.location.city}, {hotel.location.province}
Description: {short_desc}
Full Description: {desc}
Amenities: {', '.join([a.value for a in hotel.amenities])}
Price Range: {price_range['min']:.0f} - {price_range['max']:.0f} LKR per night
Rating: {hotel.average_rating}/5.0 ({hotel.total_reviews} reviews)
"""
                    documents.append(doc)
            
            # Process restaurants
            for rest in restaurants:
                for lang in settings.SUPPORTED_LANGUAGES:
                    name = rest.name.get(lang, rest.name.get("en", ""))
                    desc = rest.description.get(lang, rest.description.get("en", ""))
                    short_desc = rest.short_description.get(lang, rest.short_description.get("en", ""))
                    
                    doc = f"""
Restaurant: {name}
Cuisine: {', '.join([c.value for c in rest.cuisine_types])}
Type: {rest.restaurant_type.value}
Price Range: {rest.price_range.value}
Location: {rest.location.city}, {rest.location.province}
Description: {short_desc}
Full Description: {desc}
Dietary Options: {', '.join([d.value for d in rest.dietary_options])}
Rating: {rest.average_rating}/5.0 ({rest.total_reviews} reviews)
"""
                    documents.append(doc)
            
            # Process events
            for event in events:
                for lang in settings.SUPPORTED_LANGUAGES:
                    title = event.title.get(lang, event.title.get("en", ""))
                    desc = event.description.get(lang, event.description.get("en", ""))
                    short_desc = event.short_description.get(lang, event.short_description.get("en", ""))
                    
                    doc = f"""
Event: {title}
Category: {event.category.value}
Location: {event.location.city}, {event.location.province}
Schedule: {event.schedule.start_date} to {event.schedule.end_date or event.schedule.start_date}
Description: {short_desc}
Full Description: {desc}
Tags: {', '.join(event.tags)}
Status: {event.status.value}
"""
                    documents.append(doc)
            
            # Process transport
            for trans in transport_options:
                for lang in settings.SUPPORTED_LANGUAGES:
                    name = trans.name.get(lang, trans.name.get("en", ""))
                    desc = trans.description.get(lang, trans.description.get("en", ""))
                    short_desc = trans.short_description.get(lang, trans.short_description.get("en", ""))
                    
                    routes_str = ', '.join([f"{r.origin} to {r.destination}" for r in trans.routes[:3]])
                    
                    doc = f"""
Transport: {name}
Type: {trans.transport_type.value}
Category: {trans.category.value}
Operator: {trans.operator_name or 'N/A'}
Routes: {routes_str}
Description: {short_desc}
Full Description: {desc}
Service Areas: {', '.join(trans.service_areas)}
Rating: {trans.average_rating}/5.0 ({trans.total_reviews} reviews)
"""
                    documents.append(doc)
            
            # Create vector store
            if documents and self.embeddings:
                logger.info(f"Creating vector store with {len(documents)} documents...")
                self.vector_store = FAISS.from_texts(
                    documents,
                    self.embeddings
                )
                logger.info(f"Knowledge base built successfully with {len(documents)} documents")
            else:
                logger.warning("No documents found to build knowledge base")
                
        except Exception as e:
            logger.error(f"Failed to build knowledge base: {e}", exc_info=True)
    
    def _format_opening_hours(self, opening_hours: List) -> str:
        """Format opening hours for display"""
        if not opening_hours:
            return "Not specified"
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        formatted = []
        for oh in opening_hours[:7]:
            day_name = days[oh.day_of_week] if oh.day_of_week < 7 else "Unknown"
            if oh.is_closed:
                formatted.append(f"{day_name}: Closed")
            elif oh.open_time and oh.close_time:
                formatted.append(f"{day_name}: {oh.open_time.strftime('%H:%M')} - {oh.close_time.strftime('%H:%M')}")
        
        return "; ".join(formatted) if formatted else "Not specified"
    
    @cached(ttl=300, prefix="llm:response")
    async def get_response(
        self,
        message: str,
        language: str = "en",
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Get response from LLM using RAG
        
        Args:
            message: User message
            language: Response language
            context: Additional context (user location, preferences)
            conversation_history: Previous conversation messages
        
        Returns:
            Response dictionary with text, confidence, sources
        """
        # Ensure LLM is initialized
        if not self.enabled:
            initialized = await self.ensure_initialized()
            if not initialized:
                # Fallback to Rasa
                from backend.app.services.rasa_service import RasaService
                rasa = RasaService()
                return await rasa.get_response(message, "llm_fallback", language)
        
        try:
            # Retrieve relevant documents from knowledge base
            tourism_context = None
            if self.vector_store:
                try:
                    docs = self.vector_store.similarity_search(message, k=5)
                    # Combine top 3 most relevant documents
                    tourism_context = "\n\n".join([doc.page_content for doc in docs[:3]])
                except Exception as e:
                    logger.warning(f"Error in similarity search: {e}")
            
            # Implement fallback chain: Primary → Fallback 1 → Fallback 2
            providers_chain = [
                settings.LLM_PROVIDER.lower(),
                settings.LLM_FALLBACK_PROVIDER_1.lower(),
                settings.LLM_FALLBACK_PROVIDER_2.lower()
            ]
            
            # Try each provider in the chain
            for provider in providers_chain:
                if self._is_circuit_open(provider):
                    try:
                        response = await self._try_provider(
                            provider=provider,
                            message=message,
                            language=language,
                            context=context,
                            conversation_history=conversation_history,
                            tourism_context=tourism_context
                        )
                        
                        if response:
                            # Reset failure count on success
                            self.provider_failures[provider] = 0
                            logger.info(f"Successfully got response from {provider}")
                            return response
                            
                    except Exception as e:
                        logger.error(f"Provider {provider} failed: {e}")
                        self._record_failure(provider)
                else:
                    logger.warning(f"Provider {provider} circuit breaker is open, skipping")
            
            # All providers failed, fallback to Rasa
            logger.warning("All LLM providers failed, falling back to Rasa")
            from backend.app.services.rasa_service import RasaService
            rasa = RasaService()
            return await rasa.get_response(message, "llm_error_fallback", language)
            
        except Exception as e:
            logger.error(f"LLM service error: {e}", exc_info=True)
            # Ultimate fallback to Rasa
            from backend.app.services.rasa_service import RasaService
            rasa = RasaService()
            return await rasa.get_response(message, "llm_fallback", language)
    
    def _is_circuit_open(self, provider: str) -> bool:
        """Check if circuit breaker is open for a provider"""
        if provider not in self.provider_failures:
            # Initialize tracking for new provider
            self.provider_failures[provider] = 0
            self.provider_last_failure[provider] = None
            return True
        
        failures = self.provider_failures[provider]
        last_failure = self.provider_last_failure.get(provider)
        
        # Circuit is open if failures exceed threshold
        if failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            # Check if enough time has passed to reset
            if last_failure:
                time_since_failure = (datetime.utcnow() - last_failure).total_seconds()
                if time_since_failure > self.CIRCUIT_BREAKER_RESET_TIME:
                    # Reset circuit breaker
                    self.provider_failures[provider] = 0
                    self.provider_last_failure[provider] = None
                    logger.info(f"Circuit breaker reset for {provider}")
                    return True
            return False
        
        return True
    
    def _record_failure(self, provider: str):
        """Record a failure for a provider"""
        if provider not in self.provider_failures:
            self.provider_failures[provider] = 0
            self.provider_last_failure[provider] = None
        
        self.provider_failures[provider] += 1
        self.provider_last_failure[provider] = datetime.utcnow()
        logger.warning(f"Provider {provider} failure count: {self.provider_failures[provider]}")
    
    async def _try_provider(
        self,
        provider: str,
        message: str,
        language: str,
        context: Optional[Dict],
        conversation_history: Optional[List[Dict]],
        tourism_context: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Try to get response from a specific provider"""
        if provider == "gemini" and await self.gemini_service.is_available():
            return await self.gemini_service.get_response(
                message=message,
                language=language,
                context=context,
                conversation_history=conversation_history,
                tourism_context=tourism_context
            )
        elif provider == "qwen" and await self.qwen_service.is_available():
            return await self.qwen_service.get_response(
                message=message,
                language=language,
                context=context,
                conversation_history=conversation_history,
                tourism_context=tourism_context
            )
        elif provider == "mistral" and await self.mistral_service.is_available():
            return await self.mistral_service.get_response(
                message=message,
                language=language,
                context=context,
                conversation_history=conversation_history,
                tourism_context=tourism_context
            )
        
        return None


# Singleton instance
llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
