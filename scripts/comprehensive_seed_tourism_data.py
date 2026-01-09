"""
Comprehensive seed data for Sri Lanka Tourism Chatbot
Creates realistic tourism data for all major categories
"""

import asyncio
import sys
import os
from datetime import datetime, date, time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.app.core.config import settings
from backend.app.models.attraction import (
    Attraction, AttractionCategory, AccessibilityFeature,
    Location, OpeningHours, PricingTier, MultilingualContent,
    AttractionImage
)
from backend.app.models.hotel import (
    Hotel, HotelCategory, StarRating, Room, RoomType, Amenity
)
from backend.app.models.restaurant import (
    Restaurant, CuisineType, RestaurantType, PriceRange, DietaryOption, MenuItem
)
from backend.app.models.transport import (
    Transport, TransportType, TransportCategory, ServiceLevel,
    Schedule, Route, PricingOption
)
from backend.app.models.event import (
    Event, EventCategory, EventStatus, TicketType,
    EventSchedule, Ticket, Organizer
)


async def clear_collections():
    """Clear existing data"""
    print("Clearing existing data...")
    await Attraction.delete_all()
    await Hotel.delete_all()
    await Restaurant.delete_all()
    await Transport.delete_all()
    await Event.delete_all()
    print("Existing data cleared!")


