"""
Load Testing with Locust
Tests API performance under load
"""

from locust import HttpUser, task, between, events
import json
import random


class TourismChatbotUser(HttpUser):
    """
    Simulates a user interacting with the Tourism Chatbot API
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - login or register"""
        # Register a test user
        self.username = f"loadtest_user_{random.randint(1000, 9999)}"
        self.email = f"{self.username}@loadtest.com"
        self.password = "LoadTest123!"
        
        # Try to register
        response = self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "full_name": "Load Test User"
        }, catch_response=True)
        
        if response.status_code in [200, 201]:
            self.token = response.json().get("access_token")
        else:
            # User might already exist, try login
            response = self.client.post("/api/v1/auth/login", json={
                "email": self.email,
                "password": self.password
            })
            if response.status_code == 200:
                self.token = response.json().get("access_token")
    
    @property
    def headers(self):
        """Authorization headers"""
        return {"Authorization": f"Bearer {self.token}"} if hasattr(self, 'token') else {}
    
    @task(10)
    def get_attractions(self):
        """Get attractions list - most common operation"""
        self.client.get("/api/v1/attractions", headers=self.headers)
    
    @task(5)
    def get_hotels(self):
        """Get hotels list"""
        self.client.get("/api/v1/hotels", headers=self.headers)
    
    @task(5)
    def get_restaurants(self):
        """Get restaurants list"""
        self.client.get("/api/v1/restaurants", headers=self.headers)
    
    @task(8)
    def send_chat_message(self):
        """Send chat message - core functionality"""
        messages = [
            "What are the best beaches in Sri Lanka?",
            "Show me hotels in Colombo",
            "What's the weather like in Kandy?",
            "Tell me about Sigiriya",
            "What are the top attractions in Galle?"
        ]
        
        self.client.post("/api/v1/chat/message", 
            headers=self.headers,
            json={
                "message": random.choice(messages),
                "language": "en",
                "sender_id": self.username
            }
        )
    
    @task(3)
    def get_weather(self):
        """Get weather information"""
        cities = ["Colombo", "Kandy", "Galle", "Jaffna", "Trincomalee"]
        self.client.get(f"/api/v1/weather/{random.choice(cities)}", headers=self.headers)
    
    @task(2)
    def get_recommendations(self):
        """Get personalized recommendations"""
        self.client.get("/api/v1/recommendations", headers=self.headers)
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")


class AuthenticationLoadTest(HttpUser):
    """
    Tests authentication endpoints specifically
    """
    wait_time = between(2, 5)
    
    @task
    def test_login_flow(self):
        """Test complete login flow"""
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        }, catch_response=True)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            refresh_token = response.json().get("refresh_token")
            
            # Make authenticated request
            self.client.get("/api/v1/users/me", 
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Refresh token
            self.client.post("/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )


class ReadOnlyUser(HttpUser):
    """
    Simulates unauthenticated users browsing content
    """
    wait_time = between(1, 2)
    
    @task(10)
    def browse_attractions(self):
        """Browse attractions without auth"""
        self.client.get("/api/v1/attractions")
    
    @task(5)
    def view_attraction_details(self):
        """View specific attraction"""
        # Simulate viewing random attraction IDs
        attraction_id = random.randint(1, 100)
        self.client.get(f"/api/v1/attractions/{attraction_id}", catch_response=True)
    
    @task(3)
    def browse_hotels(self):
        """Browse hotels"""
        self.client.get("/api/v1/hotels")
    
    @task(3)
    def check_weather(self):
        """Check weather"""
        cities = ["Colombo", "Kandy", "Galle"]
        self.client.get(f"/api/v1/weather/{random.choice(cities)}")


# Event listeners for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Failure rate: {environment.stats.total.fail_ratio:.2%}")
