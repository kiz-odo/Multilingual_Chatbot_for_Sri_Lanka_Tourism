# 🤖 CrewAI Setup Guide

Complete guide for enabling and using CrewAI multi-agent orchestration in the backend.

## Overview

CrewAI is a multi-agent framework that enables specialized AI agents to work together on complex tasks. In this chatbot, CrewAI is used for complex query processing with specialized agents for different tourism-related tasks.

## Features

### Specialized Agents

1. **Tourism Research Agent**
   - Researches attractions, hotels, restaurants, events
   - Provides detailed tourism information
   - Culturally sensitive responses

2. **Itinerary Planner**
   - Creates optimized travel itineraries
   - Considers travel time, budget, preferences
   - Day-by-day planning

3. **Translator**
   - Multilingual translation support
   - Sinhala, Tamil, English, and more
   - Cultural context awareness

4. **Recommender**
   - Personalized recommendations
   - Based on user preferences
   - Budget and interest-based suggestions

5. **Safety Agent**
   - Safety information and emergency contacts
   - Travel advisories
   - Weather warnings

### Available Tools

- `search_attractions` - Search tourist attractions
- `get_weather` - Get weather information
- `search_hotels` - Search hotels
- `search_restaurants` - Search restaurants
- `search_events` - Search events and festivals
- `search_transport` - Search transport options
- `convert_currency` - Currency conversion
- `get_directions` - Get directions between locations

## Installation

### 1. Install Dependencies

CrewAI is already in `requirements.txt`. Install it:

```bash
pip install crewai>=0.1.0 crewai-tools>=0.1.0 nest-asyncio>=1.5.8
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Enable CrewAI

Add to your `.env` file:

```bash
USE_CREWAI=true
CREWAI_VERBOSE=false  # Set to true for debugging
```

### 3. Verify Installation

Check if CrewAI is available:

```python
from backend.app.services.crewai_service import get_crewai_service

service = get_crewai_service()
if await service.is_available():
    print("CrewAI is ready!")
else:
    print("CrewAI not available - check installation")
```

## Configuration

### Environment Variables

```bash
# Enable CrewAI
USE_CREWAI=true

# Verbose logging (for debugging)
CREWAI_VERBOSE=false
```

### Configuration in Code

CrewAI is configured in `backend/app/core/config.py`:

```python
USE_CREWAI: bool = False  # Enable/disable CrewAI
CREWAI_VERBOSE: bool = False  # Verbose logging
```

## How It Works

### Query Routing

CrewAI is used for **complex queries** that require multi-agent processing:

1. **Simple Queries** → Rasa NLU (fast, structured intents)
2. **Complex Queries** → CrewAI (multi-agent orchestration)
3. **Very Complex** → LLM (Gemini/Qwen/Mistral)

### Query Types Handled by CrewAI

- **Itinerary Planning**: "Plan a 3-day trip to Kandy"
- **Recommendations**: "Recommend best beaches for families"
- **Complex Research**: "What are the best cultural sites and restaurants in Galle?"
- **Multi-step Queries**: "Find hotels near Sigiriya and plan a day trip"

### Agent Selection

CrewAI automatically selects agents based on query content:

- Keywords like "itinerary", "plan", "schedule" → Itinerary Planner + Researcher
- Keywords like "recommend", "suggest", "best" → Recommender + Researcher
- Keywords like "safety", "emergency" → Safety Agent
- General queries → Tourism Researcher

## Usage Examples

### Example 1: Itinerary Planning

**Query**: "Plan a 3-day trip to Colombo with budget of 50000 LKR"

**Agents Used**:
- Tourism Researcher (research attractions, hotels, restaurants)
- Itinerary Planner (create optimized itinerary)

**Response**: Complete day-by-day itinerary with activities, accommodations, and meals

### Example 2: Recommendations

**Query**: "Recommend best beaches for families with kids"

**Agents Used**:
- Tourism Researcher (find family-friendly beaches)
- Recommender (personalize recommendations)

**Response**: Personalized list of beaches with explanations

### Example 3: Complex Research

**Query**: "What are the best cultural sites and restaurants in Galle?"

**Agents Used**:
- Tourism Researcher (research both cultural sites and restaurants)

**Response**: Comprehensive information about cultural sites and restaurants

## Integration with Chat System

CrewAI is integrated into `HybridChatService`:

```python
# In hybrid_chat_service.py
if self.USE_CREWAI and is_complex_query:
    response = await self.crewai_service.process_query(
        query=message,
        language=language,
        context=context
    )
```

## Troubleshooting

### CrewAI Not Available

**Error**: "CrewAI not available"

**Solutions**:
1. Install dependencies: `pip install crewai crewai-tools nest-asyncio`
2. Check if CrewAI is enabled: `USE_CREWAI=true` in `.env`
3. Verify installation: `python -c "import crewai; print('OK')"`

### Event Loop Issues

**Error**: "RuntimeError: This event loop is already running"

**Solution**: `nest-asyncio` is included in requirements. It handles nested event loops automatically.

### Agent Initialization Failed

**Error**: "Failed to initialize CrewAI agents"

**Solutions**:
1. Check logs for specific error
2. Verify all dependencies are installed
3. Check if tools are working correctly

## Performance Considerations

### When to Use CrewAI

✅ **Use CrewAI for**:
- Complex multi-step queries
- Itinerary planning
- Personalized recommendations
- Research requiring multiple data sources

❌ **Don't use CrewAI for**:
- Simple questions (use Rasa)
- Single-fact queries (use Rasa)
- Quick lookups (use direct database queries)

### Performance Impact

- **Response Time**: 5-15 seconds (multi-agent processing)
- **Resource Usage**: Higher CPU/memory (multiple agents)
- **Cost**: No additional cost (uses existing services)

## Best Practices

1. **Enable for Complex Queries Only**: CrewAI is for complex queries, not simple ones
2. **Monitor Performance**: Track response times and resource usage
3. **Use Verbose Mode for Debugging**: Set `CREWAI_VERBOSE=true` to see agent activity
4. **Test Agent Selection**: Verify correct agents are selected for queries

## API Usage

### Check CrewAI Status

```python
from backend.app.services.crewai_service import get_crewai_service

service = get_crewai_service()
status = service.get_agent_status()
# Returns: {'tourism_researcher': True, 'itinerary_planner': True, ...}
```

### Process Query Directly

```python
response = await service.process_query(
    query="Plan a trip to Kandy",
    language="en",
    context={"budget": 50000, "duration": 3}
)
```

## Future Enhancements

1. **Custom Agents**: Add domain-specific agents
2. **Agent Collaboration**: Enhanced agent-to-agent communication
3. **Learning**: Agents learn from user interactions
4. **Caching**: Cache agent responses for similar queries

## Support

For issues or questions:
1. Check logs: `logs/app.log`
2. Enable verbose mode: `CREWAI_VERBOSE=true`
3. Review agent status: `service.get_agent_status()`

---

**CrewAI enables powerful multi-agent orchestration for complex tourism queries!** 🚀

