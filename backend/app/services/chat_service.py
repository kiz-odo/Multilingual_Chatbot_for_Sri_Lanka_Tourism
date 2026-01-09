"""
Chat service for managing conversations and messages
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from backend.app.models.conversation import (
    Conversation, ConversationCreate, ConversationContext,
    Message, MessageSender, MessageType
)
from backend.app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service class"""
    
    def __init__(self):
        self.user_service = UserService()
    
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text
        
        Args:
            text: Input text to detect language
            
        Returns:
            Language code (en, si, ta)
        """
        if not text or not text.strip():
            return "en"
        
        try:
            # Check for Sinhala unicode range (0D80-0DFF)
            has_sinhala = any(0x0D80 <= ord(c) <= 0x0DFF for c in text)
            if has_sinhala:
                return 'si'
            
            # Check for Tamil unicode range (0B80-0BFF)
            has_tamil = any(0x0B80 <= ord(c) <= 0x0BFF for c in text)
            if has_tamil:
                return 'ta'
            
            # Use langdetect for other languages
            from langdetect import detect
            detected = detect(text)
            
            # Map detected language to supported languages
            if detected == 'ta':
                return 'ta'
            return "en"
        except:
            # Default to English if detection fails
            return "en"
    
    async def call_rasa(self, message: str, sender: str = "user") -> list:
        """
        Call Rasa NLU service to process message
        
        Args:
            message: User message text
            sender: Sender ID
            
        Returns:
            List of response dictionaries from Rasa
        """
        # Placeholder for Rasa integration
        # In production, this would call the Rasa server
        return [{
            "text": "This is a placeholder response. Rasa integration pending.",
            "intent": {"name": "greet", "confidence": 0.9},
            "entities": []
        }]
    
    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            message: User message text
            user_id: User ID
            session_id: Session ID
            language: Language code
            
        Returns:
            Response dictionary with text and metadata
        """
        try:
            # Call Rasa to get response
            rasa_response = await self.call_rasa(message, sender=user_id or "anonymous")
            
            # Extract text from response
            if rasa_response and len(rasa_response) > 0:
                response_text = rasa_response[0].get("text", "I'm sorry, I couldn't understand that.")
                intent = self.extract_intent(rasa_response)
                entities = self.extract_entities(rasa_response)
                
                return {
                    "text": response_text,
                    "intent": intent,
                    "entities": entities,
                    "language": language
                }
            else:
                return {
                    "text": "I'm sorry, I couldn't process your request.",
                    "intent": None,
                    "entities": [],
                    "language": language
                }
        except Exception as e:
            # Fallback response on error
            return {
                "text": "I'm experiencing technical difficulties. Please try again.",
                "intent": None,
                "entities": [],
                "language": language,
                "error": str(e)
            }
    
    async def get_or_create_conversation(
        self, 
        user_id: Optional[str], 
        session_id: str, 
        language: str = "en"
    ) -> Conversation:
        """Get existing conversation or create new one"""
        
        # Try to find existing conversation by session_id
        conversation = await Conversation.find_one({"session_id": session_id})
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                primary_language=language,
                context=ConversationContext()
            )
            await conversation.save()
            
            # Update user stats if user is logged in
            if user_id:
                await self.user_service.update_user_stats(user_id, increment_conversations=True)
        
        return conversation
    
    async def get_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Optional[Conversation]:
        """Get conversation by ID"""
        try:
            conversation = await Conversation.get(conversation_id)
            
            # Check if user has access to this conversation
            if user_id and conversation.user_id != user_id:
                return None
            
            return conversation
        except:
            return None
    
    async def get_user_conversations(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Conversation]:
        """Get user's conversations"""
        return await Conversation.find(
            Conversation.user_id == user_id
        ).sort(-Conversation.updated_at).skip(offset).limit(limit).to_list()
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        await conversation.delete()
        return True
    
    async def delete_all_user_conversations(self, user_id: str) -> bool:
        """Delete all conversations for a user"""
        try:
            result = await Conversation.find(
                Conversation.user_id == user_id
            ).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting user conversations: {e}")
            return False
    
    async def add_message_to_conversation(
        self,
        conversation_id: str,
        sender: MessageSender,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        **kwargs
    ) -> Optional[Conversation]:
        """Add message to conversation"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        conversation.add_message(sender, content, message_type, **kwargs)
        await conversation.save()
        
        # Update user stats if user message
        if sender == MessageSender.USER and conversation.user_id:
            await self.user_service.update_user_stats(conversation.user_id, increment_queries=True)
        
        return conversation
    
    async def update_conversation_context(
        self,
        conversation_id: str,
        context_updates: Dict[str, Any]
    ) -> Optional[Conversation]:
        """Update conversation context"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        # Update context
        for key, value in context_updates.items():
            if hasattr(conversation.context, key):
                setattr(conversation.context, key, value)
            else:
                conversation.context.session_variables[key] = value
        
        conversation.updated_at = datetime.utcnow()
        await conversation.save()
        return conversation
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Message]:
        """Get conversation message history"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation.get_recent_messages(limit)
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Conversation]:
        """Search conversations by content"""
        # This is a basic implementation - in production, you might want to use
        # a more sophisticated search engine like Elasticsearch
        conversations = await Conversation.find(
            Conversation.user_id == user_id
        ).to_list()
        
        matching_conversations = []
        for conv in conversations:
            # Search in messages
            for message in conv.messages:
                if query.lower() in message.content.lower():
                    matching_conversations.append(conv)
                    break
            
            if len(matching_conversations) >= limit:
                break
        
        return matching_conversations
    
    async def get_suggestions(self, intent: Optional[str] = None, language: str = "en") -> List[str]:
        """Get conversation suggestions based on intent and language"""
        
        # Default suggestions by language
        suggestions_by_language = {
            "en": [
                "What are the popular attractions in Sri Lanka?",
                "Tell me about Sri Lankan food",
                "How can I get around in Sri Lanka?",
                "What's the weather like?",
                "Emergency contacts in Sri Lanka"
            ],
            "si": [
                "ශ්‍රී ලංකාවේ ප්‍රසිද්ධ ආකර්ෂණීය ස්ථාන මොනවද?",
                "ශ්‍රී ලංකන් ආහාර ගැන කියන්න",
                "ශ්‍රී ලංකාවේ ගමන් කරන්නේ කොහොමද?",
                "කාලගුණය කොහොමද?",
                "හදිසි සම්බන්ධතා"
            ],
            "ta": [
                "இலங்கையின் பிரபலமான இடங்கள் எவை?",
                "இலங்கை உணவு பற்றி சொல்லுங்கள்",
                "இலங்கையில் எப்படி பயணம் செய்வது?",
                "வானிலை எப்படி உள்ளது?",
                "அவசர தொடர்புகள்"
            ]
        }
        
        # Intent-specific suggestions
        intent_suggestions = {
            "ask_attractions": [
                "Tell me about historical sites",
                "What beaches should I visit?",
                "Show me wildlife parks"
            ],
            "ask_food": [
                "What are traditional Sri Lankan dishes?",
                "Where can I find good restaurants?",
                "Tell me about local street food"
            ],
            "ask_transport": [
                "How to get to Kandy?",
                "Train schedules to Ella",
                "Taxi services in Colombo"
            ],
            "ask_accommodation": [
                "Hotels in Galle",
                "Budget stays in Sigiriya",
                "Beach resorts in Mirissa"
            ]
        }
        
        if intent and intent in intent_suggestions:
            return intent_suggestions[intent]
        
        return suggestions_by_language.get(language, suggestions_by_language["en"])
    
    async def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        conversations = await Conversation.find(Conversation.user_id == user_id).to_list()
        
        total_conversations = len(conversations)
        total_messages = sum(len(conv.messages) for conv in conversations)
        total_user_messages = sum(
            len([msg for msg in conv.messages if msg.sender == MessageSender.USER])
            for conv in conversations
        )
        
        # Language distribution
        language_count = {}
        for conv in conversations:
            lang = conv.primary_language
            language_count[lang] = language_count.get(lang, 0) + 1
        
        # Most active conversation
        most_active_conv = max(conversations, key=lambda c: len(c.messages)) if conversations else None
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_user_messages": total_user_messages,
            "language_distribution": language_count,
            "most_active_conversation_id": str(most_active_conv.id) if most_active_conv else None,
            "average_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0
        }
    
    async def format_response(self, response: Dict[str, Any], language: str = "en", **kwargs) -> Dict[str, Any]:
        """
        Format chatbot response with language-specific formatting
        
        Args:
            response: Response dictionary from Rasa
            language: Target language
            **kwargs: Additional formatting options
            
        Returns:
            Formatted response dictionary with text key
        """
        # Extract text from response
        if isinstance(response, dict):
            text = response.get("text", "")
        else:
            text = str(response)
        
        # Basic formatting
        formatted_text = text.strip()
        
        # Add language-specific formatting if needed
        if language == "si" and not any(ord(c) > 0x0D80 for c in formatted_text):
            # Response is in English but language is Sinhala - could trigger translation
            pass
        
        return {
            "text": formatted_text,
            "language": language,
            **{k: v for k, v in response.items() if k != "text"}
        }
    
    def extract_entities(self, rasa_response: list) -> list:
        """
        Extract entities from Rasa response
        
        Args:
            rasa_response: Rasa response list containing entities
            
        Returns:
            List of entity dictionaries
        """
        if not rasa_response or not isinstance(rasa_response, list) or len(rasa_response) == 0:
            return []
        
        # Extract entities from first response
        first_response = rasa_response[0]
        entities = first_response.get("entities", [])
        
        return entities if isinstance(entities, list) else []
    
    def extract_intent(self, rasa_response: list) -> Optional[str]:
        """
        Extract user intent from Rasa response
        
        Args:
            rasa_response: Rasa response list containing intent
            
        Returns:
            Intent string or None
        """
        if not rasa_response or not isinstance(rasa_response, list) or len(rasa_response) == 0:
            return None
        
        # Extract intent from first response
        first_response = rasa_response[0]
        intent_data = first_response.get("intent")
        
        if isinstance(intent_data, dict):
            return intent_data.get("name")
        elif isinstance(intent_data, str):
            return intent_data
        
        return None
    
    async def save_conversation(self, conversation_data: Dict[str, Any]) -> None:
        """
        Save conversation to database
        
        Args:
            conversation_data: Dictionary containing conversation data
        """
        # Create or update conversation
        # This is a simplified version - in production, would handle full conversation persistence
        pass
    
    def generate_suggestions(self, context: Dict[str, Any], language: str = "en") -> list[str]:
        """
        Generate contextual suggestions for user
        
        Args:
            context: Conversation context
            language: Language for suggestions
            
        Returns:
            List of suggestion strings
        """
        suggestions = {
            "en": [
                "Show me attractions",
                "Find hotels",
                "Check weather",
                "Plan an itinerary"
            ],
            "si": [
                "ආකර්ෂණීය ස්ථාන පෙන්වන්න",
                "හෝටල් සොයන්න",
                "කාලගුණය පරීක්ෂා කරන්න",
                "සංචාරයක් සැලසුම් කරන්න"
            ],
            "ta": [
                "ஈர்ப்புகளைக் காட்டு",
                "ஹோட்டல்களைக் கண்டுபிடி",
                "வானிலையைச் சரிபார்",
                "பயணத்தைத் திட்டமிடு"
            ]
        }
        
        return suggestions.get(language, suggestions["en"])
