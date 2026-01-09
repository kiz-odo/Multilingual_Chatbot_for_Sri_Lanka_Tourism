# 📚 API Documentation

Complete REST API reference for the Sri Lanka Tourism Multilingual Chatbot backend.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure via environment variables

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Getting an Access Token

```bash
# Register a new user
POST /api/v1/auth/register

# Login
POST /api/v1/auth/login
```

## API Versioning

All endpoints are versioned under `/api/v1/`. Future versions will use `/api/v2/`, etc.

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Success message",
  "status": "success"
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": { ... }
  },
  "status": "error"
}
```

## Endpoints

### Authentication (`/api/v1/auth`)

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "preferred_language": "en"
}
```

**Response**: `201 Created`
```json
{
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "message": "User registered successfully"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Update Current User
```http
PUT /api/v1/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Updated",
  "preferred_language": "si"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

#### Enable MFA
```http
POST /api/v1/auth/enable-mfa
Authorization: Bearer <access_token>
```

**Response**: QR code data for authenticator app

#### Verify MFA
```http
POST /api/v1/auth/verify-mfa
Content-Type: application/json

{
  "token": "123456"
}
```

### Chat & AI (`/api/v1/chat`)

#### Send Message
```http
POST /api/v1/chat/message
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What are the best beaches in Sri Lanka?",
  "language": "en",
  "conversation_id": "optional_conversation_id"
}
```

**Response**: `200 OK`
```json
{
  "response": "Sri Lanka has many beautiful beaches...",
  "conversation_id": "conv_id",
  "language": "en",
  "confidence": 0.95
}
```

#### Voice Message
```http
POST /api/v1/chat/voice
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "audio": <file>,
  "language": "en"
}
```

#### Detect Language
```http
POST /api/v1/chat/detect-language
Content-Type: application/json

{
  "text": "සිංහල පෙළ"
}
```

**Response**:
```json
{
  "language": "si",
  "confidence": 0.98
}
```

#### Get Conversations
```http
GET /api/v1/chat/conversations
Authorization: Bearer <access_token>
```

#### Get Conversation by ID
```http
GET /api/v1/chat/conversations/{conversation_id}
Authorization: Bearer <access_token>
```

#### Delete Conversation
```http
DELETE /api/v1/chat/conversations/{conversation_id}
Authorization: Bearer <access_token>
```

#### Get Suggestions
```http
GET /api/v1/chat/suggestions?language=en
Authorization: Bearer <access_token>
```

#### Get Supported Languages
```http
GET /api/v1/chat/supported-languages
```

### Attractions (`/api/v1/attractions`)

#### List Attractions
```http
GET /api/v1/attractions?page=1&limit=20&category=beach
```

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `category` (str): Filter by category
- `search` (str): Search query

#### Search Attractions
```http
GET /api/v1/attractions/search?q=beach&location=colombo
```

#### Get Attraction by ID
```http
GET /api/v1/attractions/{attraction_id}
```

#### Get Categories
```http
GET /api/v1/attractions/categories
```

#### Get Featured Attractions
```http
GET /api/v1/attractions/featured
```

#### Get Popular Attractions
```http
GET /api/v1/attractions/popular
```

#### Get Nearby Attractions
```http
GET /api/v1/attractions/nearby?lat=6.9271&lng=79.8612&radius=10
```

#### Add Review
```http
POST /api/v1/attractions/{attraction_id}/reviews
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rating": 5,
  "comment": "Beautiful place!"
}
```

#### Favorite Attraction
```http
POST /api/v1/attractions/{attraction_id}/favorite
Authorization: Bearer <access_token>
```

### Hotels (`/api/v1/hotels`)

#### List Hotels
```http
GET /api/v1/hotels?page=1&limit=20&location=colombo
```

#### Search Hotels
```http
GET /api/v1/hotels/search?q=luxury&min_price=100&max_price=500
```

#### Get Hotel by ID
```http
GET /api/v1/hotels/{hotel_id}
```

### Restaurants (`/api/v1/restaurants`)

#### List Restaurants
```http
GET /api/v1/restaurants?page=1&limit=20&cuisine=sri_lankan
```

