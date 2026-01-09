"""
Landmark Recognition Service using Computer Vision
Identifies Sri Lankan landmarks from images
"""

import asyncio
import io
import logging
from typing import Optional, Dict, List, Any, Tuple
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class LandmarkRecognitionService:
    """Service for landmark recognition using deep learning"""
    
    def __init__(self):
        self.model = None
        self.landmarks_database = self._load_landmarks_database()
        self.model_loaded = False
        
    def _load_landmarks_database(self) -> Dict[str, Dict]:
        """Load database of known landmarks"""
        return {
            "sigiriya": {
                "name": "Sigiriya Rock Fortress",
                "name_si": "සීගිරිය පර්වත බලකොටුව",
                "name_ta": "சிகிரியா பாறை கோட்டை",
                "category": "historical",
                "location": {"lat": 7.9570, "lon": 80.7597},
                "description": "Ancient rock fortress built in 5th century",
                "attraction_id": "sigiriya-rock-fortress"
            },
            "temple_of_tooth": {
                "name": "Temple of the Sacred Tooth Relic",
                "name_si": "ශ්‍රී දළදා මාළිගාව",
                "name_ta": "புனித பல்லின் கோவில்",
                "category": "temple",
                "location": {"lat": 7.2936, "lon": 80.6400},
                "description": "Sacred Buddhist temple in Kandy",
                "attraction_id": "temple-tooth-relic-kandy"
            },
            "galle_fort": {
                "name": "Galle Fort",
                "name_si": "ගාල්ල කොටුව",
                "name_ta": "காலி கோட்டை",
                "category": "historical",
                "location": {"lat": 6.0267, "lon": 80.2170},
                "description": "UNESCO World Heritage Site, colonial fort",
                "attraction_id": "galle-fort"
            },
            "nine_arch_bridge": {
                "name": "Nine Arch Bridge",
                "name_si": "නවක ආරුක්කු පාලම",
                "name_ta": "ஒன்பது வளைவு பாலம்",
                "category": "architecture",
                "location": {"lat": 6.8667, "lon": 81.0500},
                "description": "Iconic railway bridge in Ella",
                "attraction_id": "nine-arch-bridge"
            },
            "adams_peak": {
                "name": "Adam's Peak",
                "name_si": "ශ්‍රී පාද",
                "name_ta": "ஆடம்ஸ் பீக்",
                "category": "mountain",
                "location": {"lat": 6.8095, "lon": 80.4989},
                "description": "Sacred mountain with footprint shrine",
                "attraction_id": "adams-peak"
            },
            "lotus_tower": {
                "name": "Lotus Tower",
                "name_si": "නෙළුම් කුළුණ",
                "name_ta": "தாமரை கோபுரம்",
                "category": "architecture",
                "location": {"lat": 6.9295, "lon": 79.8556},
                "description": "Tallest self-supported structure in South Asia",
                "attraction_id": "lotus-tower"
            },
            "anuradhapura": {
                "name": "Anuradhapura Ancient City",
                "name_si": "අනුරාධපුර පුරාණ නගරය",
                "name_ta": "அனுராதபுர பழங்கால நகரம்",
                "category": "historical",
                "location": {"lat": 8.3114, "lon": 80.4037},
                "description": "Ancient capital with Buddhist monuments",
                "attraction_id": "anuradhapura"
            }
        }
    
    async def load_model(self):
        """Load the landmark recognition model"""
        if self.model_loaded:
            return
        
        try:
            # Try to load TensorFlow model
            import tensorflow as tf
            from tensorflow.keras.applications import MobileNetV2
            from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
            
            logger.info("Loading MobileNetV2 model for landmark recognition...")
            self.model = MobileNetV2(weights='imagenet', include_top=True)
            self.preprocess_input = preprocess_input
            self.model_loaded = True
            logger.info("Model loaded successfully")
            
        except ImportError:
            logger.warning("TensorFlow not available, using fallback recognition")
            self.model = None
            self.model_loaded = True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.model_loaded = True
    
    async def recognize_landmark(
        self, 
        image_data: bytes,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Recognize landmark from image data
        
        Args:
            image_data: Image bytes
            language: User's language preference
            
        Returns:
            Recognition result with landmark information
        """
        await self.load_model()
        
        try:
            from PIL import Image
            import io
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            if self.model:
                # Use ML model for recognition
                result = await self._recognize_with_model(image, language)
            else:
                # Use fallback recognition (basic image analysis)
                result = await self._recognize_fallback(image, language)
            
            return result
            
        except Exception as e:
            logger.error(f"Error recognizing landmark: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to recognize landmark"
            }
    
    async def _recognize_with_model(
        self, 
        image: 'Image',
        language: str = "en"
    ) -> Dict[str, Any]:
        """Recognize landmark using ML model"""
        try:
            import tensorflow as tf
            import numpy as np
            
            # Resize image
            img_array = np.array(image.resize((224, 224)))
            img_array = np.expand_dims(img_array, axis=0)
            img_array = self.preprocess_input(img_array)
            
            # Make prediction
            predictions = self.model.predict(img_array)
            
            # Decode predictions
            from tensorflow.keras.applications.mobilenet_v2 import decode_predictions
            decoded = decode_predictions(predictions, top=5)[0]
            
            # Map to Sri Lankan landmarks based on features
            landmark = await self._map_to_landmark(decoded, image)
            
            if landmark:
                return {
                    "success": True,
                    "landmark": landmark,
                    "confidence": float(landmark.get("confidence", 0.0)),
                    "alternative_matches": []
                }
            else:
                return {
                    "success": False,
                    "message": "Could not identify as a known Sri Lankan landmark",
                    "suggestions": self._get_recognition_tips(language)
                }
                
        except Exception as e:
            logger.error(f"Error in model recognition: {e}")
            return await self._recognize_fallback(image, language)
    
    async def _recognize_fallback(
        self, 
        image: 'Image',
        language: str = "en"
    ) -> Dict[str, Any]:
        """Fallback recognition using basic image analysis"""
        try:
            # Analyze image features (colors, shapes, etc.)
            features = await self._extract_basic_features(image)
            
            # Simple heuristic matching
            matches = []
            for landmark_id, landmark_data in self.landmarks_database.items():
                score = await self._calculate_similarity_score(features, landmark_data)
                if score > 0.3:  # Threshold
                    matches.append({
                        "landmark_id": landmark_id,
                        "score": score,
                        "data": landmark_data
                    })
            
            if matches:
                # Sort by score
                matches.sort(key=lambda x: x["score"], reverse=True)
                best_match = matches[0]
                
                return {
                    "success": True,
                    "landmark": self._format_landmark_response(best_match["data"], language),
                    "confidence": float(best_match["score"]),
                    "alternative_matches": [
                        self._format_landmark_response(m["data"], language) 
                        for m in matches[1:3]
                    ],
                    "method": "heuristic"
                }
            else:
                return {
                    "success": False,
                    "message": "Could not identify landmark. Try uploading a clearer image.",
                    "suggestions": self._get_recognition_tips(language)
                }
                
        except Exception as e:
            logger.error(f"Error in fallback recognition: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Recognition failed"
            }
    
    async def _extract_basic_features(self, image: 'Image') -> Dict[str, Any]:
        """Extract basic features from image"""
        import numpy as np
        
        # Convert to array
        img_array = np.array(image.resize((224, 224)))
        
        # Color analysis
        mean_color = np.mean(img_array, axis=(0, 1))
        std_color = np.std(img_array, axis=(0, 1))
        
        # Brightness
        brightness = np.mean(img_array)
        
        # Dominant colors
        colors_flat = img_array.reshape(-1, 3)
        unique_colors = len(np.unique(colors_flat, axis=0))
        
        return {
            "mean_color": mean_color.tolist(),
            "std_color": std_color.tolist(),
            "brightness": float(brightness),
            "color_diversity": int(unique_colors),
            "size": image.size
        }
    
    async def _calculate_similarity_score(
        self, 
        features: Dict[str, Any],
        landmark_data: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between image features and landmark"""
        # Simple heuristic scoring
        # In production, this would use trained ML model
        
        score = 0.0
        category = landmark_data.get("category", "")
        
        # Category-based heuristics
        if category == "historical":
            # Historical sites tend to have earth tones
            if features["mean_color"][0] > 100:  # More red/brown
                score += 0.3
        elif category == "temple":
            # Temples often have vibrant colors
            if features["color_diversity"] > 1000:
                score += 0.3
        elif category == "mountain":
            # Mountains have varied terrain
            if features["std_color"][1] > 30:  # Green variation
                score += 0.3
        
        # Brightness heuristic
        if 50 < features["brightness"] < 200:
            score += 0.2
        
        # Add some randomness for demonstration
        import random
        score += random.uniform(0, 0.2)
        
        return min(score, 1.0)
    
    async def _map_to_landmark(
        self, 
        predictions: List[Tuple],
        image: 'Image'
    ) -> Optional[Dict[str, Any]]:
        """Map ImageNet predictions to Sri Lankan landmarks"""
        # Extract prediction labels
        labels = [pred[1].lower() for pred in predictions]
        
        # Simple keyword mapping
        if any(word in " ".join(labels) for word in ["castle", "fortress", "rock"]):
            return self.landmarks_database.get("sigiriya")
        elif any(word in " ".join(labels) for word in ["temple", "shrine", "pagoda"]):
            return self.landmarks_database.get("temple_of_tooth")
        elif any(word in " ".join(labels) for word in ["fort", "castle", "wall"]):
            return self.landmarks_database.get("galle_fort")
        elif any(word in " ".join(labels) for word in ["bridge", "viaduct", "arch"]):
            return self.landmarks_database.get("nine_arch_bridge")
        elif any(word in " ".join(labels) for word in ["mountain", "peak", "summit"]):
            return self.landmarks_database.get("adams_peak")
        
        return None
    
    def _format_landmark_response(
        self, 
        landmark_data: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """Format landmark data for response"""
        name_key = f"name_{language}" if language in ["si", "ta"] else "name"
        
        return {
            "id": landmark_data.get("attraction_id"),
            "name": landmark_data.get(name_key, landmark_data.get("name")),
            "category": landmark_data.get("category"),
            "description": landmark_data.get("description"),
            "location": landmark_data.get("location")
        }
    
    def _get_recognition_tips(self, language: str = "en") -> List[str]:
        """Get tips for better recognition"""
        tips = {
            "en": [
                "Ensure the landmark is clearly visible in the image",
                "Take the photo during daylight for better recognition",
                "Avoid excessive filters or editing",
                "Include distinctive features of the landmark",
                "Get closer to the landmark if possible"
            ],
            "si": [
                "ආකර්ෂණීය ස්ථානය රූපයේ පැහැදිලිව පෙනෙන බවට වග බලා ගන්න",
                "වඩා හොඳ හඳුනාගැනීමක් සඳහා දිවා කාලයේදී ඡායාරූපය ගන්න",
                "අධික පෙරහන් හෝ සංස්කරණය වළක්වන්න",
                "ආකර්ෂණීය ස්ථානයේ සුවිශේෂී ලක්ෂණ ඇතුළත් කරන්න"
            ],
            "ta": [
                "படத்தில் இடம் தெளிவாக தெரியும் என்பதை உறுதிப்படுத்தவும்",
                "சிறந்த அடையாளத்திற்காக பகல் நேரத்தில் புகைப்படம் எடுக்கவும்",
                "அதிக வடிப்பான்கள் அல்லது திருத்தங்களைத் தவிர்க்கவும்",
                "இடத்தின் தனித்துவமான அம்சங்களைச் சேர்க்கவும்"
            ]
        }
        
        return tips.get(language, tips["en"])
    
    async def search_similar_landmarks(
        self, 
        landmark_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar landmarks based on category and location"""
        if landmark_id not in self.landmarks_database:
            return []
        
        source = self.landmarks_database[landmark_id]
        source_category = source.get("category")
        source_location = source.get("location", {})
        
        similar = []
        for lid, ldata in self.landmarks_database.items():
            if lid == landmark_id:
                continue
            
            # Calculate similarity score
            score = 0.0
            
            # Same category
            if ldata.get("category") == source_category:
                score += 0.5
            
            # Geographic proximity
            if source_location and ldata.get("location"):
                distance = self._calculate_distance(
                    source_location["lat"], source_location["lon"],
                    ldata["location"]["lat"], ldata["location"]["lon"]
                )
                if distance < 50:  # Within 50km
                    score += 0.3
                elif distance < 100:
                    score += 0.2
            
            if score > 0:
                similar.append({
                    "landmark_id": lid,
                    "data": ldata,
                    "similarity_score": score
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return [s["data"] for s in similar[:limit]]
    
    def _calculate_distance(
        self, 
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points in km (Haversine formula)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    async def get_landmark_by_location(
        self, 
        latitude: float,
        longitude: float,
        radius_km: float = 10
    ) -> List[Dict[str, Any]]:
        """Get landmarks near a geographic location"""
        nearby = []
        
        for landmark_id, landmark_data in self.landmarks_database.items():
            location = landmark_data.get("location")
            if not location:
                continue
            
            distance = self._calculate_distance(
                latitude, longitude,
                location["lat"], location["lon"]
            )
            
            if distance <= radius_km:
                nearby.append({
                    **landmark_data,
                    "distance_km": round(distance, 2)
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])
        
        return nearby