async def seed_attractions():
    """Seed attraction data"""
    print("Seeding attractions...")
    
    attractions_data = [
        {
            "name": MultilingualContent(
                en="Sigiriya Rock Fortress",
                si="සීගිරිය පර්වත බලකොටුව",
                ta="சிகிரியா பாறை கோட்டை"
            ),
            "description": MultilingualContent(
                en="Ancient rock fortress and UNESCO World Heritage Site with stunning frescoes and gardens. Built by King Kashyapa in the 5th century AD.",
                si="5 වන සියවසේ කාශ්‍යප රජු විසින් ඉදිකරන ලද අභිරහස් ශිලාලේඛන සහ උද්‍යාන සහිත පුරාණ ශිලා බලකොටුව. යුනෙස්කෝ ලෝක උරුම ස්ථානයකි.",
                ta="5 ஆம் நூற்றாண்டில் காஷ்யப மன்னரால் கட்டப்பட்ட பழங்கால பாறை கோட்டை மற்றும் UNESCO உலக பாரம்பரிய தளம்."
            ),
            "short_description": MultilingualContent(
                en="Ancient rock fortress with breathtaking views",
                si="විශ්මයජනක දසුන් සහිත පුරාණ ශිලා බලකොටුව",
                ta="மூச்சடைக்கக்கூடிய காட்சிகளுடன் கூடிய பழங்கால பாறை கோட்டை"
            ),
            "category": AttractionCategory.HISTORICAL,
            "subcategories": ["archaeological", "unesco_heritage"],
            "tags": ["ancient", "fortress", "rock", "history", "unesco", "frescoes"],
            "location": Location(
                address="Sigiriya, Dambulla",
                city="Dambulla",
                province="Central Province",
                coordinates=[80.7597, 7.9570]
            ),
            "opening_hours": [
                OpeningHours(day_of_week=i, open_time="07:00", close_time="17:30")
                for i in range(7)
            ],
            "pricing": [
                PricingTier(category="foreign_adult", price=5670, currency="LKR"),
                PricingTier(category="foreign_child", price=2835, currency="LKR"),
                PricingTier(category="local_adult", price=100, currency="LKR"),
                PricingTier(category="local_child", price=50, currency="LKR"),
            ],
            "is_free": False,
            "requires_booking": False,
            "estimated_visit_duration": "2-3 hours",
            "best_time_to_visit": "Early morning (7-9 AM) to avoid heat",
            "difficulty_level": "moderate",
            "amenities": ["parking", "restrooms", "guides", "souvenir_shop"],
            "accessibility_features": [AccessibilityFeature.ACCESSIBLE_PARKING],
            "parking_available": True,
            "guided_tours_available": True,
            "languages_supported": ["en", "si", "ta", "de", "fr", "zh", "ja"],
            "how_to_get_there": MultilingualContent(
                en="Located 169km from Colombo. Accessible by car (3.5 hours), bus, or train to Habarana then taxi.",
                si="කොළඹ සිට කිලෝමීටර 169ක් දුරින්. මෝටර් රථයෙන් (පැය 3.5), බස් රථයෙන් හෝ හබරණ දක්වා දුම්රියෙන් පසුව කුලී රථයකින් ළඟා විය හැක.",
                ta="கொழும்பிலிருந்து 169 கிமீ தொலைவில். கார் (3.5 மணி), பேருந்து அல்லது ஹபரானா வரை ரயில் பின்னர் டாக்ஸி மூலம் அணுகலாம்."
            ),
            "slug": "sigiriya-rock-fortress",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 98.5,
            "average_rating": 4.8
        },
        {
            "name": MultilingualContent(
                en="Temple of the Sacred Tooth Relic",
                si="ශ්‍රී දළදා මාළිගාව",
                ta="புனித பல்லின் கோவில்"
            ),
            "description": MultilingualContent(
                en="Sacred Buddhist temple in Kandy housing the tooth relic of the Buddha. Major pilgrimage site and UNESCO World Heritage Site.",
                si="බුදුරජාණන් වහන්සේගේ දන්ත ධාතුව වැඩ වසන මහ නුවර පිහිටි ශුද්ධ වූ බෞද්ධ විහාරය. ප්‍රධාන බෞද්ධ වන්දනා ස්ථානය සහ යුනෙස්කෝ ලෝක උරුම ස්ථානයකි.",
                ta="புத்தரின் பல்லின் நினைவுச்சின்னத்தை கொண்டுள்ள கண்டியில் உள்ள புனித பௌத்த கோவில். முக்கிய யாத்திரை தலம் மற்றும் UNESCO உலக பாரம்பரிய தளம்."
            ),
            "short_description": MultilingualContent(
                en="Sacred Buddhist temple housing Buddha's tooth relic",
                si="බුදුරජාණන් වහන්සේගේ දන්ත ධාතුව වැඩ වසන ශුද්ධ විහාරය",
                ta="புத்தரின் பல் நினைவுச்சின்னத்தை கொண்ட புனித கோவில்"
            ),
            "category": AttractionCategory.TEMPLE,
            "subcategories": ["buddhist", "pilgrimage", "unesco_heritage"],
            "tags": ["temple", "buddhist", "sacred", "kandy", "tooth_relic", "unesco"],
            "location": Location(
                address="Sri Dalada Veediya, Kandy",
                city="Kandy",
                province="Central Province",
                coordinates=[80.6400, 7.2936]
            ),
            "opening_hours": [
                OpeningHours(day_of_week=i, open_time="05:30", close_time="20:00")
                for i in range(7)
            ],
            "pricing": [
                PricingTier(category="foreign_adult", price=2000, currency="LKR"),
                PricingTier(category="local", price=0, currency="LKR", description="Free for locals"),
            ],
            "is_free": False,
            "estimated_visit_duration": "1-2 hours",
            "amenities": ["parking", "restrooms", "museum", "gift_shop"],
            "parking_available": True,
            "guided_tours_available": True,
            "how_to_get_there": MultilingualContent(
                en="Located in Kandy city center, 115km from Colombo. Accessible by car (3 hours), bus, or train.",
                si="මහ නුවර නගර මධ්‍යයේ පිහිටා ඇත, කොළඹ සිට කිලෝමීටර 115ක්. මෝටර් රථයෙන් (පැය 3), බස් රථයෙන් හෝ දුම්රියෙන් ළඟා විය හැක.",
                ta="கண்டி நகர மையத்தில் அமைந்துள்ளது, கொழும்பிலிருந்து 115 கிமீ. கார் (3 மணி), பேருந்து அல்லது ரயில் மூலம் அணுகலாம்."
            ),
            "slug": "temple-tooth-relic-kandy",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 95.0,
            "average_rating": 4.7
        },
        {
            "name": MultilingualContent(
                en="Yala National Park",
                si="යාල ජාතික වනෝද්‍යානය",
                ta="யால தேசிய பூங்கா"
            ),
            "description": MultilingualContent(
                en="Sri Lanka's most visited national park, famous for its high leopard density and diverse wildlife including elephants, sloth bears, and numerous bird species.",
                si="ශ්‍රී ලංකාවේ වඩාත් ජනප්‍රිය ජාතික වනෝද්‍යානය, එහි ඉහළ දිවියන් ගහණය සහ අලි, වලසුන් සහ විවිධ කුරුලු විශේෂ ඇතුළු විවිධ වන ජීවීන් සඳහා ප්‍රසිද්ධය.",
                ta="இலங்கையின் மிகவும் பார்வையிடப்பட்ட தேசிய பூங்கா, உயர் சிறுத்தை அடர்த்தி மற்றும் யானைகள், கரடிகள் மற்றும் பல பறவை இனங்கள் உட்பட பல்வேறு வன்முறை விலங்குகளுக்கு புகழ்பெற்றது."
            ),
            "short_description": MultilingualContent(
                en="Premier wildlife sanctuary with highest leopard density",
                si="ඉහළම දිවියන් ගහණය සහිත ප්‍රමුඛ වන ජීවී සංරක්ෂණාගාරය",
                ta="மிக உயர்ந்த சிறுத்தை அடர்த்தியுடன் கூடிய முதன்மை வனவிலங்கு சரணாலயம்"
            ),
            "category": AttractionCategory.WILDLIFE,
            "subcategories": ["safari", "nature", "photography"],
            "tags": ["wildlife", "safari", "leopards", "elephants", "national_park"],
            "location": Location(
                address="Yala, Tissamaharama",
                city="Tissamaharama",
                province="Southern Province",
                coordinates=[81.5084, 6.3725]
            ),
            "opening_hours": [
                OpeningHours(day_of_week=i, open_time="06:00", close_time="18:00")
                for i in range(7)
            ],
            "pricing": [
                PricingTier(category="foreign_adult", price=4000, currency="LKR", description="Per person"),
                PricingTier(category="vehicle", price=2500, currency="LKR", description="Per vehicle"),
                PricingTier(category="tracker_fee", price=2500, currency="LKR"),
            ],
            "is_free": False,
            "requires_booking": True,
            "estimated_visit_duration": "3-4 hours",
            "best_time_to_visit": "February to July (dry season)",
            "how_to_get_there": MultilingualContent(
                en="Located 290km from Colombo near Tissamaharama. Accessible by car (5-6 hours) or bus to Tissamaharama.",
                si="තිස්සමහාරාමය අසලින් කොළඹ සිට කිලෝමීටර 290ක් දුරින්. මෝටර් රථයෙන් (පැය 5-6) හෝ තිස්සමහාරාමය දක්වා බස් රථයෙන් ළඟා විය හැක.",
                ta="கொழும்பிலிருந்து 290 கிமீ தொலைவில் திஸ்ஸமஹாராம அருகே. கார் (5-6 மணி) அல்லது திஸ்ஸமஹாராம வரை பேருந்து மூலம் அணுகலாம்."
            ),
            "slug": "yala-national-park",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 93.0,
            "average_rating": 4.6
        },
        {
            "name": MultilingualContent(
                en="Mirissa Beach",
                si="මිරිස්ස වෙරළ",
                ta="மிரிஸ்ஸா கடற்கரை"
            ),
            "description": MultilingualContent(
                en="Beautiful crescent beach on the southern coast, famous for whale watching, surfing, and stunning sunsets.",
                si="දකුණු වෙරළ තීරයේ පිහිටි අලංකාර අර්ධ සඳ හැඩැති වෙරළ, තල්මැස්සන් නැරඹීම, සර්ෆින් සහ අපූරු හිරු බැස යෑම සඳහා ප්‍රසිද්ධය.",
                ta="தென் கடற்கரையில் அழகான பிறை வடிவ கடற்கரை, திமிங்கலங்களை பார்ப்பதற்கும், சர்ஃபிங் மற்றும் அற்புதமான சூரிய அஸ்தமனங்களுக்கும் புகழ்பெற்றது."
            ),
            "short_description": MultilingualContent(
                en="Pristine beach perfect for whale watching and surfing",
                si="තල්මැස්සන් නැරඹීම සහ සර්ෆින් සඳහා හිත සුන්දර වෙරළ",
                ta="திமிங்கலங்களை பார்ப்பதற்கும் சர்ஃபிங்குக்கும் சரியான சுத்தமான கடற்கரை"
            ),
            "category": AttractionCategory.BEACH,
            "subcategories": ["water_sports", "whale_watching", "relaxation"],
            "tags": ["beach", "whale_watching", "surfing", "sunset", "swimming"],
            "location": Location(
                address="Mirissa, Matara",
                city="Matara",
                province="Southern Province",
                coordinates=[80.4697, 5.9470]
            ),
            "is_free": True,
            "estimated_visit_duration": "Half day to full day",
            "amenities": ["restaurants", "restrooms", "water_sports", "boat_tours"],
            "how_to_get_there": MultilingualContent(
                en="Located 150km from Colombo on the southern coast. Accessible by car (2.5-3 hours) via Southern Expressway or by train to Weligama then taxi.",
                si="දකුණු වෙරළ තීරයේ කොළඹ සිට කිලෝමීටර 150ක් දුරින්. දකුණු අධිවේගී මාර්ගය හරහා මෝටර් රථයෙන් (පැය 2.5-3) හෝ වැලිගම දක්වා දුම්රියෙන් පසුව කුලී රථයකින් ළඟා විය හැක.",
                ta="தென் கடற்கரையில் கொழும்பிலிருந்து 150 கிமீ தொலைவில். தெற்கு விரைவுச்சாலை வழியாக கார் (2.5-3 மணி) அல்லது வெலிகம வரை ரயில் பின்னர் டாக்ஸி மூலம் அணுகலாம்."
            ),
            "slug": "mirissa-beach",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 90.0,
            "average_rating": 4.7
        },
        {
            "name": MultilingualContent(
                en="Nuwara Eliya Hill Station",
                si="නුවර එළිය කඳුකර නගරය",
                ta="நுவரெலியா மலை நகரம்"
            ),
            "description": MultilingualContent(
                en="Colonial hill station known as 'Little England' with tea plantations, cool climate, and British colonial architecture.",
                si="'කුඩා එංගලන්තය' ලෙස හැඳින්වෙන යටත් විජිත කඳුකර නගරය, තේ වතු, සිසිල් දේශගුණය සහ බ්‍රිතාන්‍ය යටත් විජිත ගෘහ නිර්මාණ ශිල්පය සහිතය.",
                ta="'சிறிய இங்கிலாந்து' என்று அழைக்கப்படும் காலனித்துவ மலை நகரம், தேயிலை தோட்டங்கள், குளிர்ந்த காலநிலை மற்றும் பிரிட்டிஷ் காலனித்துவ கட்டிடக்கலை."
            ),
            "short_description": MultilingualContent(
                en="Scenic hill country with tea plantations",
                si="තේ වතු සහිත දර්ශනීය කඳුකර ප්‍රදේශය",
                ta="தேயிலை தோட்டங்களுடன் கூடிய இயற்கை எழில் மிக்க மலைநாடு"
            ),
            "category": AttractionCategory.MOUNTAIN,
            "subcategories": ["tea_plantations", "colonial", "nature"],
            "tags": ["hill_country", "tea", "colonial", "cool_climate", "scenic"],
            "location": Location(
                address="Nuwara Eliya",
                city="Nuwara Eliya",
                province="Central Province",
                coordinates=[80.7891, 6.9497]
            ),
            "is_free": True,
            "estimated_visit_duration": "1-2 days",
            "how_to_get_there": MultilingualContent(
                en="Located 180km from Colombo in the central highlands. Accessible by car (4-5 hours) or scenic train ride through tea country.",
                si="මධ්‍යම කඳුකර ප්‍රදේශයේ කොළඹ සිට කිලෝමීටර 180ක් දුරින්. මෝටර් රථයෙන් (පැය 4-5) හෝ තේ වතු හරහා දර්ශනීය දුම්රිය ගමනකින් ළඟා විය හැක.",
                ta="மத்திய மலைநாட்டில் கொழும்பிலிருந்து 180 கிமீ தொலைவில். கார் (4-5 மணி) அல்லது தேயிலை நாடு வழியாக இயற்கை எழில் மிக்க ரயில் பயணம் மூலம் அணுகலாம்."
            ),
            "slug": "nuwara-eliya-hill-station",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 88.0,
            "average_rating": 4.5
        }
    ]
    
    for data in attractions_data:
        attraction = Attraction(**data)
        await attraction.insert()
    
    print(f"Seeded {len(attractions_data)} attractions!")


