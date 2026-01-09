"""
Generate Sample Tourism Data for Sri Lanka
==========================================

This script generates realistic sample data for:
- Emergency Services
- Hotels
- Restaurants
- Events
- Transport

Data is saved to JSON files for import into MongoDB.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
import random


def generate_emergency_services() -> List[Dict]:
    """Generate emergency services data"""
    
    services = [
        # Police Services
        {
            "service_type": "police",
            "name": {
                "en": "Tourist Police - Colombo",
                "si": "සංචාරක පොලිසිය - කොළඹ",
                "ta": "சுற்றுலா காவல்துறை - கொழும்பு"
            },
            "description": {
                "en": "24/7 police assistance for tourists in Colombo",
                "si": "කොළඹ සංචාරකයින් සඳහා පැය 24 පොලිස් සහාය",
                "ta": "கொழும்பில் சுற்றுலாப் பயணிகளுக்கான 24/7 காவல்துறை உதவி"
            },
            "phone": "+94 11 242 1451",
            "emergency_number": "119",
            "location": {
                "city": "Colombo",
                "address": "Galle Face, Colombo 03",
                "coordinates": {"latitude": 6.9271, "longitude": 79.8612}
            },
            "operating_hours": "24/7",
            "is_active": True,
            "priority": "high"
        },
        {
            "service_type": "police",
            "name": {
                "en": "Tourist Police - Kandy",
                "si": "සංචාරක පොලිසිය - මහනුවර",
                "ta": "சுற்றுலா காவல்துறை - கண்டி"
            },
            "description": {
                "en": "Tourist assistance police unit in Kandy",
                "si": "මහනුවර සංචාරක සහාය පොලිස් ඒකකය",
                "ta": "கண்டியில் சுற்றுலாப் பயணிகள் உதவி காவல்துறை பிரிவு"
            },
            "phone": "+94 81 222 2222",
            "emergency_number": "119",
            "location": {
                "city": "Kandy",
                "address": "Temple Street, Kandy",
                "coordinates": {"latitude": 7.2906, "longitude": 80.6337}
            },
            "operating_hours": "24/7",
            "is_active": True,
            "priority": "high"
        },
        
        # Hospitals
        {
            "service_type": "medical",
            "name": {
                "en": "National Hospital of Sri Lanka",
                "si": "ශ්‍රී ලංකා ජාතික රෝහල",
                "ta": "இலங்கை தேசிய வைத்தியசாலை"
            },
            "description": {
                "en": "Main government hospital in Colombo with emergency services",
                "si": "හදිසි සේවා සහිත කොළඹ ප්‍රධාන රජයේ රෝහල",
                "ta": "அவசர சேவைகளுடன் கூடிய கொழும்பு பிரதான அரசு வைத்தியசாலை"
            },
            "phone": "+94 11 269 1111",
            "emergency_number": "110",
            "location": {
                "city": "Colombo",
                "address": "Regent Street, Colombo 07",
                "coordinates": {"latitude": 6.9167, "longitude": 79.8611}
            },
            "operating_hours": "24/7",
            "is_active": True,
            "priority": "critical",
            "facilities": ["Emergency", "ICU", "Surgery", "Pharmacy"]
        },
        {
            "service_type": "medical",
            "name": {
                "en": "Asiri Central Hospital",
                "si": "අසිරි සෙන්ට්‍රල් රෝහල",
                "ta": "அசிரி மத்திய வைத்தியசாலை"
            },
            "description": {
                "en": "Private hospital with international standards",
                "si": "ජාත්‍යන්තර ප්‍රමිතීන් සහිත පුද්ගලික රෝහල",
                "ta": "சர்வதேச தரங்களுடன் கூடிய தனியார் வைத்தியசாலை"
            },
            "phone": "+94 11 466 5500",
            "emergency_number": "110",
            "location": {
                "city": "Colombo",
                "address": "114 Norris Canal Road, Colombo 10",
                "coordinates": {"latitude": 6.9147, "longitude": 79.8837}
            },
            "operating_hours": "24/7",
            "is_active": True,
            "priority": "high",
            "facilities": ["Emergency", "ICU", "Surgery", "Pharmacy", "Lab"]
        },
        {
            "service_type": "medical",
            "name": {
                "en": "Teaching Hospital Kandy",
                "si": "ශික්ෂණ රෝහල මහනුවර",
                "ta": "கற்பித்தல் வைத்தியசாலை கண்டி"
            },
            "description": {
                "en": "Major hospital in Kandy with emergency care",
                "si": "හදිසි සත්කාර සහිත මහනුවර ප්‍රධාන රෝහල",
                "ta": "அவசர பராமரிப்புடன் கூடிய கண்டியின் பிரதான வைத்தியசாலை"
            },
            "phone": "+94 81 223 3337",
            "emergency_number": "110",
            "location": {
                "city": "Kandy",
                "address": "William Gopallawa Mawatha, Kandy",
                "coordinates": {"latitude": 7.2843, "longitude": 80.6247}
            },
            "operating_hours": "24/7",
            "is_active": True,
            "priority": "critical"
        },
        
        # Fire Services
        {
            "service_type": "fire",
            "name": {
                "en": "Fire & Rescue Services - Colombo",
                "si": "ගිනි නිවීමේ හා ගලවා ගැනීමේ සේවා - කොළඹ",
                "ta": "தீ மற்றும் மீட்பு சேவைகள் - கொழும்பு"
            },
            "description": {
                "en": "Main fire station in Colombo",
                "si": "කොළඹ ප්‍රධාන ගිනි නිවීමේ ස්ථානය",
                "ta": "கொழும்பு பிரதான தீயணைப்பு நிலையம்"
            },
            "phone": "+94 11 242 2222",
            "emergency_number": "110",
            "location": {
                "city": "Colombo",
                "address": "Maradana, Colombo 10",
                "coordinates": {"latitude": 6.9291, "longitude": 79.8686}
            },
            "operating_hours": "24/7",
            "is_active": True,
            "priority": "critical"
        },
        
        # Embassies
        {
            "service_type": "embassy",
            "name": {
                "en": "Embassy of the United States",
                "si": "එක්සත් ජනපද තානාපති කාර්යාලය",
                "ta": "அமெரிக்க தூதரகம்"
            },
            "description": {
                "en": "US Embassy providing consular services",
                "si": "කොන්සියුලර් සේවා සපයන එක්සත් ජනපද තානාපති කාර්යාලය",
                "ta": "தூதரக சேவைகளை வழங்கும் அமெரிக்க தூதரகம்"
            },
            "phone": "+94 11 249 8500",
            "emergency_number": "+94 11 249 8500",
            "location": {
                "city": "Colombo",
                "address": "210 Galle Road, Colombo 03",
                "coordinates": {"latitude": 6.8986, "longitude": 79.8535}
            },
            "operating_hours": "Mon-Fri 8:00-17:00",
            "is_active": True,
            "priority": "medium"
        },
        {
            "service_type": "embassy",
            "name": {
                "en": "British High Commission",
                "si": "බ්‍රිතාන්‍ය මහ කොමසාරිස් කාර්යාලය",
                "ta": "பிரித்தானிய உயர் ஆணையாளர் அலுவலகம்"
            },
            "description": {
                "en": "UK High Commission in Colombo",
                "si": "කොළඹ එක්සත් රාජධානිය මහ කොමසාරිස් කාර්යාලය",
                "ta": "கொழும்பில் உள்ள இங்கிலாந்து உயர் ஆணையாளர் அலுவலகம்"
            },
            "phone": "+94 11 539 0639",
            "emergency_number": "+94 11 539 0639",
            "location": {
                "city": "Colombo",
                "address": "389 Bauddhaloka Mawatha, Colombo 07",
                "coordinates": {"latitude": 6.9061, "longitude": 79.8655}
            },
            "operating_hours": "Mon-Thu 8:00-16:00, Fri 8:00-13:00",
            "is_active": True,
            "priority": "medium"
        },
        {
            "service_type": "embassy",
            "name": {
                "en": "High Commission of India",
                "si": "ඉන්දියානු මහ කොමසාරිස් කාර්යාලය",
                "ta": "இந்திய உயர் ஆணையாளர் அலுவலகம்"
            },
            "description": {
                "en": "Indian High Commission in Colombo",
                "si": "කොළඹ ඉන්දියානු මහ කොමසාරිස් කාර්යාලය",
                "ta": "கொழும்பில் உள்ள இந்திய உயர் ஆணையாளர் அலுவலகம்"
            },
            "phone": "+94 11 242 1605",
            "emergency_number": "+94 11 242 1605",
            "location": {
                "city": "Colombo",
                "address": "36-38 Galle Road, Colombo 03",
                "coordinates": {"latitude": 6.9013, "longitude": 79.8518}
            },
            "operating_hours": "Mon-Fri 9:00-17:30",
            "is_active": True,
            "priority": "medium"
        }
    ]
    
    return services


def generate_hotels() -> List[Dict]:
    """Generate hotels data"""
    
    hotels = [
        {
            "name": {
                "en": "Galle Face Hotel",
                "si": "ගාලු මුහුණ හෝටලය",
                "ta": "காலி முகம் ஹோட்டல்"
            },
            "description": {
                "en": "Historic luxury hotel by the sea, established in 1864",
                "si": "1864 දී ආරම්භ කරන ලද මුහුද අසල ඓතිහාසික සුඛෝපභෝගී හෝටලය",
                "ta": "1864 இல் நிறுவப்பட்ட கடலோர வரலாற்று சிறப்புமிக்க ஹோட்டல்"
            },
            "category": "luxury",
            "star_rating": "five_star",
            "location": {
                "city": "Colombo",
                "address": "2 Kollupitiya Road, Colombo 03",
                "coordinates": {"latitude": 6.9236, "longitude": 79.8445}
            },
            "contact": {
                "phone": "+94 11 254 1010",
                "email": "reservations@gallefacehotel.com",
                "website": "https://www.gallefacehotel.com"
            },
            "price_range": {"min": 25000, "max": 75000, "currency": "LKR"},
            "amenities": ["Pool", "Spa", "Restaurant", "Bar", "Gym", "WiFi", "Parking"],
            "room_count": 90,
            "check_in": "14:00",
            "check_out": "12:00",
            "is_active": True,
            "popularity_score": 95,
            "rating": 4.5
        },
        {
            "name": {
                "en": "Cinnamon Grand Colombo",
                "si": "සිනමන් ග්‍රෑන්ඩ් කොළඹ",
                "ta": "சின்னமன் கிராண்ட் கொழும்பு"
            },
            "description": {
                "en": "Five-star hotel in the heart of Colombo",
                "si": "කොළඹ හදවතේ පස් තරු හෝටලය",
                "ta": "கொழும்பின் மையத்தில் ஐந்து நட்சத்திர ஹோட்டல்"
            },
            "category": "luxury",
            "star_rating": "five_star",
            "location": {
                "city": "Colombo",
                "address": "77 Galle Road, Colombo 03",
                "coordinates": {"latitude": 6.9193, "longitude": 79.8467}
            },
            "contact": {
                "phone": "+94 11 243 7437",
                "email": "cinnamongrande@cinnamonhotels.com",
                "website": "https://www.cinnamonhotels.com"
            },
            "price_range": {"min": 20000, "max": 60000, "currency": "LKR"},
            "amenities": ["Pool", "Spa", "Multiple Restaurants", "Bar", "Gym", "WiFi", "Business Center"],
            "room_count": 501,
            "check_in": "14:00",
            "check_out": "12:00",
            "is_active": True,
            "popularity_score": 92,
            "rating": 4.4
        },
        {
            "name": {
                "en": "Shangri-La Hotel Colombo",
                "si": "ශැන්ග්‍රි-ලා හෝටලය කොළඹ",
                "ta": "ஷாங்க்ரி-லா ஹோட்டல் கொழும்பு"
            },
            "description": {
                "en": "Modern luxury hotel with panoramic city and ocean views",
                "si": "දර්ශනීය නගර සහ සාගර දසුන් සහිත නවීන සුඛෝපභෝගී හෝටලය",
                "ta": "நகர மற்றும் கடல் காட்சிகளுடன் கூடிய நவீன சொகுசு ஹோட்டல்"
            },
            "category": "luxury",
            "star_rating": "five_star",
            "location": {
                "city": "Colombo",
                "address": "1 Galle Face, Colombo 02",
                "coordinates": {"latitude": 6.9246, "longitude": 79.8434}
            },
            "contact": {
                "phone": "+94 11 788 8288",
                "email": "slcb@shangri-la.com",
                "website": "https://www.shangri-la.com/colombo"
            },
            "price_range": {"min": 30000, "max": 100000, "currency": "LKR"},
            "amenities": ["Pool", "Spa", "Multiple Restaurants", "Bar", "Gym", "WiFi", "Conference Halls"],
            "room_count": 500,
            "check_in": "15:00",
            "check_out": "12:00",
            "is_active": True,
            "popularity_score": 98,
            "rating": 4.7
        },
        {
            "name": {
                "en": "Jetwing Lighthouse",
                "si": "ජෙට්වින්ග් ප්‍රදීපාගාරය",
                "ta": "ஜெட்விங் கலங்கரை விளக்கம்"
            },
            "description": {
                "en": "Iconic clifftop hotel designed by Geoffrey Bawa in Galle",
                "si": "ගාල්ලේ ජෙෆ්රි බාවා විසින් නිර්මාණය කරන ලද කඳු මුදුනේ සංකේතාත්මක හෝටලය",
                "ta": "காலியில் ஜெஃப்ரி பாவாவால் வடிவமைக்கப்பட்ட பாறை மீதுள்ள ஹோட்டல்"
            },
            "category": "boutique",
            "star_rating": "five_star",
            "location": {
                "city": "Galle",
                "address": "Dadalla, Galle",
                "coordinates": {"latitude": 6.0367, "longitude": 80.2170}
            },
            "contact": {
                "phone": "+94 91 223 3744",
                "email": "lighthouse@jetwinghotels.com",
                "website": "https://www.jetwinghotels.com/jetwinglighthouse"
            },
            "price_range": {"min": 18000, "max": 45000, "currency": "LKR"},
            "amenities": ["Pool", "Spa", "Restaurant", "Bar", "WiFi", "Beach Access"],
            "room_count": 63,
            "check_in": "14:00",
            "check_out": "12:00",
            "is_active": True,
            "popularity_score": 90,
            "rating": 4.6
        },
        {
            "name": {
                "en": "The Kingsbury Colombo",
                "si": "කිංස්බරි කොළඹ",
                "ta": "கிங்ஸ்பரி கொழும்பு"
            },
            "description": {
                "en": "Five-star hotel with stunning ocean views",
                "si": "විශිෂ්ට සාගර දසුන් සහිත පස් තරු හෝටලය",
                "ta": "அழகான கடல் காட்சிகளுடன் கூடிய ஐந்து நட்சத்திர ஹோட்டல்"
            },
            "category": "luxury",
            "star_rating": "five_star",
            "location": {
                "city": "Colombo",
                "address": "48 Janadhipathi Mawatha, Colombo 01",
                "coordinates": {"latitude": 6.9349, "longitude": 79.8444}
            },
            "contact": {
                "phone": "+94 11 242 1221",
                "email": "info@thekingsburyhotel.com",
                "website": "https://www.thekingsburyhotel.com"
            },
            "price_range": {"min": 22000, "max": 65000, "currency": "LKR"},
            "amenities": ["Pool", "Spa", "Restaurants", "Bar", "Gym", "WiFi"],
            "room_count": 229,
            "check_in": "14:00",
            "check_out": "12:00",
            "is_active": True,
            "popularity_score": 88,
            "rating": 4.3
        }
    ]
    
    # Add more budget/mid-range hotels
    budget_hotels = [
        {
            "name": {"en": "Colombo City Hotel", "si": "කොළඹ නගර හෝටලය", "ta": "கொழும்பு நகர ஹோட்டல்"},
            "description": {"en": "Comfortable budget hotel in central Colombo", "si": "මධ්‍යම කොළඹ සුවපහසු අයවැය හෝටලය", "ta": "மத்திய கொழும்புவில் வசதியான பட்ஜெட் ஹோட்டல்"},
            "category": "budget",
            "star_rating": "three_star",
            "location": {"city": "Colombo", "address": "Main Street, Colombo 11", "coordinates": {"latitude": 6.9497, "longitude": 79.8611}},
            "contact": {"phone": "+94 11 232 1234", "email": "info@colombocityhotel.com", "website": "https://www.colombocityhotel.com"},
            "price_range": {"min": 5000, "max": 12000, "currency": "LKR"},
            "amenities": ["WiFi", "Restaurant", "Parking"],
            "room_count": 45,
            "check_in": "14:00",
            "check_out": "11:00",
            "is_active": True,
            "popularity_score": 70,
            "rating": 3.8
        }
    ]
    
    return hotels + budget_hotels


def generate_restaurants() -> List[Dict]:
    """Generate restaurants data"""
    
    restaurants = [
        {
            "name": {
                "en": "Ministry of Crab",
                "si": "කැකුළු අමාත්‍යාංශය",
                "ta": "நண்டு அமைச்சகம்"
            },
            "description": {
                "en": "World-renowned seafood restaurant specializing in Sri Lankan crab",
                "si": "ශ්‍රී ලාංකික කකුළුවන් විශේෂීකරණය කරන ලෝක ප්‍රසිද්ධ මුහුදු ආහාර අවන්හල",
                "ta": "இலங்கை நண்டுகளில் நிபுணத்துவம் பெற்ற உலகப் புகழ்பெற்ற கடல் உணவு உணவகம்"
            },
            "cuisine_types": ["seafood", "fine_dining", "sri_lankan"],
            "price_range": "luxury",
            "location": {
                "city": "Colombo",
                "address": "Old Dutch Hospital, Colombo 01",
                "coordinates": {"latitude": 6.9344, "longitude": 79.8428}
            },
            "contact": {
                "phone": "+94 11 243 4722",
                "email": "reservations@ministryofcrab.com",
                "website": "https://www.ministryofcrab.com"
            },
            "operating_hours": {
                "monday": "12:00-15:00, 18:00-23:00",
                "tuesday": "12:00-15:00, 18:00-23:00",
                "wednesday": "12:00-15:00, 18:00-23:00",
                "thursday": "12:00-15:00, 18:00-23:00",
                "friday": "12:00-15:00, 18:00-23:30",
                "saturday": "12:00-15:00, 18:00-23:30",
                "sunday": "12:00-15:00, 18:00-23:00"
            },
            "popular_dishes": ["Pepper Crab", "Garlic Chili Crab", "Baked Crab"],
            "is_active": True,
            "rating": 4.8,
            "popularity_score": 98
        },
        {
            "name": {
                "en": "Curry Leaf",
                "si": "කරපිංචා",
                "ta": "கறிவேப்பிலை"
            },
            "description": {
                "en": "Authentic Sri Lankan cuisine in elegant setting",
                "si": "අලංකාර පරිසරයක සත්‍ය ශ්‍රී ලාංකික ආහාර",
                "ta": "நேர்த்தியான அமைப்பில் உண்மையான இலங்கை உணவு வகைகள்"
            },
            "cuisine_types": ["sri_lankan", "fine_dining"],
            "price_range": "mid_range",
            "location": {
                "city": "Colombo",
                "address": "The Hilton Colombo, Lotus Road, Colombo 01",
                "coordinates": {"latitude": 6.9348, "longitude": 79.8456}
            },
            "contact": {
                "phone": "+94 11 249 2492",
                "email": "info@curryleaf.lk",
                "website": "https://www.hilton.com"
            },
            "operating_hours": {
                "monday": "12:00-14:30, 19:00-22:30",
                "tuesday": "12:00-14:30, 19:00-22:30",
                "wednesday": "12:00-14:30, 19:00-22:30",
                "thursday": "12:00-14:30, 19:00-22:30",
                "friday": "12:00-14:30, 19:00-22:30",
                "saturday": "12:00-14:30, 19:00-22:30",
                "sunday": "12:00-14:30, 19:00-22:30"
            },
            "popular_dishes": ["Rice & Curry", "Kottu Roti", "Hoppers", "Lamprais"],
            "is_active": True,
            "rating": 4.5,
            "popularity_score": 92
        },
        {
            "name": {
                "en": "The Gallery Café",
                "si": "ගැලරි කැෆේ",
                "ta": "கேலரி கஃபே"
            },
            "description": {
                "en": "Stylish café in Geoffrey Bawa-designed space",
                "si": "ජෙෆ්රි බාවා නිර්මාණය කළ අවකාශයේ දක්ෂ කැෆේ",
                "ta": "ஜெஃப்ரி பாவா வடிவமைத்த இடத்தில் நாகரீகமான கஃபே"
            },
            "cuisine_types": ["international", "cafe", "fusion"],
            "price_range": "mid_range",
            "location": {
                "city": "Colombo",
                "address": "2 Alfred House Road, Colombo 03",
                "coordinates": {"latitude": 6.9019, "longitude": 79.8563}
            },
            "contact": {
                "phone": "+94 11 258 2162",
                "email": "info@gallerycafe.lk",
                "website": "https://www.gallerycafe.lk"
            },
            "operating_hours": {
                "monday": "10:00-23:00",
                "tuesday": "10:00-23:00",
                "wednesday": "10:00-23:00",
                "thursday": "10:00-23:00",
                "friday": "10:00-23:00",
                "saturday": "10:00-23:00",
                "sunday": "10:00-23:00"
            },
            "popular_dishes": ["Gallery Burger", "Caesar Salad", "Pasta"],
            "is_active": True,
            "rating": 4.4,
            "popularity_score": 85
        },
        {
            "name": {
                "en": "Nuga Gama",
                "si": "නුගගම",
                "ta": "நுககம"
            },
            "description": {
                "en": "Traditional Sri Lankan village experience restaurant",
                "si": "සාම්ප්‍රදායික ශ්‍රී ලාංකික ගම්මාන අත්දැකීම් අවන්හල",
                "ta": "பாரம்பரிய இலங்கை கிராமிய அனுபவ உணவகம்"
            },
            "cuisine_types": ["sri_lankan", "traditional"],
            "price_range": "mid_range",
            "location": {
                "city": "Colombo",
                "address": "Cinnamon Grand, 77 Galle Road, Colombo 03",
                "coordinates": {"latitude": 6.9193, "longitude": 79.8467}
            },
            "contact": {
                "phone": "+94 11 243 7437",
                "email": "nugagama@cinnamonhotels.com",
                "website": "https://www.cinnamonhotels.com"
            },
            "operating_hours": {
                "monday": "19:00-23:00",
                "tuesday": "19:00-23:00",
                "wednesday": "19:00-23:00",
                "thursday": "19:00-23:00",
                "friday": "19:00-23:00",
                "saturday": "12:00-15:00, 19:00-23:00",
                "sunday": "12:00-15:00, 19:00-23:00"
            },
            "popular_dishes": ["Village Rice & Curry", "Wood-fired Roti", "Watalappan"],
            "is_active": True,
            "rating": 4.6,
            "popularity_score": 88
        },
        {
            "name": {
                "en": "Upali's by Nawaloka",
                "si": "උපාලි'ස් නාවලෝක",
                "ta": "உபாலி'ஸ் நாவலோக"
            },
            "description": {
                "en": "Popular Sri Lankan restaurant chain",
                "si": "ජනප්‍රිය ශ්‍රී ලාංකික අවන්හල් දාමය",
                "ta": "பிரபலமான இலங்கை உணவக சங்கிலி"
            },
            "cuisine_types": ["sri_lankan", "chinese"],
            "price_range": "budget",
            "location": {
                "city": "Colombo",
                "address": "33 Nawala Road, Colombo 05",
                "coordinates": {"latitude": 6.8867, "longitude": 79.8863}
            },
            "contact": {
                "phone": "+94 11 258 8234",
                "email": "info@upalis.lk",
                "website": "https://www.upalis.lk"
            },
            "operating_hours": {
                "monday": "11:00-22:30",
                "tuesday": "11:00-22:30",
                "wednesday": "11:00-22:30",
                "thursday": "11:00-22:30",
                "friday": "11:00-22:30",
                "saturday": "11:00-22:30",
                "sunday": "11:00-22:30"
            },
            "popular_dishes": ["Fried Rice", "Deviled Chicken", "Kottu"],
            "is_active": True,
            "rating": 4.2,
            "popularity_score": 82
        }
    ]
    
    return restaurants


def generate_events() -> List[Dict]:
    """Generate events data"""
    
    # Get dates for upcoming year
    today = datetime.now()
    
    events = [
        {
            "title": {
                "en": "Esala Perahera",
                "si": "ඇසළ පෙරහැර",
                "ta": "ஏசல பெரஹெர"
            },
            "description": {
                "en": "Grand cultural pageant in Kandy featuring decorated elephants and traditional dancers",
                "si": "සරසන ලද අලි ඇතුන් සහ සාම්ප්‍රදායික නර්තන ශිල්පීන් සහිත මහනුවර මහා සංස්කෘතික පෙරහැර",
                "ta": "அலங்கரிக்கப்பட்ட யானைகள் மற்றும் பாரம்பரிய நடனக் கலைஞர்களைக் கொண்ட கண்டியின் பெரும் கலாச்சார கண்காட்சி"
            },
            "category": "cultural",
            "schedule": {
                "start_date": datetime(today.year, 7, 20).isoformat(),
                "end_date": datetime(today.year, 8, 1).isoformat(),
                "start_time": "19:00",
                "duration_days": 12
            },
            "location": {
                "city": "Kandy",
                "venue": "Temple of the Sacred Tooth Relic",
                "address": "Sri Dalada Veediya, Kandy",
                "coordinates": {"latitude": 7.2934, "longitude": 80.6410}
            },
            "entry_fee": {"amount": 0, "currency": "LKR", "notes": "Free to watch from streets"},
            "status": "published",
            "is_active": True,
            "popularity_score": 100
        },
        {
            "title": {
                "en": "Vesak Festival",
                "si": "වෙසක් උත්සවය",
                "ta": "வெசாக் திருவிழா"
            },
            "description": {
                "en": "Buddhist festival celebrating the birth, enlightenment and death of Buddha",
                "si": "බුදුන්ගේ උපත, බුද්ධත්වය සහ මරණය සමරන බෞද්ධ උත්සවය",
                "ta": "புத்தரின் பிறப்பு, அறிவொளி மற்றும் மரணத்தைக் கொண்டாடும் புத்த விழா"
            },
            "category": "religious",
            "schedule": {
                "start_date": datetime(today.year, 5, 22).isoformat(),
                "end_date": datetime(today.year, 5, 24).isoformat(),
                "start_time": "00:00",
                "duration_days": 3
            },
            "location": {
                "city": "Colombo",
                "venue": "Nationwide celebration",
                "address": "All over Sri Lanka",
                "coordinates": {"latitude": 6.9271, "longitude": 79.8612}
            },
            "entry_fee": {"amount": 0, "currency": "LKR", "notes": "Free public festival"},
            "status": "published",
            "is_active": True,
            "popularity_score": 95
        },
        {
            "title": {
                "en": "Sinhala & Tamil New Year",
                "si": "සිංහල හා දෙමළ අලුත් අවුරුද්ද",
                "ta": "சிங்கள மற்றும் தமிழ் புத்தாண்டு"
            },
            "description": {
                "en": "Traditional New Year celebration with cultural customs and festivities",
                "si": "සංස්කෘතික චාරිත්‍ර හා උත්සව සමග සාම්ප්‍රදායික අලුත් අවුරුදු සැමරුම",
                "ta": "கலாச்சார பழக்கவழக்கங்கள் மற்றும் விழாக்களுடன் பாரம்பரிய புத்தாண்டு கொண்டாட்டம்"
            },
            "category": "cultural",
            "schedule": {
                "start_date": datetime(today.year, 4, 13).isoformat(),
                "end_date": datetime(today.year, 4, 14).isoformat(),
                "start_time": "00:00",
                "duration_days": 2
            },
            "location": {
                "city": "Colombo",
                "venue": "Nationwide celebration",
                "address": "All over Sri Lanka",
                "coordinates": {"latitude": 7.8731, "longitude": 80.7718}
            },
            "entry_fee": {"amount": 0, "currency": "LKR", "notes": "Public holiday"},
            "status": "published",
            "is_active": True,
            "popularity_score": 98
        },
        {
            "title": {
                "en": "Galle Literary Festival",
                "si": "ගාලු සාහිත්‍ය උළෙල",
                "ta": "காலி இலக்கிய திருவிழா"
            },
            "description": {
                "en": "Annual international literary festival featuring authors and workshops",
                "si": "කතුවරුන් සහ වැඩමුළු සහිත වාර්ෂික ජාත්‍යන්තර සාහිත්‍ය උළෙල",
                "ta": "ஆசிரியர்கள் மற்றும் பட்டறைகளைக் கொண்ட வருடாந்திர சர்வதேச இலக்கிய திருவிழா"
            },
            "category": "cultural",
            "schedule": {
                "start_date": datetime(today.year, 1, 25).isoformat(),
                "end_date": datetime(today.year, 1, 28).isoformat(),
                "start_time": "09:00",
                "duration_days": 4
            },
            "location": {
                "city": "Galle",
                "venue": "Galle Fort",
                "address": "Church Street, Galle Fort",
                "coordinates": {"latitude": 6.0261, "longitude": 80.2168}
            },
            "entry_fee": {"amount": 5000, "currency": "LKR", "notes": "Pass for all days"},
            "status": "published",
            "is_active": True,
            "popularity_score": 75
        },
        {
            "title": {
                "en": "Navam Perahera",
                "si": "නවම් පෙරහැර",
                "ta": "நவம் பெரஹெர"
            },
            "description": {
                "en": "Annual Buddhist procession in Colombo",
                "si": "කොළඹ වාර්ෂික බෞද්ධ පෙරහැර",
                "ta": "கொழும்பில் வருடாந்திர புத்த ஊர்வலம்"
            },
            "category": "religious",
            "schedule": {
                "start_date": datetime(today.year, 2, 15).isoformat(),
                "end_date": datetime(today.year, 2, 16).isoformat(),
                "start_time": "18:00",
                "duration_days": 2
            },
            "location": {
                "city": "Colombo",
                "venue": "Gangaramaya Temple",
                "address": "61 Sri Jinaratana Road, Colombo 02",
                "coordinates": {"latitude": 6.9167, "longitude": 79.8550}
            },
            "entry_fee": {"amount": 0, "currency": "LKR", "notes": "Free to watch"},
            "status": "published",
            "is_active": True,
            "popularity_score": 85
        }
    ]
    
    return events


def main():
    """Main function to generate all data"""
    
    print("🎯 Generating Sample Tourism Data for Sri Lanka")
    print("=" * 60)
    
    # Generate data
    print("\n📊 Generating data...")
    emergency_data = generate_emergency_services()
    hotels_data = generate_hotels()
    restaurants_data = generate_restaurants()
    events_data = generate_events()
    
    # Create combined dataset
    full_dataset = {
        "emergency_services": emergency_data,
        "hotels": hotels_data,
        "restaurants": restaurants_data,
        "events": events_data,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_records": {
                "emergency": len(emergency_data),
                "hotels": len(hotels_data),
                "restaurants": len(restaurants_data),
                "events": len(events_data)
            }
        }
    }
    
    # Save to JSON file
    output_file = "sample_tourism_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_dataset, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Data generated successfully!")
    print(f"📁 Saved to: {output_file}")
    print(f"\n📈 Summary:")
    print(f"   - Emergency Services: {len(emergency_data)}")
    print(f"   - Hotels: {len(hotels_data)}")
    print(f"   - Restaurants: {len(restaurants_data)}")
    print(f"   - Events: {len(events_data)}")
    print(f"   - Total Records: {sum(full_dataset['metadata']['total_records'].values())}")
    print("\n🚀 Ready to import into database!")
    print("\n💡 Next step: Run import script to load into MongoDB")
    

if __name__ == "__main__":
    main()
