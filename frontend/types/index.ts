export type Language = "en" | "si" | "ta" | "de" | "fr" | "zh" | "ja";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role?: string;
  preferences?: {
    preferred_language?: Language;
    interests?: string[];
  };
  avatar?: string;
}

export interface ChatMessage {
  id: string;
  message: string;
  response: string;
  language: Language;
  intent?: string;
  confidence?: number;
  entities?: Array<{
    entity: string;
    value: string;
    start: number;
    end: number;
  }>;
  suggestions?: string[];
  multimedia?: Array<{
    type: string;
    url?: string;
    coordinates?: [number, number];
    zoom?: number;
  }>;
  timestamp: string;
  response_time_ms?: number;
}

export interface Attraction {
  id: string;
  name: {
    en: string;
    si?: string;
    ta?: string;
    [key: string]: string | undefined;
  };
  description: {
    en: string;
    si?: string;
    ta?: string;
    [key: string]: string | undefined;
  };
  category: string;
  location: {
    address: string;
    city: string;
    province: string;
    coordinates: [number, number];
  };
  is_featured?: boolean;
  popularity_score?: number;
  average_rating?: number;
  total_reviews?: number;
  estimated_visit_duration?: string;
  pricing?: Array<{
    category: string;
    price: number;
    currency: string;
  }>;
  images?: Array<{
    url: string;
    alt_text?: {
      en: string;
      si?: string;
      ta?: string;
    };
    is_primary?: boolean;
  }>;
}

export interface Hotel {
  id: string;
  name: {
    en: string;
    si?: string;
    ta?: string;
  };
  description: {
    en: string;
    si?: string;
    ta?: string;
  };
  location: {
    address: string;
    city: string;
    coordinates: [number, number];
  };
  star_rating?: number;
  price_per_night?: number;
  amenities?: string[];
  images?: Array<{
    url: string;
    alt_text?: string;
    is_primary?: boolean;
  }>;
}

export interface Restaurant {
  id: string;
  name: {
    en: string;
    si?: string;
    ta?: string;
  };
  description: {
    en: string;
    si?: string;
    ta?: string;
  };
  cuisine_type: string;
  location: {
    address: string;
    city: string;
    coordinates: [number, number];
  };
  price_range?: string;
  rating?: number;
  images?: Array<{
    url: string;
    alt_text?: string;
  }>;
}

export interface Event {
  id: string;
  name: {
    en: string;
    si?: string;
    ta?: string;
  };
  description: {
    en: string;
    si?: string;
    ta?: string;
  };
  category: string;
  start_date: string;
  end_date?: string;
  status?: "upcoming" | "ongoing" | "past" | "cancelled";
  location: {
    address: string;
    city: string;
    coordinates: [number, number];
  };
  images?: Array<{
    url: string;
    alt_text?: string;
  }>;
}

export interface Weather {
  city: string;
  temperature: number;
  feels_like?: number;
  humidity?: number;
  description: string;
  icon?: string;
  wind_speed?: number;
  visibility?: number;
  sunrise?: string;
  sunset?: string;
}

export interface WeatherForecast {
  city: string;
  forecast: Array<{
    date: string;
    temperature_high: number;
    temperature_low: number;
    description: string;
    icon?: string;
    precipitation_chance?: number;
  }>;
}

export interface CurrencyRate {
  from: string;
  to: string;
  rate: number;
  amount?: number;
  converted?: number;
  last_updated?: string;
}

export interface Itinerary {
  id: string;
  user_id: string;
  travel_dates: {
    start: string;
    end: string;
  };
  cities: string[];
  budget?: number;
  preferences?: string[];
  days: Array<{
    day: number;
    date: string;
    activities: Array<{
      time: string;
      title: string;
      description: string;
      location?: string;
      duration?: string;
      cost?: number;
    }>;
  }>;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContact {
  id: string;
  name: string;
  type: "police" | "medical" | "fire" | "tourist_police";
  phone: string;
  description?: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
  };
  request_id?: string;
  timestamp?: string;
}

// ============================================
// Additional Types for Missing Components
// ============================================

/**
 * Notification Types
 */
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  createdAt: Date;
  action?: {
    label: string;
    url: string;
  };
}

/**
 * Challenge/Gamification Types
 */
export interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'exploration' | 'social' | 'learning' | 'adventure';
  points: number;
  completed: boolean;
  progress: number;
  totalSteps: number;
  reward?: {
    type: 'badge' | 'points' | 'achievement';
    name: string;
    icon?: string;
  };
  startDate?: Date;
  endDate?: Date;
  createdAt: Date;
}

/**
 * Forum/Community Types
 */
