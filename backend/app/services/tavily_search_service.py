"""
Tavily Search API Service - AI-Optimized Web Search
Tavily provides search results specifically optimized for AI applications
Better than Google Custom Search for chatbot use cases
"""

from typing import Dict, Any, Optional, List
import logging
import httpx
from backend.app.core.config import settings
from backend.app.services.cache_service import cached

logger = logging.getLogger(__name__)

# Try to import Tavily Python client
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("Tavily Python client not installed. Run: pip install tavily-python")


class TavilySearchService:
    """
    Tavily Search API service for AI-optimized web search
    
    Advantages over Google Custom Search:
    - AI-optimized results with relevance scoring
    - Automatic content extraction and summarization
    - No need for custom search engine setup
    - Better pricing for API usage
    - Cleaner, more structured responses
    """

    def __init__(self):
        self.enabled = False
        self.client = None
        self.api_key = settings.TAVILY_API_KEY if hasattr(settings, 'TAVILY_API_KEY') else None
        
        if not TAVILY_AVAILABLE:
            logger.warning("Tavily client library not available")
            return
            
        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                self.enabled = True
                logger.info("✅ Tavily Search service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
        else:
            logger.warning("Tavily API key not configured. Set TAVILY_API_KEY in .env")

    async def is_available(self) -> bool:
        """Check if Tavily Search service is available"""
        return self.enabled and TAVILY_AVAILABLE

    @cached(prefix="tavily_search", ttl=3600)  # Cache for 1 hour
    async def search(
        self,
        query: str,
        language: str = "en",
        search_depth: str = "basic",  # "basic" or "advanced"
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search using Tavily API
        
        Args:
            query: Search query
            language: Language code (not directly supported, added to query)
            search_depth: "basic" for faster results, "advanced" for deeper search
            max_results: Number of results to return (default 5)
            include_domains: Optional list of domains to prioritize
            exclude_domains: Optional list of domains to exclude
        
        Returns:
            Dictionary with search results optimized for AI
        """
        if not await self.is_available():
            return {
                "success": False,
                "error": "Tavily search service not available",
                "results": []
            }

        try:
            # Enhance query with language context if needed
            enhanced_query = query
            if language != "en":
                lang_map = {
                    "si": "Sinhala",
                    "ta": "Tamil",
                    "fr": "French",
                    "de": "German",
                    "es": "Spanish",
                    "ja": "Japanese",
                    "zh": "Chinese"
                }
                if language in lang_map:
                    enhanced_query = f"{query} (in {lang_map[language]} or English)"

            # Prepare search parameters
            search_params = {
                "query": enhanced_query,
                "search_depth": search_depth,
                "max_results": max_results,
                "include_answer": True,  # Get AI-generated answer
                "include_raw_content": False,  # Don't need full HTML
            }

            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains

            # Execute search
            response = self.client.search(**search_params)

            # Format results
            formatted_results = []
            if "results" in response:
                for result in response["results"]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "score": result.get("score", 0.0),  # Relevance score
                    })

            return {
                "success": True,
                "query": query,
                "answer": response.get("answer", ""),  # AI-generated answer
                "results": formatted_results,
                "total_results": len(formatted_results),
                "search_depth": search_depth,
                "model": "tavily",
                "provider": "tavily"
            }

        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def get_fallback_response(
        self,
        query: str,
        language: str = "en",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get fallback response for unknown queries using Tavily
        
        Args:
            query: User query
            language: Language code
            context: Optional conversation context
        
        Returns:
            Formatted response with search results
        """
        if not await self.is_available():
            return {
                "success": False,
                "message": "Tavily search is not available",
                "response": "I don't have enough information to answer this question.",
                "model": "tavily",
                "provider": "tavily"
            }

        # Add Sri Lanka tourism context for better results
        tourism_domains = [
            "srilanka.travel",
            "tourism.gov.lk",
            "lonelyplanet.com",
            "tripadvisor.com"
        ]

        # Enhance query with Sri Lanka context if tourism-related
        tourism_keywords = ["sri lanka", "ceylon", "colombo", "kandy", "galle", "sigiriya"]
        is_tourism_query = any(keyword in query.lower() for keyword in tourism_keywords)
        
        enhanced_query = query
        if is_tourism_query and "sri lanka" not in query.lower():
            enhanced_query = f"{query} Sri Lanka"

        # Perform search
        search_results = await self.search(
            query=enhanced_query,
            language=language,
            search_depth="advanced" if is_tourism_query else "basic",
            max_results=5,
            include_domains=tourism_domains if is_tourism_query else None
        )

        if not search_results.get("success"):
            return {
                "success": False,
                "message": "Search failed",
                "response": "I couldn't find reliable information for this question.",
                "model": "tavily",
                "provider": "tavily"
            }

        # Format response with AI-generated answer and sources
        answer = search_results.get("answer", "")
        results = search_results.get("results", [])

        if answer:
            response_text = f"{answer}\n\n"
        else:
            response_text = "Based on my search, here's what I found:\n\n"

        # Add top results
        for i, result in enumerate(results[:3], 1):
            response_text += f"{i}. {result['snippet']}\n"
            response_text += f"   Source: {result['url']}\n\n"

        return {
            "success": True,
            "message": "Information retrieved via Tavily search",
            "response": response_text.strip(),
            "sources": [r["url"] for r in results[:3]],
            "confidence": 0.7,  # Moderate confidence for web search
            "fallback_reason": "tavily_web_search",
            "model": "tavily",
            "provider": "tavily"
        }


# Singleton instance
tavily_search_service = None


def get_tavily_search_service() -> TavilySearchService:
    """Get or create Tavily search service singleton"""
    global tavily_search_service
    if tavily_search_service is None:
        tavily_search_service = TavilySearchService()
    return tavily_search_service
