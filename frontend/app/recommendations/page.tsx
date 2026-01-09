"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  MapPin,
  Star,
  Plus,
  Filter,
  Compass,
  Building2,
  UtensilsCrossed,
  Calendar,
  MessageCircle,
  Wifi,
  Droplets,
  Dumbbell,
  Waves,
  Coffee,
  Flame,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { useAuthStore } from "@/store/auth-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Attraction, Hotel, Restaurant } from "@/types";

type FilterType = "for-you" | "attractions" | "stays" | "dining" | "events";

export default function RecommendationsPage() {
  const { currentLanguage } = useLanguageStore();
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [activeFilter, setActiveFilter] = React.useState<FilterType>("for-you");
  const [selectedCity, setSelectedCity] = React.useState("Kandy");
  const [selectedInterests, setSelectedInterests] = React.useState<string[]>(["Nature", "History"]);

  const userId = user?.id || "anonymous";

  // Generate session ID for recommendations
  const sessionId = React.useMemo(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("rec_session_id");
      if (stored) return stored;
      const newId = `rec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("rec_session_id", newId);
      return newId;
    }
    return `rec_${Date.now()}`;
  }, []);

  // Fetch personalized recommendations
  const { data: recommendations, isLoading: isLoadingRecs } = useQuery({
    queryKey: ["recommendations", userId, selectedCity, selectedInterests, sessionId],
    queryFn: async () => {
      try {
        // Use the POST endpoint with proper format
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/recommendations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId !== "anonymous" ? userId : null,
            session_id: sessionId,
            resource_type: null,
            context: {
              city: selectedCity,
              interests: selectedInterests,
            },
            limit: 20,
          }),
        });
        
        if (!response.ok) {
          throw new Error("Failed to fetch recommendations");
        }
        
        const data = await response.json();
        return data;
      } catch (error) {
        console.error("Failed to fetch recommendations:", error);
        return null;
      }
    },
    enabled: activeFilter === "for-you",
  });

  // Fetch attractions
  const { data: attractions, isLoading: isLoadingAttractions } = useQuery({
    queryKey: ["attractions-recommendations", selectedCity],
    queryFn: async () => {
      try {
        const response = await apiClient.attractions.list({
          city: selectedCity,
          limit: 10,
        } as any);
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch attractions:", error);
        return [];
      }
    },
    enabled: activeFilter === "attractions" || activeFilter === "for-you",
  });

  // Fetch hotels
  const { data: hotels, isLoading: isLoadingHotels } = useQuery({
    queryKey: ["hotels-recommendations", selectedCity],
    queryFn: async () => {
      try {
        const response = await apiClient.hotels.list({
          city: selectedCity,
          limit: 10,
        } as any);
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch hotels:", error);
        return [];
      }
    },
    enabled: activeFilter === "stays" || activeFilter === "for-you",
  });

  // Fetch restaurants
  const { data: restaurants, isLoading: isLoadingRestaurants } = useQuery({
    queryKey: ["restaurants-recommendations", selectedCity],
    queryFn: async () => {
      try {
        const response = await apiClient.restaurants.list({
          city: selectedCity,
          limit: 10,
        } as any);
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch restaurants:", error);
        return [];
      }
    },
    enabled: activeFilter === "dining" || activeFilter === "for-you",
  });

  // Calculate match percentage (mock for now, would come from ML in production)
  const calculateMatch = (item: any, interests: string[]) => {
    // Simple mock calculation based on category matching
    const baseMatch = 80 + Math.floor(Math.random() * 20);
    return Math.min(99, baseMatch);
  };

  // Get tags for attractions
  const getAttractionTags = (attraction: Attraction) => {
    const category = attraction.category?.toLowerCase() || "";
    const tags: string[] = [];
    
    if (category.includes("temple") || category.includes("cultural")) {
      tags.push("CULTURE", "SPIRITUALITY");
    }
    if (category.includes("nature") || category.includes("garden")) {
      tags.push("NATURE", "RELAXING");
    }
    if (category.includes("fortress") || category.includes("historical")) {
      tags.push("HISTORY", "HIKING");
    }
    if (category.includes("beach")) {
      tags.push("BEACH", "RELAXING");
    }
    
    return tags.length > 0 ? tags : ["TOURISM"];
  };

  const userName = user?.full_name || user?.username || "Traveler";
  const userInterests = selectedInterests.join(" and ");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative h-[400px] md:h-[500px] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=1920&q=80"
            alt="Sri Lanka Tea Plantations"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/30 to-black/60" />
        </div>
        
        <div className="relative z-10 h-full flex flex-col justify-center px-4 md:px-8 lg:px-12">
          <div className="max-w-4xl">
            <Badge className="mb-4 bg-white/20 text-white border-white/30 backdrop-blur-sm">
              <Sparkles className="w-3 h-3 mr-1" />
              AI Curated
            </Badge>
            
            <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white mb-4">
              Top picks for your trip to {selectedCity}, {userName}
            </h1>
            
            <p className="text-lg md:text-xl text-white/90 mb-6 max-w-2xl">
              Personalized for you based on your interest in {userInterests}
            </p>
            
            <Button
              onClick={() => router.push("/dashboard/settings")}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 text-base"
            >
              <Filter className="w-4 h-4 mr-2" />
              Refine Preferences
            </Button>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 px-4 md:px-8 lg:px-12 py-3 md:py-4">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          {[
            { id: "for-you", label: "For You", icon: Sparkles },
            { id: "attractions", label: "Attractions", icon: Compass },
            { id: "stays", label: "Stays", icon: Building2 },
            { id: "dining", label: "Dining", icon: UtensilsCrossed },
            { id: "events", label: "Events", icon: Calendar },
          ].map((filter) => {
            const Icon = filter.icon;
            const isActive = activeFilter === filter.id;
            return (
              <button
                key={filter.id}
                onClick={() => setActiveFilter(filter.id as FilterType)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? "bg-black text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                <Icon className="w-4 h-4" />
                {filter.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="px-4 md:px-8 lg:px-12 py-6 md:py-8 space-y-10 md:space-y-12">
        {/* Must-Visit Attractions */}
        {(activeFilter === "for-you" || activeFilter === "attractions") && (
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl md:text-3xl font-bold">Must-Visit Attractions</h2>
              <Link href="/explore/attractions">
                <Button variant="ghost" className="text-blue-600">
                  View All →
                </Button>
              </Link>
            </div>

            {isLoadingAttractions ? (
              <div className="flex gap-4 overflow-x-auto pb-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="min-w-[320px] bg-gray-200 animate-pulse rounded-lg h-96" />
                ))}
              </div>
            ) : (
              <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
                {attractions?.slice(0, 4).map((attraction: Attraction, idx: number) => {
                  const match = calculateMatch(attraction, selectedInterests);
                  const tags = getAttractionTags(attraction);
                  
                  return (
                    <div
                      key={attraction.id}
                      className="min-w-[320px] md:min-w-[360px] bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow"
                    >
                      <div className="relative h-48">
                        {attraction.images?.[0]?.url ? (
                          <Image
                            src={attraction.images[0].url}
                            alt={getLocalizedText(attraction.name, currentLanguage) || "Attraction"}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="h-full w-full bg-gradient-to-br from-teal-200 to-blue-200 flex items-center justify-center">
                            <Compass className="w-12 h-12 text-teal-600" />
                          </div>
                        )}
                        <div className="absolute top-3 left-3">
                          <Badge className="bg-white text-gray-900 font-semibold">
                            {match}% Match
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="p-4">
                        <div className="flex flex-wrap gap-1 mb-2">
                          {tags.map((tag, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                        
                        <h3 className="font-bold text-lg mb-1 line-clamp-1">
                          {getLocalizedText(attraction.name, currentLanguage)}
                        </h3>
                        
                        <div className="flex items-center text-sm text-gray-600 mb-2">
                          <MapPin className="w-4 h-4 mr-1" />
                          {attraction.location?.city || attraction.location?.province || "Sri Lanka"}
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                          {getLocalizedText(attraction.description, currentLanguage)}
                        </p>
                        
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            className="flex-1 text-blue-600 border-blue-600"
                            onClick={() => router.push(`/explore/attractions/${attraction.id}`)}
                          >
                            Details
                          </Button>
                          <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
                            <Plus className="w-4 h-4 mr-1" />
                            Add
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {/* Discover More Card */}
                <div className="min-w-[320px] md:min-w-[360px] bg-white rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center hover:border-blue-500 transition-colors cursor-pointer">
                  <div className="text-center p-8">
                    <Compass className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 font-medium">Discover More Attractions</p>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Stays You'll Love */}
        {(activeFilter === "for-you" || activeFilter === "stays") && (
          <section>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl md:text-3xl font-bold">Stays You'll Love</h2>
                <Badge className="bg-orange-100 text-orange-700 border-orange-300">
                  High Demand
                </Badge>
              </div>
              <Link href="/explore/hotels">
                <Button variant="ghost" className="text-blue-600">
                  View All →
                </Button>
              </Link>
            </div>

            {isLoadingHotels ? (
              <div className="flex gap-4 overflow-x-auto pb-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="min-w-[320px] bg-gray-200 animate-pulse rounded-lg h-96" />
                ))}
              </div>
            ) : (
              <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
                {hotels?.slice(0, 3).map((hotel: Hotel, idx: number) => {
                  const match = calculateMatch(hotel, selectedInterests);
                  const priceRange = hotel.price_per_night
                    ? `$${Math.round(hotel.price_per_night)}/night`
                    : "$100-200/night";
                  const hotelType = hotel.star_rating
                    ? `${getHotelType(hotel)} ${"$".repeat(Math.ceil((hotel.price_per_night || 100) / 100))}`
                    : "Hotel $$";
                  
                  return (
                    <div
                      key={hotel.id}
                      className="min-w-[320px] md:min-w-[360px] bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow"
                    >
                      <div className="relative h-48">
                        {hotel.images?.[0]?.url ? (
                          <Image
                            src={hotel.images[0].url}
                            alt={getLocalizedText(hotel.name, currentLanguage) || "Hotel"}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="h-full w-full bg-gradient-to-br from-blue-200 to-purple-200 flex items-center justify-center">
                            <Building2 className="w-12 h-12 text-blue-600" />
                          </div>
                        )}
                        <div className="absolute top-3 left-3">
                          <Badge className="bg-white text-gray-900 font-semibold">
                            {match}% Match
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <Badge variant="outline" className="text-xs">
                            {hotelType}
                          </Badge>
                          {hotel.star_rating && (
                            <div className="flex items-center gap-1">
                              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-sm font-medium">
                                {typeof hotel.star_rating === "number" 
                                  ? hotel.star_rating.toFixed(1) 
                                  : hotel.star_rating}
                              </span>
                            </div>
                          )}
                        </div>
                        
                        <h3 className="font-bold text-lg mb-2 line-clamp-1">
                          {getLocalizedText(hotel.name, currentLanguage)}
                        </h3>
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          {hotel.amenities?.slice(0, 2).map((amenity, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {getAmenityIcon(amenity)}
                              {amenity}
                            </Badge>
                          ))}
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-lg font-bold text-gray-900">{priceRange}</span>
                          <Button className="bg-blue-600 hover:bg-blue-700">
                            <Plus className="w-4 h-4 mr-1" />
                            Add
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {/* Authentic Dining */}
        {(activeFilter === "for-you" || activeFilter === "dining") && (
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl md:text-3xl font-bold">Authentic Dining</h2>
              <Link href="/explore/restaurants">
                <Button variant="ghost" className="text-blue-600">
                  View All →
                </Button>
              </Link>
            </div>

            {isLoadingRestaurants ? (
              <div className="flex gap-4 overflow-x-auto pb-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="min-w-[280px] bg-gray-200 animate-pulse rounded-lg h-64" />
                ))}
              </div>
            ) : (
              <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
                {restaurants?.slice(0, 4).map((restaurant: Restaurant, idx: number) => {
                  const match = calculateMatch(restaurant, selectedInterests);
                  const priceRange = restaurant.price_range || "$";
                  const cuisineType = restaurant.cuisine_type || "Local";
                  
                  return (
                    <div
                      key={restaurant.id}
                      className="min-w-[280px] md:min-w-[300px] bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow"
                    >
                      <div className="relative h-40">
                        {restaurant.images?.[0]?.url ? (
                          <Image
                            src={restaurant.images[0].url}
                            alt={getLocalizedText(restaurant.name, currentLanguage) || "Restaurant"}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="h-full w-full bg-gradient-to-br from-orange-200 to-red-200 flex items-center justify-center">
                            <UtensilsCrossed className="w-10 h-10 text-orange-600" />
                          </div>
                        )}
                        <div className="absolute top-2 right-2">
                          <Badge className="bg-white text-gray-900 font-semibold text-xs">
                            {match}% Match for you
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="p-4">
                        <Badge variant="outline" className="mb-2 text-xs">
                          {cuisineType} {priceRange}
                        </Badge>
                        
                        <h3 className="font-bold text-base mb-1 line-clamp-1">
                          {getLocalizedText(restaurant.name, currentLanguage)}
                        </h3>
                        
                        {restaurant.rating && (
                          <div className="flex items-center gap-1 mb-2">
                            <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                            <span className="text-xs text-gray-600">{restaurant.rating.toFixed(1)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}
      </div>

      {/* Floating AI Assistant Button */}
      <Link href="/chat">
        <button className="fixed bottom-4 right-4 md:bottom-6 md:right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3 md:p-4 shadow-lg hover:shadow-xl transition-all z-50 group">
          <MessageCircle className="w-5 h-5 md:w-6 md:h-6" />
          <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-sm px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            Ask AI Assistant
          </span>
          <span className="sr-only">Ask AI Assistant</span>
        </button>
      </Link>
    </div>
  );
}

// Helper functions
function getHotelType(hotel: Hotel): string {
  if (hotel.star_rating && hotel.star_rating >= 4.5) return "Luxury Resort";
  if (hotel.star_rating && hotel.star_rating >= 4) return "Boutique Hotel";
  return "Modern Hotel";
}

function getAmenityIcon(amenity: string): React.ReactNode {
  const lower = amenity.toLowerCase();
  if (lower.includes("wifi") || lower.includes("wi-fi")) return <Wifi className="w-3 h-3 mr-1 inline" />;
  if (lower.includes("pool")) return <Waves className="w-3 h-3 mr-1 inline" />;
  if (lower.includes("spa")) return <Droplets className="w-3 h-3 mr-1 inline" />;
  if (lower.includes("gym") || lower.includes("fitness")) return <Dumbbell className="w-3 h-3 mr-1 inline" />;
  return null;
}
