# 📊 Data Models Documentation

Complete documentation of all data models in the backend using Beanie ODM.

## Overview

All models use **Beanie** (async MongoDB ODM) for type-safe database operations. Models are defined as Pydantic models with Beanie Document base class.

## Model Structure

```
backend/app/models/
├── user.py              # User accounts and profiles
├── conversation.py      # Chat conversations and messages
├── attraction.py       # Tourist attractions
├── hotel.py            # Hotel listings
├── restaurant.py       # Restaurant listings
├── transport.py       # Transport options
├── itinerary.py       # Trip itineraries
├── event.py            # Tourism events
├── feedback.py         # User feedback
├── emergency.py        # Emergency services
├── safety.py           # Safety data
├── challenge.py        # Tourism challenges
├── forum.py            # Forum posts and comments
├── recommendation.py   # Recommendations
├── analytics.py        # Analytics data
├── notification.py     # Notifications
└── security.py         # Security-related models
```

## Core Models

### 1. User Model

**Location**: `backend/app/models/user.py`

**Purpose**: User accounts, profiles, and authentication.

**Fields**:
```python
class User(Document):
    email: Indexed(str, unique=True)
    hashed_password: str
    full_name: str
    role: UserRole  # guest, user, moderator, admin
    preferred_language: str
    preferences: UserPreferences
    location: Optional[UserLocation]
    stats: UserStats
    email_verified: bool
    mfa_enabled: bool
    mfa_secret: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
```

**Indexes**:
- `email`: Unique index for fast lookups
- `role`: Index for role-based queries

**Relationships**:
- One-to-many with `Conversation`
- One-to-many with `Itinerary`
- One-to-many with `Feedback`

### 2. Conversation Model

**Location**: `backend/app/models/conversation.py`

**Purpose**: Chat conversations and messages.

**Fields**:
```python
class Conversation(Document):
    user_id: str
    title: Optional[str]
    language: str
    messages: List[Message]
    context: ConversationContext
    created_at: datetime
    updated_at: datetime
    archived: bool

class Message(BaseModel):
    id: str
    sender: MessageSender  # user, assistant
    content: str
    type: MessageType  # text, image, audio
    language: str
    timestamp: datetime
    metadata: Optional[Dict]
```

**Indexes**:
- `user_id`: Index for user conversations
- `created_at`: Index for sorting

**Relationships**:
- Many-to-one with `User`

### 3. Attraction Model

**Location**: `backend/app/models/attraction.py`

**Purpose**: Tourist attractions data.

**Fields**:
```python
class Attraction(Document):
    name: str
    description: str
    category: str  # beach, temple, national_park, etc.
    location: Location
    images: List[str]
    rating: float
    reviews_count: int
    opening_hours: Optional[Dict]
    entry_fee: Optional[float]
    contact_info: Optional[ContactInfo]
    features: List[str]
    languages: List[str]  # Available languages
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `category`: Index for category filtering
- `location.coordinates`: Geospatial index
- `rating`: Index for sorting

**Relationships**:
- Many-to-many with `User` (favorites)

### 4. Hotel Model

**Location**: `backend/app/models/hotel.py`

**Purpose**: Hotel listings.

**Fields**:
```python
class Hotel(Document):
    name: str
    description: str
    location: Location
    star_rating: int
    price_range: str
    amenities: List[str]
    images: List[str]
    contact_info: ContactInfo
    booking_url: Optional[str]
    availability: Optional[Dict]
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `location.coordinates`: Geospatial index
- `star_rating`: Index for filtering
- `price_range`: Index for price filtering

### 5. Restaurant Model

**Location**: `backend/app/models/restaurant.py`

**Purpose**: Restaurant listings.

**Fields**:
```python
class Restaurant(Document):
    name: str
    description: str
    cuisine_type: str
    location: Location
    price_range: str
    rating: float
    images: List[str]
    opening_hours: Dict
    contact_info: ContactInfo
    dietary_options: List[str]  # vegetarian, vegan, halal, etc.
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `cuisine_type`: Index for cuisine filtering
- `location.coordinates`: Geospatial index
- `rating`: Index for sorting

### 6. Transport Model

**Location**: `backend/app/models/transport.py`

**Purpose**: Transport options.

**Fields**:
```python
class Transport(Document):
    type: TransportType  # train, bus, taxi, tuk_tuk
    name: str
    description: str
    route: Optional[Route]
    schedule: Optional[Dict]
    price: Optional[float]
    contact_info: Optional[ContactInfo]
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `type`: Index for type filtering

### 7. Itinerary Model

**Location**: `backend/app/models/itinerary.py`