async def seed_hotels():
    """Seed hotel data"""
    print("Seeding hotels...")
    
    hotels_data = [
        {
            "name": MultilingualContent(
                en="Galle Face Hotel",
                si="ගාල් ෆේස් හෝටලය",
                ta="கால் ஃபேஸ் ஹோட்டல்"
            ),
            "description": MultilingualContent(
                en="Historic luxury hotel facing the Indian Ocean, operating since 1864. Colonial elegance with modern amenities.",
                si="1864 සිට ක්‍රියාත්මක වන ඉන්දියන් සාගරයට මුහුණලා ඇති ඓතිහාසික සුඛෝපභෝගී හෝටලය. නවීන පහසුකම් සහිත යටත් විජිත අලංකාරය.",
                ta="1864 முதல் செயல்படும் இந்தியப் பெருங்கடலை எதிர்கொண்டுள்ள வரலாற்று ரீதியான ஆடம்பர ஹோட்டல். நவீன வசதிகளுடன் காலனித்துவ நேர்த்தி."
            ),
            "short_description": MultilingualContent(
                en="Historic oceanfront luxury hotel since 1864",
                si="1864 සිට ක්‍රියාත්මක සාගර තීරයේ ඓතිහාසික සුඛෝපභෝගී හෝටලය",
                ta="1864 முதல் கடற்கரையோர வரலாற்று ஆடம்பர ஹோட்டல்"
            ),
            "category": HotelCategory.LUXURY,
            "star_rating": StarRating.FIVE,
            "location": Location(
                address="2 Galle Road, Colombo 3",
                city="Colombo",
                province="Western Province",
                coordinates=[79.8448, 6.9271]
            ),
            "rooms": [
                Room(
                    room_type=RoomType.DELUXE,
                    name=MultilingualContent(en="Deluxe Ocean View", si="ඩිලක්ස් සාගර දසුන", ta="டீலக்ஸ் கடல் காட்சி"),
                    max_occupancy=2,
                    bed_type="king",
                    price_per_night=35000.0,
                    amenities=["ocean_view", "balcony", "mini_bar", "wifi"]
                ),
                Room(
                    room_type=RoomType.SUITE,
                    name=MultilingualContent(en="Executive Suite", si="විධායක කාමරය", ta="நிர்வாக தொகுப்பு"),
                    max_occupancy=3,
                    bed_type="king",
                    price_per_night=65000.0,
                    amenities=["ocean_view", "living_room", "mini_bar", "wifi", "bathtub"]
                )
            ],
            "amenities": [Amenity.WIFI, Amenity.POOL, Amenity.SPA, Amenity.GYM, 
                          Amenity.RESTAURANT, Amenity.BAR, Amenity.ROOM_SERVICE, 
                          Amenity.CONCIERGE, Amenity.BEACH_ACCESS],
            "accepts_online_booking": True,
            "slug": "galle-face-hotel-colombo",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 95.0,
            "average_rating": 4.7
        },
        {
            "name": MultilingualContent(
                en="Jetwing Lighthouse",
                si="ජෙට්වින් ලයිට්හවුස්",
                ta="ஜெட்விங் கலங்கரை விளக்கம்"
            ),
            "description": MultilingualContent(
                en="Award-winning boutique hotel designed by Geoffrey Bawa on a rocky outcrop overlooking the ocean in Galle.",
                si="ජෙෆ්රි බාවා විසින් නිර්මාණය කරන ලද, ගාල්ලේ සාගරයට ඉහළින් පාෂාණමය පර්වතයක ඉදිකරන ලද සම්මානලාභී බුටික් හෝටලය.",
                ta="கேஃப்ரி பாவாவால் வடிவமைக்கப்பட்ட, காலியில் கடலைக் கண்காணிக்கும் பாறை மேடையில் உள்ள விருது பெற்ற பூட்டிக் ஹோட்டல்."
            ),
            "short_description": MultilingualContent(
                en="Boutique hotel by Geoffrey Bawa overlooking Galle",
                si="ජෙෆ්රි බාවාගේ ගාල්ලට ඉහළින් බුටික් හෝටලය",
                ta="காலியைக் கண்காணிக்கும் ஜெஃப்ரி பாவாவின் பூட்டிக் ஹோட்டல்"
            ),
            "category": HotelCategory.BOUTIQUE,
            "star_rating": StarRating.FIVE,
            "location": Location(
                address="Dadella, Galle",
                city="Galle",
                province="Southern Province",
                coordinates=[80.2470, 6.0236]
            ),
            "rooms": [
                Room(
                    room_type=RoomType.DOUBLE,
                    name=MultilingualContent(en="Ocean Room", si="සාගර කාමරය", ta="கடல் அறை"),
                    max_occupancy=2,
                    price_per_night=28000.0,
                    amenities=["ocean_view", "balcony", "wifi", "air_conditioning"]
                )
            ],
            "amenities": [Amenity.WIFI, Amenity.POOL, Amenity.SPA, Amenity.RESTAURANT, 
                          Amenity.BAR, Amenity.BEACH_ACCESS],
            "slug": "jetwing-lighthouse-galle",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 92.0,
            "average_rating": 4.8
        },
        {
            "name": MultilingualContent(
                en="Heritance Kandalama",
                si="හෙරිටන්ස් කඳලම",
                ta="ஹெரிடன்ஸ் கந்தலாமா"
            ),
            "description": MultilingualContent(
                en="Eco-friendly resort designed by Geoffrey Bawa, built into a rock face overlooking Kandalama Lake.",
                si="කඳලම වැවට ඉහළින් පාෂාණමය මුහුණතකට තනන ලද, ජෙෆ්රි බාවා විසින් නිර්මාණය කරන ලද පරිසර හිතකාමී නිවාඩු නිකේතනය.",
                ta="கந்தலாமா ஏரியைக் கண்காணிக்கும் பாறை முகத்தில் கட்டப்பட்ட, ஜெஃப்ரி பாவாவால் வடிவமைக்கப்பட்ட சுற்றுச்சூழல் நட்பு ரிசார்ட்."
            ),
            "short_description": MultilingualContent(
                en="Eco-resort built into rock face with lake views",
                si="විල් දසුන් සහිත පාෂාණමය මුහුණතට තනන ලද පරිසර නිකේතනය",
                ta="ஏரி காட்சிகளுடன் பாறை முகத்தில் கட்டப்பட்ட சுற்றுச்சூழல் ரிசார்ட்"
            ),
            "category": HotelCategory.RESORT,
            "star_rating": StarRating.FIVE,
            "location": Location(
                address="Dambulla",
                city="Dambulla",
                province="Central Province",
                coordinates=[80.6467, 7.9104]
            ),
            "rooms": [
                Room(
                    room_type=RoomType.DOUBLE,
                    name=MultilingualContent(en="Lake View Room", si="විල් දසුන් කාමරය", ta="ஏரி காட்சி அறை"),
                    max_occupancy=2,
                    price_per_night=22000.0,
                    amenities=["lake_view", "balcony", "wifi"]
                )
            ],
            "amenities": [Amenity.WIFI, Amenity.POOL, Amenity.SPA, Amenity.GYM, 
                          Amenity.RESTAURANT, Amenity.LAUNDRY],
            "slug": "heritance-kandalama",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 90.0,
            "average_rating": 4.6
        }
    ]
    
    for data in hotels_data:
        hotel = Hotel(**data)
        await hotel.insert()
    
    print(f"Seeded {len(hotels_data)} hotels!")


