"""
Unit tests for chat service
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.app.services.chat_service import ChatService


class TestChatService:
    """Test chat service methods"""
    
    @pytest.fixture
    def chat_service(self):
        """Create chat service instance"""
        return ChatService()
    
    @pytest.mark.asyncio
    async def test_detect_language_english(self, chat_service):
        """Test language detection for English text"""
        text = "Hello, how are you today?"
        language = await chat_service.detect_language(text)
        
        assert language in ["en", "english"]
    
    @pytest.mark.asyncio
    async def test_detect_language_sinhala(self, chat_service):
        """Test language detection for Sinhala text"""
        text = "ආයුබෝවන් ඔබට කොහොමද?"
        language = await chat_service.detect_language(text)
        
        # Should detect as Sinhala
        assert language in ["si", "sinhala"]
    
    @pytest.mark.asyncio
    async def test_detect_language_empty(self, chat_service):
        """Test language detection with empty text"""
        text = ""
        language = await chat_service.detect_language(text)
        
        # Should default to English
        assert language == "en"
    
    @pytest.mark.asyncio
    @patch('backend.app.services.chat_service.ChatService.call_rasa')
    async def test_process_message_success(self, mock_rasa, chat_service):
        """Test message processing with successful Rasa response"""
        mock_rasa.return_value = [{
            "text": "Sigiriya is an ancient rock fortress...",
            "intent": "ask_attraction_info",
            "entities": [{"entity": "attraction", "value": "Sigiriya"}]
        }]
        
        response = await chat_service.process_message(
            message="Tell me about Sigiriya",
            user_id="test_user",
            language="en"
        )
        
        assert response is not None
        assert "text" in response
        assert len(response["text"]) > 0
    
    @pytest.mark.asyncio
    @patch('backend.app.services.chat_service.ChatService.call_rasa')
    async def test_process_message_rasa_failure(self, mock_rasa, chat_service):
        """Test message processing when Rasa fails"""
        mock_rasa.side_effect = Exception("Rasa connection error")
        
        response = await chat_service.process_message(
            message="Tell me about Sigiriya",
            user_id="test_user",
            language="en"
        )
        
        # Should return fallback response
        assert response is not None
        assert "text" in response
    
    @pytest.mark.asyncio
    async def test_format_response_multilingual(self, chat_service):
        """Test response formatting for multiple languages"""
        response_data = {
            "text": "Sigiriya is an ancient rock fortress",
            "intent": "ask_attraction_info"
        }
        
        # Test English
        en_response = await chat_service.format_response(response_data, "en")
        assert "text" in en_response
        
        # Test Sinhala
        si_response = await chat_service.format_response(response_data, "si")
        assert "text" in si_response
    
    @pytest.mark.asyncio
    async def test_save_conversation_history(self, chat_service):
        """Test saving conversation to database"""
        conversation_data = {
            "user_id": "test_user",
            "message": "Tell me about Sigiriya",
            "response": "Sigiriya is an ancient rock fortress...",
            "language": "en",
            "intent": "ask_attraction_info"
        }
        
        # Should not raise exception
        await chat_service.save_conversation(conversation_data)
    
    def test_extract_entities(self, chat_service):
        """Test entity extraction from Rasa response"""
        rasa_response = [{
            "entities": [
                {"entity": "attraction", "value": "Sigiriya"},
                {"entity": "location", "value": "Matale"}
            ]
        }]
        
        entities = chat_service.extract_entities(rasa_response)
        
        assert len(entities) == 2
        assert entities[0]["entity"] == "attraction"
        assert entities[0]["value"] == "Sigiriya"
    
    def test_extract_intent(self, chat_service):
        """Test intent extraction from Rasa response"""
        rasa_response = [{
            "intent": {"name": "ask_attraction_info", "confidence": 0.95}
        }]
        
        intent = chat_service.extract_intent(rasa_response)
        
        assert intent == "ask_attraction_info"
    
    def test_generate_suggestions(self, chat_service):
        """Test suggestion generation based on intent"""
        intent = "ask_attraction_info"
        
        suggestions = chat_service.generate_suggestions(intent)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)