export interface ForumPost {
  id: string;
  userId: string;
  author: {
    id: string;
    username: string;
    avatar?: string;
  };
  title: string;
  content: string;
  category?: string;
  tags?: string[];
  replies: ForumReply[];
  replyCount: number;
  viewCount: number;
  likeCount: number;
  isLiked?: boolean;
  isPinned?: boolean;
  isClosed?: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ForumReply {
  id: string;
  postId: string;
  userId: string;
  author: {
    id: string;
    username: string;
    avatar?: string;
  };
  content: string;
  likeCount: number;
  isLiked?: boolean;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Bookmark Types
 */
export type BookmarkType = 'attraction' | 'hotel' | 'restaurant' | 'event' | 'activity';

export interface Bookmark {
  id: string;
  itemId: string;
  type: BookmarkType;
  name: string;
  description?: string;
  image?: string;
  location?: {
    lat: number;
    lng: number;
    address: string;
  };
  rating?: number;
  tags?: string[];
  notes?: string;
  createdAt: Date;
}

/**
 * Trip Planning Types (Extended)
 */
export interface TripDestination {
  id: string;
  name: string;
  type: 'attraction' | 'hotel' | 'restaurant' | 'activity';
  location: {
    lat: number;
    lng: number;
    address: string;
  };
  duration?: number; // in hours
  cost?: number;
  notes?: string;
}

export interface TripDayPlan {
  day: number;
  date: Date;
  destinations: TripDestination[];
  totalCost: number;
  totalDuration: number;
}

export interface TripPlan {
  id: string;
  userId?: string;
  title: string;
  description?: string;
  destinations: string[]; // city names
  startDate: Date;
  endDate: Date;
  days: TripDayPlan[];
  budget: number;
  travelers: number;
  preferences: {
    interests?: string[];
    pace?: 'relaxed' | 'moderate' | 'fast';
    accommodation?: 'budget' | 'mid-range' | 'luxury';
  };
  status: 'draft' | 'planned' | 'active' | 'completed';
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Message/Conversation Types (Extended)
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  language?: Language;
  attachments?: {
    type: 'image' | 'audio' | 'file';
    url: string;
    name?: string;
  }[];
}

export interface Conversation {
  id: string;
  title: string;
  language: Language;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  lastMessage?: Message;
}

/**
 * Safety & Emergency Types (Extended)
 */
export interface SafetyTip {
  id: string;
  title: string;
  description: string;
  category: 'general' | 'health' | 'travel' | 'crime' | 'nature';
  priority: 'low' | 'medium' | 'high';
  region?: string;
  icon?: string;
}

export interface SOSAlert {
  id: string;
  userId: string;
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  type: 'medical' | 'security' | 'accident' | 'natural_disaster' | 'other';
  message?: string;
  status: 'active' | 'acknowledged' | 'resolved' | 'cancelled';
  createdAt: Date;
  resolvedAt?: Date;
}

/**
 * Recommendation Types
 */
export interface Recommendation {
  id: string;
  type: 'attraction' | 'hotel' | 'restaurant' | 'activity';
  item: Attraction | Hotel | Restaurant;
  score: number;
  reason: string;
  category?: string;
}

/**
 * Analytics Types
 */
export interface UserAnalytics {
  totalTrips: number;
  placesVisited: number;
  totalDistance: number;
  favoriteCategory?: string;
  mostVisitedCity?: string;
  averageTripDuration?: number;
  totalSpent?: number;
}

/**
 * Admin Types
 */
export interface AdminStatistics {
  totalUsers: number;
  activeUsers: number;
  totalConversations: number;
  totalMessages: number;
  totalTrips: number;
  totalFeedback: number;
  systemHealth: {
    status: 'healthy' | 'degraded' | 'down';
    uptime: number;
    latency: number;
  };
}

/**
 * Feedback Types
 */
export interface Feedback {
  id: string;
  userId: string;
  type: 'bug' | 'feature' | 'improvement' | 'other';
  subject: string;
  message: string;
  status: 'new' | 'in_progress' | 'resolved' | 'closed';
  priority?: 'low' | 'medium' | 'high';
  rating?: number;
  attachments?: string[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Transport Types
 */
export interface TransportOption {
  id: string;
  type: 'bus' | 'train' | 'taxi' | 'tuk-tuk' | 'rental' | 'flight';
  name: string;
  from: string;
  to: string;
  duration?: string;
  cost?: number;
  schedule?: string[];
  description?: string;
}

/**
 * Map/Location Types
 */
export interface MapLocation {
  lat: number;
  lng: number;
  name?: string;
  address?: string;
  placeId?: string;
}

export interface DirectionsResult {
  distance: string;
  duration: string;
  steps: Array<{
    instruction: string;
    distance: string;
    duration: string;
    startLocation: MapLocation;
    endLocation: MapLocation;
  }>;
  polyline?: string;
}

/**
 * Voice/Speech Types
 */
export interface VoiceRecording {
  id: string;
  audioBlob: Blob;
  duration: number;
  language?: Language;
  transcription?: string;
  timestamp: Date;
}

/**
 * Landmark Recognition Types
 */
export interface LandmarkRecognitionResult {
  id: string;
  name: string;
  confidence: number;
  description?: string;
  category?: string;
  location?: MapLocation;
  images?: string[];
  relatedAttractions?: string[];
}