async def seed_restaurants():
    """Seed restaurant data"""
    print("Seeding restaurants...")
    
    restaurants_data = [
        {
            "name": MultilingualContent(
                en="Ministry of Crab",
                si="කකුළුවන් අමාත්‍යාංශය",
                ta="நண்டு அமைச்சகம்"
            ),
            "description": MultilingualContent(
                en="World-renowned restaurant specializing in Sri Lankan lagoon crabs. Located in a restored colonial Dutch hospital building.",
                si="ශ්‍රී ලංකා කලපු කකුළුවන් සඳහා විශේෂිත වූ ලෝක ප්‍රකට අවන්හල. ප්‍රතිසංස්කරණය කරන ලද යටත් විජිත ලන්දේසි රෝහල් ගොඩනැගිල්ලක පිහිටා ඇත.",
                ta="இலங்கை குளம் நண்டுகளில் நிபுணத்துவம் பெற்ற உலகப் புகழ்பெற்ற உணவகம். மீட்டெடுக்கப்பட்ட காலனித்துவ டச்சு மருத்துவமனை கட்டிடத்தில் அமைந்துள்ளது."
            ),
            "short_description": MultilingualContent(
                en="World-famous restaurant for Sri Lankan crabs",
                si="ශ්‍රී ලංකා කකුළුවන් සඳහා ලෝක ප්‍රකට අවන්හල",
                ta="இலங்கை நண்டுகளுக்கான உலகப் புகழ்பெற்ற உணவகம்"
            ),
            "cuisine_types": [CuisineType.SEAFOOD, CuisineType.SRI_LANKAN],
            "restaurant_type": RestaurantType.FINE_DINING,
            "price_range": PriceRange.LUXURY,
            "location": Location(
                address="Old Dutch Hospital, Hospital Street, Colombo 1",
                city="Colombo",
                province="Western Province",
                coordinates=[79.8448, 6.9336]
            ),
            "opening_hours": [
                OpeningHours(day_of_week=i, open_time="12:00", close_time="15:00")
                for i in range(7)
            ] + [
                OpeningHours(day_of_week=i, open_time="18:00", close_time="23:00")
                for i in range(7)
            ],
            "accepts_reservations": True,
            "dietary_options": [DietaryOption.GLUTEN_FREE],
            "air_conditioning": True,
            "wifi_available": True,
            "parking_available": True,
            "payment_methods": ["cash", "card", "mobile_payment"],
            "slug": "ministry-of-crab-colombo",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 98.0,
            "average_rating": 4.8
        },
        {
            "name": MultilingualContent(
                en="Heladiv Tea Club",
                si="හෙලදිව් තේ සමාජය",
                ta="ஹெலடிவ் தேயிலை கிளப்"
            ),
            "description": MultilingualContent(
                en="Elegant restaurant offering Sri Lankan cuisine and Ceylon tea experience with panoramic views of Colombo.",
                si="කොළඹ නගරයේ පරිදර්ශන සමඟ ශ්‍රී ලංකා ආහාර සහ ලංකා තේ අත්දැකීම් සපයන අලංකාර අවන්හල.",
                ta="கொழும்பின் பரந்த காட்சிகளுடன் இலங்கை உணவு வகைகள் மற்றும் இலங்கை தேயிலை அனுபவத்தை வழங்கும் நேர்த்தியான உணவகம்."
            ),
            "short_description": MultilingualContent(
                en="Sri Lankan cuisine with panoramic city views",
                si="පරිදර්ශන නගර දසුන් සහිත ශ්‍රී ලංකා ආහාර",
                ta="பரந்த நகர காட்சிகளுடன் இலங்கை உணவு வகைகள்"
            ),
            "cuisine_types": [CuisineType.SRI_LANKAN, CuisineType.CONTINENTAL],
            "restaurant_type": RestaurantType.FINE_DINING,
            "price_range": PriceRange.EXPENSIVE,
            "location": Location(
                address="Level 34, World Trade Center, Colombo 1",
                city="Colombo",
                province="Western Province",
                coordinates=[79.8461, 6.9320]
            ),
            "dietary_options": [DietaryOption.VEGETARIAN, DietaryOption.HALAL],
            "slug": "heladiv-tea-club-colombo",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 85.0,
            "average_rating": 4.5
        }
    ]
    
    for data in restaurants_data:
        restaurant = Restaurant(**data)
        await restaurant.insert()
    
    print(f"Seeded {len(restaurants_data)} restaurants!")


