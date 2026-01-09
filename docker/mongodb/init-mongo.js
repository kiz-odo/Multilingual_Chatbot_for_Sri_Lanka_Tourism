// MongoDB initialization script for Sri Lanka Tourism Chatbot

// Switch to the tourism database
db = db.getSiblingDB('sri_lanka_tourism_bot');

// Create collections with indexes
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "created_at": -1 });

db.createCollection('conversations');
db.conversations.createIndex({ "user_id": 1 });
db.conversations.createIndex({ "session_id": 1 });
db.conversations.createIndex({ "created_at": -1 });

db.createCollection('attractions');
db.attractions.createIndex({ "name.en": 1 });
db.attractions.createIndex({ "category": 1 });
db.attractions.createIndex({ "location.city": 1 });
db.attractions.createIndex({ "location.coordinates": "2dsphere" });
db.attractions.createIndex({ "slug": 1 }, { unique: true });
db.attractions.createIndex({ "is_featured": 1 });
db.attractions.createIndex({ "popularity_score": -1 });

db.createCollection('restaurants');
db.restaurants.createIndex({ "name.en": 1 });
db.restaurants.createIndex({ "cuisine_types": 1 });
db.restaurants.createIndex({ "location.city": 1 });
db.restaurants.createIndex({ "location.coordinates": "2dsphere" });
db.restaurants.createIndex({ "slug": 1 }, { unique: true });

db.createCollection('hotels');
db.hotels.createIndex({ "name.en": 1 });
db.hotels.createIndex({ "category": 1 });
db.hotels.createIndex({ "location.city": 1 });
db.hotels.createIndex({ "location.coordinates": "2dsphere" });
db.hotels.createIndex({ "slug": 1 }, { unique: true });

db.createCollection('transport');
db.transport.createIndex({ "name.en": 1 });
db.transport.createIndex({ "transport_type": 1 });
db.transport.createIndex({ "slug": 1 }, { unique: true });

db.createCollection('emergency_services');
db.emergency_services.createIndex({ "service_type": 1 });
db.emergency_services.createIndex({ "location.city": 1 });
db.emergency_services.createIndex({ "location.coordinates": "2dsphere" });
db.emergency_services.createIndex({ "emergency_number": 1 });

db.createCollection('events');
db.events.createIndex({ "title.en": 1 });
db.events.createIndex({ "category": 1 });
db.events.createIndex({ "schedule.start_date": 1 });
db.events.createIndex({ "location.city": 1 });
db.events.createIndex({ "slug": 1 }, { unique: true });

db.createCollection('feedback');
db.feedback.createIndex({ "user_id": 1 });
db.feedback.createIndex({ "feedback_type": 1 });
db.feedback.createIndex({ "status": 1 });
db.feedback.createIndex({ "created_at": -1 });

print('MongoDB initialization completed successfully!');
