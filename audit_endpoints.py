"""
Comprehensive Backend Endpoint Audit
"""
import subprocess
import json
import sys

def check_endpoint_files():
    """Check if all router files exist and count endpoints"""
    
    endpoint_files = [
        "auth.py",
        "users.py", 
        "chat.py",
        "attractions.py",
        "restaurants.py",
        "hotels.py",
        "transport.py",
        "emergency.py",
        "events.py",
        "feedback.py",
        "admin.py",
        "maps.py",
        "weather.py",
        "currency.py",
        "email_verification.py",
        "itinerary.py",
        "safety.py",
        "oauth.py",
        "challenges.py",
        "forum.py",
        "recommendations.py",
        "landmarks.py",
        "health.py",
        "websocket.py"
    ]
    
    print("=" * 80)
    print("BACKEND ENDPOINT AUDIT")
    print("=" * 80)
    print()
    
    total_endpoints = 0
    missing_files = []
    
    for file in endpoint_files:
        file_path = f"backend/app/api/v1/{file}"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count @router decorators
                get_count = content.count('@router.get(')
                post_count = content.count('@router.post(')
                put_count = content.count('@router.put(')
                delete_count = content.count('@router.delete(')
                patch_count = content.count('@router.patch(')
                websocket_count = content.count('@router.websocket(')
                
                endpoint_count = get_count + post_count + put_count + delete_count + patch_count + websocket_count
                
                if endpoint_count > 0:
                    print(f"✅ {file:<30} {endpoint_count:>3} endpoints")
                    print(f"   └─ GET: {get_count}, POST: {post_count}, PUT: {put_count}, DELETE: {delete_count}, PATCH: {patch_count}, WS: {websocket_count}")
                else:
                    print(f"⚠️  {file:<30} {endpoint_count:>3} endpoints (EMPTY)")
                
                total_endpoints += endpoint_count
                
        except FileNotFoundError:
            print(f"❌ {file:<30} MISSING FILE")
            missing_files.append(file)
    
    print()
    print("=" * 80)
    print(f"TOTAL ENDPOINTS: {total_endpoints}")
    print(f"TOTAL FILES: {len(endpoint_files)}")
    print(f"MISSING FILES: {len(missing_files)}")
    
    if missing_files:
        print()
        print("Missing files:")
        for f in missing_files:
            print(f"  - {f}")
    
    print("=" * 80)
    print()
    
    # Check GraphQL
    print("📊 ADDITIONAL SERVICES:")
    print()
    
    try:
        with open("backend/app/graphql/__init__.py", 'r', encoding='utf-8') as f:
            print("✅ GraphQL API - Available")
    except:
        print("❌ GraphQL API - Missing")
    
    try:
        with open("backend/app/api/v1/websocket.py", 'r', encoding='utf-8') as f:
            content = f.read()
            ws_count = content.count('@router.websocket(')
            print(f"✅ WebSocket API - {ws_count} endpoint(s)")
    except:
        print("❌ WebSocket API - Missing")
    
    print()
    print("=" * 80)
    
    # Key features check
    print()
    print("🔑 KEY FEATURES:")
    print()
    
    features = {
        "Authentication (JWT)": "backend/app/api/v1/auth.py",
        "User Management": "backend/app/api/v1/users.py",
        "Chat & AI": "backend/app/api/v1/chat.py",
        "Attractions Database": "backend/app/api/v1/attractions.py",
        "Hotels & Accommodation": "backend/app/api/v1/hotels.py",
        "Restaurants": "backend/app/api/v1/restaurants.py",
        "Transport Info": "backend/app/api/v1/transport.py",
        "Emergency Services": "backend/app/api/v1/emergency.py",
        "Events Calendar": "backend/app/api/v1/events.py",
        "Feedback System": "backend/app/api/v1/feedback.py",
        "Admin Panel": "backend/app/api/v1/admin.py",
        "Maps & Geolocation": "backend/app/api/v1/maps.py",
        "Weather Info": "backend/app/api/v1/weather.py",
        "Currency Exchange": "backend/app/api/v1/currency.py",
        "Email Verification": "backend/app/api/v1/email_verification.py",
        "Trip Itinerary": "backend/app/api/v1/itinerary.py",
        "Safety Tips": "backend/app/api/v1/safety.py",
        "OAuth Social Login": "backend/app/api/v1/oauth.py",
        "Gamification": "backend/app/api/v1/challenges.py",
        "Community Forum": "backend/app/api/v1/forum.py",
        "AI Recommendations": "backend/app/api/v1/recommendations.py",
        "Landmarks Info": "backend/app/api/v1/landmarks.py"
    }
    
    for feature, file_path in features.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                endpoint_count = (
                    content.count('@router.get(') + 
                    content.count('@router.post(') + 
                    content.count('@router.put(') + 
                    content.count('@router.delete(') +
                    content.count('@router.patch(')
                )
                if endpoint_count > 0:
                    print(f"✅ {feature:<30} ({endpoint_count} endpoints)")
                else:
                    print(f"⚠️  {feature:<30} (0 endpoints)")
        except:
            print(f"❌ {feature:<30} (Missing)")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    check_endpoint_files()
