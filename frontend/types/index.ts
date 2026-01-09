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






