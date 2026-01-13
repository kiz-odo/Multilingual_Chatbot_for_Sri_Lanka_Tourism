"""
CrewAI Service - Multi-agent orchestration for tourism chatbot
Uses CrewAI framework to create specialized agents for different tourism tasks
"""

from typing import Dict, Any, Optional, List
import logging
import asyncio

# Helper function to run async code from sync context
def run_async(coro):
    """Run async coroutine from sync context, handling existing event loops"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need nest_asyncio
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(coro)
            except ImportError:
                # Fallback: create new thread with new event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(coro)

try:
    from crewai import Agent, Task, Crew
    try:
        from crewai.tools import tool
    except ImportError:
        from crewai_tools import tool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI library not installed. CrewAI features will be disabled.")
    
    # Define dummy classes/decorators when crewai is not available
    def tool(func):
        """Dummy tool decorator when CrewAI is not installed"""
        return func
    
    class Agent:
        """Dummy Agent class when CrewAI is not installed"""
        def __init__(self, *args, **kwargs):
            pass
    
    class Task:
        """Dummy Task class when CrewAI is not installed"""
        def __init__(self, *args, **kwargs):
            pass
    
    class Crew:
        """Dummy Crew class when CrewAI is not installed"""
        def __init__(self, *args, **kwargs):
            pass
        def kickoff(self):
            return "CrewAI not available"

from backend.app.core.config import settings
from backend.app.services.attraction_service import AttractionService
from backend.app.services.itinerary_service import ItineraryService
from backend.app.services.weather_service import WeatherService
from backend.app.services.currency_service import CurrencyService
from backend.app.services.maps_service import MapsService
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.event import Event
from backend.app.models.transport import Transport

logger = logging.getLogger(__name__)


# CrewAI Tools - Functions that agents can use
@tool
def search_attractions(query: str, category: Optional[str] = None, city: Optional[str] = None) -> str:
    """Search for tourist attractions in Sri Lanka
    
    Args:
        query: Search query
        category: Optional category filter
        city: Optional city filter
    
    Returns:
        Formatted string with attraction information
    """
    try:
        service = AttractionService()
        attractions = run_async(service.search_attractions(
            query=query,
            category=category,
            location=city,
            limit=5
        ))
        
        if not attractions:
            return f"No attractions found for '{query}'"
        
        result = f"Found {len(attractions)} attractions:\n\n"
        for attr in attractions:
            name = attr.name.get("en", "Unknown")
            desc = attr.short_description.get("en", "")
            location = f"{attr.location.city}, {attr.location.province}"
            result += f"- {name} ({location})\n  {desc}\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error in search_attractions tool: {e}")
        return f"Error searching attractions: {str(e)}"


@tool
def get_weather(location: str) -> str:
    """Get current weather information for a location in Sri Lanka
    
    Args:
        location: City or location name
    
    Returns:
        Weather information as formatted string
    """
    try:
        service = WeatherService()
        weather = run_async(service.get_current_weather(city=location))
        
        if not weather:
            return f"Weather information not available for {location}"
        
        temp = weather.get("main", {}).get("temp", "N/A")
        description = weather.get("weather", [{}])[0].get("description", "N/A")
        humidity = weather.get("main", {}).get("humidity", "N/A")
        
        return f"Weather in {location}: {description}, Temperature: {temp}°C, Humidity: {humidity}%"
    except Exception as e:
        logger.error(f"Error in get_weather tool: {e}")
        return f"Error getting weather: {str(e)}"


@tool
def search_hotels(location: str, budget: Optional[str] = None, 
                  star_rating: Optional[str] = None) -> str:
    """Search for hotels in a location
    
    Args:
        location: City or location name
        budget: Optional budget range (budget, mid-range, luxury)
        star_rating: Optional star rating (one_star, two_star, three_star, four_star, five_star)
    
    Returns:
        Hotel information as formatted string
    """
    try:
        # Query hotels directly from database
        query = Hotel.find(Hotel.is_active == True)
        
        if location:
            query = query.find(Hotel.location.city == location)
        
        if star_rating:
            query = query.find(Hotel.star_rating == star_rating)
        
        hotels = run_async(query.sort(-Hotel.average_rating).limit(5).to_list())
        
        if not hotels:
            return f"No hotels found in {location}"
        
        result = f"Found {len(hotels)} hotels in {location}:\n\n"
        for hotel in hotels:
            name = hotel.name.get("en", "Unknown")
            desc = hotel.short_description.get("en", "")
            location_str = f"{hotel.location.city}, {hotel.location.province}"
            price_range = hotel.get_price_range()
            result += f"- {name} ({location_str})\n"
            result += f"  {desc}\n"
            result += f"  Price: {price_range['min']:.0f} - {price_range['max']:.0f} LKR/night\n"
            result += f"  Rating: {hotel.average_rating}/5.0 ({hotel.total_reviews} reviews)\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error in search_hotels tool: {e}")
        return f"Error searching hotels: {str(e)}"


@tool
def search_restaurants(location: str, cuisine: Optional[str] = None,
                      price_range: Optional[str] = None) -> str:
    """Search for restaurants in a location
    
    Args:
        location: City or location name
        cuisine: Optional cuisine type
        price_range: Optional price range (budget, moderate, expensive)
    
    Returns:
        Restaurant information as formatted string
    """
    try:
        # Query restaurants directly from database
        query = Restaurant.find(Restaurant.is_active == True)
        
        if location:
            query = query.find(Restaurant.location.city == location)
        
        if cuisine:
            # Match cuisine type (case-insensitive)
            from backend.app.models.restaurant import CuisineType
            try:
                cuisine_enum = CuisineType(cuisine.lower())
                query = query.find(Restaurant.cuisine_types == cuisine_enum)
            except:
                pass  # If enum doesn't match, ignore filter
        
        if price_range:
            query = query.find(Restaurant.price_range == price_range)
        
        restaurants = run_async(query.sort(-Restaurant.average_rating).limit(5).to_list())
        
        if not restaurants:
            return f"No restaurants found in {location}"
        
        result = f"Found {len(restaurants)} restaurants in {location}:\n\n"
        for rest in restaurants:
            name = rest.name.get("en", "Unknown")
            desc = rest.short_description.get("en", "")
            location_str = f"{rest.location.city}, {rest.location.province}"
            cuisines = ", ".join([c.value for c in rest.cuisine_types[:3]])
            result += f"- {name} ({location_str})\n"
            result += f"  {desc}\n"
            result += f"  Cuisine: {cuisines}\n"
            result += f"  Price Range: {rest.price_range.value}\n"
            result += f"  Rating: {rest.average_rating}/5.0 ({rest.total_reviews} reviews)\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error in search_restaurants tool: {e}")
        return f"Error searching restaurants: {str(e)}"


@tool
def search_events(location: Optional[str] = None, 
                  category: Optional[str] = None,
                  date: Optional[str] = None) -> str:
    """Search for events and festivals in Sri Lanka
    
    Args:
        location: Optional city or location name
        category: Optional event category
        date: Optional date filter (YYYY-MM-DD)
    
    Returns:
        Event information as formatted string
    """
    try:
        from datetime import datetime
        
        query = Event.find(Event.status == "published")
        
        if location:
            query = query.find(Event.location.city == location)
        
        if category:
            from backend.app.models.event import EventCategory
            try:
                category_enum = EventCategory(category.lower())
                query = query.find(Event.category == category_enum)
            except:
                pass
        
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                query = query.find(Event.schedule.start_date <= filter_date)
            except:
                pass
        
        events = run_async(query.sort(-Event.schedule.start_date).limit(5).to_list())
        
        if not events:
            return f"No events found" + (f" in {location}" if location else "")
        
        result = f"Found {len(events)} events:\n\n"
        for event in events:
            title = event.title.get("en", "Unknown")
            desc = event.short_description.get("en", "")
            location_str = f"{event.location.city}, {event.location.province}"
            start_date = event.schedule.start_date.strftime("%Y-%m-%d")
            result += f"- {title} ({location_str})\n"
            result += f"  {desc}\n"
            result += f"  Date: {start_date}\n"
            result += f"  Category: {event.category.value}\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error in search_events tool: {e}")
        return f"Error searching events: {str(e)}"


@tool
def search_transport(origin: str, destination: str,
                     transport_type: Optional[str] = None) -> str:
    """Search for transportation options between locations
    
    Args:
        origin: Origin city or location
        destination: Destination city or location
        transport_type: Optional transport type (train, bus, taxi, etc.)
    
    Returns:
        Transport information as formatted string
    """
    try:
        query = Transport.find(Transport.is_active == True)
        
        if transport_type:
            from backend.app.models.transport import TransportType
            try:
                type_enum = TransportType(transport_type.lower())
                query = query.find(Transport.transport_type == type_enum)
            except:
                pass
        
        transport_options = run_async(query.limit(5).to_list())
        
        if not transport_options:
            return f"No transport options found from {origin} to {destination}"
        
        result = f"Transport options from {origin} to {destination}:\n\n"
        for trans in transport_options:
            name = trans.name.get("en", "Unknown")
            trans_type = trans.transport_type.value
            # Check if route matches
            matching_routes = [r for r in trans.routes 
                             if origin.lower() in r.origin.lower() 
                             and destination.lower() in r.destination.lower()]
            
            if matching_routes or not origin or not destination:
                result += f"- {name} ({trans_type})\n"
                if matching_routes:
                    route = matching_routes[0]
                    result += f"  Route: {route.origin} to {route.destination}\n"
                    if route.duration_minutes:
                        result += f"  Duration: {route.duration_minutes} minutes\n"
                result += f"  Service Areas: {', '.join(trans.service_areas[:3])}\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error in search_transport tool: {e}")
        return f"Error searching transport: {str(e)}"


@tool
def convert_currency(amount: float, from_currency: str, 
                     to_currency: str) -> str:
    """Convert currency amounts
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., USD, EUR, LKR)
        to_currency: Target currency code (e.g., USD, EUR, LKR)
    
    Returns:
        Converted amount as formatted string
    """
    try:
        service = CurrencyService()
        result = run_async(service.convert_currency(
            amount=amount,
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper()
        ))
        
        if result:
            converted = result.get("converted_amount", amount)
            rate = result.get("exchange_rate", 1.0)
            return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()} (Rate: {rate:.4f})"
        else:
            return f"Currency conversion not available for {from_currency} to {to_currency}"
    except Exception as e:
        logger.error(f"Error in convert_currency tool: {e}")
        return f"Error converting currency: {str(e)}"


@tool
def get_directions(origin: str, destination: str,
                  mode: str = "driving") -> str:
    """Get directions and travel information between locations
    
    Args:
        origin: Origin location
        destination: Destination location
        mode: Travel mode (driving, walking, transit)
    
    Returns:
        Directions and travel time as formatted string
    """
    try:
        service = MapsService()
        directions = run_async(service.get_directions(
            origin=origin,
            destination=destination,
            mode=mode
        ))
        
        if directions:
            distance = directions.get("distance", {}).get("text", "N/A")
            duration = directions.get("duration", {}).get("text", "N/A")
            return f"Directions from {origin} to {destination}:\nDistance: {distance}\nDuration: {duration}\nMode: {mode}"
        else:
            return f"Directions not available from {origin} to {destination}"
    except Exception as e:
        logger.error(f"Error in get_directions tool: {e}")
        return f"Error getting directions: {str(e)}"


class CrewAIService:
    """CrewAI multi-agent orchestration service for tourism chatbot"""
    
    def __init__(self):
        self.enabled = False
        self.agents = {}
        self.tools = [
            search_attractions,
            get_weather,
            search_hotels,
            search_restaurants,
            search_events,
            search_transport,
            convert_currency,
            get_directions
        ]
        
        if CREWAI_AVAILABLE:
            self._initialize_agents()
        else:
            logger.warning("CrewAI not available - install with: pip install crewai crewai-tools")
    
    def _initialize_agents(self):
        """Initialize specialized agents for tourism tasks"""
        try:
            # Tourism Research Agent
            self.agents['tourism_researcher'] = Agent(
                role="Tourism Research Specialist",
                goal="Research and provide detailed, accurate information about Sri Lanka tourism including attractions, hotels, restaurants, events, and cultural information",
                backstory="""You are an expert tourism researcher specializing in Sri Lanka. 
                You have extensive knowledge of:
                - Tourist attractions (temples, beaches, mountains, wildlife)
                - Hotels and accommodations
                - Restaurants and cuisine
                - Cultural events and festivals
                - Transportation options
                - Local customs and traditions
                
                You provide accurate, helpful, and culturally sensitive information.""",
                tools=self.tools,
                verbose=True,
                allow_delegation=False,
                max_iter=3
            )
            
            # Itinerary Planning Agent
            self.agents['itinerary_planner'] = Agent(
                role="Travel Itinerary Planner",
                goal="Create optimized, realistic travel itineraries for Sri Lanka",
                backstory="""You are a professional travel planner with years of experience 
                creating itineraries for Sri Lanka. You consider:
                - Travel time between locations
                - Opening hours and availability
                - Budget constraints
                - User preferences
                - Weather conditions
                - Cultural events
                
                You create practical, enjoyable itineraries that maximize the travel experience.""",
                tools=self.tools,
                verbose=True,
                allow_delegation=True,
                max_iter=5
            )
            
            # Translation Agent
            self.agents['translator'] = Agent(
                role="Multilingual Translator",
                goal="Provide accurate translations between Sinhala, Tamil, English, and other languages",
                backstory="""You are a professional translator specializing in Sri Lankan languages 
                (Sinhala, Tamil) and international languages. You provide culturally appropriate 
                translations that maintain context and meaning. You understand cultural nuances 
                and ensure translations are natural and understandable.""",
                verbose=True,
                allow_delegation=False,
                max_iter=2
            )
            
            # Recommendation Agent
            self.agents['recommender'] = Agent(
                role="Personalized Recommendation Specialist",
                goal="Provide personalized tourism recommendations based on user preferences",
                backstory="""You analyze user preferences, past behavior, and context to provide 
                personalized recommendations for attractions, hotels, restaurants, and activities 
                in Sri Lanka. You consider budget, interests, travel style, and cultural preferences 
                to suggest the best options.""",
                tools=self.tools,
                verbose=True,
                allow_delegation=True,
                max_iter=3
            )
            
            # Safety Agent
            self.agents['safety_agent'] = Agent(
                role="Safety and Emergency Information Specialist",
                goal="Provide safety information, emergency contacts, and travel advisories for Sri Lanka",
                backstory="""You are a safety expert specializing in travel safety for Sri Lanka. 
                You provide information about:
                - Emergency contacts
                - Safety tips for tourists
                - Health and medical information
                - Weather warnings
                - Travel advisories
                
                You prioritize user safety and provide clear, actionable information.""",
                tools=[get_weather],
                verbose=True,
                allow_delegation=False,
                max_iter=2
            )
            
            self.enabled = True
            logger.info("CrewAI agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI agents: {e}", exc_info=True)
            self.enabled = False
    
    async def process_query(
        self,
        query: str,
        language: str = "en",
        context: Optional[Dict] = None,
        agent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process query using multi-agent crew
        
        Args:
            query: User query
            language: Response language
            context: Additional context (user preferences, location, etc.)
            agent_type: Specific agent to use (optional, auto-selects if None)
        
        Returns:
            Response dictionary with text, intent, confidence, etc.
        """
        if not self.enabled:
            raise Exception("CrewAI service not initialized or not available")
        
        try:
            # Determine which agents to use based on query
            if agent_type and agent_type in self.agents:
                agents_to_use = [self.agents[agent_type]]
                tasks_to_create = [self._create_task_for_agent(query, agent_type)]
            else:
                # Auto-select agents based on query content
                agents_to_use, tasks_to_create = self._select_agents_for_query(query)
            
            if not agents_to_use:
                raise Exception("No suitable agents found for query")
            
            # Create crew
            crew = Crew(
                agents=agents_to_use,
                tasks=tasks_to_create,
                verbose=getattr(settings, 'CREWAI_VERBOSE', False) or settings.DEBUG,
                process="sequential"  # Sequential processing or "hierarchical"
            )
            
            # Execute crew (run in executor to avoid blocking)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: crew.kickoff()
            )
            
            # Format response
            response_text = str(result)
            
            # If translation is needed
            if language != "en" and 'translator' in [a.role for a in agents_to_use]:
                # Translation agent should handle this, but we can add fallback
                pass
            
            return {
                "text": response_text,
                "intent": "crewai_processed",
                "confidence": 0.9,
                "entities": [],
                "suggestions": [],
                "model": "crewai",
                "provider": "crewai",
                "agents_used": [agent.role for agent in agents_to_use]
            }
            
        except Exception as e:
            logger.error(f"CrewAI processing error: {e}", exc_info=True)
            raise
    
    def _select_agents_for_query(self, query: str) -> tuple:
        """Select appropriate agents based on query content"""
        query_lower = query.lower()
        agents_to_use = []
        tasks = []
        
        # Itinerary planning queries
        if any(keyword in query_lower for keyword in ["itinerary", "plan", "schedule", "trip", "route"]):
            agents_to_use.append(self.agents['itinerary_planner'])
            agents_to_use.append(self.agents['tourism_researcher'])
            tasks.append(Task(
                description=f"Research tourism information for: {query}",
                agent=self.agents['tourism_researcher'],
                expected_output="Detailed research findings about attractions, hotels, and activities"
            ))
            tasks.append(Task(
                description=f"Create an optimized itinerary based on: {query}",
                agent=self.agents['itinerary_planner'],
                expected_output="Complete travel itinerary with day-by-day plan"
            ))
        
        # Recommendation queries
        elif any(keyword in query_lower for keyword in ["recommend", "suggest", "best", "top", "popular"]):
            agents_to_use.append(self.agents['recommender'])
            agents_to_use.append(self.agents['tourism_researcher'])
            tasks.append(Task(
                description=f"Research options for: {query}",
                agent=self.agents['tourism_researcher'],
                expected_output="List of relevant tourism options"
            ))
            tasks.append(Task(
                description=f"Provide personalized recommendations for: {query}",
                agent=self.agents['recommender'],
                expected_output="Personalized recommendations with explanations"
            ))
        
        # Safety/emergency queries
        elif any(keyword in query_lower for keyword in ["safety", "emergency", "danger", "safe", "help"]):
            agents_to_use.append(self.agents['safety_agent'])
            tasks.append(Task(
                description=f"Provide safety information for: {query}",
                agent=self.agents['safety_agent'],
                expected_output="Safety information and emergency contacts"
            ))
        
        # General research queries
        else:
            agents_to_use.append(self.agents['tourism_researcher'])
            tasks.append(Task(
                description=f"Research and provide information about: {query}",
                agent=self.agents['tourism_researcher'],
                expected_output="Comprehensive information about the query topic"
            ))
        
        return agents_to_use, tasks
    
    def _create_task_for_agent(self, query: str, agent_type: str) -> Task:
        """Create a task for a specific agent"""
        agent = self.agents[agent_type]
        
        task_descriptions = {
            'tourism_researcher': f"Research detailed information about: {query}",
            'itinerary_planner': f"Create an itinerary for: {query}",
            'translator': f"Translate or provide multilingual support for: {query}",
            'recommender': f"Provide recommendations for: {query}",
            'safety_agent': f"Provide safety information for: {query}"
        }
        
        expected_outputs = {
            'tourism_researcher': "Detailed research findings",
            'itinerary_planner': "Complete travel itinerary",
            'translator': "Accurate translation",
            'recommender': "Personalized recommendations",
            'safety_agent': "Safety information and emergency contacts"
        }
        
        return Task(
            description=task_descriptions.get(agent_type, f"Process: {query}"),
            agent=agent,
            expected_output=expected_outputs.get(agent_type, "Processed response")
        )
    
    async def is_available(self) -> bool:
        """Check if CrewAI service is available"""
        return self.enabled and CREWAI_AVAILABLE
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Get status of all agents"""
        return {
            agent_name: agent is not None
            for agent_name, agent in self.agents.items()
        }


# Singleton instance
crewai_service = None


def get_crewai_service() -> CrewAIService:
    """Get or create CrewAI service singleton"""
    global crewai_service
    if crewai_service is None:
        crewai_service = CrewAIService()
    return crewai_service

