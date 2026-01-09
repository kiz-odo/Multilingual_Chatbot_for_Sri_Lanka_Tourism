"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
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
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Attraction } from "@/types";

type Category = "all" | "historical" | "wildlife" | "beaches" | "adventure" | "cultural";

const categories = [
  { id: "all", label: "All", icon: null },
  { id: "historical", label: "Historical", icon: Building2 },
  { id: "wildlife", label: "Wildlife", icon: TreePine },
  { id: "beaches", label: "Beaches", icon: Umbrella },
  { id: "adventure", label: "Adventure", icon: Mountain },
];

export default function ExplorePage() {
  const { currentLanguage } = useLanguageStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<Category>("all");
  const [selectedLocation, setSelectedLocation] = React.useState("any");
  const [selectedRating, setSelectedRating] = React.useState("any");
  const [displayLimit, setDisplayLimit] = React.useState(6);
  const [favorites, setFavorites] = React.useState<Set<string>>(new Set());

  // Fetch attractions
  const { data, isLoading, refetch, error } = useQuery({
    queryKey: ["attractions", selectedCategory, selectedLocation, selectedRating, currentLanguage, displayLimit],
    queryFn: async () => {
      try {
        const params: any = {
          limit: displayLimit,
          language: currentLanguage,
        };

        if (selectedCategory !== "all") {
          params.category = selectedCategory;
        }

        if (selectedLocation !== "any") {
          params.city = selectedLocation;
        }

        const response = await apiClient.attractions.list(params);
        return response.data || [];
      } catch (error: any) {
        console.error("Failed to fetch attractions:", error);
        
        // Return empty array on network error to prevent UI crash
        // The error will be handled by the error state below
        if (error?.code === "ERR_NETWORK" || error?.message === "Network Error") {
          console.warn("Network error - API may be unavailable. Using fallback data.");
          return [];
        }
        throw error;
      }
    },
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Search attractions
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ["attractions-search", searchQuery, currentLanguage],
    queryFn: async () => {
      if (!searchQuery.trim()) return null;
      try {
        const response = await apiClient.attractions.search({
          q: searchQuery,
          category: selectedCategory !== "all" ? selectedCategory : undefined,
          language: currentLanguage,
          limit: 50,
        } as any);
        return response.data || [];
      } catch (error: any) {
        console.error("Failed to search attractions:", error);
        // Return empty array on network error
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

  const attractions: Attraction[] = searchQuery.trim() ? (searchResults || []) : (data || []);
  const totalResults = 124; // This would come from backend in production

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

      {/* Top Header Bar */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-8 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Left: Logo */}
          <Link href="/" className="text-xl font-bold text-blue-600">
            Sri Lanka Tourism
          </Link>

          {/* Middle: Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              Home
            </Link>
            <Link
              href="/explore"
              className="text-blue-600 border-b-2 border-blue-600 pb-1 font-medium"
            >
              Attractions
            </Link>
            <Link href="/planner" className="text-gray-700 hover:text-blue-600 transition-colors">
              Plan Trip
            </Link>
            <Link href="/contact" className="text-gray-700 hover:text-blue-600 transition-colors">
              Contact
            </Link>
          </div>

          {/* Right: Dark Mode & Login */}
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Moon className="w-5 h-5 text-gray-600" />
            </button>
            <Link href="/auth/login">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                Login
              </Button>
            </Link>
          </div>
        </div>
      </div>

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

      {/* Category and Filter Bar */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-8 lg:px-12 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Left: Categories */}
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

            <div className="relative">
              <select
                value={selectedRating}
                onChange={(e) => setSelectedRating(e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="any">Any Rating</option>
                <option value="4.5">4.5+ Stars</option>
                <option value="4.0">4.0+ Stars</option>
                <option value="3.5">3.5+ Stars</option>
              </select>
              <Star className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>
      </div>

      {/* Popular Destinations Section */}
      <div className="px-4 md:px-8 lg:px-12 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Popular Destinations</h2>
            <p className="text-gray-600 text-sm md:text-base">
              Showing {attractions.length} of {totalResults} results
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
          ) : error && attractions.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Unable to Load Attractions
              </h3>
              <p className="text-gray-600 mb-4">
                There was a problem connecting to the server. Please check your connection and try again.
              </p>
              <Button onClick={() => refetch()} variant="outline">
                Retry
              </Button>
            </div>
          ) : attractions.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <p className="text-gray-500">No attractions found. Try adjusting your filters.</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {attractions.slice(0, displayLimit).map((attraction) => {
                  const categoryBadge = getCategoryBadge(attraction.category || "historical");
                  const isFavorite = favorites.has(attraction.id);

                  return (
                    <div
                      key={attraction.id}
                      className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
                    >
                      {/* Image */}
                      <div className="relative h-48">
                        {attraction.images?.[0]?.url ? (
                          <Image
                            src={attraction.images[0].url}
                            alt={getLocalizedText(attraction.name, currentLanguage) || "Attraction"}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="h-full w-full bg-gradient-to-br from-teal-200 to-blue-200" />
                        )}

                        {/* Category Badge */}
                        <div className="absolute top-3 left-3">
                          <Badge className="bg-teal-500 text-white font-semibold text-xs">
                            {categoryBadge}
                          </Badge>
                        </div>

                        {/* Favorite Button */}
                        <button
                          onClick={() => toggleFavorite(attraction.id)}
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
                          {getLocalizedText(attraction.name, currentLanguage)}
                        </h3>

                        <div className="flex items-center text-sm text-gray-600 mb-2">
                          <MapPin className="w-4 h-4 mr-1" />
                          {attraction.location?.city || attraction.location?.province || "Sri Lanka"}
                          {attraction.location?.district && `, ${attraction.location.district}`}
                        </div>

                        <div className="flex items-center gap-1 mb-3">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-medium text-gray-700">
                            {formatRating(attraction.average_rating, attraction.total_reviews)}
                          </span>
                        </div>

                        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                          {getLocalizedText(attraction.description, currentLanguage)}
                        </p>

                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            className="flex-1 border-blue-600 text-blue-600 hover:bg-blue-50"
                            onClick={() => router.push(`/explore/attractions/${attraction.id}`)}
                          >
                            Details
                          </Button>
                          <Button
                            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                            onClick={() =>
                              router.push(
                                `/chat?query=${encodeURIComponent(
                                  getLocalizedText(attraction.name, currentLanguage) || ""
                                )}`
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
              {attractions.length >= displayLimit && (
                <div className="text-center mt-8">
                  <Button
                    variant="outline"
                    onClick={() => setDisplayLimit((prev) => prev + 6)}
                    className="px-6"
                  >
                    Load More Attractions
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-blue-50 border-t border-blue-100 px-4 md:px-8 lg:px-12 py-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-green-500 rounded"></div>
            <span className="text-sm text-gray-700">© 2024 Sri Lanka Tourism</span>
          </div>
          <div className="flex gap-4 text-sm text-gray-600">
            <Link href="/privacy" className="hover:text-gray-900">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-gray-900">
              Terms & Conditions
            </Link>
          </div>
        </div>
      </footer>

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
