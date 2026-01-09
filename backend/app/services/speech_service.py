"""
Speech service for voice interactions
"""

import asyncio
import tempfile
import os
from typing import Optional
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechService:
    """Speech service for voice-to-text and text-to-voice"""
    
    def __init__(self):
        self.google_credentials = settings.GOOGLE_APPLICATION_CREDENTIALS
        self.google_speech_api_key = settings.GOOGLE_SPEECH_API_KEY
        self.google_tts_api_key = settings.GOOGLE_TTS_API_KEY
        self.supported_languages = {
            'en': 'en-US',
            'si': 'si-LK',  # Sinhala (Sri Lanka)
            'ta': 'ta-LK',  # Tamil (Sri Lanka)
            'de': 'de-DE',
            'fr': 'fr-FR',
            'zh': 'zh-CN',
            'ja': 'ja-JP'
        }
    
    async def speech_to_text(self, audio_data: bytes, language: Optional[str] = None) -> Optional[str]:
        """Convert speech to text using Google Cloud Speech-to-Text"""
        
        if not self.google_credentials:
            logger.warning("Google Cloud credentials not configured, using fallback")
            return await self._fallback_speech_to_text(audio_data)
        
        try:
            from google.cloud import speech
            
            # Initialize client
            client = speech.SpeechClient()
            
            # Configure recognition
            language_code = self.supported_languages.get(language, 'en-US')
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=language_code,
                alternative_language_codes=[
                    'en-US', 'si-LK', 'ta-LK'  # Enable multilingual detection
                ],
                enable_automatic_punctuation=True,
                model='latest_long'
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Perform recognition
            response = client.recognize(config=config, audio=audio)
            
            # Extract text from response
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                logger.info(f"Speech recognition successful: confidence={confidence}")
                return transcript.strip()
            
            return None
            
        except ImportError:
            logger.warning("Google Cloud Speech library not installed, using fallback")
            return await self._fallback_speech_to_text(audio_data)
        except Exception as e:
            logger.error(f"Speech-to-text error: {str(e)}")
            return await self._fallback_speech_to_text(audio_data)
    
    async def text_to_speech(self, text: str, language: str = 'en') -> Optional[bytes]:
        """Convert text to speech using Google Cloud Text-to-Speech"""
        
        if not self.google_credentials:
            logger.warning("Google Cloud credentials not configured, using fallback")
            return await self._fallback_text_to_speech(text, language)
        
        try:
            from google.cloud import texttospeech
            
            # Initialize client
            client = texttospeech.TextToSpeechClient()
            
            # Configure synthesis
            language_code = self.supported_languages.get(language, 'en-US')
            
            # Select voice based on language
            voice_names = {
                'en-US': 'en-US-Neural2-F',  # Female neural voice
                'si-LK': 'si-LK-Standard-A',
                'ta-LK': 'ta-LK-Standard-A',
                'de-DE': 'de-DE-Neural2-F',
                'fr-FR': 'fr-FR-Neural2-A',
                'zh-CN': 'zh-CN-Neural2-A',
                'ja-JP': 'ja-JP-Neural2-B'
            }
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_names.get(language_code, 'en-US-Neural2-F')
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Synthesize speech
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except ImportError:
            logger.warning("Google Cloud Text-to-Speech library not installed, using fallback")
            return await self._fallback_text_to_speech(text, language)
        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            return await self._fallback_text_to_speech(text, language)
    
    async def _fallback_speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Fallback speech-to-text using local libraries"""
        try:
            import speech_recognition as sr
            import io
            import wave
            
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Initialize recognizer
                recognizer = sr.Recognizer()
                
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    audio = recognizer.record(source)
                
                # Try Google Web Speech API (free tier)
                try:
                    text = recognizer.recognize_google(audio, language='en-US')
                    return text
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition request error: {e}")
                    return None
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except ImportError:
            logger.error("speech_recognition library not installed")
            return None
        except Exception as e:
            logger.error(f"Fallback speech-to-text error: {str(e)}")
            return None
    
    async def _fallback_text_to_speech(self, text: str, language: str = 'en') -> Optional[bytes]:
        """Fallback text-to-speech using gTTS"""
        try:
            from gtts import gTTS
            import io
            
            # Map language codes
            gtts_languages = {
                'en': 'en',
                'si': 'si',
                'ta': 'ta',
                'de': 'de',
                'fr': 'fr',
                'zh': 'zh',
                'ja': 'ja'
            }
            
            gtts_lang = gtts_languages.get(language, 'en')
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except ImportError:
            logger.error("gTTS library not installed")
            return None
        except Exception as e:
            logger.error(f"Fallback text-to-speech error: {str(e)}")
            return None
    
    async def analyze_audio_sentiment(self, audio_data: bytes) -> dict:
        """Analyze sentiment from audio (placeholder for advanced feature)"""
        # This would involve:
        # 1. Converting audio to features (pitch, tone, speed)
        # 2. Using ML models to detect emotions
        # 3. Returning sentiment analysis
        
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "emotions": {
                "happy": 0.3,
                "sad": 0.2,
                "angry": 0.1,
                "neutral": 0.4
            }
        }
    
    def get_supported_languages(self) -> dict:
        """Get supported languages for speech services"""
        return {
            code: {
                "code": code,
                "google_code": google_code,
                "name": self._get_language_name(code)
            }
            for code, google_code in self.supported_languages.items()
        }
    
    def _get_language_name(self, code: str) -> str:
        """Get language name from code"""
        names = {
            'en': 'English',
            'si': 'Sinhala',
            'ta': 'Tamil',
            'de': 'German',
            'fr': 'French',
            'zh': 'Chinese',
            'ja': 'Japanese'
        }
        return names.get(code, code)
    
    async def validate_audio_format(self, audio_data: bytes) -> bool:
        """Validate audio format and quality"""
        try:
            # Basic validation - check if audio data is not empty
            if not audio_data or len(audio_data) < 1000:  # At least 1KB
                return False
            
            # Could add more sophisticated validation:
            # - Check audio format headers
            # - Validate sample rate
            # - Check duration limits
            
            return True
            
        except Exception as e:
            logger.error(f"Audio validation error: {str(e)}")
            return False
