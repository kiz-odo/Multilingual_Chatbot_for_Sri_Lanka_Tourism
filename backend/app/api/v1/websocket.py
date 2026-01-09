"""
WebSocket endpoints for real-time chat
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
import logging
import json
from datetime import datetime

from backend.app.services.rasa_service import RasaService
from backend.app.services.translation_service import TranslationService
from backend.app.models.conversation import Conversation, Message, MessageSender, MessageType

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and store connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """Remove connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, message: dict, session_id: str):
        """Send message to specific connection"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    user_id: str = Query(None),
    language: str = Query("en")
):
    """
    WebSocket endpoint for real-time chat
    
    Client sends:
    {
        "message": "Hello",
        "language": "en",
        "message_type": "text"
    }
    
    Server responds:
    {
        "response": "Hello! How can I help you?",
        "intent": "greet",
        "confidence": 0.95,
        "entities": [],
        "timestamp": "2024-..."
    }
    """
    
    # Initialize services
    rasa_service = RasaService()
    translation_service = TranslationService()
    
    # Connect
    await manager.connect(websocket, session_id)
    
    # Get or create conversation
    conversation = await Conversation.find_one(
        Conversation.session_id == session_id
    )
    
    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            primary_language=language
        )
        await conversation.insert()
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "message": "Connected to Sri Lanka Tourism Chatbot"
        })
        
        # Main loop - receive and process messages
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                msg_language = message_data.get("language", language)
                msg_type = message_data.get("message_type", "text")
                
                # Save user message
                conversation.add_message(
                    sender=MessageSender.USER,
                    content=user_message,
                    message_type=MessageType.TEXT,
                    detected_language=msg_language
                )
                await conversation.save()
                
                # Get bot response from Rasa
                rasa_response = await rasa_service.get_response(
                    message=user_message,
                    sender_id=session_id,
                    language=msg_language
                )
                
                bot_text = rasa_response.get("text", "I'm sorry, I didn't understand that.")
                
                # Save bot message
                conversation.add_message(
                    sender=MessageSender.BOT,
                    content=bot_text,
                    message_type=MessageType.TEXT,
                    intent=rasa_response.get("intent", {}).get("name"),
                    entities=rasa_response.get("entities", []),
                    intent_confidence=rasa_response.get("intent", {}).get("confidence")
                )
                await conversation.save()
                
                # Send response
                response = {
                    "type": "message",
                    "response": bot_text,
                    "intent": rasa_response.get("intent", {}),
                    "entities": rasa_response.get("entities", []),
                    "language": msg_language,
                    "timestamp": datetime.utcnow().isoformat(),
                    "buttons": rasa_response.get("buttons", []),
                    "quick_replies": rasa_response.get("quick_replies", [])
                }
                
                await websocket.send_json(response)
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Error processing your message. Please try again."
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"Client {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)


@router.websocket("/ws/voice/{session_id}")
async def websocket_voice(
    websocket: WebSocket,
    session_id: str,
    user_id: str = Query(None),
    language: str = Query("en")
):
    """
    WebSocket endpoint for real-time voice chat
    
    Client sends audio chunks (base64 or binary)
    Server responds with transcription and bot response
    """
    
    from backend.app.services.speech_service import SpeechService
    
    speech_service = SpeechService()
    rasa_service = RasaService()
    
    await manager.connect(websocket, session_id)
    
    try:
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Voice chat ready"
        })
        
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            try:
                # Convert speech to text
                text = await speech_service.speech_to_text(data, language)
                
                if text:
                    # Send transcription
                    await websocket.send_json({
                        "type": "transcription",
                        "text": text
                    })
                    
                    # Get bot response
                    rasa_response = await rasa_service.get_response(
                        message=text,
                        sender_id=session_id,
                        language=language
                    )
                    
                    bot_text = rasa_response.get("text", "")
                    
                    # Convert response to speech
                    audio_data = await speech_service.text_to_speech(bot_text, language)
                    
                    # Send bot response
                    await websocket.send_json({
                        "type": "response",
                        "text": bot_text,
                        "audio": audio_data.hex() if audio_data else None
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Could not transcribe audio"
                    })
            
            except Exception as e:
                logger.error(f"Error processing voice: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Error processing voice input"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        manager.disconnect(session_id)

