"""
Translation service for multilingual support
"""

import httpx
from typing import Tuple, Optional, Dict, Any
import logging

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    def detect(text):
        # Fallback to 'en' if langdetect is not available
        return 'en'
    
    def detect_langs(text):
        # Fallback to English with high confidence
        class MockLang:
            def __init__(self, lang, prob):
                self.lang = lang
                self.prob = prob
        return [MockLang('en', 0.99)]

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class TranslationService:
    """Translation service for multilingual chatbot"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_TRANSLATE_API_KEY
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_language = settings.DEFAULT_LANGUAGE
    
    async def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            detected = detect(text)
            
            # Map detected language to supported languages
            language_mapping = {
                'si': 'si',  # Sinhala
                'ta': 'ta',  # Tamil
                'en': 'en',  # English
                'de': 'de',  # German
                'fr': 'fr',  # French
                'zh': 'zh',  # Chinese (simplified)
                'zh-cn': 'zh',
                'zh-tw': 'zh',
                'ja': 'ja',  # Japanese
            }
            
            mapped_language = language_mapping.get(detected, self.default_language)
            
            # Return mapped language if supported, otherwise default
            return mapped_language if mapped_language in self.supported_languages else self.default_language
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return self.default_language
    
    async def detect_language_with_confidence(self, text: str) -> Tuple[str, float]:
        """Detect language with confidence score"""
        try:
            detected_langs = detect_langs(text)
            
            if detected_langs:
                best_detection = detected_langs[0]
                detected_lang = best_detection.lang
                confidence = best_detection.prob
                
                # Map to supported language
                language_mapping = {
                    'si': 'si', 'ta': 'ta', 'en': 'en', 'de': 'de',
                    'fr': 'fr', 'zh': 'zh', 'zh-cn': 'zh', 'zh-tw': 'zh', 'ja': 'ja'
                }
                
                mapped_language = language_mapping.get(detected_lang, self.default_language)
                
                if mapped_language not in self.supported_languages:
                    mapped_language = self.default_language
                    confidence = 0.5  # Lower confidence for fallback
                
                return mapped_language, confidence
            else:
                return self.default_language, 0.0
                
        except Exception as e:
            logger.error(f"Language detection with confidence error: {str(e)}")
            return self.default_language, 0.0
    
    async def translate_text(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str] = None
    ) -> str:
        """Translate text using Google Translate API"""
        
        # If no translation needed
        if source_language == target_language:
            return text
        
        # If no API key available, return original text
        if not self.google_api_key:
            logger.warning("Google Translate API key not configured")
            return text
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Prepare request parameters
                params = {
                    'key': self.google_api_key,
                    'q': text,
                    'target': target_language,
                    'format': 'text'
                }
                
                if source_language:
                    params['source'] = source_language
                
                # Make API request
                response = await client.post(
                    'https://translation.googleapis.com/language/translate/v2',
                    params=params
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'data' in result and 'translations' in result['data']:
                        translations = result['data']['translations']
                        if translations:
                            return translations[0]['translatedText']
                
                logger.error(f"Translation API error: {response.status_code}")
                return text
                
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
    
    async def translate_multilingual_content(
        self, 
        content: Dict[str, str], 
        target_language: str
    ) -> str:
        """Get content in target language from multilingual content"""
        
        # Try to get content in target language
        if target_language in content and content[target_language]:
            return content[target_language]
        
        # Try English as fallback
        if 'en' in content and content['en']:
            english_content = content['en']
            
            # If target is English, return directly
            if target_language == 'en':
                return english_content
            
            # Otherwise translate from English
            return await self.translate_text(english_content, target_language, 'en')
        
        # Get any available content and translate
        for lang, text in content.items():
            if text:
                return await self.translate_text(text, target_language, lang)
        
        return ""
    
    async def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages with names"""
        
        language_info = {
            'si': {
                'code': 'si',
                'name': 'Sinhala',
                'native_name': 'සිංහල',
                'flag': '🇱🇰'
            },
            'ta': {
                'code': 'ta',
                'name': 'Tamil',
                'native_name': 'தமிழ்',
                'flag': '🇱🇰'
            },
            'en': {
                'code': 'en',
                'name': 'English',
                'native_name': 'English',
                'flag': '🇺🇸'
            },
            'de': {
                'code': 'de',
                'name': 'German',
                'native_name': 'Deutsch',
                'flag': '🇩🇪'
            },
            'fr': {
                'code': 'fr',
                'name': 'French',
                'native_name': 'Français',
                'flag': '🇫🇷'
            },
            'zh': {
                'code': 'zh',
                'name': 'Chinese',
                'native_name': '中文',
                'flag': '🇨🇳'
            },
            'ja': {
                'code': 'ja',
                'name': 'Japanese',
                'native_name': '日本語',
                'flag': '🇯🇵'
            }
        }
        
        return {lang: language_info[lang] for lang in self.supported_languages if lang in language_info}
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language in self.supported_languages
    
    async def auto_translate_response(
        self, 
        response: str, 
        detected_user_language: str
    ) -> str:
        """Auto-translate bot response to user's language"""
        
        # If response is already in user's language or user language is English, return as is
        if detected_user_language in ['en'] or not self.is_language_supported(detected_user_language):
            return response
        
        # Translate response to user's language
        return await self.translate_text(response, detected_user_language, 'en')
    
    def get_language_direction(self, language: str) -> str:
        """Get text direction for language (LTR or RTL)"""
        rtl_languages = ['ar', 'he', 'fa', 'ur']  # Arabic, Hebrew, Persian, Urdu
        return 'rtl' if language in rtl_languages else 'ltr'
    
    def get_language_font_family(self, language: str) -> str:
        """Get recommended font family for language"""
        font_families = {
            'si': 'Noto Sans Sinhala, sans-serif',
            'ta': 'Noto Sans Tamil, sans-serif',
            'zh': 'Noto Sans SC, sans-serif',
            'ja': 'Noto Sans JP, sans-serif',
            'ar': 'Noto Sans Arabic, sans-serif',
            'hi': 'Noto Sans Devanagari, sans-serif'
        }
        
        return font_families.get(language, 'system-ui, sans-serif')
