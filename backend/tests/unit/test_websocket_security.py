"""
Unit tests for WebSocket security middleware
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from backend.app.middleware.websocket_security import (
    WebSocketConnectionManager,
    secure_ws_manager,
    websocket_auth_required
)


class TestWebSocketConnectionManager:
    """Test WebSocket connection manager"""
    
    @pytest.fixture
    def connection_manager(self):
        """Create fresh connection manager for testing"""
        return WebSocketConnectionManager(
            max_connections_per_ip=3,
            max_total_connections=10,
            rate_limit_messages=5,
            rate_limit_window=60,
            max_message_size=1024
        )
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        ws = MagicMock()
        ws.headers = {}
        ws.client = MagicMock(host="192.168.1.1")
        ws.accept = AsyncMock()
        ws.close = AsyncMock()
        ws.send_json = AsyncMock()
        return ws
    
    def test_get_client_ip_from_client(self, connection_manager, mock_websocket):
        """Test getting client IP from WebSocket client"""
        ip = connection_manager.get_client_ip(mock_websocket)
        assert ip == "192.168.1.1"
    
    def test_get_client_ip_from_forwarded_header(self, connection_manager, mock_websocket):
        """Test getting client IP from X-Forwarded-For header"""
        mock_websocket.headers = {"x-forwarded-for": "10.0.0.1, 10.0.0.2"}
        ip = connection_manager.get_client_ip(mock_websocket)
        assert ip == "10.0.0.1"
    
    def test_get_client_ip_from_real_ip_header(self, connection_manager, mock_websocket):
        """Test getting client IP from X-Real-IP header"""
        mock_websocket.headers = {"x-real-ip": "10.0.0.5"}
        ip = connection_manager.get_client_ip(mock_websocket)
        assert ip == "10.0.0.5"
    
    def test_ip_not_blocked_initially(self, connection_manager):
        """Test that IPs are not blocked initially"""
        assert connection_manager.is_ip_blocked("192.168.1.1") is False
    
    def test_block_ip(self, connection_manager):
        """Test blocking an IP"""
        connection_manager.block_ip("192.168.1.1", "test reason")
        assert connection_manager.is_ip_blocked("192.168.1.1") is True
        assert "192.168.1.1" in connection_manager.blocked_ips
    
    def test_block_expires(self, connection_manager):
        """Test that IP block expires after timeout"""
        connection_manager.block_ip("192.168.1.1", "test reason")
        
        # Simulate time passing (15+ minutes)
        connection_manager.block_timestamps["192.168.1.1"] = datetime.utcnow() - timedelta(minutes=20)
        
        assert connection_manager.is_ip_blocked("192.168.1.1") is False
    
    @pytest.mark.asyncio
    async def test_can_connect_success(self, connection_manager, mock_websocket):
        """Test successful connection check"""
        allowed, reason = await connection_manager.can_connect(mock_websocket, "session1")
        assert allowed is True
        assert reason == "OK"
    
    @pytest.mark.asyncio
    async def test_can_connect_blocked_ip(self, connection_manager, mock_websocket):
        """Test blocked IP cannot connect"""
        connection_manager.block_ip("192.168.1.1", "test")
        
        allowed, reason = await connection_manager.can_connect(mock_websocket, "session1")
        assert allowed is False
        assert "blocked" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_can_connect_per_ip_limit(self, connection_manager, mock_websocket):
        """Test per-IP connection limit"""
        # Add 3 connections from same IP (at limit)
        for i in range(3):
            connection_manager.connections_by_ip["192.168.1.1"].add(f"session{i}")
            connection_manager.active_connections[f"session{i}"] = mock_websocket
        
        allowed, reason = await connection_manager.can_connect(mock_websocket, "session_new")
        assert allowed is False
        assert "too many connections" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_can_connect_total_limit(self, connection_manager, mock_websocket):
        """Test total connection limit"""
        # Fill up connections
        for i in range(10):
            connection_manager.active_connections[f"session{i}"] = mock_websocket
        
        allowed, reason = await connection_manager.can_connect(mock_websocket, "session_new")
        assert allowed is False
        assert "limit" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_connect_success(self, connection_manager, mock_websocket):
        """Test successful connection"""
        result = await connection_manager.connect(mock_websocket, "session1")
        
        assert result is True
        assert "session1" in connection_manager.active_connections
        mock_websocket.accept.assert_called_once()
    
    def test_disconnect(self, connection_manager, mock_websocket):
        """Test disconnection cleanup"""
        ip = "192.168.1.1"
        session_id = "session1"
        
        # Setup connection
        connection_manager.active_connections[session_id] = mock_websocket
        connection_manager.connections_by_ip[ip].add(session_id)
        connection_manager.connection_timestamps[session_id] = datetime.utcnow()
        connection_manager.message_counts[session_id] = [datetime.utcnow()]
        
        # Disconnect
        connection_manager.disconnect(session_id)
        
        assert session_id not in connection_manager.active_connections
        assert session_id not in connection_manager.connections_by_ip[ip]
        assert session_id not in connection_manager.connection_timestamps
        assert session_id not in connection_manager.message_counts
    
    def test_rate_limit_allowed(self, connection_manager):
        """Test message allowed within rate limit"""
        session_id = "session1"
        
        # First few messages should be allowed
        for _ in range(5):
            assert connection_manager.check_rate_limit(session_id) is True
    
    def test_rate_limit_exceeded(self, connection_manager):
        """Test message blocked when rate limit exceeded"""
        session_id = "session1"
        
        # Fill up rate limit
        for _ in range(5):
            connection_manager.check_rate_limit(session_id)
        
        # Next message should be blocked
        assert connection_manager.check_rate_limit(session_id) is False
    
    def test_message_size_allowed(self, connection_manager):
        """Test small message allowed"""
        message = "Hello, this is a test message"
        assert connection_manager.check_message_size(message) is True
    
    def test_message_size_exceeded(self, connection_manager):
        """Test large message blocked"""
        # Create message larger than 1024 bytes
        message = "x" * 2000
        assert connection_manager.check_message_size(message) is False
    
    def test_connection_not_expired(self, connection_manager):
        """Test fresh connection is not expired"""
        session_id = "session1"
        connection_manager.connection_timestamps[session_id] = datetime.utcnow()
        
        assert connection_manager.is_connection_expired(session_id) is False
    
    def test_connection_expired(self, connection_manager):
        """Test old connection is expired"""
        session_id = "session1"
        connection_manager.connection_timestamps[session_id] = datetime.utcnow() - timedelta(hours=2)
        
        assert connection_manager.is_connection_expired(session_id) is True
    
    def test_get_stats(self, connection_manager, mock_websocket):
        """Test getting connection statistics"""
        # Add some connections
        connection_manager.active_connections["session1"] = mock_websocket
        connection_manager.active_connections["session2"] = mock_websocket
        connection_manager.connections_by_ip["192.168.1.1"] = {"session1", "session2"}
        connection_manager.block_ip("192.168.1.2", "test")
        
        stats = connection_manager.get_stats()
        
        assert stats["total_connections"] == 2
        assert stats["unique_ips"] == 1
        assert stats["blocked_ips"] == 1


class TestWebSocketAuth:
    """Test WebSocket authentication"""
    
    @pytest.fixture
    def mock_websocket(self):
        ws = MagicMock()
        ws.query_params = {}
        ws.headers = {}
        return ws
    
    @pytest.mark.asyncio
    async def test_auth_with_token_param(self, mock_websocket):
        """Test auth with token in query params"""
        mock_websocket.query_params = {"token": "valid_token"}
        
        with patch('backend.app.services.auth_service.AuthService.decode_token') as mock_decode:
            mock_decode.return_value = "user123"
            
            user_id = await websocket_auth_required(mock_websocket)
            
            assert user_id == "user123"
    
    @pytest.mark.asyncio
    async def test_auth_with_bearer_header(self, mock_websocket):
        """Test auth with Authorization header"""
        mock_websocket.headers = {"authorization": "Bearer valid_token"}
        
        with patch('backend.app.services.auth_service.AuthService.decode_token') as mock_decode:
            mock_decode.return_value = "user456"
            
            user_id = await websocket_auth_required(mock_websocket)
            
            assert user_id == "user456"
    
    @pytest.mark.asyncio
    async def test_auth_no_token(self, mock_websocket):
        """Test auth fails without token"""
        user_id = await websocket_auth_required(mock_websocket)
        assert user_id is None
    
    @pytest.mark.asyncio
    async def test_auth_invalid_token(self, mock_websocket):
        """Test auth fails with invalid token"""
        mock_websocket.query_params = {"token": "invalid_token"}
        
        with patch('backend.app.services.auth_service.AuthService.decode_token') as mock_decode:
            mock_decode.side_effect = Exception("Invalid token")
            
            user_id = await websocket_auth_required(mock_websocket)
            
            assert user_id is None
