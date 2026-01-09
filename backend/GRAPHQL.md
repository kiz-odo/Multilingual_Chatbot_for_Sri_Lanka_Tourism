# 🔷 GraphQL API Documentation

Complete GraphQL API documentation for the backend.

## Overview

The backend provides a GraphQL API alongside the REST API for flexible data querying. GraphQL allows clients to request exactly the data they need.

## GraphQL Endpoint

### Base URL

- **Development**: `http://localhost:8000/graphql`
- **Production**: `https://api.yourdomain.com/graphql`

### GraphQL Playground

Access the interactive GraphQL Playground at:
- **Development**: http://localhost:8000/graphql

## Authentication

GraphQL queries require authentication via JWT token:

```http
Authorization: Bearer <access_token>
```

## GraphQL Schema

### Types

#### User

```graphql
type User {
  id: ID!
  email: String!
  fullName: String!
  role: UserRole!
  preferredLanguage: String!
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum UserRole {
  GUEST
  USER
  MODERATOR
  ADMIN
}
```

#### Attraction

```graphql
type Attraction {
  id: ID!
  name: String!
  description: String!
  category: String!
  location: Location!
  images: [String!]!
  rating: Float!
  reviewsCount: Int!
  entryFee: Float
  createdAt: DateTime!
}

type Location {
  address: String!
  city: String!
  province: String!
  coordinates: [Float!]!
}
```

#### Conversation

```graphql
type Conversation {
  id: ID!
  userId: ID!
  title: String
  language: String!
  messages: [Message!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Message {
  id: ID!
  sender: MessageSender!
  content: String!
  type: MessageType!
  language: String!
  timestamp: DateTime!
}

enum MessageSender {
  USER
  ASSISTANT
}

enum MessageType {
  TEXT
  IMAGE
  AUDIO
}
```

#### Itinerary

```graphql
type Itinerary {
  id: ID!
  userId: ID!
  title: String!
  destination: String!
  durationDays: Int!
  budget: Float
  days: [ItineraryDay!]!
  shareToken: String
  isPublic: Boolean!
  createdAt: DateTime!
}

type ItineraryDay {
  day: Int!
  date: DateTime
  activities: [Activity!]!
  accommodations: [String!]!
  meals: [String!]!
}

type Activity {
  name: String!
  description: String
  time: String
  location: Location
}
```

## Queries

### Get Current User

```graphql
query {
  me {
    id
    email
    fullName
    role
    preferredLanguage
  }
}
```

**Response**:
```json
{
  "data": {
    "me": {
      "id": "user123",
      "email": "user@example.com",
      "fullName": "John Doe",
      "role": "USER",
      "preferredLanguage": "en"
    }
  }
}
```

### Get Attractions

```graphql
query {
  attractions(
    page: 1
    limit: 20
    category: "beach"
  ) {
    id
    name
    description
    category
    location {
      address
      city
      coordinates
    }
    rating
    images
  }
}
```

**Response**:
```json
{
  "data": {
    "attractions": [
      {
        "id": "attr1",
        "name": "Unawatuna Beach",
        "description": "Beautiful beach...",
        "category": "beach",
        "location": {
          "address": "Unawatuna",
          "city": "Galle",
          "coordinates": [80.25, 6.0]
        },
        "rating": 4.5,
        "images": ["url1", "url2"]
      }
    ]
  }
}
```

### Get Attraction by ID

```graphql
query {
  attraction(id: "attr1") {
    id
    name
    description
    category
    location {
      address
      city
      coordinates
    }
    rating
    reviewsCount
    entryFee
    images
  }
}
```

### Get Conversations

```graphql
query {
  conversations {
    id
    title
    language
    messages {
      id
      sender
      content
      timestamp
    }
    createdAt
  }
}
```

### Get Conversation by ID

```graphql
query {
  conversation(id: "conv1") {
    id
    title
    language
    messages {
      id
      sender
      content
      type
      timestamp
    }
    createdAt
    updatedAt
  }
}
```

### Get Itineraries

```graphql
query {
  itineraries {
    id
    title
    destination
    durationDays
    budget
    days {
      day
      activities {
        name
        description
        time
      }
    }
    createdAt
  }
}
```

### Get Itinerary by ID

```graphql
query {
  itinerary(id: "itinerary1") {
    id
    title
    destination
    durationDays
    budget
    days {
      day
      date
      activities {
        name
        description
        time
        location {
          address
          coordinates
        }
      }
      accommodations
      meals
    }
    shareToken
    isPublic
  }
}
```

### Search Attractions

```graphql
query {
  searchAttractions(
    query: "beach"
    location: {
      lat: 6.9271
      lng: 79.8612
    }
    radius: 10
  ) {
    id
    name
    description
    location {
      address
      city
      coordinates
    }
    rating
  }
}
```

## Mutations

### Send Chat Message

