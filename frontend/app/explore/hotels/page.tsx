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
  Calendar,
  Users,
  ChevronDown,
  Wifi,
  Droplets,
  Dumbbell,
  Waves,
  Car,
  Wind,
  MessageCircle,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Hotel } from "@/types";
import { format, addDays } from "date-fns";

type SortOption = "recommended" | "lowest-price" | "highest-rated";

export default function HotelsPage() {
  const { currentLanguage } = useLanguageStore();
  const router = useRouter();
  const [checkIn, setCheckIn] = React.useState(format(addDays(new Date(), 7), "yyyy-MM-dd"));
  const [checkOut, setCheckOut] = React.useState(format(addDays(new Date(), 10), "yyyy-MM-dd"));
  const [guests, setGuests] = React.useState({ adults: 2, rooms: 1 });
  const [priceRange, setPriceRange] = React.useState([50, 800]);
  const [selectedStars, setSelectedStars] = React.useState<number[]>([]);
  const [selectedAmenities, setSelectedAmenities] = React.useState<string[]>([]);
  const [sortBy, setSortBy] = React.useState<SortOption>("recommended");
  const [displayLimit, setDisplayLimit] = React.useState(6);
  const [favorites, setFavorites] = React.useState<Set<string>>(new Set());

  // Fetch hotels
  const { data, isLoading } = useQuery({
    queryKey: ["hotels", selectedStars, selectedAmenities, priceRange, sortBy, displayLimit, currentLanguage],
    queryFn: async () => {
      try {
        const params: any = {
          limit: displayLimit,
          language: currentLanguage,
        };

        if (selectedStars.length > 0) {
          // Filter by minimum star rating
          params.star_rating = Math.min(...selectedStars);
        }

        const response = await apiClient.hotels.list(params);
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch hotels:", error);
        return [];
      }
    },
  });

  const hotels: Hotel[] = data || [];
  const totalResults = 142;

  // Filter hotels by price and amenities (client-side for now)
  const filteredHotels = React.useMemo(() => {
    let filtered = [...hotels];

    // Filter by price
    filtered = filtered.filter((hotel) => {
      const price = hotel.price_per_night || 0;
      return price >= priceRange[0] && price <= priceRange[1];
    });

    // Filter by amenities
    if (selectedAmenities.length > 0) {
      filtered = filtered.filter((hotel) => {
        const hotelAmenities = (hotel.amenities || []).map((a) => a.toLowerCase());
        return selectedAmenities.every((amenity) =>
          hotelAmenities.some((h) => h.includes(amenity.toLowerCase()))
        );
      });
    }

    // Sort
    if (sortBy === "lowest-price") {
      filtered.sort((a, b) => (a.price_per_night || 0) - (b.price_per_night || 0));
    } else if (sortBy === "highest-rated") {
      filtered.sort((a, b) => (b.star_rating || 0) - (a.star_rating || 0));
    }

    return filtered;
  }, [hotels, priceRange, selectedAmenities, sortBy]);

  const toggleStar = (stars: number) => {
    setSelectedStars((prev) => {
      if (prev.includes(stars)) {
        return prev.filter((s) => s !== stars);
      }
      return [...prev, stars];
    });
  };

  const toggleAmenity = (amenity: string) => {
    setSelectedAmenities((prev) => {
      if (prev.includes(amenity)) {
        return prev.filter((a) => a !== amenity);
      }
      return [...prev, amenity];
    });
  };

  const toggleFavorite = (hotelId: string) => {
    setFavorites((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(hotelId)) {
        newSet.delete(hotelId);
      } else {
        newSet.add(hotelId);
      }
      return newSet;
    });
  };

  const getAmenityIcon = (amenity: string) => {
    const lower = amenity.toLowerCase();
    if (lower.includes("wifi") || lower.includes("wi-fi")) return <Wifi className="w-3 h-3" />;
    if (lower.includes("spa")) return <Droplets className="w-3 h-3" />;
    if (lower.includes("gym") || lower.includes("fitness")) return <Dumbbell className="w-3 h-3" />;
    if (lower.includes("pool")) return <Waves className="w-3 h-3" />;
    if (lower.includes("parking")) return <Car className="w-3 h-3" />;
    if (lower.includes("ac") || lower.includes("air")) return <Wind className="w-3 h-3" />;
    return null;
  };

  const formatPrice = (price?: number) => {
    if (!price) return "$150";
    return `$${Math.round(price)}`;
  };

  const calculateDiscount = (originalPrice: number, currentPrice: number) => {
    return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative h-[400px] md:h-[500px] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=1920&q=80"
            alt="Tropical Paradise"
            fill
            className="object-cover blur-sm"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60" />
        </div>

        <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 text-center">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4">
            Stay in Paradise
          </h1>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl mb-8">
            Find your perfect accommodation in Sri Lanka, from luxury resorts to cozy villas
          </p>

          {/* Search Widget */}
          <div className="bg-white rounded-lg shadow-xl p-4 md:p-6 flex flex-col md:flex-row gap-4 w-full max-w-4xl">
            <div className="flex items-center gap-3 flex-1">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <input
                  type="date"
                  value={checkIn}
                  onChange={(e) => setCheckIn(e.target.value)}
                  className="text-sm font-medium text-gray-900 outline-none"
                />
                <span className="mx-2 text-gray-400">-</span>
                <input
                  type="date"
                  value={checkOut}
                  onChange={(e) => setCheckOut(e.target.value)}
                  className="text-sm font-medium text-gray-900 outline-none"
                />
              </div>
            </div>

            <div className="flex items-center gap-3 flex-1">
              <Users className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">
                {guests.adults} Adults, {guests.rooms} Room
              </span>
            </div>

            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6">
              Search
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-4 md:px-8 lg:px-12 py-8">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1 space-y-6">
            {/* Map Section */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <div className="relative h-48 bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                <MapPin className="w-8 h-8 text-gray-400" />
                <span className="absolute bottom-2 left-2 text-xs text-gray-500">
                  Map View
                </span>
              </div>
              <Button variant="outline" className="w-full">
                <MapPin className="w-4 h-4 mr-2" />
                Show on map
              </Button>
            </div>

            {/* Price Range */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Price Range</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>${priceRange[0]}</span>
                  <span>${priceRange[1]}+</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="800"
                  value={priceRange[1]}
                  onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <p className="text-xs text-gray-500 text-center">Per night</p>
              </div>
            </div>

            {/* Star Rating */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Star Rating</h3>
              <div className="space-y-3">
                {[5, 4, 3].map((stars) => {
                  const isSelected = selectedStars.includes(stars);
                  const count = stars === 5 ? 124 : stars === 4 ? 45 : 23;
                  return (
                    <button
                      key={stars}
                      onClick={() => toggleStar(stars)}
                      className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-4 h-4 rounded-full border-2 ${
                            isSelected
                              ? "bg-blue-600 border-blue-600"
                              : "border-gray-300"
                          }`}
                        />
                        <div className="flex items-center gap-1">
                          {Array.from({ length: stars }).map((_, i) => (
                            <Star
                              key={i}
                              className="w-4 h-4 fill-yellow-400 text-yellow-400"
                            />
                          ))}
                          {stars < 5 && <span className="text-sm text-gray-600 ml-1">& Up</span>}
                        </div>
                      </div>
                      <span className="text-sm text-gray-500">({count})</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Amenities */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Amenities</h3>
              <div className="space-y-2">
                {["Wifi", "Spa", "Gym", "Pool", "Parking", "AC"].map((amenity) => {
                  const isSelected = selectedAmenities.includes(amenity);
                  return (
                    <label
                      key={amenity}
                      className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleAmenity(amenity)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{amenity}</span>
                    </label>
                  );
                })}
                <Link href="#" className="text-sm text-blue-600 hover:underline block mt-2">
                  Show all 24 amenities
                </Link>
              </div>
            </div>
          </div>

          {/* Right Section - Hotel Listings */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                <span className="font-semibold text-gray-900">{filteredHotels.length}</span> Properties found
              </p>
              <div className="flex gap-2">
                {(["recommended", "lowest-price", "highest-rated"] as SortOption[]).map((option) => (
                  <button
                    key={option}
                    onClick={() => setSortBy(option)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      sortBy === option
                        ? "bg-blue-600 text-white"
                        : "bg-white text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    {option === "recommended"
                      ? "Recommended"
                      : option === "lowest-price"
                      ? "Lowest Price"
                      : "Highest Rated"}
                  </button>
                ))}
              </div>
            </div>

            {/* Hotel Cards */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
            ) : filteredHotels.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <p className="text-gray-500">No hotels found. Try adjusting your filters.</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {filteredHotels.slice(0, displayLimit).map((hotel) => {
                    const isFavorite = favorites.has(hotel.id);
                    const currentPrice = hotel.price_per_night || 150;
                    const originalPrice = currentPrice * 1.2; // Mock discount
                    const hasDiscount = Math.random() > 0.5; // Random for demo
                    const isSoldOut = Math.random() > 0.9; // Random for demo

                    return (
                      <div
                        key={hotel.id}
                        className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
                      >
                        {/* Image */}
                        <div className="relative h-48">
                          {hotel.images?.[0]?.url ? (
                            <Image
                              src={hotel.images[0].url}
                              alt={getLocalizedText(hotel.name, currentLanguage) || "Hotel"}
                              fill
                              className="object-cover"
                            />
                          ) : (
                            <div className="h-full w-full bg-gradient-to-br from-blue-200 to-teal-200" />
                          )}

                          {/* Badges */}
                          <div className="absolute top-3 left-3 flex gap-2">
                            {hasDiscount && !isSoldOut && (
                              <Badge className="bg-teal-500 text-white font-semibold">
                                Great Deal
                              </Badge>
                            )}
                            {isSoldOut && (
                              <Badge className="bg-red-500 text-white font-semibold">
                                Sold Out Soon
                              </Badge>
                            )}
                          </div>

                          {/* Favorite Button */}
                          <button
                            onClick={() => toggleFavorite(hotel.id)}
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
                            {getLocalizedText(hotel.name, currentLanguage)}
                          </h3>

                          <div className="flex items-center text-sm text-gray-600 mb-2">
                            <MapPin className="w-4 h-4 mr-1" />
                            {hotel.location?.city || "Sri Lanka"}, Sri Lanka
                          </div>

                          <div className="flex items-center gap-1 mb-3">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium text-gray-700">
                              {hotel.star_rating?.toFixed(1) || "4.5"}
                            </span>
                          </div>

                          {/* Amenities */}
                          <div className="flex flex-wrap gap-2 mb-4">
                            {hotel.amenities?.slice(0, 3).map((amenity, idx) => (
                              <Badge
                                key={idx}
                                variant="outline"
                                className="text-xs flex items-center gap-1"
                              >
                                {getAmenityIcon(amenity)}
                                {amenity}
                              </Badge>
                            ))}
                          </div>

                          {/* Price */}
                          <div className="flex items-center justify-between">
                            <div>
                              {hasDiscount && (
                                <p className="text-sm text-gray-400 line-through mb-1">
                                  {formatPrice(originalPrice)}
                                </p>
                              )}
                              <p className="text-lg font-bold text-gray-900">
                                {formatPrice(currentPrice)} /night
                              </p>
                            </div>
                            <Button
                              className="bg-blue-600 hover:bg-blue-700 text-white"
                              onClick={() => router.push(`/explore/hotels/${hotel.id}`)}
                            >
                              View Deal
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Load More Button */}
                {filteredHotels.length >= displayLimit && (
                  <div className="text-center mt-8">
                    <Button
                      variant="outline"
                      onClick={() => setDisplayLimit((prev) => prev + 6)}
                      className="px-6"
                    >
                      Load More Hotels
                      <ChevronDown className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Floating Chat Assistant Button */}
      <Link href="/chat">
        <button className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all z-50">
          <MessageCircle className="w-6 h-6" />
          <span className="sr-only">Chat Assistant</span>
        </button>
      </Link>
    </div>
  );
}