**Purpose**: User trip plans.

**Fields**:
```python
class Itinerary(Document):
    user_id: str
    title: str
    destination: str
    duration_days: int
    budget: Optional[float]
    days: List[ItineraryDay]
    share_token: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime

class ItineraryDay(BaseModel):
    day: int
    date: Optional[datetime]
    activities: List[Activity]
    accommodations: List[str]
    meals: List[str]
```

**Indexes**:
- `user_id`: Index for user itineraries
- `share_token`: Unique index for sharing
- `created_at`: Index for sorting

**Relationships**:
- Many-to-one with `User`

### 8. Event Model

**Location**: `backend/app/models/event.py`

**Purpose**: Tourism events.

**Fields**:
```python
class Event(Document):
    name: str
    description: str
    category: str  # festival, cultural, sports, etc.
    location: Location
    start_date: datetime
    end_date: datetime
    images: List[str]
    contact_info: Optional[ContactInfo]
    ticket_info: Optional[Dict]
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `category`: Index for category filtering
- `start_date`: Index for date filtering
- `location.coordinates`: Geospatial index

### 9. Feedback Model

**Location**: `backend/app/models/feedback.py`

**Purpose**: User feedback.

**Fields**:
```python
class Feedback(Document):
    user_id: Optional[str]
    type: FeedbackType  # bug, suggestion, complaint, praise
    message: str
    rating: Optional[int]  # 1-5
    status: FeedbackStatus  # pending, reviewed, resolved
    metadata: Optional[Dict]
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `user_id`: Index for user feedback
- `status`: Index for status filtering
- `created_at`: Index for sorting

**Relationships**:
- Many-to-one with `User` (optional)

### 10. Emergency Model

**Location**: `backend/app/models/emergency.py`

**Purpose**: Emergency services.

**Fields**:
```python
class EmergencyService(Document):
    name: str
    type: EmergencyType  # hospital, police, fire, ambulance
    location: Location
    contact_info: ContactInfo
    languages: List[str]
    available_24_7: bool
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `type`: Index for type filtering
- `location.coordinates`: Geospatial index

### 11. Safety Model

**Location**: `backend/app/models/safety.py`

**Purpose**: Safety-related data.

**Fields**:
```python
class SafetyAlert(Document):
    user_id: str
    type: SafetyAlertType  # sos, check_in, location_sharing
    location: Location
    message: Optional[str]
    status: AlertStatus
    created_at: datetime
    resolved_at: Optional[datetime]

class SafetyScore(BaseModel):
    city: str
    score: float  # 0-100
    factors: Dict[str, float]
    last_updated: datetime
```

**Indexes**:
- `user_id`: Index for user alerts
- `status`: Index for status filtering
- `location.coordinates`: Geospatial index

### 12. Challenge Model

**Location**: `backend/app/models/challenge.py`

**Purpose**: Tourism challenges and gamification.

**Fields**:
```python
class Challenge(Document):
    name: str
    description: str
    type: ChallengeType  # visit, photo, review, etc.
    location: Optional[Location]
    points: int
    badge: Optional[str]
    requirements: Dict
    active: bool
    created_at: datetime
    updated_at: datetime

class ChallengeProgress(Document):
    user_id: str
    challenge_id: str
    status: ProgressStatus  # not_started, in_progress, completed
    progress: Dict
    completed_at: Optional[datetime]
    created_at: datetime
```

**Indexes**:
- `user_id`: Index for user progress
- `challenge_id`: Index for challenge lookups
- `status`: Index for status filtering

**Relationships**:
- Many-to-one with `User`
- Many-to-one with `Challenge`

### 13. Forum Model

**Location**: `backend/app/models/forum.py`

**Purpose**: Forum posts and comments.

**Fields**:
```python
class Post(Document):
    user_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    upvotes: int
    downvotes: int
    comments_count: int
    created_at: datetime
    updated_at: datetime

class Comment(Document):
    post_id: str
    user_id: str
    content: str
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- `user_id`: Index for user posts
- `category`: Index for category filtering
- `created_at`: Index for sorting

**Relationships**:
- Many-to-one with `User`
- One-to-many with `Comment`

### 14. Recommendation Model

**Location**: `backend/app/models/recommendation.py`

**Purpose**: User recommendations.

**Fields**:
```python
class Recommendation(Document):
    user_id: str
    resource_type: ResourceType  # attraction, hotel, restaurant
    resource_id: str
    score: float
    reason: str
    created_at: datetime
```

**Indexes**:
- `user_id`: Index for user recommendations
- `resource_type`: Index for type filtering
- `score`: Index for sorting

