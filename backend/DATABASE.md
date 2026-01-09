# 🗄️ Database Documentation

Complete documentation of database schema, migrations, and best practices.

## Overview

The backend uses **MongoDB** as the primary database with **Beanie ODM** for async operations. Redis is used for caching and session storage.

## Database Architecture

### MongoDB

- **Version**: 6.0+
- **ODM**: Beanie 1.24.0
- **Connection**: Async via Motor driver
- **Collections**: Document-based collections

### Redis

- **Version**: 7.0+
- **Purpose**: Caching, session storage, rate limiting
- **Connection**: Async Redis client

## Database Schema

### Collections

1. **users** - User accounts and profiles
2. **conversations** - Chat conversations
3. **attractions** - Tourist attractions
4. **hotels** - Hotel listings
5. **restaurants** - Restaurant listings
6. **transport** - Transport options
7. **itineraries** - Trip plans
8. **events** - Tourism events
9. **feedback** - User feedback
10. **emergency_services** - Emergency services
11. **safety_alerts** - Safety alerts
12. **challenges** - Tourism challenges
13. **challenge_progress** - Challenge progress
14. **forum_posts** - Forum posts
15. **forum_comments** - Forum comments
16. **recommendations** - User recommendations
17. **analytics** - System analytics
18. **notifications** - User notifications

See [MODELS.md](./MODELS.md) for detailed model documentation.

## Indexes

### Index Strategy

Indexes are defined in models and created during migrations:

```python
from beanie import Document, Indexed

class User(Document):
    email: Indexed(str, unique=True)
    role: Indexed(str)
```

### Index Types

1. **Single Field Indexes**
   ```python
   email: Indexed(str, unique=True)
   ```

2. **Compound Indexes**
   ```python
   # Created via migration
   await User.create_index([("user_id", 1), ("created_at", -1)])
   ```

3. **Geospatial Indexes**
   ```python
   # For location queries
   await Attraction.create_index([("location.coordinates", "2dsphere")])
   ```

4. **Text Indexes**
   ```python
   # For full-text search
   await Attraction.create_index([("name", "text"), ("description", "text")])
   ```

### Index Creation

Indexes are created in `backend/app/core/database_indexes.py`:

```python
async def create_indexes():
    """Create all database indexes"""
    # User indexes
    await User.create_index([("email", 1)], unique=True)
    await User.create_index([("role", 1)])
    
    # Attraction indexes
    await Attraction.create_index([("category", 1)])
    await Attraction.create_index([("location.coordinates", "2dsphere")])
    await Attraction.create_index([("rating", -1)])
    
    # Conversation indexes
    await Conversation.create_index([("user_id", 1), ("created_at", -1)])
```

## Migrations

### Migration System

Migrations are handled in `backend/app/core/migrations.py`.

### Running Migrations

```bash
# Run all pending migrations
python -m backend.app.core.migrations migrate

# Rollback last migration
python -m backend.app.core.migrations rollback

# Show migration status
python -m backend.app.core.migrations status
```

### Creating Migrations

1. **Create migration file**:
   ```python
   # backend/app/core/migrations/versions/001_add_user_indexes.py
   
   async def upgrade():
       """Add user indexes"""
       await User.create_index([("email", 1)], unique=True)
   
   async def downgrade():
       """Remove user indexes"""
       await User.drop_index("email_1")
   ```

2. **Register migration**:
   ```python
   # backend/app/core/migrations/__init__.py
   MIGRATIONS = [
       ("001_add_user_indexes", upgrade, downgrade)
   ]
   ```

### Migration Best Practices

1. **Idempotent**: Migrations should be idempotent
2. **Reversible**: Always provide downgrade function
3. **Tested**: Test migrations on staging first
4. **Backup**: Backup database before migrations
5. **Atomic**: Use transactions when possible

## Connection Management

### Database Connection

**Location**: `backend/app/core/database.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

async def init_database():
    """Initialize database connection"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User,
            Conversation,
            Attraction,
            # ... other models
        ]
    )
```

### Connection Pooling

MongoDB connection pooling is handled by Motor:

```python
# Connection string with pool settings
MONGODB_URL = "mongodb://localhost:27017/?maxPoolSize=50&minPoolSize=10"
```

**Pool Settings**:
- `maxPoolSize`: Maximum connections (default: 100)
- `minPoolSize`: Minimum connections (default: 0)
- `maxIdleTimeMS`: Max idle time (default: None)

### Redis Connection

**Location**: `backend/app/core/cache.py`

```python
import redis.asyncio as redis

async def init_redis():
    """Initialize Redis connection"""
    redis_client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    return redis_client
```

## Query Patterns

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
attractions = await Attraction.find_all()\
    .skip((page - 1) * limit)\
    .limit(limit)\
    .to_list()

# Sorting
attractions = await Attraction.find_all()\
    .sort(-Attraction.rating)\
    .to_list()

# Projection (select fields)
users = await User.find_all()\
    .project(UserResponse)\
    .to_list()

