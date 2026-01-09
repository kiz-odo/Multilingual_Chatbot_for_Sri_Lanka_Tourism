"""
Conversation model for the Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Message types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    LOCATION = "location"
    QUICK_REPLY = "quick_reply"
    CAROUSEL = "carousel"
    BUTTON = "button"


class MessageSender(str, Enum):
    """Message sender types"""
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Conversation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Message(BaseModel):
    """Individual message model"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    sender: MessageSender
    message_type: MessageType = MessageType.TEXT
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Language detection
    detected_language: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Intent and entities (from Rasa)
    intent: Optional[str] = None
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    intent_confidence: Optional[float] = None
    
    # Response metadata
    response_time: Optional[float] = None  # in seconds
    external_apis_used: List[str] = Field(default_factory=list)


class ConversationContext(BaseModel):
    """Conversation context model"""
    current_topic: Optional[str] = None
    user_location: Optional[Dict[str, Any]] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    session_variables: Dict[str, Any] = Field(default_factory=dict)
    last_intent: Optional[str] = None
    conversation_flow: List[str] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    """Conversation summary model"""
    total_messages: int = 0
    user_messages: int = 0
    bot_messages: int = 0
    primary_language: Optional[str] = None
    main_topics: List[str] = Field(default_factory=list)
    user_satisfaction: Optional[float] = None
    resolved_queries: List[str] = Field(default_factory=list)


class Conversation(Document):
    """Conversation document model"""
    
    # Basic Information
    user_id: Optional[Indexed(str)] = None  # Allow anonymous users
    session_id: str
    title: Optional[str] = None
    
    # Messages
    messages: List[Message] = Field(default_factory=list)
    
    # Context and State
    context: ConversationContext = Field(default_factory=ConversationContext)
    status: ConversationStatus = ConversationStatus.ACTIVE
    
    # Language and Localization
    primary_language: str = "en"
    supported_languages: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    
    # Analytics
    summary: ConversationSummary = Field(default_factory=ConversationSummary)
    
    # Additional Data
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "conversations"
        indexes = [
            "user_id",
            "session_id",
            "created_at",
            "status",
            "primary_language"
        ]
    
    def add_message(self, sender: MessageSender, content: str, message_type: MessageType = MessageType.TEXT, **kwargs):
        """Add a message to the conversation"""
        message = Message(
            sender=sender,
            content=content,
            message_type=message_type,
            **kwargs
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        
        # Update summary
        self.summary.total_messages += 1
        if sender == MessageSender.USER:
            self.summary.user_messages += 1
        elif sender == MessageSender.BOT:
            self.summary.bot_messages += 1
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages"""
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def get_conversation_duration(self) -> Optional[float]:
        """Get conversation duration in seconds"""
        if not self.messages:
            return None
        
        start_time = self.messages[0].timestamp
        end_time = self.messages[-1].timestamp
        return (end_time - start_time).total_seconds()


class ConversationCreate(BaseModel):
    """Conversation creation model"""
    user_id: Optional[str] = None  # Allow anonymous users
    session_id: Optional[str] = None
    title: Optional[str] = None
    primary_language: str = "en"


class ConversationUpdate(BaseModel):
    """Conversation update model"""
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    context: Optional[ConversationContext] = None
    tags: Optional[List[str]] = None


class MessageCreate(BaseModel):
    """Message creation model"""
    sender: MessageSender
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: str
    user_id: Optional[str] = None  # Allow anonymous users
    session_id: str
    title: Optional[str] = None
    status: ConversationStatus
    primary_language: str
    messages: List[Message]
    context: ConversationContext
    summary: ConversationSummary
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime] = None
