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
  ChevronDown,
  UtensilsCrossed,
  MessageCircle,
  Wifi,
  Building2,
  Check,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Restaurant } from "@/types";

type SortOption = "recommended" | "lowest-price" | "highest-rated";
type CuisineType = "sri_lankan" | "indian" | "chinese" | "italian" | "seafood";

export default function RestaurantsPage() {
  const { currentLanguage } = useLanguageStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [locationInput, setLocationInput] = React.useState("");
  const [selectedCuisine, setSelectedCuisine] = React.useState<CuisineType>("sri_lankan");
  const [priceRange, setPriceRange] = React.useState([1000, 8000]);
  const [dietaryFeatures, setDietaryFeatures] = React.useState<string[]>(["veg", "halal"]);
  const [sortBy, setSortBy] = React.useState<SortOption>("recommended");
  const [displayLimit, setDisplayLimit] = React.useState(6);

  // Fetch restaurants
  const { data, isLoading } = useQuery({
    queryKey: ["restaurants", locationInput, selectedCuisine, priceRange, sortBy, displayLimit, currentLanguage],
    queryFn: async () => {
      try {
        const params: any = {
          limit: displayLimit,
          language: currentLanguage,
        };

        if (locationInput.trim()) {
          params.city = locationInput.trim();
        }

        if (selectedCuisine) {
          params.cuisine_type = selectedCuisine;
        }

        const response = await apiClient.restaurants.list(params);
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch restaurants:", error);
        return [];
      }
    },
  });

  const restaurants: Restaurant[] = data || [];
  const totalResults = 42;

  // Filter by price and dietary features (client-side)
  const filteredRestaurants = React.useMemo(() => {
    let filtered = [...restaurants];

    // Filter by price (mock for now - would need price data from backend)
    // This is a placeholder - actual filtering would use restaurant.price_range

    // Sort
    if (sortBy === "lowest-price") {
      filtered.sort((a, b) => {
        const priceA = getPriceValue(a.price_range || "$");
        const priceB = getPriceValue(b.price_range || "$");
        return priceA - priceB;
      });
    } else if (sortBy === "highest-rated") {
      filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    }

    return filtered;
  }, [restaurants, priceRange, sortBy]);

  const getPriceValue = (priceRange: string) => {
    const priceMap: Record<string, number> = {
      $: 1,
      $$: 2,
      $$$: 3,
      $$$$: 4,
    };
    return priceMap[priceRange] || 2;
  };

  const toggleDietaryFeature = (feature: string) => {
    setDietaryFeatures((prev) => {
      if (prev.includes(feature)) {
        return prev.filter((f) => f !== feature);
      }
      return [...prev, feature];
    });
  };

  const formatPriceRange = (range?: string) => {
    return range || "$$";
  };

  const formatReviews = (count?: number) => {
    if (!count) return "1.2k";
    return count >= 1000 ? `${(count / 1000).toFixed(1)}k` : count.toString();
  };

  const cuisines = [
    { id: "sri_lankan", label: "Sri Lankan" },
    { id: "indian", label: "Indian" },
    { id: "chinese", label: "Chinese" },
    { id: "italian", label: "Italian/Western" },
    { id: "seafood", label: "Seafood" },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Trigger search
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative h-[400px] md:h-[500px] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="https://images.unsplash.com/photo-1555939594-58d7cb561b1e?w=1920&q=80"
            alt="Sri Lankan Food"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-black/60" />
        </div>

        <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 text-center">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4">
            Taste the Spice of Sri Lanka
          </h1>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl mb-8">
            Discover authentic flavors, from street food kottu to fine dining seafood
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
                  placeholder="Find kottu, seafood, or spicy curries..."
                  className="flex-1 px-4 py-3 outline-none text-gray-900"
                />
              </div>
              <Button
                type="submit"
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg"
              >
                Search
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-4 md:px-8 lg:px-12 py-8">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1 space-y-6">
            {/* Location */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <div className="flex items-center gap-2 mb-3">
                <MapPin className="w-5 h-5 text-gray-600" />
                <h3 className="font-semibold text-gray-900">Location</h3>
              </div>
              <input
                type="text"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                placeholder="Colombo, Kandy, Galle..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              />
            </div>

            {/* Cuisine */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Cuisine</h3>
              <div className="space-y-2">
                {cuisines.map((cuisine) => {
                  const isSelected = selectedCuisine === cuisine.id;
                  return (
                    <label
                      key={cuisine.id}
                      className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <div className="relative">
                        <input
                          type="radio"
                          name="cuisine"
                          checked={isSelected}
                          onChange={() => setSelectedCuisine(cuisine.id as CuisineType)}
                          className="w-4 h-4 text-green-600 focus:ring-green-500"
                        />
                        {isSelected && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <Check className="w-3 h-3 text-green-600" />
                          </div>
                        )}
                      </div>
                      <span className="text-sm text-gray-700">{cuisine.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Price Range */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Price Range</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>{priceRange[0] / 1000}k</span>
                  <span>{priceRange[1] / 1000}k</span>
                </div>
                <input
                  type="range"
                  min="1000"
                  max="8000"
                  value={priceRange[1]}
                  onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
                />
                <p className="text-xs text-gray-500 text-center">LKR</p>
              </div>
            </div>

            {/* Dietary & Features */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Dietary & Features</h3>
              <div className="flex flex-wrap gap-2">
                {[
                  { id: "veg", label: "Veg" },
                  { id: "halal", label: "Halal" },
                  { id: "wifi", label: "Wifi" },
                  { id: "outdoor", label: "Outdoor" },
                ].map((feature) => {
                  const isSelected = dietaryFeatures.includes(feature.id);
                  return (
                    <button
                      key={feature.id}
                      onClick={() => toggleDietaryFeature(feature.id)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        isSelected
                          ? "bg-green-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {feature.id === "outdoor" && <Building2 className="w-3 h-3 inline mr-1" />}
                      {feature.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Section - Restaurant Listings */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                <span className="font-semibold text-gray-900">{filteredRestaurants.length}</span> restaurants nearby
              </p>
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="recommended">Recommended</option>
                  <option value="lowest-price">Lowest Price</option>
                  <option value="highest-rated">Highest Rated</option>
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* Restaurant Cards */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-xl shadow-sm animate-pulse">
                    <div className="h-48 bg-gray-200 rounded-t-xl" />
                    <div className="p-4 space-y-3">
                      <div className="h-4 bg-gray-200 rounded w-3/4" />
                      <div className="h-3 bg-gray-200 rounded w-1/2" />
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredRestaurants.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <p className="text-gray-500">No restaurants found. Try adjusting your filters.</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredRestaurants.slice(0, displayLimit).map((restaurant) => {
                    const priceRangeStr = formatPriceRange(restaurant.price_range);
                    const hasMenu = Math.random() > 0.5; // Random for demo
                    
                    return (
                      <div
                        key={restaurant.id}
                        className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
                      >
                        {/* Image */}
                        <div className="relative h-48">
                          {restaurant.images?.[0]?.url ? (
                            <Image
                              src={restaurant.images[0].url}
                              alt={getLocalizedText(restaurant.name, currentLanguage) || "Restaurant"}
                              fill
                              className="object-cover"
                            />
                          ) : (
                            <div className="h-full w-full bg-gradient-to-br from-orange-200 to-red-200" />
                          )}
                        </div>

                        {/* Content */}
                        <div className="p-4">
                          <div className="flex items-center gap-1 mb-2">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium text-gray-900">
                              {restaurant.rating?.toFixed(1) || "4.5"}
                            </span>
                            <span className="text-sm text-gray-500">
                              ({formatReviews(restaurant.total_reviews)} reviews)
                            </span>
                          </div>

                          <h3 className="text-lg font-bold mb-1 line-clamp-1">
                            {getLocalizedText(restaurant.name, currentLanguage)}
                          </h3>

                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm font-semibold text-gray-700">{priceRangeStr}</span>
                            <span className="text-gray-400">•</span>
                            <span className="text-sm text-gray-600">{restaurant.cuisine_type || "Sri Lankan"}</span>
                          </div>

                          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                            {getLocalizedText(restaurant.description, currentLanguage)}
                          </p>

                          <div className="flex items-center text-sm text-gray-600 mb-4">
                            <MapPin className="w-4 h-4 mr-1" />
                            {restaurant.location?.city || restaurant.location?.address || "Sri Lanka"}
                          </div>

                          <Button
                            className="w-full bg-green-600 hover:bg-green-700 text-white"
                            onClick={() => router.push(`/explore/restaurants/${restaurant.id}`)}
                          >
                            {hasMenu ? "View Menu" : "Reserve"}
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Show More Button */}
                {filteredRestaurants.length >= displayLimit && (
                  <div className="text-center mt-8">
                    <Button
                      variant="outline"
                      onClick={() => setDisplayLimit((prev) => prev + 6)}
                      className="px-6"
                    >
                      Show More Restaurants
                      <ChevronDown className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Floating AI Assistant Button */}
      <Link href="/chat">
        <button className="fixed bottom-6 right-6 bg-green-600 hover:bg-green-700 text-white rounded-lg p-4 shadow-lg hover:shadow-xl transition-all z-50">
          <MessageCircle className="w-6 h-6" />
          <span className="sr-only">Ask AI Assistant</span>
        </button>
      </Link>
    </div>
  );
}
