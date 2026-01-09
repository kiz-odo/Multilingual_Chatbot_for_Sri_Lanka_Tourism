"""
Rasa service for NLU and dialogue management
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class RasaService:
    """Rasa service for chatbot interactions"""
    
    def __init__(self):
        self.rasa_url = settings.RASA_SERVER_URL
        self.timeout = 30.0
    
    async def get_response(
        self, 
        message: str, 
        sender_id: str, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get response from Rasa chatbot"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:  # Shorter timeout
                # Send message to Rasa
                response = await client.post(
                    f"{self.rasa_url}/webhooks/rest/webhook",
                    json={
                        "sender": sender_id,
                        "message": message,
                        "metadata": {
                            "language": language
                        }
                    }
                )
                
                if response.status_code == 200:
                    rasa_responses = response.json()
                    
                    # Get the first response (Rasa can return multiple responses)
                    if rasa_responses:
                        return rasa_responses[0]
                    else:
                        return self._get_fallback_response(message, language)
                else:
                    logger.warning(f"Rasa server error: {response.status_code}, using fallback")
                    return self._get_fallback_response(message, language)
                    
        except Exception as e:
            logger.warning(f"Rasa server not available: {str(e)}, using fallback response")
            return self._get_fallback_response(message, language)
    
    async def parse_message(self, message: str, language: str = "en") -> Dict[str, Any]:
        """Parse message to extract intent and entities"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.rasa_url}/model/parse",
                    json={
                        "text": message,
                        "message_id": f"parse_{hash(message)}"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Rasa parse error: {response.status_code}")
                    return {"intent": {"name": "unknown", "confidence": 0.0}, "entities": []}
                    
        except Exception as e:
            logger.error(f"Error parsing message with Rasa: {str(e)}")
            return {"intent": {"name": "unknown", "confidence": 0.0}, "entities": []}
    
    async def train_model(self) -> bool:
        """Trigger Rasa model training"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout for training
                response = await client.post(f"{self.rasa_url}/model/train")
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error training Rasa model: {str(e)}")
            return False
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get Rasa model status"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.rasa_url}/status")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "message": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error getting Rasa status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def add_training_example(
        self, 
        text: str, 
        intent: str, 
        entities: List[Dict[str, Any]] = None
    ) -> bool:
        """Add training example to Rasa (for continuous learning)"""
        try:
            # This would typically involve updating the training data
            # and retraining the model. Implementation depends on your
            # specific Rasa setup and training pipeline.
            
            training_example = {
                "text": text,
                "intent": intent,
                "entities": entities or []
            }
            
            # In a production system, you might:
            # 1. Store this in a training data database
            # 2. Periodically retrain the model with new examples
            # 3. Use Rasa X for interactive learning
            
            logger.info(f"Added training example: {training_example}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding training example: {str(e)}")
            return False
    
    def _get_fallback_response(self, message: str, language: str = "en") -> Dict[str, Any]:
        """Get fallback response when Rasa is unavailable"""
        
        # Simple keyword-based fallback responses
        message_lower = message.lower()
        
        # Greetings
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            responses = {
                "en": "Hello! I'm your Sri Lanka Tourism assistant. How can I help you today?",
                "si": "ආයුබෝවන්! මම ඔබේ ශ්‍රී ලංකා සංචාරක සහායකයා. අද මම ඔබට කෙසේ උදව් කළ හැකිද?",
                "ta": "வணக்கம்! நான் உங்கள் இலங்கை சுற்றுலா உதவியாளர். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?"
            }
        
        # Attractions
        elif any(word in message_lower for word in ["attraction", "place", "visit", "see", "tourist"]):
            responses = {
                "en": "Sri Lanka has many beautiful attractions! Some popular ones include Sigiriya Rock Fortress, Temple of the Tooth in Kandy, and the beaches of Mirissa. What type of attractions interest you?",
                "si": "ශ්‍රී ලංකාවේ බොහෝ ලස්සන ආකර්ෂණීය ස්ථාන තිබේ! සමහර ජනප්‍රිය ඒවා අතර සීගිරිය පර්වත බලකොටුව, කන්දේ දළදා මාළිගාව සහ මිරිස්සේ වෙරළ ඇතුළත් වේ. ඔබ කුමන ආකාරයේ ආකර්ෂණීය ස්ථාන ගැන උනන්දුද?",
                "ta": "இலங்கையில் பல அழகான இடங்கள் உள்ளன! சில பிரபலமான இடங்களில் சிகிரியா பாறை கோட்டை, கண்டியில் உள்ள பல் கோவில் மற்றும் மிரிஸ்ஸாவின் கடற்கரைகள் அடங்கும். எந்த வகையான இடங்கள் உங்களுக்கு ஆர்வமாக உள்ளன?"
            }
        
        # Food
        elif any(word in message_lower for word in ["food", "eat", "restaurant", "cuisine", "dish"]):
            responses = {
                "en": "Sri Lankan cuisine is delicious and diverse! Try rice and curry, kottu roti, hoppers, and string hoppers. Would you like restaurant recommendations or information about specific dishes?",
                "si": "ශ්‍රී ලංකන් ආහාර රසවත් හා විවිධාකාර ය! බත් සහ කරි, කොත්තු රොටි, ආප්ප සහ ඉදි ආප්ප උත්සාහ කරන්න. ඔබට අවන්හල් නිර්දේශ හෝ විශේෂ කෑම වර්ග ගැන තොරතුරු අවශ්‍යද?",
                "ta": "இலங்கை உணவு சுவையாகவும் பல்வகையாகவும் உள்ளது! சாதம் மற்றும் கறி, கொத்து ரொட்டி, ஆப்பம் மற்றும் இடியாப்பம் முயற்சிக்கவும். உங்களுக்கு உணவகப் பரிந்துரைகள் அல்லது குறிப்பிட்ட உணவுகள் பற்றிய தகவல் வேண்டுமா?"
            }
        
        # Transport
        elif any(word in message_lower for word in ["transport", "travel", "bus", "train", "taxi", "get to"]):
            responses = {
                "en": "Sri Lanka has various transportation options including trains, buses, taxis, and tuk-tuks. Where would you like to go? I can help you find the best way to get there.",
                "si": "ශ්‍රී ලංකාවේ දුම්රිය, බස්, කුලී රථ සහ ත්‍රී රෝද ඇතුළු විවිධ ප්‍රවාහන විකල්ප තිබේ. ඔබ කොහේ යන්න කැමතිද? එහි යාමට හොඳම ක්‍රමය සොයා ගැනීමට මම ඔබට උදව් කළ හැකිය.",
                "ta": "இலங்கையில் ரயில், பேருந்து, டாக்சி மற்றும் ட்ரைக் போன்ற பல்வேறு போக்குவரத்து விருப்பங்கள் உள்ளன. நீங்கள் எங்கு செல்ல விரும்புகிறீர்கள்? அங்கு செல்வதற்கான சிறந்த வழியைக் கண்டறிய நான் உங்களுக்கு உதவ முடியும்."
            }
        
        # Default
        else:
            responses = {
                "en": "I'm here to help you with Sri Lanka tourism information. You can ask me about attractions, food, transportation, accommodation, or any other travel-related questions.",
                "si": "ශ්‍රී ලංකා සංචාරක තොරතුරු සමඟ ඔබට උදව් කිරීමට මම මෙහි සිටිමි. ඔබට ආකර්ෂණීය ස්ථාන, ආහාර, ප්‍රවාහනය, නවාතැන් හෝ වෙනත් ගමන් සම්බන්ධ ප්‍රශ්න ගැන මගෙන් විමසිය හැකිය.",
                "ta": "இலங்கை சுற்றுலா தகவல்களுடன் உங்களுக்கு உதவ நான் இங்கே இருக்கிறேன். நீங்கள் என்னிடம் இடங்கள், உணவு, போக்குவரத்து, தங்குமிடம் அல்லது வேறு எந்த பயண தொடர்பான கேள்விகளையும் கேட்கலாம்."
            }
        
        response_text = responses.get(language, responses["en"])
        
        return {
            "text": response_text,
            "intent": {"name": "fallback", "confidence": 1.0},
            "entities": [],
            "provider": "rasa",
            "model": "fallback",
            "confidence": 1.0,
            "sources": []
        }
