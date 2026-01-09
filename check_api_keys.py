"""Quick script to check API key configuration"""
from backend.app.core.config import settings

print("=" * 60)
print("API KEYS CONFIGURATION STATUS")
print("=" * 60)

print("\n🔑 REQUIRED FOR CORE FUNCTIONALITY:")
print(f"  ✓ SECRET_KEY: {'SET ✅' if settings.SECRET_KEY and settings.SECRET_KEY != 'CHANGE-THIS-TO-A-SECURE-RANDOM-KEY-IN-PRODUCTION' else 'NOT SET ❌'}")
print(f"  ✓ MONGODB_URL: {'SET ✅' if settings.MONGODB_URL else 'NOT SET ❌'}")

print("\n🤖 AI/LLM SERVICES:")
print(f"  • LLM_ENABLED: {settings.LLM_ENABLED}")
print(f"  • GEMINI_API_KEY: {'SET ✅' if settings.GEMINI_API_KEY else 'NOT SET ⚠️'}")
print(f"  • QWEN_API_KEY: {'SET ✅' if settings.QWEN_API_KEY else 'NOT SET ⚠️'}")
print(f"  • MISTRAL_API_KEY: {'SET ✅' if settings.MISTRAL_API_KEY else 'NOT SET ⚠️'}")

print("\n🌤️ WEATHER SERVICE:")
print(f"  • OPENWEATHER_API_KEY: {'SET ✅' if settings.OPENWEATHER_API_KEY else 'NOT SET ⚠️'}")

print("\n💱 CURRENCY SERVICE:")
print(f"  • CURRENCYLAYER_API_KEY: {'SET ✅' if settings.CURRENCYLAYER_API_KEY else 'NOT SET ⚠️'}")

print("\n🗺️ GOOGLE SERVICES (Optional):")
print(f"  • GOOGLE_MAPS_API_KEY: {'SET ✅' if settings.GOOGLE_MAPS_API_KEY else 'NOT SET ℹ️'}")
print(f"  • GOOGLE_TRANSLATE_API_KEY: {'SET ✅' if settings.GOOGLE_TRANSLATE_API_KEY else 'NOT SET ℹ️'}")

print("\n🔍 SEARCH SERVICE:")
print(f"  • TAVILY_API_KEY: {'SET ✅' if settings.TAVILY_API_KEY else 'NOT SET ℹ️'}")

print("\n" + "=" * 60)
print("SUMMARY:")
critical_keys = [
    bool(settings.SECRET_KEY and settings.SECRET_KEY != 'CHANGE-THIS-TO-A-SECURE-RANDOM-KEY-IN-PRODUCTION'),
    bool(settings.MONGODB_URL)
]
optional_keys = [
    bool(settings.GEMINI_API_KEY),
    bool(settings.OPENWEATHER_API_KEY),
    bool(settings.CURRENCYLAYER_API_KEY)
]

print(f"Critical Keys: {sum(critical_keys)}/2")
print(f"Optional Keys: {sum(optional_keys)}/3")
print("=" * 60)
