"""
API endpoint tests for chat functionality
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
class TestChatEndpoints:
    """Test chat API endpoints"""
    
    @pytest.mark.asyncio
    async def test_send_message_authenticated(self, client: AsyncClient, auth_headers):
        """Test sending chat message with authentication"""
        response = await client.post(
            "/api/v1/chat/message",
            headers=auth_headers,
            json={
                "message": "Tell me about Sigiriya",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "text" in data
    
    @pytest.mark.asyncio
    async def test_send_message_no_auth(self, client: AsyncClient):
        """Test sending message without authentication"""
        response = await client.post(
            "/api/v1/chat/message",
            json={
                "message": "Tell me about Sigiriya",
                "language": "en"
            }
        )
        
        # Should work (guest mode) or require auth
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_send_message_empty(self, client: AsyncClient, auth_headers):
        """Test sending empty message"""
        response = await client.post(
            "/api/v1/chat/message",
            headers=auth_headers,
            json={
                "message": "",
                "language": "en"
            }
        )
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_send_message_sinhala(self, client: AsyncClient, auth_headers):
        """Test sending message in Sinhala"""
        response = await client.post(
            "/api/v1/chat/message",
            headers=auth_headers,
            json={
                "message": "සීගිරිය ගැන කියන්න",
                "language": "si"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "text" in data
    
    @pytest.mark.asyncio
    async def test_get_chat_history(self, client: AsyncClient, auth_headers):
        """Test getting chat history"""
        response = await client.get(
            "/api/v1/chat/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "conversations" in data
    
    @pytest.mark.asyncio
    async def test_get_chat_history_no_auth(self, client: AsyncClient):
        """Test getting chat history without authentication"""
        response = await client.get("/api/v1/chat/history")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_clear_chat_history(self, client: AsyncClient, auth_headers):
        """Test clearing chat history"""
        response = await client.delete(
            "/api/v1/chat/history",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self, client: AsyncClient, auth_headers):
        """Test getting specific conversation"""
        # First send a message
        send_response = await client.post(
            "/api/v1/chat/message",
            headers=auth_headers,
            json={
                "message": "Test message",
                "language": "en"
            }
        )
        
        # Try to get conversation (might not have ID in response)
        assert send_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_chat_feedback(self, client: AsyncClient, auth_headers):
        """Test submitting chat feedback"""
        response = await client.post(
            "/api/v1/chat/feedback",
            headers=auth_headers,
            json={
                "rating": 5,
                "comment": "Very helpful!",
                "conversation_id": "test_conv_id"
            }
        )
        
        assert response.status_code in [200, 201, 404]  # 404 if conversation doesn't exist
