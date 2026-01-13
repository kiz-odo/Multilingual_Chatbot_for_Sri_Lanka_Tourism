import type { Language } from "@/types";

export const translations: Record<
  Language,
  Record<string, string>
> = {
  en: {
    // Navigation
    "nav.home": "Home",
    "nav.chat": "Chat",
    "nav.explore": "Explore",
    "nav.planner": "Planner",
    "nav.safety": "Safety",
    "nav.dashboard": "Dashboard",
    "nav.login": "Login",
    "nav.register": "Register",
    "nav.logout": "Logout",
    
    // Home
    "home.hero.title": "Explore Sri Lanka with an AI Travel Assistant",
    "home.hero.subtitle": "Instant answers, personalized itineraries, and local secrets—available 24/7",
    "home.cta.startChat": "Start Chat",
    "home.cta.explore": "Explore Attractions",
    "home.cta.planTrip": "Plan My Trip",
    "home.featured.title": "Featured Destinations",
    "home.featured.viewAll": "View all",
    
    // Chat
    "chat.title": "AI Chat Assistant",
    "chat.placeholder": "Ask me anything about Sri Lanka...",
    "chat.send": "Send",
    "chat.voice": "Voice Input",
    "chat.suggestions": "Suggested Questions",
    "chat.clear": "Clear History",
    
    // Common
    "common.loading": "Loading...",
    "common.error": "An error occurred",
    "common.retry": "Retry",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.edit": "Edit",
    "common.close": "Close",
    "common.search": "Search",
    "common.filter": "Filter",
    "common.sort": "Sort",
    "common.view": "View",
    "common.back": "Back",
    "common.next": "Next",
    "common.previous": "Previous",
    
    // Auth
    "auth.login.title": "Login",
    "auth.login.username": "Username",
    "auth.login.password": "Password",
    "auth.login.submit": "Sign In",
    "auth.login.forgot": "Forgot Password?",
    "auth.login.noAccount": "Don't have an account?",
    "auth.register.title": "Create Account",
    "auth.register.email": "Email",
    "auth.register.confirmPassword": "Confirm Password",
    "auth.register.submit": "Sign Up",
    "auth.register.hasAccount": "Already have an account?",
    
    // Attractions
    "attractions.title": "Attractions",
    "attractions.featured": "Featured",
    "attractions.all": "All Attractions",
    "attractions.details": "View Details",
    "attractions.rating": "Rating",
    "attractions.reviews": "Reviews",
    "attractions.duration": "Visit Duration",
    "attractions.location": "Location",
    "attractions.price": "Price",
    
    // Itinerary
    "itinerary.title": "Plan Your Trip",
    "itinerary.generate": "Generate AI Itinerary",
    "itinerary.dates": "Travel Dates",
    "itinerary.cities": "Cities",
    "itinerary.budget": "Budget",
    "itinerary.preferences": "Preferences",
    "itinerary.export.pdf": "Export PDF",
    "itinerary.export.calendar": "Export to Calendar",
    
    // Safety
    "safety.title": "Safety & Emergency",
    "safety.sos": "Emergency SOS",
    "safety.contacts": "Emergency Contacts",
    "safety.tips": "Safety Tips",
    "safety.location": "Share Location",
    
    // Dashboard
    "dashboard.title": "Dashboard",
    "dashboard.profile": "Profile",
    "dashboard.saved": "Saved Attractions",
    "dashboard.itineraries": "My Itineraries",
    "dashboard.chatHistory": "Chat History",
    "dashboard.settings": "Settings",
  },
  si: {
    "nav.home": "මුල් පිටුව",
    "nav.chat": "චැට්",
    "nav.explore": "ගවේෂණය",
    "nav.planner": "සැලසුම්කරු",
    "nav.safety": "ආරක්ෂාව",
    "nav.dashboard": "උපකරණ පුවරුව",
    "home.hero.title": "AI ගමන් සහායකයෙකු සමඟ ශ්‍රී ලංකාව ගවේෂණය කරන්න",
    "home.hero.subtitle": "ක්ෂණික පිළිතුරු, පුද්ගලීකරණය කළ සැලසුම්, සහ දේශීය රහස්",
  },
  ta: {
    "nav.home": "முகப்பு",
    "nav.chat": "அரட்டை",
    "nav.explore": "ஆராய",
    "nav.planner": "திட்டமிடுபவர்",
    "nav.safety": "பாதுகாப்பு",
    "nav.dashboard": "டாஷ்போர்டு",
    "home.hero.title": "AI பயண உதவியாளருடன் இலங்கையை ஆராயுங்கள்",
    "home.hero.subtitle": "உடனடி பதில்கள், தனிப்பயனாக்கப்பட்ட வழிகாட்டிகள், மற்றும் உள்ளூர் ரகசியங்கள்",
  },
  de: {},
  fr: {},
  zh: {},
  ja: {},
};

export function t(key: string, language: Language = "en"): string {
  return translations[language]?.[key] || translations.en[key] || key;
}

export function getLocalizedText(
  obj: Record<string, string | undefined> | undefined,
  language: Language = "en",
  fallback: string = ""
): string {
  if (!obj) return fallback;
  return obj[language] || obj.en || fallback;
}







