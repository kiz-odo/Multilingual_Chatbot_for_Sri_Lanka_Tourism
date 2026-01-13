"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Heart,
  MapPin,
  Star,
  Trash2,
  Search,
  Building2,
  TreePine,
  Umbrella,
  Mountain,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";
import type { Attraction } from "@/types";

export default function BookmarksPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [filterType, setFilterType] = React.useState<"all" | "attractions" | "hotels" | "restaurants">("all");

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  // Fetch user favorites/bookmarks
  const { data: favoritesData, isLoading } = useQuery({
    queryKey: ["user-favorites", user?.id],
    queryFn: async () => {
      if (!isAuthenticated || !user) return { attractions: [], hotels: [], restaurants: [] };
      try {
        const response = await apiClient.users.getMe();
        const userData = response.data;
        
        // Fetch favorite attractions
        const attractions = userData.favorite_attractions || [];
        const attractionsData = await Promise.all(
          attractions.map(async (id: string) => {
            try {
              const res = await apiClient.attractions.get(id);
              return res.data;
            } catch {
              return null;
            }
          })
        );

        return {
          attractions: attractionsData.filter(Boolean),
          hotels: [],
          restaurants: [],
        };
      } catch (error) {
        console.error("Failed to fetch favorites:", error);
        return { attractions: [], hotels: [], restaurants: [] };
      }
    },
    enabled: isAuthenticated && !!user,
  });

  // Remove from favorites mutation
  const removeFavoriteMutation = useMutation({
    mutationFn: async (attractionId: string) => {
      await apiClient.users.removeFavoriteAttraction(attractionId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-favorites", user?.id] });
      addToast({
        title: "Success",
        description: "Removed from favorites",
        variant: "success",
      });
    },
    onError: () => {
      addToast({
        title: "Error",
        description: "Failed to remove from favorites",
        variant: "error",
      });
    },
  });

  const handleRemoveFavorite = (id: string) => {
    if (confirm("Remove from favorites?")) {
      removeFavoriteMutation.mutate(id);
    }
  };

  // Filter favorites
  const filteredFavorites = React.useMemo(() => {
    let items: any[] = [];
    
    if (filterType === "all" || filterType === "attractions") {
      items = [...items, ...(favoritesData?.attractions || []).map((a: Attraction) => ({ ...a, type: "attraction" }))];
    }
    if (filterType === "all" || filterType === "hotels") {
      items = [...items, ...(favoritesData?.hotels || []).map((h: any) => ({ ...h, type: "hotel" }))];
    }
    if (filterType === "all" || filterType === "restaurants") {
      items = [...items, ...(favoritesData?.restaurants || []).map((r: any) => ({ ...r, type: "restaurant" }))];
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      items = items.filter((item) => {
        const name = item.name?.toLowerCase() || "";
        const city = item.city?.toLowerCase() || "";
        return name.includes(query) || city.includes(query);
      });
    }

    return items;
  }, [favoritesData, filterType, searchQuery]);

  if (!isAuthenticated) {
    return null;
  }

  const getCategoryIcon = (category: string) => {
    const categoryMap: Record<string, any> = {
      historical: Building2,
      wildlife: TreePine,
      beaches: Umbrella,
      adventure: Mountain,
    };
    return categoryMap[category?.toLowerCase() || ""] || MapPin;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button variant="ghost" onClick={() => router.back()} className="p-2">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Bookmarks</h1>
              <p className="text-gray-600 mt-1">
                Your saved places and favorites
              </p>
            </div>
          </div>

          {/* Search and Filter */}
          <div className="flex gap-4 mt-6">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search bookmarks..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div className="flex gap-2">
              {(["all", "attractions", "hotels", "restaurants"] as const).map((type) => (
                <Button
                  key={type}
                  variant={filterType === type ? "default" : "outline"}
                  onClick={() => setFilterType(type)}
                  size="sm"
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Bookmarks Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
          </div>
        ) : filteredFavorites.length === 0 ? (
          <Card className="p-12 text-center">
            <CardContent>
              <div className="flex flex-col items-center">
                <Heart className="w-16 h-16 text-gray-300 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {searchQuery ? "No bookmarks found" : "No bookmarks yet"}
                </h3>
                <p className="text-gray-600 mb-6">
                  {searchQuery
                    ? "Try adjusting your search query"
                    : "Start exploring and save your favorite places"}
                </p>
                {!searchQuery && (
                  <Link href="/explore">
                    <Button className="bg-teal-500 hover:bg-teal-600 text-white">
                      Explore Attractions
                    </Button>
                  </Link>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredFavorites.map((item: any) => {
              const CategoryIcon = getCategoryIcon(item.category);
              
              return (
                <Card key={item.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-0">
                    {/* Image */}
                    <div className="relative h-48 rounded-t-lg overflow-hidden bg-gradient-to-br from-teal-400 to-blue-500">
                      {item.images?.[0]?.url ? (
                        <Image
                          src={item.images[0].url}
                          alt={item.name || "Bookmark"}
                          fill
                          className="object-cover"
                        />
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <CategoryIcon className="w-16 h-16 text-white/30" />
                        </div>
                      )}
                      <Badge className="absolute top-3 right-3 bg-white/90 text-gray-900">
                        {item.type === "attraction" ? "Attraction" : item.type}
                      </Badge>
                    </div>

                    {/* Content */}
                    <div className="p-6 space-y-3">
                      <h3 className="text-lg font-bold text-gray-900 line-clamp-2">
                        {item.name || "Untitled"}
                      </h3>

                      {item.city && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <MapPin className="w-4 h-4" />
                          <span>{item.city}</span>
                        </div>
                      )}

                      {item.rating && (
                        <div className="flex items-center gap-2 text-sm">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium">{item.rating.toFixed(1)}</span>
                          {item.reviews && (
                            <span className="text-gray-500">({item.reviews})</span>
                          )}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                        <Link href={`/explore/attractions/${item.id}`}>
                          <Button variant="ghost" size="sm">
                            View Details
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveFavorite(item.id)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}


