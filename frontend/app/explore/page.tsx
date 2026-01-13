"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  MapPin,
  Star,
  Heart,
  ChevronDown,
  MessageCircle,
  Moon,
  Building2,
  TreePine,
  Umbrella,
  Mountain,
  Landmark,
  Hotel as HotelIcon,
  UtensilsCrossed,
  Calendar,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText } from "@/lib/i18n";
import { getImageUrl, getFallbackImageUrl } from "@/lib/image-utils";
import apiClient from "@/lib/api-client";
import type { Attraction, Hotel, Restaurant, Event } from "@/types";

type Category = "all" | "historical" | "wildlife" | "beaches" | "adventure" | "cultural";
type ExploreType = "attractions" | "hotels" | "restaurants" | "events";

const categories = [
  { id: "all", label: "All", icon: null },
  { id: "historical", label: "Historical", icon: Building2 },
  { id: "wildlife", label: "Wildlife", icon: TreePine },
  { id: "beaches", label: "Beaches", icon: Umbrella },
  { id: "adventure", label: "Adventure", icon: Mountain },
];

const exploreTabs = [
  { id: "attractions", label: "Attractions", icon: Landmark, path: "/explore" },
  { id: "hotels", label: "Hotels", icon: HotelIcon, path: "/explore/hotels" },
  { id: "restaurants", label: "Restaurants", icon: UtensilsCrossed, path: "/explore/restaurants" },
  { id: "events", label: "Events", icon: Calendar, path: "/explore/events" },
];

