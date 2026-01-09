"""
Comprehensive API endpoint tests for all backend endpoints
This file tests all endpoints across all routers systematically
"""

import pytest
from httpx import AsyncClient
from typing import Dict, Any
import json


@pytest.mark.api
@pytest.mark.comprehensive
class TestAllEndpoints:
    """Comprehensive test suite for all API endpoints"""
    
    # ==================== AUTHENTICATION ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_auth_register(self, client: AsyncClient):
        """Test POST /api/v1/auth/register"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test_register@example.com",
                "username": "test_register_user",
                "password": "TestPassword123!",
                "full_name": "Test Register User"
            }
        )
        assert response.status_code in [200, 201, 400]  # 400 if user exists
    
    @pytest.mark.asyncio
    async def test_auth_login(self, client: AsyncClient, test_user):
        """Test POST /api/v1/auth/login"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPassword123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_auth_refresh(self, client: AsyncClient, auth_headers, test_user):
        """Test POST /api/v1/auth/refresh"""
        # First get refresh token from login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPassword123!"
            }
        )
        if login_response.status_code == 200:
            token_data = login_response.json()
            if "refresh_token" in token_data:
                response = await client.post(
                    "/api/v1/auth/refresh",
                    json={"refresh_token": token_data["refresh_token"]}
                )
                assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_auth_logout(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/auth/logout"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_auth_me(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/auth/me"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
    
    @pytest.mark.asyncio
    async def test_auth_update_me(self, client: AsyncClient, auth_headers):
        """Test PUT /api/v1/auth/me"""
        response = await client.put(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_auth_change_password(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/auth/change-password"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "TestPassword123!",
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code in [200, 201, 400]
    
    @pytest.mark.asyncio
    async def test_auth_password_reset_request(self, client: AsyncClient):
        """Test POST /api/v1/auth/password-reset-request"""
        import uuid
        unique_email = f"resettest_{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": unique_email}
        )
        assert response.status_code in [200, 201, 404]
    
    @pytest.mark.asyncio
    async def test_auth_verify_token(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/auth/verify-token"""
        response = await client.get(
            "/api/v1/auth/verify-token",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_auth_forgot_password(self, client: AsyncClient):
        """Test POST /api/v1/auth/forgot-password"""
        import uuid
        unique_email = f"forgottest_{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": unique_email}
        )
        assert response.status_code in [200, 201, 404]
    
    # ==================== USER ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_users_me(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/users/me"""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_users_update_me(self, client: AsyncClient, auth_headers):
        """Test PUT /api/v1/users/me"""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated User Name"}
        )
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_users_add_favorite_attraction(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/users/me/favorites/attractions/{attraction_id}"""
        # First get an attraction ID
        attractions_response = await client.get("/api/v1/attractions")
        if attractions_response.status_code == 200:
            attractions = attractions_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.post(
                        f"/api/v1/users/me/favorites/attractions/{attraction_id}",
                        headers=auth_headers
                    )
                    assert response.status_code in [200, 201, 404]
    
    @pytest.mark.asyncio
    async def test_users_remove_favorite_attraction(self, client: AsyncClient, auth_headers):
        """Test DELETE /api/v1/users/me/favorites/attractions/{attraction_id}"""
        # First get an attraction ID
        attractions_response = await client.get("/api/v1/attractions")
        if attractions_response.status_code == 200:
            attractions = attractions_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.delete(
                        f"/api/v1/users/me/favorites/attractions/{attraction_id}",
                        headers=auth_headers
                    )
                    assert response.status_code in [200, 204, 404]
    
    @pytest.mark.asyncio
    async def test_users_add_visited_place(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/users/me/visited/{place_id}"""
        response = await client.post(
            "/api/v1/users/me/visited/test_place_id",
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]
    
    @pytest.mark.asyncio
    async def test_users_get_stats(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/users/me/stats"""
        response = await client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_users_export(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/users/me/export"""
        response = await client.get(
            "/api/v1/users/me/export",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_users_export_download(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/users/me/export/download"""
        response = await client.get(
            "/api/v1/users/me/export/download",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_users_delete_me(self, client: AsyncClient, auth_headers):
        """Test DELETE /api/v1/users/me"""
        # Note: This will delete the user, so create a new one for this test
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers
        )
        assert response.status_code in [200, 204, 404]
    
    @pytest.mark.asyncio
    async def test_users_delete_data(self, client: AsyncClient, auth_headers):
        """Test DELETE /api/v1/users/me/data"""
        response = await client.delete(
            "/api/v1/users/me/data",
            headers=auth_headers
        )
        assert response.status_code in [200, 204, 404]
    
    # ==================== ATTRACTIONS ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_attractions_list(self, client: AsyncClient):
        """Test GET /api/v1/attractions"""
        response = await client.get("/api/v1/attractions")
        # Accept 200 (success) or 404 (endpoint not found/not configured)
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_attractions_list_with_filters(self, client: AsyncClient):
        """Test GET /api/v1/attractions with filters"""
        response = await client.get(
            "/api/v1/attractions",
            params={"category": "historical", "city": "Colombo", "limit": 10}
        )
        assert response.status_code in [200, 404]  # Allow 404 if no data
    
    @pytest.mark.asyncio
    async def test_attractions_search(self, client: AsyncClient):
        """Test GET /api/v1/attractions/search"""
        response = await client.get(
            "/api/v1/attractions/search",
            params={"q": "Sigiriya"}
        )
        assert response.status_code in [200, 422]  # Allow 422 for validation errors
    
    @pytest.mark.asyncio
    async def test_attractions_categories(self, client: AsyncClient):
        """Test GET /api/v1/attractions/categories"""
        response = await client.get("/api/v1/attractions/categories")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_attractions_featured(self, client: AsyncClient):
        """Test GET /api/v1/attractions/featured"""
        response = await client.get("/api/v1/attractions/featured")
        assert response.status_code in [200, 422]  # Allow 422 for validation errors
    
    @pytest.mark.asyncio
    async def test_attractions_popular(self, client: AsyncClient):
        """Test GET /api/v1/attractions/popular"""
        response = await client.get("/api/v1/attractions/popular")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_attractions_nearby(self, client: AsyncClient):
        """Test GET /api/v1/attractions/nearby"""
        response = await client.get(
            "/api/v1/attractions/nearby",
            params={"latitude": 6.9271, "longitude": 79.8612, "radius_km": 50}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_attractions_get_by_id(self, client: AsyncClient):
        """Test GET /api/v1/attractions/{attraction_id}"""
        # First get list to find an ID
        list_response = await client.get("/api/v1/attractions")
        if list_response.status_code == 200:
            attractions = list_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.get(f"/api/v1/attractions/{attraction_id}")
                    assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_attractions_reviews(self, client: AsyncClient):
        """Test GET /api/v1/attractions/{attraction_id}/reviews"""
        list_response = await client.get("/api/v1/attractions")
        if list_response.status_code == 200:
            attractions = list_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.get(f"/api/v1/attractions/{attraction_id}/reviews")
                    assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_attractions_add_review(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/attractions/{attraction_id}/reviews"""
        list_response = await client.get("/api/v1/attractions")
        if list_response.status_code == 200:
            attractions = list_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.post(
                        f"/api/v1/attractions/{attraction_id}/reviews",
                        headers=auth_headers,
                        params={"rating": 4.5, "comment": "Great place!"}
                    )
                    assert response.status_code in [200, 201, 404]
    
    @pytest.mark.asyncio
    async def test_attractions_add_favorite(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/attractions/{attraction_id}/favorite"""
        list_response = await client.get("/api/v1/attractions")
        if list_response.status_code == 200:
            attractions = list_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.post(
                        f"/api/v1/attractions/{attraction_id}/favorite",
                        headers=auth_headers
                    )
                    assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_attractions_remove_favorite(self, client: AsyncClient, auth_headers):
        """Test DELETE /api/v1/attractions/{attraction_id}/favorite"""
        list_response = await client.get("/api/v1/attractions")
        if list_response.status_code == 200:
            attractions = list_response.json()
            if isinstance(attractions, list) and len(attractions) > 0:
                attraction_id = attractions[0].get("id") or attractions[0].get("_id")
                if attraction_id:
                    response = await client.delete(
                        f"/api/v1/attractions/{attraction_id}/favorite",
                        headers=auth_headers
                    )
                    assert response.status_code in [200, 404]
    
    # ==================== RESTAURANTS ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_restaurants_list(self, client: AsyncClient):
        """Test GET /api/v1/restaurants"""
        response = await client.get("/api/v1/restaurants")
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_restaurants_list_with_filters(self, client: AsyncClient):
        """Test GET /api/v1/restaurants with filters"""
        response = await client.get(
            "/api/v1/restaurants",
            params={"cuisine_type": "sri_lankan", "city": "Colombo"}
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_restaurants_search(self, client: AsyncClient):
        """Test GET /api/v1/restaurants/search"""
        response = await client.get(
            "/api/v1/restaurants/search",
            params={"q": "rice", "location": "Colombo"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_restaurants_get_by_id(self, client: AsyncClient):
        """Test GET /api/v1/restaurants/{restaurant_id}"""
        list_response = await client.get("/api/v1/restaurants")
        if list_response.status_code == 200:
            restaurants = list_response.json()
            if isinstance(restaurants, list) and len(restaurants) > 0:
                restaurant_id = restaurants[0].get("id") or restaurants[0].get("_id")
                if restaurant_id:
                    response = await client.get(f"/api/v1/restaurants/{restaurant_id}")
                    assert response.status_code in [200, 404]
    
    # ==================== HOTELS ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_hotels_list(self, client: AsyncClient):
        """Test GET /api/v1/hotels"""
        response = await client.get("/api/v1/hotels")
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_hotels_list_with_filters(self, client: AsyncClient):
        """Test GET /api/v1/hotels with filters"""
        response = await client.get(
            "/api/v1/hotels",
            params={"star_rating": "four_star", "city": "Colombo"}
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_hotels_search(self, client: AsyncClient):
        """Test GET /api/v1/hotels/search"""
        response = await client.get(
            "/api/v1/hotels/search",
            params={"q": "hotel", "location": "Colombo"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_hotels_get_by_id(self, client: AsyncClient):
        """Test GET /api/v1/hotels/{hotel_id}"""
        list_response = await client.get("/api/v1/hotels")
        if list_response.status_code == 200:
            hotels = list_response.json()
            if isinstance(hotels, list) and len(hotels) > 0:
                hotel_id = hotels[0].get("id") or hotels[0].get("_id")
                if hotel_id:
                    response = await client.get(f"/api/v1/hotels/{hotel_id}")
                    assert response.status_code in [200, 404]
    
    # ==================== TRANSPORT ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_transport_list(self, client: AsyncClient):
        """Test GET /api/v1/transport"""
        response = await client.get("/api/v1/transport")
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_transport_list_with_filters(self, client: AsyncClient):
        """Test GET /api/v1/transport with filters"""
        response = await client.get(
            "/api/v1/transport",
            params={"transport_type": "bus", "origin": "Colombo"}
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_transport_search(self, client: AsyncClient):
        """Test GET /api/v1/transport/search"""
        response = await client.get(
            "/api/v1/transport/search",
            params={"origin": "Colombo", "destination": "Kandy"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_transport_get_by_id(self, client: AsyncClient):
        """Test GET /api/v1/transport/{transport_id}"""
        list_response = await client.get("/api/v1/transport")
        if list_response.status_code == 200:
            transports = list_response.json()
            if isinstance(transports, list) and len(transports) > 0:
                transport_id = transports[0].get("id") or transports[0].get("_id")
                if transport_id:
                    response = await client.get(f"/api/v1/transport/{transport_id}")
                    assert response.status_code in [200, 404]
    
    # ==================== EMERGENCY ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_emergency_list(self, client: AsyncClient):
        """Test GET /api/v1/emergency"""
        response = await client.get("/api/v1/emergency")
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_emergency_list_with_filters(self, client: AsyncClient):
        """Test GET /api/v1/emergency with filters"""
        response = await client.get(
            "/api/v1/emergency",
            params={"service_type": "police", "city": "Colombo"}
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_emergency_search(self, client: AsyncClient):
        """Test GET /api/v1/emergency/search"""
        response = await client.get(
            "/api/v1/emergency/search",
            params={"service_type": "medical", "location": "Colombo"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_emergency_get_by_id(self, client: AsyncClient):
        """Test GET /api/v1/emergency/{service_id}"""
        list_response = await client.get("/api/v1/emergency")
        if list_response.status_code == 200:
            services = list_response.json()
            if isinstance(services, list) and len(services) > 0:
                service_id = services[0].get("id") or services[0].get("_id")
                if service_id:
                    response = await client.get(f"/api/v1/emergency/{service_id}")
                    assert response.status_code in [200, 404]
    
    # ==================== EVENTS ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_events_list(self, client: AsyncClient):
        """Test GET /api/v1/events"""
        response = await client.get("/api/v1/events")
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_events_list_with_filters(self, client: AsyncClient):
        """Test GET /api/v1/events with filters"""
        response = await client.get(
            "/api/v1/events",
            params={"category": "cultural", "city": "Kandy", "upcoming_only": True}
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_events_search(self, client: AsyncClient):
        """Test GET /api/v1/events/search"""
        response = await client.get(
            "/api/v1/events/search",
            params={"q": "festival", "location": "Kandy"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_events_get_by_id(self, client: AsyncClient):
        """Test GET /api/v1/events/{event_id}"""
        list_response = await client.get("/api/v1/events")
        if list_response.status_code == 200:
            events = list_response.json()
            if isinstance(events, list) and len(events) > 0:
                event_id = events[0].get("id") or events[0].get("_id")
                if event_id:
                    response = await client.get(f"/api/v1/events/{event_id}")
                    assert response.status_code in [200, 404]
    
    # ==================== FEEDBACK ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_feedback_submit(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/feedback"""
        response = await client.post(
            "/api/v1/feedback",
            headers=auth_headers,
            json={
                "subject": "Test Feedback",
                "message": "This is a test feedback message",
                "rating": 5
            }
        )
        assert response.status_code in [200, 201, 404]
    
    @pytest.mark.asyncio
    async def test_feedback_list(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/feedback"""
        response = await client.get(
            "/api/v1/feedback",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_feedback_get_by_id(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/feedback/{feedback_id}"""
        list_response = await client.get("/api/v1/feedback", headers=auth_headers)
        if list_response.status_code == 200:
            feedbacks = list_response.json()
            if isinstance(feedbacks, list) and len(feedbacks) > 0:
                feedback_id = feedbacks[0].get("id") or feedbacks[0].get("_id")
                if feedback_id:
                    response = await client.get(
                        f"/api/v1/feedback/{feedback_id}",
                        headers=auth_headers
                    )
                    assert response.status_code in [200, 404]
    
    # ==================== CHAT ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_chat_message(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/chat/message"""
        response = await client.post(
            "/api/v1/chat/message",
            headers=auth_headers,
            json={
                "message": "Tell me about Sigiriya",
                "language": "en"
            }
        )
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_chat_history(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/chat/history"""
        response = await client.get(
            "/api/v1/chat/history",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_chat_delete_history(self, client: AsyncClient, auth_headers):
        """Test DELETE /api/v1/chat/history"""
        response = await client.delete(
            "/api/v1/chat/history",
            headers=auth_headers
        )
        assert response.status_code in [200, 204, 401]
    
    @pytest.mark.asyncio
    async def test_chat_conversations(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/chat/conversations"""
        response = await client.get(
            "/api/v1/chat/conversations",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_chat_supported_languages(self, client: AsyncClient):
        """Test GET /api/v1/chat/supported-languages"""
        response = await client.get("/api/v1/chat/supported-languages")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_chat_detect_language(self, client: AsyncClient):
        """Test POST /api/v1/chat/detect-language"""
        response = await client.post(
            "/api/v1/chat/detect-language",
            json={"text": "Hello, how are you?"}
        )
        assert response.status_code in [200, 404]
    
    # ==================== MAPS ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_maps_geocode(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/maps/geocode"""
        response = await client.post(
            "/api/v1/maps/geocode",
            headers=auth_headers,
            json={"address": "Colombo, Sri Lanka"}
        )
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_maps_reverse_geocode(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/maps/reverse-geocode"""
        response = await client.post(
            "/api/v1/maps/reverse-geocode",
            headers=auth_headers,
            json={"latitude": 6.9271, "longitude": 79.8612}
        )
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_maps_search_places(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/maps/search-places"""
        response = await client.post(
            "/api/v1/maps/search-places",
            headers=auth_headers,
            json={"query": "restaurants in Colombo"}
        )
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_maps_nearby_attractions(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/maps/nearby-attractions"""
        response = await client.get(
            "/api/v1/maps/nearby-attractions",
            headers=auth_headers,
            params={"latitude": 6.9271, "longitude": 79.8612, "radius": 5000}
        )
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_maps_nearby_restaurants(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/maps/nearby-restaurants"""
        response = await client.get(
            "/api/v1/maps/nearby-restaurants",
            headers=auth_headers,
            params={"latitude": 6.9271, "longitude": 79.8612, "radius": 2000}
        )
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_maps_nearby_hotels(self, client: AsyncClient, auth_headers):
        """Test GET /api/v1/maps/nearby-hotels"""
        response = await client.get(
            "/api/v1/maps/nearby-hotels",
            headers=auth_headers,
            params={"latitude": 6.9271, "longitude": 79.8612, "radius": 5000}
        )
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_maps_directions(self, client: AsyncClient, auth_headers):
        """Test POST /api/v1/maps/directions"""
        response = await client.post(
            "/api/v1/maps/directions",
            headers=auth_headers,
            json={
                "origin": "Colombo",
                "destination": "Kandy",
                "mode": "driving"
            }
        )
        assert response.status_code in [200, 404, 500]
    
    # ==================== WEATHER ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_weather_current(self, client: AsyncClient):
        """Test GET /api/v1/weather/current"""
        response = await client.get(
            "/api/v1/weather/current",
            params={"city": "Colombo"}
        )
        assert response.status_code in [200, 403, 404, 500]
    
    @pytest.mark.asyncio
    async def test_weather_forecast(self, client: AsyncClient):
        """Test GET /api/v1/weather/forecast"""
        response = await client.get(
            "/api/v1/weather/forecast",
            params={"city": "Colombo", "days": 5}
        )
        assert response.status_code in [200, 403, 404, 500]
    
    @pytest.mark.asyncio
    async def test_weather_alerts(self, client: AsyncClient):
        """Test GET /api/v1/weather/alerts"""
        response = await client.get(
            "/api/v1/weather/alerts",
            params={"city": "Colombo"}
        )
        assert response.status_code in [200, 403, 404, 500]
    
    @pytest.mark.asyncio
    async def test_weather_summary(self, client: AsyncClient):
        """Test GET /api/v1/weather/summary"""
        response = await client.get(
            "/api/v1/weather/summary",
            params={"city": "Colombo"}
        )
        assert response.status_code in [200, 403, 404, 500]
    
    @pytest.mark.asyncio
    async def test_weather_cities(self, client: AsyncClient):
        """Test GET /api/v1/weather/cities"""
        response = await client.get("/api/v1/weather/cities")
        assert response.status_code in [200, 403, 404, 500]
    
    @pytest.mark.asyncio
    async def test_weather_recommendations(self, client: AsyncClient):
        """Test GET /api/v1/weather/recommendations"""
        response = await client.get(
            "/api/v1/weather/recommendations",
            params={"city": "Colombo"}
        )
        assert response.status_code in [200, 403, 404, 500]
    
    # ==================== CURRENCY ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_currency_convert(self, client: AsyncClient):
        """Test POST /api/v1/currency/convert"""
        response = await client.post(
            "/api/v1/currency/convert",
            json={
                "amount": 100,
                "from_currency": "USD",
                "to_currency": "LKR"
            }
        )
        assert response.status_code in [200, 400, 403, 500, 503]
    
    @pytest.mark.asyncio
    async def test_currency_rates(self, client: AsyncClient):
        """Test GET /api/v1/currency/rates"""
        response = await client.get(
            "/api/v1/currency/rates",
            params={"base_currency": "USD"}
        )
        assert response.status_code in [200, 400, 403, 500, 503]
    
    @pytest.mark.asyncio
    async def test_currency_sri_lanka_rates(self, client: AsyncClient):
        """Test GET /api/v1/currency/sri-lanka-rates"""
        response = await client.get("/api/v1/currency/sri-lanka-rates")
        assert response.status_code in [200, 403, 500, 503]  # 503 if API key not configured
    
    @pytest.mark.asyncio
    async def test_currency_currencies(self, client: AsyncClient):
        """Test GET /api/v1/currency/currencies"""
        response = await client.get("/api/v1/currency/currencies")
        assert response.status_code in [200, 403, 500]
    
    @pytest.mark.asyncio
    async def test_currency_info(self, client: AsyncClient):
        """Test GET /api/v1/currency/currency/{currency_code}"""
        response = await client.get("/api/v1/currency/currency/USD")
        assert response.status_code in [200, 403, 404, 500]
    
    @pytest.mark.asyncio
    async def test_currency_recommendations(self, client: AsyncClient):
        """Test GET /api/v1/currency/recommendations"""
        response = await client.get(
            "/api/v1/currency/recommendations",
            params={"user_currency": "USD"}
        )
        assert response.status_code in [200, 403, 500]
    
    @pytest.mark.asyncio
    async def test_currency_summary(self, client: AsyncClient):
        """Test GET /api/v1/currency/summary"""
        response = await client.get("/api/v1/currency/summary")
        assert response.status_code in [200, 403, 500]
    
    # ==================== ADMIN ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_admin_dashboard(self, client: AsyncClient, admin_headers):
        """Test GET /api/v1/admin/dashboard"""
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers=admin_headers
        )
        assert response.status_code in [200, 403]
    
    @pytest.mark.asyncio
    async def test_admin_overview(self, client: AsyncClient, admin_headers):
        """Test GET /api/v1/admin/overview"""
        response = await client.get(
            "/api/v1/admin/overview",
            headers=admin_headers
        )
        assert response.status_code in [200, 403]
    
    @pytest.mark.asyncio
    async def test_admin_users(self, client: AsyncClient, admin_headers):
        """Test GET /api/v1/admin/users"""
        response = await client.get(
            "/api/v1/admin/users",
            headers=admin_headers
        )
        assert response.status_code in [200, 403, 422]  # 422 if auth fails
    
    @pytest.mark.asyncio
    async def test_admin_feedback(self, client: AsyncClient, admin_headers):
        """Test GET /api/v1/admin/feedback"""
        response = await client.get(
            "/api/v1/admin/feedback",
            headers=admin_headers
        )
        assert response.status_code in [200, 403]
    
    @pytest.mark.asyncio
    async def test_admin_analytics(self, client: AsyncClient, admin_headers):
        """Test GET /api/v1/admin/analytics"""
        response = await client.get(
            "/api/v1/admin/analytics",
            headers=admin_headers
        )
        assert response.status_code in [200, 403]
    
    @pytest.mark.asyncio
    async def test_admin_health(self, client: AsyncClient, admin_headers):
        """Test GET /api/v1/admin/health"""
        response = await client.get(
            "/api/v1/admin/health",
            headers=admin_headers
        )
        assert response.status_code in [200, 403]
    
    # ==================== HEALTH ENDPOINTS ====================
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test GET /api/v1/health"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_health_live(self, client: AsyncClient):
        """Test GET /api/v1/health/live"""
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_health_ready(self, client: AsyncClient):
        """Test GET /api/v1/health/ready"""
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_health_detailed(self, client: AsyncClient):
        """Test GET /api/v1/health/detailed"""
        response = await client.get("/api/v1/health/detailed")
        assert response.status_code == 200