#### Search Restaurants
```http
GET /api/v1/restaurants/search?q=seafood&location=colombo
```

#### Get Restaurant by ID
```http
GET /api/v1/restaurants/{restaurant_id}
```

### Transport (`/api/v1/transport`)

#### List Transport Options
```http
GET /api/v1/transport?type=train&from=colombo&to=kandy
```

#### Search Transport
```http
GET /api/v1/transport/search?q=bus&location=colombo
```

#### Get Transport by ID
```http
GET /api/v1/transport/{transport_id}
```

### Weather (`/api/v1/weather`)

#### Get Current Weather
```http
GET /api/v1/weather/current?city=colombo
```

**Response**:
```json
{
  "city": "Colombo",
  "temperature": 28,
  "condition": "Partly Cloudy",
  "humidity": 75,
  "wind_speed": 15
}
```

#### Get Forecast
```http
GET /api/v1/weather/forecast?city=colombo&days=5
```

#### Get Weather Alerts
```http
GET /api/v1/weather/alerts?city=colombo
```

### Currency (`/api/v1/currency`)

#### Convert Currency
```http
POST /api/v1/currency/convert
Content-Type: application/json

{
  "from": "USD",
  "to": "LKR",
  "amount": 100
}
```

#### Get Exchange Rates
```http
GET /api/v1/currency/rates?base=USD
```

#### Get Sri Lanka Rates
```http
GET /api/v1/currency/sri-lanka-rates
```

### Itinerary (`/api/v1/itinerary`)

#### Generate Itinerary
```http
POST /api/v1/itinerary/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "destination": "Colombo",
  "duration_days": 3,
  "budget": 50000,
  "interests": ["beaches", "culture"],
  "travel_style": "adventure"
}
```

**Response**: `201 Created`
```json
{
  "id": "itinerary_id",
  "destination": "Colombo",
  "duration_days": 3,
  "days": [
    {
      "day": 1,
      "activities": [...]
    }
  ]
}
```

#### Get My Itineraries
```http
GET /api/v1/itinerary/my-itineraries
Authorization: Bearer <access_token>
```

#### Get Itinerary by ID
```http
GET /api/v1/itinerary/{itinerary_id}
Authorization: Bearer <access_token>
```

#### Update Itinerary
```http
PUT /api/v1/itinerary/{itinerary_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "destination": "Updated Destination"
}
```

#### Share Itinerary
```http
GET /api/v1/itinerary/share/{share_token}
```

#### Export Itinerary as PDF
```http
POST /api/v1/itinerary/{itinerary_id}/export/pdf
Authorization: Bearer <access_token>
```

#### Export Itinerary as Calendar (ICS)
```http
POST /api/v1/itinerary/{itinerary_id}/export/calendar/ics
Authorization: Bearer <access_token>
```

### Maps (`/api/v1/maps`)

#### Geocode Address
```http
POST /api/v1/maps/geocode
Content-Type: application/json

{
  "address": "Colombo, Sri Lanka"
}
```

#### Reverse Geocode
```http
POST /api/v1/maps/reverse-geocode
Content-Type: application/json

{
  "lat": 6.9271,
  "lng": 79.8612
}
```

#### Search Places
```http
POST /api/v1/maps/search-places
Content-Type: application/json

{
  "query": "restaurants",
  "location": {
    "lat": 6.9271,
    "lng": 79.8612
  }
}
```

#### Get Directions
```http
POST /api/v1/maps/directions
Content-Type: application/json

{
  "origin": {
    "lat": 6.9271,
    "lng": 79.8612
  },
  "destination": {
    "lat": 7.2906,
    "lng": 80.6337
  }
}
```

### Safety (`/api/v1/safety`)

#### Send SOS Alert
```http
POST /api/v1/safety/sos
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "location": {
    "lat": 6.9271,
    "lng": 79.8612
  },
  "message": "Emergency situation"
}
```

#### Get Safety Score
```http
GET /api/v1/safety/score/{city}
```

#### Get Travel Alerts
```http
GET /api/v1/safety/alerts?location=colombo
```

#### Get Emergency Numbers
```http
GET /api/v1/safety/emergency-numbers
```

### Emergency Services (`/api/v1/emergency`)

