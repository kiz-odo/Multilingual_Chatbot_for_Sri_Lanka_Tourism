"""
WebSocket Security Middleware
Rate limiting, connection limits, and authentication for WebSocket connections
"""

import logging
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """
    Secure WebSocket connection manager with:
    - Per-IP connection limits
    - Rate limiting
    - Message size limits
    - Connection timeout
    - Authentication validation
    """
    
    def __init__(
        self,
        max_connections_per_ip: int = 5,
        max_total_connections: int = 1000,
        rate_limit_messages: int = 30,
        rate_limit_window: int = 60,  # seconds
        max_message_size: int = 65536,  # 64KB
        connection_timeout: int = 3600,  # 1 hour
        heartbeat_interval: int = 30  # seconds
    ):
        self.max_connections_per_ip = max_connections_per_ip
        self.max_total_connections = max_total_connections
        self.rate_limit_messages = rate_limit_messages
        self.rate_limit_window = rate_limit_window
        self.max_message_size = max_message_size
        self.connection_timeout = connection_timeout
        self.heartbeat_interval = heartbeat_interval
        
        # Connection tracking
        self.active_connections: Dict[str, WebSocket] = {}
        self.connections_by_ip: Dict[str, Set[str]] = defaultdict(set)
        self.connection_timestamps: Dict[str, datetime] = {}
        
        # Rate limiting
        self.message_counts: Dict[str, list] = defaultdict(list)
        
        # Blocked IPs
        self.blocked_ips: Set[str] = set()
        self.block_timestamps: Dict[str, datetime] = {}
        
    def get_client_ip(self, websocket: WebSocket) -> str:
        """Extract client IP from WebSocket connection"""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = websocket.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = websocket.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if websocket.client:
            return websocket.client.host
        
        return "unknown"
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if ip not in self.blocked_ips:
            return False
        
        # Check if block has expired (15 minutes)
        block_time = self.block_timestamps.get(ip)
        if block_time and datetime.utcnow() - block_time > timedelta(minutes=15):
            self.blocked_ips.discard(ip)
            del self.block_timestamps[ip]
            return False
        
        return True
    
    def block_ip(self, ip: str, reason: str):
        """Temporarily block an IP"""
        self.blocked_ips.add(ip)
        self.block_timestamps[ip] = datetime.utcnow()
        logger.warning(f"Blocked IP {ip}: {reason}")
    
    async def can_connect(self, websocket: WebSocket, session_id: str) -> tuple[bool, str]:
        """
        Check if connection is allowed
        
        Returns: (allowed, reason)
        """
        ip = self.get_client_ip(websocket)
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            return False, "IP temporarily blocked due to abuse"
        
        # Check total connections limit
        if len(self.active_connections) >= self.max_total_connections:
            return False, "Server connection limit reached"
        
        # Check per-IP limit
        if len(self.connections_by_ip[ip]) >= self.max_connections_per_ip:
            return False, f"Too many connections from this IP (max: {self.max_connections_per_ip})"
        
        # Check for duplicate session
        if session_id in self.active_connections:
            return False, "Session already connected"
        
        return True, "OK"
    
    async def connect(self, websocket: WebSocket, session_id: str) -> bool:
        """
        Accept and register WebSocket connection
        
        Returns: True if connected successfully
        """
        ip = self.get_client_ip(websocket)
        
        allowed, reason = await self.can_connect(websocket, session_id)
        if not allowed:
            logger.warning(f"Connection rejected for {ip}: {reason}")
            await websocket.close(code=1008, reason=reason)
            return False
        
        await websocket.accept()
        
        self.active_connections[session_id] = websocket
        self.connections_by_ip[ip].add(session_id)
        self.connection_timestamps[session_id] = datetime.utcnow()
        
        logger.info(f"WebSocket connected: {session_id} from {ip}")
        return True
    
    def disconnect(self, session_id: str):
        """Remove connection from tracking"""
        if session_id not in self.active_connections:
            return
        
        websocket = self.active_connections[session_id]
        ip = self.get_client_ip(websocket)
        
        del self.active_connections[session_id]
        self.connections_by_ip[ip].discard(session_id)
        
        if session_id in self.connection_timestamps:
            del self.connection_timestamps[session_id]
        
        if session_id in self.message_counts:
            del self.message_counts[session_id]
        
        # Clean up empty IP entries
        if not self.connections_by_ip[ip]:
            del self.connections_by_ip[ip]
        
        logger.info(f"WebSocket disconnected: {session_id}")
    
    def check_rate_limit(self, session_id: str) -> bool:
        """
        Check if message is within rate limit
        
        Returns: True if allowed, False if rate limited
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.rate_limit_window)
        
        # Clean old timestamps
        self.message_counts[session_id] = [
            ts for ts in self.message_counts[session_id]
            if ts > window_start
        ]
        
        # Check limit
        if len(self.message_counts[session_id]) >= self.rate_limit_messages:
            return False
        
        # Record message
        self.message_counts[session_id].append(now)
        return True
    
    def check_message_size(self, message: str) -> bool:
        """Check if message is within size limit"""
        return len(message.encode('utf-8')) <= self.max_message_size
    
    def is_connection_expired(self, session_id: str) -> bool:
        """Check if connection has exceeded timeout"""
        if session_id not in self.connection_timestamps:
            return True
        
        connected_at = self.connection_timestamps[session_id]
        return datetime.utcnow() - connected_at > timedelta(seconds=self.connection_timeout)
    
    async def send_message(self, session_id: str, message: dict) -> bool:
        """Send message to specific connection"""
        if session_id not in self.active_connections:
            return False
        
        try:
            await self.active_connections[session_id].send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending to {session_id}: {e}")
            self.disconnect(session_id)
            return False
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        """Broadcast message to all connections"""
        exclude = exclude or set()
        
        for session_id in list(self.active_connections.keys()):
            if session_id not in exclude:
                await self.send_message(session_id, message)
    
    async def cleanup_expired_connections(self):
        """Remove expired connections (call periodically)"""
        expired = [
            session_id for session_id in self.active_connections
            if self.is_connection_expired(session_id)
        ]
        
        for session_id in expired:
            try:
                websocket = self.active_connections[session_id]
                await websocket.close(code=1000, reason="Connection timeout")
            except:
                pass
            self.disconnect(session_id)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired connections")
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "unique_ips": len(self.connections_by_ip),
            "blocked_ips": len(self.blocked_ips),
            "max_connections": self.max_total_connections,
            "connections_by_ip": {
                ip: len(sessions) 
                for ip, sessions in self.connections_by_ip.items()
            }
        }


# Global secure connection manager
secure_ws_manager = WebSocketConnectionManager(
    max_connections_per_ip=int(getattr(settings, 'WS_MAX_CONNECTIONS_PER_IP', 5)),
    max_total_connections=int(getattr(settings, 'WS_MAX_TOTAL_CONNECTIONS', 1000)),
    rate_limit_messages=int(getattr(settings, 'WS_RATE_LIMIT_MESSAGES', 30)),
    rate_limit_window=int(getattr(settings, 'WS_RATE_LIMIT_WINDOW', 60)),
    max_message_size=int(getattr(settings, 'WS_MAX_MESSAGE_SIZE', 65536))
)


async def websocket_auth_required(websocket: WebSocket, token: str = None) -> Optional[str]:
    """
    Validate WebSocket authentication token
    
    Returns: user_id if authenticated, None otherwise
    """
    from backend.app.services.auth_service import AuthService
    
    if not token:
        # Try to get token from query params or headers
        token = websocket.query_params.get("token")
        if not token:
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
    
    if not token:
        return None
    
    try:
        user_id = AuthService.decode_token(token)
        return user_id
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        return None


# Background task for cleanup
async def websocket_cleanup_task():
    """Periodic cleanup of expired WebSocket connections"""
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        await secure_ws_manager.cleanup_expired_connections()