**Relationships**:
- Many-to-one with `User`

### 15. Analytics Model

**Location**: `backend/app/models/analytics.py`

**Purpose**: System analytics.

**Fields**:
```python
class Analytics(Document):
    date: datetime
    metrics: Dict[str, Any]
    user_stats: Dict[str, int]
    api_stats: Dict[str, int]
    created_at: datetime
```

**Indexes**:
- `date`: Index for date queries

### 16. Notification Model

**Location**: `backend/app/models/notification.py`

**Purpose**: User notifications.

**Fields**:
```python
class Notification(Document):
    user_id: str
    type: NotificationType
    title: str
    message: str
    read: bool
    metadata: Optional[Dict]
    created_at: datetime
```

**Indexes**:
- `user_id`: Index for user notifications
- `read`: Index for unread filtering
- `created_at`: Index for sorting

**Relationships**:
- Many-to-one with `User`

## Common Field Types

### Location
```python
class Location(BaseModel):
    address: str
    city: str
    province: str
    country: str
    coordinates: List[float]  # [longitude, latitude]
    postal_code: Optional[str]
```

### ContactInfo
```python
class ContactInfo(BaseModel):
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    social_media: Optional[Dict]
```

## Model Relationships

### One-to-Many
- `User` → `Conversation`
- `User` → `Itinerary`
- `User` → `Feedback`
- `User` → `Notification`
- `Post` → `Comment`

### Many-to-Many
- `User` ↔ `Attraction` (favorites)
- `User` ↔ `Challenge` (progress)

## Indexes

### Index Strategy

1. **Unique Indexes**: Email, share tokens
2. **Single Field Indexes**: Category, status, rating
3. **Compound Indexes**: User ID + created_at
4. **Geospatial Indexes**: Location coordinates
5. **Text Indexes**: Searchable text fields

### Index Creation

Indexes are defined in models and created during migration:

```python
class User(Document):
    email: Indexed(str, unique=True)
    # Index created automatically
```

See [DATABASE.md](./DATABASE.md) for migration guide.

## Validation

### Pydantic Validation

All models use Pydantic for validation:

```python
from pydantic import field_validator

class User(Document):
    email: EmailStr
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        # Custom validation
        return v.lower()
```

### Custom Validators

Models can have custom validators for business logic:

```python
@field_validator('password')
@classmethod
def validate_password(cls, v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    return v
```

## Model Methods

### Instance Methods

```python
class User(Document):
    # ... fields ...
    
    async def update_last_login(self):
        self.last_login = datetime.utcnow()
        await self.save()
    
    def get_full_name(self) -> str:
        return self.full_name
```

### Class Methods

```python
class User(Document):
    # ... fields ...
    
    @classmethod
    async def get_by_email(cls, email: str):
        return await cls.find_one(cls.email == email)
    
    @classmethod
    async def get_active_users(cls):
        return await cls.find_all(cls.is_active == True).to_list()
```

## Querying Models

### Basic Queries

```python
# Find one
user = await User.find_one(User.email == "user@example.com")

# Find all
users = await User.find_all().to_list()

# Find with filter
attractions = await Attraction.find_all(
    Attraction.category == "beach"
).to_list()
```

### Advanced Queries

```python
# Pagination
attractions = await Attraction.find_all().skip(0).limit(20).to_list()

# Sorting
attractions = await Attraction.find_all().sort(-Attraction.rating).to_list()

# Geospatial
attractions = await Attraction.find(
    {"location.coordinates": {
        "$near": {
            "$geometry": {
                "type": "Point",
                "coordinates": [79.8612, 6.9271]
            },
            "$maxDistance": 10000
        }
    }}
).to_list()
```

## Model Serialization

### Response Models

Separate Pydantic models for API responses:

```python
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    
    class Config:
        from_attributes = True
```

### Excluding Fields

```python
class User(Document):
    hashed_password: str  # Excluded from responses
    
    def to_response(self) -> UserResponse:
        return UserResponse(
            id=str(self.id),
            email=self.email,
            full_name=self.full_name,
            role=self.role.value
        )
```

## Best Practices

1. **Use Indexes**: Index frequently queried fields
2. **Validate Input**: Use Pydantic validators
3. **Type Hints**: Always use type hints
4. **Async Methods**: All database operations are async
5. **Error Handling**: Handle database errors gracefully
6. **Relationships**: Use references for relationships
7. **Soft Deletes**: Consider soft deletes for important data

## Migration

Models are migrated using Beanie migrations:

```bash
python -m backend.app.core.migrations migrate
```

See [DATABASE.md](./DATABASE.md) for detailed migration guide.

