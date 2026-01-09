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
  Calendar,
  ChevronDown,
  Star,
  Clock,
  MessageCircle,
  Users,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Event } from "@/types";
import { format, addDays } from "date-fns";

export default function EventsPage() {
  const { currentLanguage } = useLanguageStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [dateFrom, setDateFrom] = React.useState(format(new Date(), "yyyy-MM-dd"));
  const [dateTo, setDateTo] = React.useState(format(addDays(new Date(), 30), "yyyy-MM-dd"));
  const [selectedLocation, setSelectedLocation] = React.useState("all");
  const [selectedCategories, setSelectedCategories] = React.useState<string[]>([
    "cultural",
    "religious",
  ]);
  const [displayLimit, setDisplayLimit] = React.useState(6);

  // Fetch events
  const { data, isLoading } = useQuery({
    queryKey: ["events", dateFrom, dateTo, selectedLocation, selectedCategories, currentLanguage, displayLimit],
    queryFn: async () => {
      try {
        const params: any = {
          limit: displayLimit,
          language: currentLanguage,
          date_from: dateFrom,
          date_to: dateTo,
        };

        if (selectedLocation !== "all") {
          params.city = selectedLocation;
        }

        if (selectedCategories.length > 0) {
          // Use first selected category for now (backend may need array support)
          params.category = selectedCategories[0];
        }

        const response = await apiClient.events.list(params);
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch events:", error);
        return [];
      }
    },
  });

  const events: Event[] = data || [];
  const totalResults = events.length;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Trigger search
  };

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) => {
      if (prev.includes(category)) {
        return prev.filter((c) => c !== category);
      }
      return [...prev, category];
    });
  };

  const getCategoryLabel = (category: string) => {
    const categoryMap: Record<string, string> = {
      cultural: "CULTURAL",
      religious: "RELIGIOUS",
      music: "MUSIC",
      food: "FOOD & DRINK",
      literature: "LITERATURE & ARTS",
      lifestyle: "LIFESTYLE",
    };
    return categoryMap[category.toLowerCase()] || category.toUpperCase();
  };

  const formatEventDate = (dateString?: string) => {
    if (!dateString) return { month: "TBD", day: "--" };
    const date = new Date(dateString);
    return {
      month: format(date, "MMM").toUpperCase(),
      day: format(date, "d"),
    };
  };

  const getDuration = (event: Event) => {
    if (!event.start_date || !event.end_date) return "TBD";
    const start = new Date(event.start_date);
    const end = new Date(event.end_date);
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    
    if (days === 1) return "1 day";
    if (days === 2) return "Weekend";
    if (days <= 7) return `${days} days long`;
    return `${days} days long`;
  };

  const categories = [
    { id: "cultural", label: "Cultural & Heritage" },
    { id: "religious", label: "Religious" },
    { id: "music", label: "Music & Arts" },
    { id: "food", label: "Food & Drink" },
    { id: "wellness", label: "Wellness" },
  ];

  const locations = [
    { value: "all", label: "All Regions" },
    { value: "Colombo", label: "Colombo" },
    { value: "Kandy", label: "Kandy" },
    { value: "Galle", label: "Galle" },
    { value: "Ella", label: "Ella" },
    { value: "Hikkaduwa", label: "Hikkaduwa" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative h-[500px] md:h-[600px] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=1920&q=80"
            alt="Cultural Performers"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/60 to-black/70" />
        </div>

        <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 text-center">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4">
            Discover Events & Festivals
          </h1>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl mb-8">
            Immerse yourself in the vibrant culture, music, and traditions of Sri Lanka
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
                  placeholder="Search for Esala Perahera, Jazz Festival..."
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

      {/* Main Content */}
      <div className="px-4 md:px-8 lg:px-12 py-8">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1 space-y-6">
            {/* When are you visiting? */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <div className="flex items-center gap-2 mb-4">
                <Calendar className="w-5 h-5 text-gray-600" />
                <h3 className="font-semibold text-gray-900">When are you visiting?</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">From</label>
                  <div className="relative">
                    <input
                      type="date"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                    <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">To</label>
                  <div className="relative">
                    <input
                      type="date"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                    <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                  </div>
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <div className="flex items-center gap-2 mb-4">
                <MapPin className="w-5 h-5 text-gray-600" />
                <h3 className="font-semibold text-gray-900">Location</h3>
              </div>
              <div className="relative">
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  className="w-full appearance-none px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                >
                  {locations.map((loc) => (
                    <option key={loc.value} value={loc.value}>
                      {loc.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* Categories */}
            <div className="bg-white rounded-xl shadow-sm p-4">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-gray-600" />
                <h3 className="font-semibold text-gray-900">Categories</h3>
              </div>
              <div className="space-y-2">
                {categories.map((category) => {
                  const isSelected = selectedCategories.includes(category.id);
                  return (
                    <label
                      key={category.id}
                      className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleCategory(category.id)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{category.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Section - Event Listings */}
          <div className="lg:col-span-3">
            {/* Section Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl md:text-3xl font-bold">Upcoming Events</h2>
              <p className="text-gray-600 text-sm md:text-base">
                Showing {events.length} results
              </p>
            </div>

            {/* Event Cards */}
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
            ) : events.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <p className="text-gray-500">No events found. Try adjusting your filters.</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {events.slice(0, displayLimit).map((event, idx) => {
                    const dateInfo = formatEventDate(event.start_date);
                    const isFeatured = idx === 0; // First event is featured
                    
                    return (
                      <div
                        key={event.id}
                        className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                        onClick={() => router.push(`/explore/events/${event.id}`)}
                      >
                        {/* Image */}
                        <div className="relative h-48">
                          {event.images?.[0]?.url ? (
                            <Image
                              src={event.images[0].url}
                              alt={getLocalizedText(event.name, currentLanguage) || "Event"}
                              fill
                              className="object-cover"
                            />
                          ) : (
                            <div className="h-full w-full bg-gradient-to-br from-purple-200 to-pink-200" />
                          )}

                          {/* Featured Badge */}
                          {isFeatured && (
                            <div className="absolute top-3 left-3">
                              <Badge className="bg-yellow-500 text-white">
                                <Star className="w-3 h-3 mr-1 fill-white" />
                                Featured
                              </Badge>
                            </div>
                          )}

                          {/* Date Badge */}
                          <div className="absolute bottom-3 right-3 bg-white/95 rounded-lg px-3 py-2 text-center min-w-[70px]">
                            <div className="text-xs font-semibold text-gray-600 uppercase">
                              {dateInfo.month}
                            </div>
                            <div className="text-xl font-bold text-gray-900">{dateInfo.day}</div>
                          </div>
                        </div>

                        {/* Content */}
                        <div className="p-4">
                          <Badge className="mb-2 bg-green-500 text-white text-xs">
                            {getCategoryLabel(event.category || "cultural")}
                          </Badge>

                          <h3 className="text-lg font-bold mb-2 line-clamp-1">
                            {getLocalizedText(event.name, currentLanguage)}
                          </h3>

                          <div className="flex items-center text-sm text-gray-600 mb-2">
                            <MapPin className="w-4 h-4 mr-1" />
                            {event.location?.city || "Sri Lanka"}
                            {event.location?.province && `, ${event.location.province}`}
                          </div>

                          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                            {getLocalizedText(event.description, currentLanguage)}
                          </p>

                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              {getDuration(event)}
                            </div>
                            <Link
                              href={`/explore/events/${event.id}`}
                              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                              onClick={(e) => e.stopPropagation()}
                            >
                              View Details →
                            </Link>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Load More Button */}
                {events.length >= displayLimit && (
                  <div className="text-center mt-8">
                    <Button
                      variant="outline"
                      onClick={() => setDisplayLimit((prev) => prev + 6)}
                      className="px-6"
                    >
                      Load More Events
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
        <button className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-4 shadow-lg hover:shadow-xl transition-all z-50">
          <MessageCircle className="w-6 h-6" />
          <span className="sr-only">Chat Assistant</span>
        </button>
      </Link>
    </div>
  );
}
