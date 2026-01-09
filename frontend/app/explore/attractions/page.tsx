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
  Building2,
  TreePine,
  Umbrella,
  Mountain,
  Filter,
  Grid,
  List,
  MessageCircle,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { useAuthStore } from "@/store/auth-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";
import type { Attraction } from "@/types";

type Category = "all" | "historical" | "wildlife" | "beaches" | "adventure" | "cultural";
type ViewMode = "grid" | "list";

const categories = [
  { id: "all", label: "All", icon: null },
  { id: "historical", label: "Historical", icon: Building2 },
  { id: "wildlife", label: "Wildlife", icon: TreePine },
  { id: "beaches", label: "Beaches", icon: Umbrella },
  { id: "adventure", label: "Adventure", icon: Mountain },
  { id: "cultural", label: "Cultural", icon: Building2 },
];

export default function AttractionsPage() {
  const { currentLanguage } = useLanguageStore();
  const { user, isAuthenticated } = useAuthStore();
  const { addToast } = useToast();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<Category>("all");
  const [selectedLocation, setSelectedLocation] = React.useState("any");
  const [selectedRating, setSelectedRating] = React.useState("any");
  const [displayLimit, setDisplayLimit] = React.useState(12);
  const [viewMode, setViewMode] = React.useState<ViewMode>("grid");
  const [favorites, setFavorites] = React.useState<Set<string>>(new Set());

  // Fetch user favorites
  React.useEffect(() => {
    if (isAuthenticated && user) {
      apiClient.users.getMe().then((response) => {
        const favoriteIds = response.data.favorite_attractions || [];
        setFavorites(new Set(favoriteIds));
      }).catch(() => {});
    }
  }, [isAuthenticated, user]);

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

  const toggleFavorite = async (attractionId: string) => {
    if (!isAuthenticated) {
      addToast({
        title: "Login Required",
        description: "Please login to save favorites",
        variant: "error",
      });
      router.push("/auth/login");
      return;
    }

    try {
      if (favorites.has(attractionId)) {
        await apiClient.users.removeFavoriteAttraction(attractionId);
        setFavorites((prev) => {
          const newSet = new Set(prev);
          newSet.delete(attractionId);
          return newSet;
        });
        addToast({
          title: "Removed",
          description: "Removed from favorites",
          variant: "success",
        });
      } else {
        await apiClient.users.addFavoriteAttraction(attractionId);
        setFavorites((prev) => new Set(prev).add(attractionId));
        addToast({
          title: "Added",
          description: "Added to favorites",
          variant: "success",
        });
      }
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
      addToast({
        title: "Error",
        description: "Failed to update favorites",
        variant: "error",
      });
    }
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
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                Attractions
              </h1>
              <p className="text-gray-600">
                Discover amazing places to visit in Sri Lanka
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant={viewMode === "grid" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("grid")}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("list")}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search attractions..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            {/* Category Filter */}
            <div className="flex gap-2">
              {categories.map((category) => {
                const Icon = category.icon;
                return (
                  <Button
                    key={category.id}
                    variant={selectedCategory === category.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedCategory(category.id as Category)}
                  >
                    {Icon && <Icon className="w-4 h-4 mr-2" />}
                    {category.label}
                  </Button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 md:px-8 py-8">
        {isLoading || isSearching ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500 mb-4"></div>
            <p className="text-gray-600">Loading attractions...</p>
          </div>
        ) : error && attractions.length === 0 ? (
          <div className="text-center py-12">
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
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No attractions found</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => {
                setSearchQuery("");
                setSelectedCategory("all");
                setSelectedLocation("any");
              }}
            >
              Clear Filters
            </Button>
          </div>
        ) : (
          <div
            className={
              viewMode === "grid"
                ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                : "space-y-4"
            }
          >
            {attractions.map((attraction) => (
              <Link
                key={attraction.id}
                href={`/explore/attractions/${attraction.id}`}
                className="group"
              >
                <div
                  className={`bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition-shadow ${
                    viewMode === "list" ? "flex gap-4" : ""
                  }`}
                >
                  {/* Image */}
                  <div
                    className={`relative ${
                      viewMode === "list" ? "w-48 h-48 flex-shrink-0" : "h-48"
                    } bg-gradient-to-br from-cyan-400 to-blue-500`}
                  >
                    {attraction.images?.[0]?.url ? (
                      <Image
                        src={attraction.images[0].url}
                        alt={getLocalizedText(attraction.name, currentLanguage) || "Attraction"}
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Building2 className="w-16 h-16 text-white/30" />
                      </div>
                    )}
                    <Badge className="absolute top-3 left-3 bg-white/90 text-gray-900">
                      {getCategoryBadge(attraction.category || "")}
                    </Badge>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        toggleFavorite(attraction.id);
                      }}
                      className="absolute top-3 right-3 p-2 bg-white/90 hover:bg-white rounded-full transition-colors"
                    >
                      <Heart
                        className={`w-5 h-5 ${
                          favorites.has(attraction.id)
                            ? "fill-red-500 text-red-500"
                            : "text-gray-600"
                        }`}
                      />
                    </button>
                  </div>

                  {/* Content */}
                  <div className="p-4 flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-cyan-600 transition-colors">
                      {getLocalizedText(attraction.name, currentLanguage) || "Attraction"}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <MapPin className="w-4 h-4" />
                      <span>{attraction.location?.city || "Unknown"}</span>
                    </div>
                    {attraction.average_rating && (
                      <div className="flex items-center gap-2 text-sm">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="font-medium">
                          {formatRating(attraction.average_rating, attraction.review_count)}
                        </span>
                      </div>
                    )}
                    {attraction.description && viewMode === "list" && (
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        {getLocalizedText(attraction.description, currentLanguage)}
                      </p>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Load More */}
        {!searchQuery && attractions.length > 0 && attractions.length >= displayLimit && (
          <div className="text-center mt-8">
            <Button
              variant="outline"
              onClick={() => setDisplayLimit((prev) => prev + 12)}
            >
              Load More Attractions
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

