"""
Custom Rasa Actions for Sri Lanka Tourism Chatbot
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

# Backend API URL - should match your FastAPI server
BACKEND_API_URL = "http://localhost:8000/api/v1"


class ActionSearchAttractions(Action):
    """Action to search for attractions"""
    
    def name(self) -> Text:
        return "action_search_attractions"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get entities and slots
        category = next(tracker.get_latest_entity_values("category"), None)
        location = tracker.get_slot("user_location")
        attraction_name = next(tracker.get_latest_entity_values("attraction_name"), None)
        user_language = tracker.get_slot("user_language") or "en"
        
        try:
            # Call backend API
            async with httpx.AsyncClient() as client:
                params = {
                    "category": category,
                    "location": location,
                    "name": attraction_name,
                    "limit": 5,
                    "language": user_language
                }
                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}
                
                response = await client.get(f"{BACKEND_API_URL}/attractions/search", params=params)
                
                if response.status_code == 200:
                    attractions = response.json()
                    
                    if attractions:
                        message = self._format_attractions_response(attractions, user_language)
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text="I couldn't find any attractions matching your criteria. Try asking about a different category or location.")
                else:
                    dispatcher.utter_message(text="I'm having trouble accessing attraction information right now. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Error searching attractions: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I encountered an error while searching for attractions. Please try again.")
        
        return []
    
    def _format_attractions_response(self, attractions: List[Dict], language: str) -> str:
        """Format attractions response based on language"""
        
        if language == "si":
            header = "🏛️ ආකර්ෂණීය ස්ථාන:\n\n"
        elif language == "ta":
            header = "🏛️ சுற்றுலா இடங்கள்:\n\n"
        else:
            header = "🏛️ Here are some amazing attractions:\n\n"
        
        formatted_attractions = []
        
        for attraction in attractions[:3]:  # Limit to 3 attractions
            name = attraction.get("name", {}).get(language, attraction.get("name", {}).get("en", "Unknown"))
            description = attraction.get("short_description", {}).get(language, 
                         attraction.get("short_description", {}).get("en", ""))
            category = attraction.get("category", "").replace("_", " ").title()
            location = attraction.get("location", {}).get("city", "")
            
            formatted_attraction = f"📍 **{name}**\n"
            if location:
                formatted_attraction += f"📍 {location}\n"
            if description:
                formatted_attraction += f"{description}\n"
            if category:
                formatted_attraction += f"🏷️ Category: {category}\n"
            
            formatted_attractions.append(formatted_attraction)
        
        return header + "\n".join(formatted_attractions) + "\n\nWould you like more details about any of these places?"


class ActionSearchRestaurants(Action):
    """Action to search for restaurants"""
    
    def name(self) -> Text:
        return "action_search_restaurants"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get entities and slots
        cuisine_type = next(tracker.get_latest_entity_values("cuisine_type"), None)
        location = tracker.get_slot("user_location")
        restaurant_name = next(tracker.get_latest_entity_values("restaurant_name"), None)
        price_range = tracker.get_slot("budget_range")
        user_language = tracker.get_slot("user_language") or "en"
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "cuisine_type": cuisine_type,
                    "location": location,
                    "name": restaurant_name,
                    "price_range": price_range,
                    "limit": 5,
                    "language": user_language
                }
                params = {k: v for k, v in params.items() if v is not None}
                
                response = await client.get(f"{BACKEND_API_URL}/restaurants/search", params=params)
                
                if response.status_code == 200:
                    restaurants = response.json()
                    
                    if restaurants:
                        message = self._format_restaurants_response(restaurants, user_language)
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text="I couldn't find any restaurants matching your preferences. Try asking about a different cuisine or location.")
                else:
                    dispatcher.utter_message(text="I'm having trouble accessing restaurant information right now. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I encountered an error while searching for restaurants. Please try again.")
        
        return []
    
    def _format_restaurants_response(self, restaurants: List[Dict], language: str) -> str:
        """Format restaurants response based on language"""
        
        if language == "si":
            header = "🍽️ අවන්හල්:\n\n"
        elif language == "ta":
            header = "🍽️ உணவகங்கள்:\n\n"
        else:
            header = "🍽️ Here are some great restaurants:\n\n"
        
        formatted_restaurants = []
        
        for restaurant in restaurants[:3]:
            name = restaurant.get("name", {}).get(language, restaurant.get("name", {}).get("en", "Unknown"))
            description = restaurant.get("short_description", {}).get(language,
                         restaurant.get("short_description", {}).get("en", ""))
            cuisine_types = restaurant.get("cuisine_types", [])
            price_range = restaurant.get("price_range", "").replace("_", " ").title()
            location = restaurant.get("location", {}).get("city", "")
            
            formatted_restaurant = f"🍽️ **{name}**\n"
            if location:
                formatted_restaurant += f"📍 {location}\n"
            if description:
                formatted_restaurant += f"{description}\n"
            if cuisine_types:
                formatted_restaurant += f"🍳 Cuisine: {', '.join(cuisine_types)}\n"
            if price_range:
                formatted_restaurant += f"💰 Price Range: {price_range}\n"
            
            formatted_restaurants.append(formatted_restaurant)
        
        return header + "\n".join(formatted_restaurants) + "\n\nWould you like more information about any of these restaurants?"


class ActionSearchHotels(Action):
    """Action to search for hotels"""
    
    def name(self) -> Text:
        return "action_search_hotels"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get entities and slots
        location = tracker.get_slot("user_location")
        hotel_name = next(tracker.get_latest_entity_values("hotel_name"), None)
        budget_range = tracker.get_slot("budget_range")
        user_language = tracker.get_slot("user_language") or "en"
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "location": location,
                    "name": hotel_name,
                    "budget_range": budget_range,
                    "limit": 5,
                    "language": user_language
                }
                params = {k: v for k, v in params.items() if v is not None}
                
                response = await client.get(f"{BACKEND_API_URL}/hotels/search", params=params)
                
                if response.status_code == 200:
                    hotels = response.json()
                    
                    if hotels:
                        message = self._format_hotels_response(hotels, user_language)
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text="I couldn't find any hotels matching your criteria. Try asking about a different location or budget range.")
                else:
                    dispatcher.utter_message(text="I'm having trouble accessing hotel information right now. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Error searching hotels: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I encountered an error while searching for hotels. Please try again.")
        
        return []
    
    def _format_hotels_response(self, hotels: List[Dict], language: str) -> str:
        """Format hotels response based on language"""
        
        if language == "si":
            header = "🏨 හෝටල්:\n\n"
        elif language == "ta":
            header = "🏨 ஹோட்டல்கள்:\n\n"
        else:
            header = "🏨 Here are some excellent hotels:\n\n"
        
        formatted_hotels = []
        
        for hotel in hotels[:3]:
            name = hotel.get("name", {}).get(language, hotel.get("name", {}).get("en", "Unknown"))
            description = hotel.get("short_description", {}).get(language,
                         hotel.get("short_description", {}).get("en", ""))
            category = hotel.get("category", "").replace("_", " ").title()
            star_rating = hotel.get("star_rating", "")
            location = hotel.get("location", {}).get("city", "")
            
            formatted_hotel = f"🏨 **{name}**\n"
            if location:
                formatted_hotel += f"📍 {location}\n"
            if description:
                formatted_hotel += f"{description}\n"
            if star_rating and star_rating != "unrated":
                formatted_hotel += f"⭐ {star_rating} star\n"
            if category:
                formatted_hotel += f"🏷️ Category: {category}\n"
            
            formatted_hotels.append(formatted_hotel)
        
        return header + "\n".join(formatted_hotels) + "\n\nWould you like more details about any of these hotels?"


class ActionSearchTransport(Action):
    """Action to search for transport options"""
    
    def name(self) -> Text:
        return "action_search_transport"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get entities and slots
        transport_type = next(tracker.get_latest_entity_values("transport_type"), None)
        origin = next(tracker.get_latest_entity_values("location"), None)
        destination = tracker.get_slot("user_location")
        user_language = tracker.get_slot("user_language") or "en"
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "transport_type": transport_type,
                    "origin": origin,
                    "destination": destination,
                    "limit": 5,
                    "language": user_language
                }
                params = {k: v for k, v in params.items() if v is not None}
                
                response = await client.get(f"{BACKEND_API_URL}/transport/search", params=params)
                
                if response.status_code == 200:
                    transport_options = response.json()
                    
                    if transport_options:
                        message = self._format_transport_response(transport_options, user_language)
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text="I couldn't find any transport options matching your criteria. Try asking about a different route or transport type.")
                else:
                    dispatcher.utter_message(text="I'm having trouble accessing transport information right now. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Error searching transport: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I encountered an error while searching for transport options. Please try again.")
        
        return []
    
    def _format_transport_response(self, transport_options: List[Dict], language: str) -> str:
        """Format transport response based on language"""
        
        if language == "si":
            header = "🚂 ප්‍රවාහන විකල්ප:\n\n"
        elif language == "ta":
            header = "🚂 போக்குவரத்து விருப்பங்கள்:\n\n"
        else:
            header = "🚂 Here are your transport options:\n\n"
        
        formatted_options = []
        
        for option in transport_options[:3]:
            name = option.get("name", {}).get(language, option.get("name", {}).get("en", "Unknown"))
            transport_type = option.get("transport_type", "").replace("_", " ").title()
            category = option.get("category", "").replace("_", " ").title()
            
            formatted_option = f"🚂 **{name}**\n"
            formatted_option += f"🚌 Type: {transport_type}\n"
            if category:
                formatted_option += f"🏷️ Category: {category}\n"
            
            # Add route information if available
            routes = option.get("routes", [])
            if routes:
                route = routes[0]  # Show first route
                if route.get("origin") and route.get("destination"):
                    formatted_option += f"📍 Route: {route['origin']} → {route['destination']}\n"
                if route.get("duration_minutes"):
                    hours = route['duration_minutes'] // 60
                    minutes = route['duration_minutes'] % 60
                    formatted_option += f"⏱️ Duration: {hours}h {minutes}m\n"
            
            formatted_options.append(formatted_option)
        
        return header + "\n".join(formatted_options) + "\n\nWould you like more details about any of these transport options?"


class ActionChangeLanguage(Action):
    """Action to change the conversation language"""
    
    def name(self) -> Text:
        return "action_change_language"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get requested language
        requested_language = next(tracker.get_latest_entity_values("language"), "en")
        
        # Map language names to codes
        language_mapping = {
            "english": "en",
            "sinhala": "si",
            "tamil": "ta",
            "german": "de",
            "french": "fr",
            "chinese": "zh",
            "japanese": "ja",
            "සිංහල": "si",
            "தமிழ்": "ta"
        }
        
        language_code = language_mapping.get(requested_language.lower(), requested_language.lower())
        
        # Confirm language change
        confirmations = {
            "en": "Language changed to English. How can I help you explore Sri Lanka?",
            "si": "භාෂාව සිංහලට වෙනස් කරන ලදි. ශ්‍රී ලංකාව ගවේෂණය කිරීමට මම ඔබට කෙසේ උදව් කළ හැකිද?",
            "ta": "மொழி தமிழுக்கு மாற்றப்பட்டது. இலங்கையை ஆராய நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "de": "Sprache auf Deutsch geändert. Wie kann ich Ihnen bei der Erkundung Sri Lankas helfen?",
            "fr": "Langue changée en français. Comment puis-je vous aider à explorer le Sri Lanka?",
            "zh": "语言已更改为中文。我如何帮助您探索斯里兰卡？",
            "ja": "言語が日本語に変更されました。スリランカの探索をどのようにお手伝いできますか？"
        }
        
        confirmation_message = confirmations.get(language_code, confirmations["en"])
        dispatcher.utter_message(text=confirmation_message)
        
        return [SlotSet("user_language", language_code)]


class ActionGetDirections(Action):
    """Action to get directions between locations"""
    
    def name(self) -> Text:
        return "action_get_directions"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get location entities
        locations = list(tracker.get_latest_entity_values("location"))
        user_language = tracker.get_slot("user_language") or "en"
        
        if len(locations) >= 2:
            origin = locations[0]
            destination = locations[1]
        else:
            # Use user's current location as origin if available
            origin = tracker.get_slot("user_location")
            destination = locations[0] if locations else None
        
        if not origin or not destination:
            if user_language == "si":
                dispatcher.utter_message(text="කරුණාකර ආරම්භක ස්ථානය සහ ගමනාන්තය දෙකම සඳහන් කරන්න.")
            elif user_language == "ta":
                dispatcher.utter_message(text="தயவுசெய்து தொடக்க இடம் மற்றும் இலக்கு இரண்டையும் குறிப்பிடுங்கள்.")
            else:
                dispatcher.utter_message(text="Please specify both origin and destination locations.")
            return []
        
        try:
            # This would typically call Google Maps API or similar
            # For now, provide general directions advice
            if user_language == "si":
                message = f"🗺️ {origin} සිට {destination} දක්වා යාමට:\n\n"
                message += "• දුම්රිය: වඩාත් දර්ශනීය සහ ආරක්ෂිත\n"
                message += "• බස්: ලාභදායී විකල්පය\n"
                message += "• කුලී රථ: වේගවත් හා පහසු\n"
                message += "• ත්‍රී රෝද: කෙටි දුරවල් සඳහා\n\n"
                message += "වැඩි විස්තර සඳහා ප්‍රවාහන විකල්ප ගැන විමසන්න."
            elif user_language == "ta":
                message = f"🗺️ {origin} இலிருந்து {destination} செல்ல:\n\n"
                message += "• ரயில்: மிகவும் அழகான மற்றும் பாதுகாப்பான\n"
                message += "• பேருந்து: மலிவான விருப்பம்\n"
                message += "• டாக்சி: வேகமான மற்றும் வசதியான\n"
                message += "• ட்ரைக்: குறுகிய தூரங்களுக்கு\n\n"
                message += "மேலும் விவரங்களுக்கு போக்குவரத்து விருப்பங்களைப் பற்றி கேளுங்கள்."
            else:
                message = f"🗺️ Getting from {origin} to {destination}:\n\n"
                message += "• Train: Most scenic and comfortable\n"
                message += "• Bus: Budget-friendly option\n"
                message += "• Taxi: Fast and convenient\n"
                message += "• Tuk-tuk: For short distances\n\n"
                message += "Ask about transport options for more details."
            
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            logger.error(f"Error getting directions: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I encountered an error while getting directions. Please try again.")
        
        return []


class ActionDefaultFallback(Action):
    """Default fallback action"""
    
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        user_language = tracker.get_slot("user_language") or "en"
        
        fallback_messages = {
            "en": "I'm sorry, I didn't understand that. I can help you with information about Sri Lankan attractions, restaurants, hotels, transport, culture, and more. What would you like to know?",
            "si": "මට ඒක තේරුණේ නැහැ. ශ්‍රී ලංකන් ආකර්ෂණීය ස්ථාන, අවන්හල්, හෝටල්, ප්‍රවාහනය, සංස්කෘතිය සහ තවත් බොහෝ දේ ගැන තොරතුරු සමඟ මම ඔබට උදව් කළ හැකිය. ඔබ දැන ගැනීමට කැමති කුමක්ද?",
            "ta": "மன்னிக்கவும், நான் அதை புரிந்து கொள்ளவில்லை. இலங்கை சுற்றுலா இடங்கள், உணவகங்கள், ஹோட்டல்கள், போக்குவரத்து, கலாச்சாரம் மற்றும் பலவற்றைப் பற்றிய தகவல்களுடன் நான் உங்களுக்கு உதவ முடியும். நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?"
        }
        
        message = fallback_messages.get(user_language, fallback_messages["en"])
        dispatcher.utter_message(text=message)
        
        return []