async def seed_transport():
    """Seed transport data"""
    print("Seeding transport...")
    
    transport_data = [
        {
            "name": MultilingualContent(
                en="Kandy to Ella Train",
                si="මහනුවර සිට ඇල්ල දුම්රිය",
                ta="கண்டி முதல் எல்லா ரயில்"
            ),
            "description": MultilingualContent(
                en="One of the most scenic train journeys in the world, passing through tea plantations, mountains, and waterfalls.",
                si="ලෝකයේ වඩාත් දර්ශනීය දුම්රිය ගමන් වලින් එකක්, තේ වතු, කඳු සහ දිය ඇලි හරහා ගමන් කරයි.",
                ta="உலகின் மிக அழகான ரயில் பயணங்களில் ஒன்று, தேயிலை தோட்டங்கள், மலைகள் மற்றும் நீர்வீழ்ச்சிகள் வழியாக செல்கிறது."
            ),
            "short_description": MultilingualContent(
                en="World's most scenic train journey",
                si="ලෝකයේ වඩාත් දර්ශනීය දුම්රිය ගමන",
                ta="உலகின் மிக அழகான ரயில் பயணம்"
            ),
            "transport_type": TransportType.TRAIN,
            "category": TransportCategory.PUBLIC,
            "service_levels": [ServiceLevel.ECONOMY, ServiceLevel.STANDARD],
            "operator_name": "Sri Lanka Railways",
            "routes": [
                Route(
                    origin="Kandy",
                    destination="Ella",
                    distance_km=123,
                    duration_minutes=390,
                    route_description=MultilingualContent(
                        en="Through hill country, tea plantations, and Nine Arch Bridge",
                        si="කඳුකර, තේ වතු සහ නවක ආරුක්කු පාලම හරහා",
                        ta="மலைநாடு, தேயிலை தோட்டங்கள் மற்றும் ஒன்பது வளைவு பாலம் வழியாக"
                    )
                )
            ],
            "schedules": [
                Schedule(
                    departure_time="08:47",
                    arrival_time="15:17",
                    duration_minutes=390,
                    days_of_week=[0, 1, 2, 3, 4, 5, 6]
                )
            ],
            "pricing_options": [
                PricingOption(
                    service_level=ServiceLevel.ECONOMY,
                    price=250.0,
                    currency="LKR",
                    price_type="per_person"
                ),
                PricingOption(
                    service_level=ServiceLevel.STANDARD,
                    price=500.0,
                    currency="LKR",
                    price_type="per_person"
                )
            ],
            "amenities": ["scenic_views", "restroom"],
            "slug": "kandy-ella-train",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 96.0,
            "average_rating": 4.9
        },
        {
            "name": MultilingualContent(
                en="Colombo Airport Taxi Service",
                si="කොළඹ ගුවන් තොටුපළ කුලී රථ සේවාව",
                ta="கொழும்பு விமான நிலைய டாக்ஸி சேவை"
            ),
            "description": MultilingualContent(
                en="Official airport taxi service providing safe and reliable transportation from Bandaranaike International Airport.",
                si="බණ්ඩාරනායක ජාත්‍යන්තර ගුවන් තොටුපළේ සිට ආරක්ෂිත හා විශ්වාසනීය ප්‍රවාහන සේවා සපයන නිල ගුවන් තොටුපළ කුලී රථ සේවාව.",
                ta="பண்டாரநாயக்க சர்வதேச விமான நிலையத்திலிருந்து பாதுகாப்பான மற்றும் நம்பகமான போக்குவரத்தை வழங்கும் உத்தியோகபூர்வ விமான நிலைய டாக்ஸி சேவை."
            ),
            "short_description": MultilingualContent(
                en="Official airport taxi service",
                si="නිල ගුවන් තොටුපළ කුලී රථ සේවාව",
                ta="உத்தியோகபூர்வ விமான நிலைய டாக்ஸி சேவை"
            ),
            "transport_type": TransportType.TAXI,
            "category": TransportCategory.PRIVATE,
            "service_levels": [ServiceLevel.STANDARD, ServiceLevel.PREMIUM],
            "operator_name": "Airport Express",
            "operates_24_7": True,
            "pricing_options": [
                PricingOption(
                    service_level=ServiceLevel.STANDARD,
                    price=3500.0,
                    currency="LKR",
                    price_type="per_vehicle",
                    description=MultilingualContent(en="To Colombo city center")
                )
            ],
            "amenities": ["air_conditioning", "luggage_assistance", "english_speaking_driver"],
            "accepts_online_booking": True,
            "slug": "colombo-airport-taxi",
            "is_active": True,
            "is_featured": True,
            "popularity_score": 82.0,
            "average_rating": 4.3
        }
    ]
    
    for data in transport_data:
        transport = Transport(**data)
        await transport.insert()
    
    print(f"Seeded {len(transport_data)} transport options!")