export default function ExplorePage() {
  const { currentLanguage } = useLanguageStore();
  const router = useRouter();
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<Category>("all");
  const [selectedLocation, setSelectedLocation] = React.useState("any");
  const [selectedRating, setSelectedRating] = React.useState("any");
  const [displayLimit, setDisplayLimit] = React.useState(6);
  const [favorites, setFavorites] = React.useState<Set<string>>(new Set());

  // Determine current explore type from pathname
  const currentType: ExploreType = React.useMemo(() => {
    if (pathname.includes("/hotels")) return "hotels";
    if (pathname.includes("/restaurants")) return "restaurants";
    if (pathname.includes("/events")) return "events";
    return "attractions";
  }, [pathname]);

  // Fetch data based on current type
  const { data, isLoading, refetch, error } = useQuery({
    queryKey: [currentType, selectedCategory, selectedLocation, selectedRating, currentLanguage, displayLimit],
    queryFn: async () => {
      try {
        const params: any = {
          limit: displayLimit,
          language: currentLanguage,
        };

        if (selectedLocation !== "any") {
          params.city = selectedLocation;
        }

        if (currentType === "attractions") {
          if (selectedCategory !== "all") {
            params.category = selectedCategory;
          }
          const response = await apiClient.attractions.list(params);
          return response.data || [];
        } else if (currentType === "hotels") {
          if (selectedRating !== "any") {
            params.star_rating = parseInt(selectedRating);
          }
          const response = await apiClient.hotels.list(params);
          return response.data || [];
        } else if (currentType === "restaurants") {
          if (selectedCategory !== "all") {
            params.cuisine_type = selectedCategory;
          }
          const response = await apiClient.restaurants.list(params);
          return response.data || [];
        } else if (currentType === "events") {
          if (selectedCategory !== "all") {
            params.category = selectedCategory;
          }
          const response = await apiClient.events.list(params);
          return response.data || [];
        }
        return [];
      } catch (error: any) {
        console.error(`Failed to fetch ${currentType}:`, error);
        if (error?.code === "ERR_NETWORK" || error?.message === "Network Error") {
          console.warn("Network error - API may be unavailable. Using fallback data.");
          return [];
        }
        throw error;
      }
    },
    enabled: true,
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000,
  });

  // Search data based on current type
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: [`${currentType}-search`, searchQuery, currentLanguage],
    queryFn: async () => {
      if (!searchQuery.trim()) return null;
      try {
        if (currentType === "attractions") {
          const response = await apiClient.attractions.search({
            q: searchQuery,
            category: selectedCategory !== "all" ? selectedCategory : undefined,
            language: currentLanguage,
            limit: 50,
          } as any);
          return response.data || [];
        } else if (currentType === "hotels") {
          const response = await apiClient.hotels.search({
            city: selectedLocation !== "any" ? selectedLocation : undefined,
          } as any);
          return response.data || [];
        } else if (currentType === "restaurants") {
          const response = await apiClient.restaurants.search({
            q: searchQuery,
            city: selectedLocation !== "any" ? selectedLocation : undefined,
          } as any);
          return response.data || [];
        } else if (currentType === "events") {
          const response = await apiClient.events.search({
            q: searchQuery,
            city: selectedLocation !== "any" ? selectedLocation : undefined,
          } as any);
          return response.data || [];
        }
        return [];
      } catch (error: any) {
        console.error(`Failed to search ${currentType}:`, error);
        if (error?.code === "ERR_NETWORK" || error?.message === "Network Error") {
          console.warn("Network error during search - API may be unavailable.");
          return [];
        }
        return [];
      }
    },
    enabled: searchQuery.trim().length > 0,
    retry: 1,
    retryDelay: 500,
  });

  const items: (Attraction | Hotel | Restaurant | Event)[] = searchQuery.trim() ? (searchResults || []) : (data || []);
  const totalResults = items.length || 0;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    refetch();
  };

  const toggleFavorite = (attractionId: string) => {
    setFavorites((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(attractionId)) {
        newSet.delete(attractionId);
      } else {
        newSet.add(attractionId);
      }
      return newSet;
    });
  };

  const getCategoryBadge = (category: string) => {
    const categoryMap: Record<string, string> = {
      historical: "HISTORICAL",
      heritage: "HISTORICAL",
      wildlife: "WILDLIFE",
      beaches: "BEACHES",
      beach: "BEACHES",
      cultural: "CULTURAL",
      adventure: "ADVENTURE",
    };
    return categoryMap[category?.toLowerCase() || ""] || "ATTRACTION";
  };

  const formatRating = (rating?: number, reviews?: number) => {
    if (!rating) return "4.8 (2.1k)";
    const formattedReviews = reviews
      ? reviews >= 1000
        ? `${(reviews / 1000).toFixed(1)}k`
        : reviews.toString()
      : "2.1k";
    return `${rating.toFixed(1)} (${formattedReviews})`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Error Banner */}
      {error && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="max-w-7xl mx-auto flex">
            <div className="flex-shrink-0">
              <MessageCircle className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>Connection Issue:</strong> Unable to connect to the server. 
                Please check your internet connection or try again later.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="relative h-[500px] md:h-[600px] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=1920&q=80"
            alt="Sri Lanka Tea Plantations"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60" />
        </div>

        <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 text-center">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4">
            Discover the Wonder of Asia
          </h1>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl mb-8">
            Explore ancient ruins, endless beaches, and the timeless culture of Sri Lanka
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="w-full max-w-3xl">
            <div className="flex gap-2 bg-white rounded-lg p-2 shadow-lg">
              <div className="flex-1 flex items-center">
                <Search className="w-5 h-5 text-gray-400 ml-3" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search attractions, cities..."
                  className="flex-1 px-4 py-3 outline-none text-gray-900"
                />
              </div>
              <Button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg"
              >
                Search
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* Tabs and Filter Bar */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-8 lg:px-12 py-4">
        <div className="max-w-7xl mx-auto">
          {/* Tabs */}
          <div className="flex items-center gap-2 mb-4 border-b border-gray-200">
            {exploreTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = pathname === tab.path || (tab.path === "/explore" && pathname === "/explore");
              return (
                <Link
                  key={tab.id}
                  href={tab.path}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                    isActive
                      ? "border-blue-600 text-blue-600"
                      : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
                  }`}
                >
                  {Icon && <Icon className="w-4 h-4" />}
                  {tab.label}
                </Link>
              );
            })}
          </div>

          {/* Filters */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            {/* Left: Categories */}
            {currentType === "attractions" && (
              <div className="flex items-center gap-4 flex-wrap">
                <span className="text-sm font-medium text-gray-700">Categories:</span>
                <div className="flex gap-2 flex-wrap">
                  {categories.map((category) => {
                    const Icon = category.icon;
                    const isActive = selectedCategory === category.id;
                    return (
                      <button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.id as Category)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                          isActive
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                        }`}
                      >
                        {Icon && <Icon className="w-4 h-4" />}
                        {category.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Right: Filters */}
            <div className="flex gap-3">
              <div className="relative">
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="any">Any Location</option>
                  <option value="Colombo">Colombo</option>
                  <option value="Kandy">Kandy</option>
                  <option value="Galle">Galle</option>
                  <option value="Sigiriya">Sigiriya</option>
                  <option value="Ella">Ella</option>
                  <option value="Matale">Matale</option>
                </select>
                <MapPin className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {(currentType === "attractions" || currentType === "hotels") && (
                <div className="relative">
                  <select
                    value={selectedRating}
                    onChange={(e) => setSelectedRating(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="any">{currentType === "hotels" ? "Any Stars" : "Any Rating"}</option>
                    <option value="4.5">4.5+ {currentType === "hotels" ? "Stars" : "Stars"}</option>
                    <option value="4.0">4.0+ {currentType === "hotels" ? "Stars" : "Stars"}</option>
                    <option value="3.5">3.5+ {currentType === "hotels" ? "Stars" : "Stars"}</option>
                  </select>
                  <Star className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="px-4 md:px-8 lg:px-12 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              {currentType === "attractions" && "Popular Destinations"}
              {currentType === "hotels" && "Hotels"}
              {currentType === "restaurants" && "Restaurants"}
              {currentType === "events" && "Events"}
            </h2>
            <p className="text-gray-600 text-sm md:text-base">
              Showing {items.length} of {totalResults} results
            </p>
          </div>

          {isLoading || isSearching ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm animate-pulse">
                  <div className="h-48 bg-gray-200 rounded-t-xl" />
                  <div className="p-4 space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                    <div className="h-3 bg-gray-200 rounded w-full" />
                  </div>
                </div>
              ))}
            </div>
          ) : error && items.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Unable to Load {currentType.charAt(0).toUpperCase() + currentType.slice(1)}
              </h3>
              <p className="text-gray-600 mb-4">
                There was a problem connecting to the server. Please check your connection and try again.
              </p>
              <Button onClick={() => refetch()} variant="outline">
                Retry
              </Button>
            </div>
          ) : items.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <p className="text-gray-500">No {currentType} found. Try adjusting your filters.</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {items.slice(0, displayLimit).map((item) => {
                  const isFavorite = favorites.has(item.id);
                  let name: any, description: any, location: any, images: any;
                  let detailPath = "";
                  let badgeText = "";

                  if (currentType === "attractions") {
                    const attraction = item as Attraction;
                    name = attraction.name;
                    description = attraction.description;
                    location = attraction.location;
                    images = attraction.images;
                    badgeText = getCategoryBadge(attraction.category || "historical");
                    detailPath = `/explore/attractions/${attraction.id}`;
                  } else if (currentType === "hotels") {
                    const hotel = item as Hotel;
                    name = hotel.name;
                    description = hotel.description;
                    location = hotel.location;
                    images = hotel.images;
                    badgeText = `${hotel.star_rating || 0} Stars`;
                    detailPath = `/explore/hotels/${hotel.id}`;
                  } else if (currentType === "restaurants") {
                    const restaurant = item as Restaurant;
                    name = restaurant.name;
                    description = restaurant.description;
                    location = restaurant.location;
                    images = restaurant.images;
                    badgeText = restaurant.cuisine_type || "RESTAURANT";
                    detailPath = `/explore/restaurants/${restaurant.id}`;
                  } else if (currentType === "events") {
                    const event = item as Event;
                    name = event.name;
                    description = event.description;
                    location = event.location;
                    images = event.images;
                    badgeText = event.category || "EVENT";
                    detailPath = `/explore/events/${event.id}`;
                  }

                  const imageUrl = getImageUrl(images?.[0]) || getFallbackImageUrl(currentType, item.id);
                  const itemName = getLocalizedText(name, currentLanguage) || currentType.slice(0, -1);

                  return (
                    <div
                      key={item.id}
                      className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
                    >
                      {/* Image */}
                      <div className="relative h-48">
                        <Image
                          src={imageUrl}
                          alt={itemName}
                          fill
                          className="object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            const parent = target.parentElement;
                            if (parent && !parent.querySelector('.image-placeholder')) {
                              const placeholder = document.createElement('div');
                              placeholder.className = 'image-placeholder h-full w-full bg-gradient-to-br from-teal-200 to-blue-200 flex items-center justify-center';
                              placeholder.innerHTML = '<span class="text-gray-400 text-sm">Image unavailable</span>';
                              parent.appendChild(placeholder);
                            }
                          }}
                        />

                        {/* Badge */}
                        <div className="absolute top-3 left-3">
                          <Badge className="bg-teal-500 text-white font-semibold text-xs">
                            {badgeText}
                          </Badge>
                        </div>

                        {/* Favorite Button */}
                        <button
                          onClick={() => toggleFavorite(item.id)}
                          className="absolute top-3 right-3 p-2 bg-white/90 hover:bg-white rounded-full transition-colors"
                          aria-label="Toggle favorite"
                        >
                          <Heart
                            className={`w-5 h-5 ${
                              isFavorite ? "fill-red-500 text-red-500" : "text-gray-600"
                            }`}
                          />
                        </button>
                      </div>

                      {/* Content */}
                      <div className="p-4">
                        <h3 className="text-lg font-bold mb-1 line-clamp-1">
                          {itemName}
                        </h3>

                        <div className="flex items-center text-sm text-gray-600 mb-2">
                          <MapPin className="w-4 h-4 mr-1" />
                          {location?.city || "Sri Lanka"}
                        </div>

                        {(currentType === "attractions" || currentType === "hotels" || currentType === "restaurants") && (
                          <div className="flex items-center gap-1 mb-3">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium text-gray-700">
                              {currentType === "attractions" 
                                ? formatRating((item as Attraction).average_rating, (item as Attraction).total_reviews)
                                : currentType === "hotels"
                                ? `${(item as Hotel).star_rating || 0} Stars`
                                : `${(item as Restaurant).rating || 0} Stars`
                              }
                            </span>
                          </div>
                        )}

                        {currentType === "hotels" && (item as Hotel).price_per_night && (
                          <div className="text-sm font-semibold text-blue-600 mb-2">
                            LKR {(item as Hotel).price_per_night}/night
                          </div>
                        )}

                        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                          {getLocalizedText(description, currentLanguage)}
                        </p>

                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            className="flex-1 border-blue-600 text-blue-600 hover:bg-blue-50"
                            onClick={() => router.push(detailPath)}
                          >
                            Details
                          </Button>
                          <Button
                            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                            onClick={() =>
                              router.push(
                                `/chat?query=${encodeURIComponent(itemName)}`
                              )
                            }
                          >
                            <MessageCircle className="w-4 h-4 mr-2" />
                            Ask Chatbot
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Load More Button */}
              {items.length >= displayLimit && (
                <div className="text-center mt-8">
                  <Button
                    variant="outline"
                    onClick={() => setDisplayLimit((prev) => prev + 6)}
                    className="px-6"
                  >
                    Load More {currentType.charAt(0).toUpperCase() + currentType.slice(1)}
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Floating Chat Assistant Button */}
      <Link href="/chat">
        <button className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-3 shadow-lg hover:shadow-xl transition-all z-50 flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          <span className="hidden sm:inline">Chat Assistant</span>
        </button>
      </Link>
    </div>
  );
}