# Aggregation
pipeline = [
    {"$match": {"category": "beach"}},
    {"$group": {"_id": "$city", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
results = await Attraction.aggregate(pipeline).to_list()
```

### Geospatial Queries

```python
# Find nearby attractions
attractions = await Attraction.find(
    {
        "location.coordinates": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [79.8612, 6.9271]  # [lng, lat]
                },
                "$maxDistance": 10000  # 10km
            }
        }
    }
).to_list()
```

### Text Search

```python
# Full-text search
attractions = await Attraction.find(
    {"$text": {"$search": "beach temple"}}
).to_list()
```

## Transactions

### Using Transactions

```python
from motor.motor_asyncio import AsyncIOMotorClient

async def transfer_points(from_user_id: str, to_user_id: str, points: int):
    async with await client.start_session() as session:
        async with session.start_transaction():
            from_user = await User.find_one(User.id == from_user_id, session=session)
            to_user = await User.find_one(User.id == to_user_id, session=session)
            
            from_user.points -= points
            to_user.points += points
            
            await from_user.save(session=session)
            await to_user.save(session=session)
```

## Caching Strategy

### Redis Caching

**Cache Keys**:
- `user:{user_id}` - User data (TTL: 1 hour)
- `attraction:{attraction_id}` - Attraction data (TTL: 24 hours)
- `conversation:{conversation_id}` - Conversation cache (TTL: 1 hour)
- `rate_limit:{ip}` - Rate limit counters (TTL: 1 minute)

### Cache Patterns

1. **Cache-Aside**:
   ```python
   # Check cache first
   cached = await redis.get(f"user:{user_id}")
   if cached:
       return json.loads(cached)
   
   # Fetch from database
   user = await User.find_one(User.id == user_id)
   
   # Store in cache
   await redis.setex(
       f"user:{user_id}",
       3600,  # TTL: 1 hour
       json.dumps(user.dict())
   )
   ```

2. **Write-Through**:
   ```python
   # Update database
   await user.save()
   
   # Update cache
   await redis.setex(f"user:{user_id}", 3600, json.dumps(user.dict()))
   ```

3. **Cache Invalidation**:
   ```python
   # Invalidate cache on update
   await user.save()
   await redis.delete(f"user:{user_id}")
   ```

## Backup and Recovery

### Backup Strategy

1. **Automated Backups**: Daily backups
2. **Manual Backups**: Before major changes
3. **Backup Storage**: Cloud storage (S3, etc.)

### Backup Commands

```bash
# MongoDB backup
mongodump --uri="mongodb://localhost:27017" \
  --db=sri_lanka_tourism_bot \
  --out=/backup/$(date +%Y%m%d)

# Redis backup
redis-cli --rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Recovery

```bash
# MongoDB restore
mongorestore --uri="mongodb://localhost:27017" \
  --db=sri_lanka_tourism_bot \
  /backup/20240101/sri_lanka_tourism_bot

# Redis restore
redis-cli --rdb /backup/redis-20240101.rdb
```

## Performance Optimization

### Query Optimization

1. **Use Indexes**: Index frequently queried fields
2. **Limit Results**: Use pagination
3. **Project Fields**: Select only needed fields
4. **Avoid N+1 Queries**: Use aggregation pipelines

### Connection Optimization

1. **Connection Pooling**: Reuse connections
2. **Async Operations**: Non-blocking I/O
3. **Batch Operations**: Group operations when possible

### Index Optimization

1. **Analyze Queries**: Use `explain()` to analyze queries
2. **Compound Indexes**: Create indexes for common query patterns
3. **Index Maintenance**: Monitor index usage and remove unused indexes

## Monitoring

### Database Metrics

Monitor the following metrics:

1. **Connection Pool**: Active connections, pool size
2. **Query Performance**: Slow queries, query execution time
3. **Index Usage**: Index hit ratio
4. **Storage**: Database size, collection sizes
5. **Replication Lag**: If using replica set

### Monitoring Tools

- **MongoDB Atlas**: Cloud monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **MongoDB Compass**: GUI for database management

## Security

### Database Security

1. **Authentication**: Enable MongoDB authentication
2. **Authorization**: Use role-based access control
3. **Encryption**: Encrypt data at rest and in transit
4. **Network**: Restrict network access
5. **Audit Logging**: Log database operations

### Connection Security

```python
# Secure connection string
MONGODB_URL = "mongodb://username:password@host:27017/db?authSource=admin&ssl=true"
```

## Best Practices

1. **Use Indexes**: Index all frequently queried fields
2. **Pagination**: Always paginate large result sets
3. **Validation**: Validate data at application level
4. **Transactions**: Use transactions for multi-document operations
5. **Backup**: Regular automated backups
6. **Monitoring**: Monitor database performance
7. **Connection Pooling**: Configure appropriate pool sizes
8. **Error Handling**: Handle database errors gracefully

## Troubleshooting

### Common Issues

1. **Connection Timeout**:
   - Check network connectivity
   - Verify connection string
   - Check firewall rules

2. **Slow Queries**:
   - Check indexes
   - Analyze query execution
   - Optimize queries

3. **Connection Pool Exhausted**:
   - Increase pool size
   - Check for connection leaks
   - Optimize connection usage

4. **Index Not Used**:
   - Verify index exists
   - Check query pattern
   - Use `explain()` to analyze

## Future Enhancements

1. **Replica Set**: High availability
2. **Sharding**: Horizontal scaling
3. **Change Streams**: Real-time data synchronization
4. **Time Series Collections**: For analytics
5. **GraphQL DataLoader**: Optimize N+1 queries