async def seed_events():
    """Seed event data"""
    print("Seeding events...")
    
    events_data = [
        {
            "title": MultilingualContent(
                en="Kandy Esala Perahera",
                si="මහ නුවර අසළ පෙරහැර",
                ta="கண்டி எசல பெரஹெர"
            ),
            "description": MultilingualContent(
                en="One of the oldest and grandest Buddhist festivals in the world, featuring decorated elephants, dancers, drummers, and fire performers.",
                si="ලෝකයේ පැරණිතම හා විශාලතම බෞද්ධ උත්සවවලින් එකක්, සරසන ලද අලි, නර්තන ශිල්පීන්, බෙර වාදකයින් සහ ගිනි කලාකරුවන් ඇතුළත් වේ.",
                ta="உலகின் பழமையான மற்றும் பிரமாண்டமான புத்த திருவிழாக்களில் ஒன்று, அலங்கரிக்கப்பட்ட யானைகள், நடனக் கலைஞர்கள், டம்ளர்கள் மற்றும் நெருப்பு கலைஞர்கள் இடம்பெறுகிறது."
            ),
            "short_description": MultilingualContent(
                en="Grand Buddhist festival with decorated elephants",
                si="සරසන ලද අලි සහිත මහා බෞද්ධ උත්සවය",
                ta="அலங்கரிக்கப்பட்ட யானைகளுடன் கூடிய பிரமாண்ட புத்த திருவிழா"
            ),
            "category": EventCategory.RELIGIOUS,
            "subcategories": ["procession", "cultural"],
            "tags": ["buddhist", "festival", "elephants", "traditional", "kandy"],
            "schedule": EventSchedule(
                start_date=datetime(2024, 8, 3),
                end_date=datetime(2024, 8, 14),
                start_time="19:30",
                is_all_day=False,
                recurring=True,
                recurring_pattern="yearly"
            ),
            "location": Location(
                address="Temple of the Tooth, Kandy",
                city="Kandy",
                province="Central Province",
                coordinates=[80.6400, 7.2936]
            ),
            "venue_name": "Temple of the Tooth and surrounding streets",
            "tickets": [
                Ticket(
                    ticket_type=TicketType.FREE,
                    name=MultilingualContent(en="General Viewing", si="සාමාන්‍ය නැරඹීම", ta="பொது பார்வை"),
                    price=0.0,
                    description=MultilingualContent(en="Free viewing from streets")
                )
            ],
            "target_audience": ["families", "tourists", "buddhists", "culture_enthusiasts"],
            "languages": ["si", "en", "ta"],
            "cultural_significance": MultilingualContent(
                en="Honors the Sacred Tooth Relic of the Buddha. Dating back to the 4th century AD.",
                si="බුදුරජාණන් වහන්සේගේ ශ්‍රී දළදා වහන්සේට ගෞරව කිරීම. ක්‍රි.ව. 4 වන සියවස දක්වා දිව යන ඉතිහාසයක් ඇත.",
                ta="புத்தரின் புனித பல் நினைவுச்சின்னத்தை மதிக்கும் திருவிழா. கி.பி 4 ஆம் நூற்றாண்டு முதல் வந்தது."
            ),
            "status": EventStatus.PUBLISHED,
            "slug": "kandy-esala-perahera",
            "is_featured": True,
            "popularity_score": 99.0
        },
        {
            "title": MultilingualContent(
                en="Galle Literary Festival",
                si="ගාල්ල සාහිත්‍ය උත්සවය",
                ta="காலி இலக்கிய திருவிழா"
            ),
            "description": MultilingualContent(
                en="Annual literary festival bringing together international and local authors, poets, and literary enthusiasts in the historic Galle Fort.",
                si="ඓතිහාසික ගාල්ල කොටුව තුළ ජාත්‍යන්තර හා දේශීය කතුවරුන්, කවියන් සහ සාහිත්‍ය ලෝලීන් එක්රැස් කරන වාර්ෂික සාහිත්‍ය උත්සවය.",
                ta="வரலாற்று கால்லே கோட்டையில் சர்வதேச மற்றும் உள்ளூர் எழுத்தாளர்கள், கவிஞர்கள் மற்றும் இலக்கிய ஆர்வலர்களை ஒன்றிணைக்கும் வருடாந்திர இலக்கிய திருவிழா."
            ),
            "short_description": MultilingualContent(
                en="Annual literary festival in historic Galle Fort",
                si="ඓතිහාසික ගාල්ල කොටුවේ වාර්ෂික සාහිත්‍ය උත්සවය",
                ta="வரலாற்று கால்லே கோட்டையில் வருடாந்திர இலக்கிய திருவிழா"
            ),
            "category": EventCategory.ART,
            "subcategories": ["literature", "cultural"],
            "tags": ["literary", "books", "authors", "galle", "cultural"],
            "schedule": EventSchedule(
                start_date=datetime(2025, 1, 25),
                end_date=datetime(2025, 1, 28),
                is_all_day=True,
                recurring=True,
                recurring_pattern="yearly"
            ),
            "location": Location(
                address="Galle Fort",
                city="Galle",
                province="Southern Province",
                coordinates=[80.2170, 6.0267]
            ),
            "is_online_event": False,
            "tickets": [
                Ticket(
                    ticket_type=TicketType.PAID,
                    name=MultilingualContent(en="Festival Pass", si="උත්සව පත්‍රය", ta="திருவிழா பாஸ்"),
                    price=5000.0,
                    description=MultilingualContent(en="Access to all sessions")
                )
            ],
            "target_audience": ["adults", "literary_enthusiasts", "students"],
            "status": EventStatus.PUBLISHED,
            "slug": "galle-literary-festival",
            "is_featured": True,
            "popularity_score": 85.0
        }
    ]
    
    for data in events_data:
        event = Event(**data)
        await event.insert()
    
    print(f"Seeded {len(events_data)} events!")


async def main():
    """Main seeding function"""
    print("Starting comprehensive data seeding...")
    print(f"Connecting to MongoDB: {settings.MONGODB_URL}")
    
    # Initialize database connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize Beanie
    await init_beanie(
        database=database,
        document_models=[Attraction, Hotel, Restaurant, Transport, Event]
    )
    
    # Clear existing data
    await clear_collections()
    
    # Seed all data
    await seed_attractions()
    await seed_hotels()
    await seed_restaurants()
    await seed_transport()
    await seed_events()
    
    print("\n✅ Comprehensive data seeding completed successfully!")
    print("\nSeeded:")
    print(f"  - {await Attraction.count()} attractions")
    print(f"  - {await Hotel.count()} hotels")
    print(f"  - {await Restaurant.count()} restaurants")
    print(f"  - {await Transport.count()} transport options")
    print(f"  - {await Event.count()} events")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(main())