```graphql
mutation {
  sendMessage(
    message: "What are the best beaches in Sri Lanka?"
    language: "en"
    conversationId: "conv1"
  ) {
    response
    conversationId
    language
    confidence
  }
}
```

**Response**:
```json
{
  "data": {
    "sendMessage": {
      "response": "Sri Lanka has many beautiful beaches...",
      "conversationId": "conv1",
      "language": "en",
      "confidence": 0.95
    }
  }
}
```

### Create Itinerary

```graphql
mutation {
  createItinerary(
    input: {
      destination: "Colombo"
      durationDays: 3
      budget: 50000
      interests: ["beaches", "culture"]
      travelStyle: "adventure"
    }
  ) {
    id
    title
    destination
    durationDays
    days {
      day
      activities {
        name
        description
      }
    }
  }
}
```

### Update Itinerary

```graphql
mutation {
  updateItinerary(
    id: "itinerary1"
    input: {
      destination: "Updated Destination"
      budget: 60000
    }
  ) {
    id
    destination
    budget
  }
}
```

### Delete Itinerary

```graphql
mutation {
  deleteItinerary(id: "itinerary1")
}
```

**Response**:
```json
{
  "data": {
    "deleteItinerary": true
  }
}
```

### Favorite Attraction

```graphql
mutation {
  favoriteAttraction(attractionId: "attr1")
}
```

### Unfavorite Attraction

```graphql
mutation {
  unfavoriteAttraction(attractionId: "attr1")
}
```

## Field Selection

GraphQL allows selecting only needed fields:

```graphql
# Minimal query
query {
  attractions {
    id
    name
  }
}

# Detailed query
query {
  attractions {
    id
    name
    description
    category
    location {
      address
      city
      province
      coordinates
    }
    rating
    reviewsCount
    entryFee
    images
    openingHours
    contactInfo {
      phone
      email
      website
    }
  }
}
```

## Variables

Use variables for dynamic queries:

```graphql
query GetAttraction($id: ID!) {
  attraction(id: $id) {
    id
    name
    description
  }
}
```

**Variables**:
```json
{
  "id": "attr1"
}
```

## Fragments

Reuse field selections with fragments:

```graphql
fragment AttractionDetails on Attraction {
  id
  name
  description
  location {
    address
    city
    coordinates
  }
  rating
}

query {
  attractions {
    ...AttractionDetails
  }
  searchAttractions(query: "beach") {
    ...AttractionDetails
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "errors": [
    {
      "message": "Authentication required",
      "extensions": {
        "code": "UNAUTHENTICATED",
        "statusCode": 401
      }
    }
  ],
  "data": null
}
```

### Common Error Codes

- `UNAUTHENTICATED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid input
- `INTERNAL_ERROR`: Server error

## Rate Limiting

GraphQL queries are subject to rate limiting:

- **Default**: 100 requests/minute
- **Authenticated**: 200 requests/minute
- **Complex Queries**: May count as multiple requests

## Best Practices

### 1. Request Only Needed Fields

```graphql
# Good: Only request needed fields
query {
  attractions {
    id
    name
    rating
  }
}

# Bad: Request all fields
query {
  attractions {
    id
    name
    description
    category
    location { ... }
    images
    rating
    reviewsCount
    # ... many more fields
  }
}
```

### 2. Use Variables

```graphql
# Good: Use variables
query GetAttraction($id: ID!) {
  attraction(id: $id) { ... }
}

# Bad: Hardcode values
query {
  attraction(id: "attr1") { ... }
}
```

### 3. Use Fragments

```graphql
# Good: Reuse with fragments
fragment AttractionDetails on Attraction { ... }
query { attractions { ...AttractionDetails } }
```

### 4. Pagination

```graphql
query {
  attractions(page: 1, limit: 20) {
    id
    name
  }
}
```

## Comparison with REST API

### GraphQL Advantages

- **Flexible Queries**: Request exactly what you need
- **Single Endpoint**: One endpoint for all queries
- **Type Safety**: Strong typing system
- **Introspection**: Self-documenting schema

### REST API Advantages

- **Caching**: Better HTTP caching support
- **Simplicity**: Simpler for simple queries
- **Familiarity**: More developers familiar with REST

## Implementation

### Schema Definition

**Location**: `backend/app/graphql/schema.py`

```python
import strawberry
from typing import List, Optional

@strawberry.type
class User:
    id: str
    email: str
    full_name: str
    role: str

@strawberry.type
class Query:
    @strawberry.field
    async def me(self) -> User:
        # Implementation
        pass
```

### Resolvers

**Location**: `backend/app/graphql/resolvers.py`

```python
async def resolve_attractions(
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None
) -> List[Attraction]:
    # Implementation
    pass
```

## Future Enhancements

1. **Subscriptions**: Real-time updates via WebSocket
2. **File Uploads**: GraphQL file upload support
3. **Batch Operations**: Batch mutations
4. **Caching**: Query result caching
5. **Rate Limiting**: Per-field rate limiting

