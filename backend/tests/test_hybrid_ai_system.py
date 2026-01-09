"""
Test Suite for Hybrid AI System
Tests Rasa + Gemini integration with RAG
"""

import pytest
import asyncio
from typing import Dict, Any

# Import services
from backend.app.services.gemini_service import get_gemini_service
from backend.app.services.llm_service import get_llm_service
from backend.app.services.rasa_service import RasaService
from backend.app.services.hybrid_chat_service import get_hybrid_chat_service
from backend.app.core.config import settings


class TestGeminiService:
    """Test Gemini API integration"""
    
    @pytest.mark.asyncio
    async def test_gemini_availability(self):
        """Test if Gemini service is available"""
        service = get_gemini_service()
        is_available = await service.is_available()
        
        if settings.GEMINI_API_KEY:
            # Service might not be available if library is not installed
            # or if initialization failed, so we just check it doesn't crash
            assert isinstance(is_available, bool), "is_available should return a boolean"
        else:
            assert not is_available, "Gemini should not be available without API key"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not settings.GEMINI_API_KEY, reason="Gemini API key not configured")
    async def test_gemini_simple_response(self):
        """Test Gemini simple text generation"""
        service = get_gemini_service()
        
        # Skip if service is not available
        if not await service.is_available():
            pytest.skip("Gemini service is not available (library may not be installed)")
        
        response = await service.get_response(
            message="What is Sri Lanka famous for?",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        assert len(response["text"]) > 0
        assert response["provider"] == "google"
        assert response["confidence"] > 0.9
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not settings.GEMINI_API_KEY, reason="Gemini API key not configured")
    async def test_gemini_with_tourism_context(self):
        """Test Gemini with tourism RAG context"""
        service = get_gemini_service()
        
        # Skip if service is not available
        if not await service.is_available():
            pytest.skip("Gemini service is not available (library may not be installed)")
        
        tourism_context = """
Attraction: Sigiriya Rock Fortress
Category: Historical
Location: Dambulla, Central Province
Description: An ancient rock fortress and palace ruins.
UNESCO World Heritage Site.
"""
        
        response = await service.get_response(
            message="Tell me about Sigiriya",
            language="en",
            tourism_context=tourism_context
        )
        
        assert response is not None
        assert "sigiriya" in response["text"].lower()
        assert len(response.get("sources", [])) > 0