#### List Emergency Services
```http
GET /api/v1/emergency
```

#### Search Emergency Services
```http
GET /api/v1/emergency/search?type=hospital&location=colombo
```

#### Get Emergency Service by ID
```http
GET /api/v1/emergency/{service_id}
```

### Events (`/api/v1/events`)

#### List Events
```http
GET /api/v1/events?date=2024-01-15&location=colombo
```

#### Search Events
```http
GET /api/v1/events/search?q=festival&category=cultural
```

#### Get Event by ID
```http
GET /api/v1/events/{event_id}
```

### Feedback (`/api/v1/feedback`)

#### Submit Feedback
```http
POST /api/v1/feedback
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "suggestion",
  "message": "Great chatbot!",
  "rating": 5
}
```

#### Get Feedback
```http
GET /api/v1/feedback
Authorization: Bearer <access_token>
```

### Recommendations (`/api/v1/recommendations`)

#### Get Recommendations
```http
POST /api/v1/recommendations
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "user_id",
  "preferences": {
    "interests": ["beaches", "culture"],
    "budget": 50000
  }
}
```

#### Get Similar Resources
```http
GET /api/v1/recommendations/similar/{resource_type}/{resource_id}
```

### Forum (`/api/v1/forum`)

#### Get Posts
```http
GET /api/v1/forum/posts?page=1&limit=20
```

#### Create Post
```http
POST /api/v1/forum/posts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Best places to visit",
  "content": "I recommend visiting..."
}
```

#### Get Post by ID
```http
GET /api/v1/forum/posts/{post_id}
```

#### Update Post
```http
PUT /api/v1/forum/posts/{post_id}
Authorization: Bearer <access_token>
```

#### Delete Post
```http
DELETE /api/v1/forum/posts/{post_id}
Authorization: Bearer <access_token>
```

#### Add Comment
```http
POST /api/v1/forum/posts/{post_id}/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Great post!"
}
```

### Challenges (`/api/v1/challenges`)

#### List Challenges
```http
GET /api/v1/challenges
```

#### Get My Progress
```http
GET /api/v1/challenges/my-progress
Authorization: Bearer <access_token>
```

#### Check In
```http
POST /api/v1/challenges/{challenge_id}/check-in
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "location": {
    "lat": 6.9271,
    "lng": 79.8612
  }
}
```

#### Get Leaderboard
```http
GET /api/v1/challenges/leaderboard
```

### Landmarks (`/api/v1/landmarks`)

#### Recognize Landmark
```http
POST /api/v1/landmarks/recognize
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "image": <file>
}
```

#### Get Nearby Landmarks
```http
GET /api/v1/landmarks/nearby?lat=6.9271&lng=79.8612&radius=5
```

### Admin (`/api/v1/admin`)

All admin endpoints require admin role.

#### Get Dashboard
```http
GET /api/v1/admin/dashboard
Authorization: Bearer <admin_access_token>
```

#### Get Users
```http
GET /api/v1/admin/users
Authorization: Bearer <admin_access_token>
```

#### Update User
```http
PUT /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_access_token>
```

#### Get Analytics
```http
GET /api/v1/admin/analytics
Authorization: Bearer <admin_access_token>
```

### Health (`/health`)

#### Basic Health Check
```http
GET /health
```

#### Liveness Probe
```http
GET /health/live
```

#### Readiness Probe
```http
GET /health/ready
```

#### Detailed Health
```http
GET /health/detailed
```

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Authenticated**: 200 requests per minute per user
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

## Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Missing or invalid token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource not found |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error |
| `503` | Service Unavailable - External service down |

## Pagination

List endpoints support pagination:

```
GET /api/v1/attractions?page=1&limit=20
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering & Sorting

Many endpoints support filtering and sorting:

```
GET /api/v1/attractions?category=beach&sort=rating&order=desc
```

## WebSocket API

WebSocket endpoint for real-time chat:

```
ws://localhost:8000/ws/chat?token=<access_token>
```

See WebSocket documentation for message formats.

## GraphQL API

GraphQL endpoint available at:

```
POST /graphql
```

See [GRAPHQL.md](./GRAPHQL.md) for GraphQL API documentation.