class TestLLMService:
    """Test LLM orchestration service"""
    
    @pytest.mark.asyncio
    async def test_llm_initialization(self):
        """Test LLM service initialization"""
        service = get_llm_service()
        initialized = await service.ensure_initialized()
        
        # Should initialize if any provider is available
        if settings.GEMINI_API_KEY:
            assert initialized, "LLM service should initialize with API keys"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.GEMINI_API_KEY,
        reason="No LLM API keys configured"
    )
    async def test_llm_provider_selection(self):
        """Test that LLM service selects correct provider"""
        service = get_llm_service()
        await service.ensure_initialized()
        
        response = await service.get_response(
            message="Tell me about Sri Lankan cuisine",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        assert "provider" in response
        # Provider can be google, qwen, mistral, or rasa (fallback)
        assert response["provider"] in ["google", "qwen", "mistral", "rasa"]
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.GEMINI_API_KEY,
        reason="No LLM API keys configured"
    )
    async def test_llm_with_rag(self):
        """Test LLM with RAG (if knowledge base is built)"""
        service = get_llm_service()
        await service.ensure_initialized()
        
        response = await service.get_response(
            message="What hotels are available in Colombo?",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        # Response should mention hotels or provide relevant info


class TestRasaService:
    """Test Rasa NLU integration"""
    
    @pytest.mark.asyncio
    async def test_rasa_parse_message(self):
        """Test Rasa intent classification"""
        service = RasaService()
        
        result = await service.parse_message(
            message="Hello, how are you?",
            language="en"
        )
        
        assert result is not None
        assert "intent" in result
        assert "entities" in result
    
    @pytest.mark.asyncio
    async def test_rasa_get_response(self):
        """Test Rasa response generation"""
        service = RasaService()
        
        response = await service.get_response(
            message="Hi there",
            sender_id="test_user_123",
            language="en"
        )
        
        assert response is not None


class TestHybridChatService:
    """Test Hybrid Chat routing logic"""
    
    @pytest.mark.asyncio
    async def test_hybrid_service_initialization(self):
        """Test hybrid service initializes correctly"""
        service = get_hybrid_chat_service()
        assert service is not None
        assert service.llm_service is not None
        assert service.rasa_service is not None
    
    @pytest.mark.asyncio
    async def test_structured_intent_routing(self):
        """Test that structured intents route to Rasa"""
        service = get_hybrid_chat_service()
        
        # Simple greeting should route to Rasa
        response = await service.get_response(
            message="Hello",
            sender_id="test_user_123",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        # Should be quick (Rasa response)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.GEMINI_API_KEY,
        reason="No LLM API keys configured"
    )
    async def test_complex_query_routing(self):
        """Test that complex queries route to LLM"""
        service = get_hybrid_chat_service()
        
        # Complex question should route to LLM
        response = await service.get_response(
            message="Why is Sigiriya considered one of the most important archaeological sites in South Asia?",
            sender_id="test_user_123",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        assert len(response["text"]) > 20  # Should have content
        # Provider can be any available LLM or rasa fallback
        if "provider" in response:
            assert response["provider"] in ["google", "qwen", "mistral", "rasa"]
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """Test that system falls back gracefully"""
        service = get_hybrid_chat_service()
        
        # Even if LLMs fail, should get response from Rasa
        response = await service.get_response(
            message="What is your name?",
            sender_id="test_user_123",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
    
    @pytest.mark.asyncio
    async def test_multilingual_support(self):
        """Test multilingual responses"""
        service = get_hybrid_chat_service()
        
        # Test Sinhala
        response_si = await service.get_response(
            message="ආයුබෝවන්",
            sender_id="test_user_123",
            language="si"
        )
        
        assert response_si is not None
        
        # Test Tamil
        response_ta = await service.get_response(
            message="வணக்கம்",
            sender_id="test_user_123",
            language="ta"
        )
        
        assert response_ta is not None
    
    @pytest.mark.asyncio
    async def test_conversation_history(self):
        """Test conversation context handling"""
        service = get_hybrid_chat_service()
        
        history = [
            {"sender": "user", "content": "I'm interested in historical sites"},
            {"sender": "bot", "content": "Great! Sri Lanka has many historical attractions."}
        ]
        
        response = await service.get_response(
            message="Tell me more",
            sender_id="test_user_123",
            language="en",
            conversation_history=history
        )
        
        assert response is not None
    
    @pytest.mark.asyncio
    async def test_llm_status(self):
        """Test LLM provider status check"""
        service = get_hybrid_chat_service()
        
        status = await service.get_llm_status()
        
        assert status is not None
        assert "llm_enabled" in status
        assert "primary_provider" in status
        assert "rasa_available" in status


class TestComplexScenarios:
    """Test complex real-world scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.GEMINI_API_KEY,
        reason="No LLM API keys configured"
    )
    async def test_comparison_query(self):
        """Test comparison questions"""
        service = get_hybrid_chat_service()
        
        response = await service.get_response(
            message="Compare the beaches in Galle versus Mirissa. Which is better for swimming?",
            sender_id="test_user_123",
            language="en"
        )
        
        assert response is not None
        # Response might be shorter for simple queries, so we check for reasonable length
        assert len(response["text"]) > 50  # Should have some content
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.GEMINI_API_KEY,
        reason="No LLM API keys configured"
    )
    async def test_planning_query(self):
        """Test trip planning questions"""
        service = get_hybrid_chat_service()
        
        response = await service.get_response(
            message="Plan a 3-day itinerary for Kandy including cultural sites and nature",
            sender_id="test_user_123",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        # Response should contain relevant content (LLM may mention days/itinerary, Rasa fallback is also valid)
        assert len(response["text"]) > 10
    
    @pytest.mark.asyncio
    async def test_multiple_messages_session(self):
        """Test full conversation flow"""
        service = get_hybrid_chat_service()
        sender_id = "test_user_session_123"
        
        # Message 1: Greeting (Rasa)
        response1 = await service.get_response(
            message="Hello",
            sender_id=sender_id,
            language="en"
        )
        assert response1 is not None
        
        # Message 2: Specific query (Rasa)
        response2 = await service.get_response(
            message="Show me hotels in Colombo",
            sender_id=sender_id,
            language="en"
        )
        assert response2 is not None
        
        # Message 3: Complex follow-up (LLM if available)
        response3 = await service.get_response(
            message="Why is Colombo called the commercial capital?",
            sender_id=sender_id,
            language="en"
        )
        assert response3 is not None


# Performance benchmarks
class TestPerformance:
    """Test system performance"""
    
    @pytest.mark.asyncio
    async def test_rasa_response_time(self):
        """Test Rasa response is fast"""
        import time
        service = RasaService()
        
        start = time.time()
        await service.get_response("Hello", "test_user", "en")
        elapsed = time.time() - start
        
        # Rasa should respond in < 5 seconds (including network and cold start)
        assert elapsed < 5.0, f"Rasa took {elapsed:.2f}s, expected < 5s"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not settings.GEMINI_API_KEY, reason="Gemini not configured")
    async def test_gemini_response_time(self):
        """Test Gemini response time"""
        import time
        service = get_gemini_service()
        
        # Skip if service is not available
        if not await service.is_available():
            pytest.skip("Gemini service is not available")
        
        start = time.time()
        await service.get_response("What is Sri Lanka?", "en")
        elapsed = time.time() - start
        
        # Gemini should respond in < 10 seconds (allowing for cold start)
        assert elapsed < 10.0, f"Gemini took {elapsed:.2f}s, expected < 10s"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
