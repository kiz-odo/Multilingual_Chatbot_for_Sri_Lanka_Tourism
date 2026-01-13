"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Calendar,
  MapPin,
  Clock,
  Eye,
  Search,
  Filter,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import { format } from "date-fns";
import type { Itinerary } from "@/types";

export default function TripHistoryPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [filterStatus, setFilterStatus] = React.useState<"all" | "upcoming" | "past">("all");

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  // Fetch trip history (itineraries)
  const { data: itineraries = [], isLoading } = useQuery({
    queryKey: ["trip-history", user?.id],
    queryFn: async () => {
      if (!isAuthenticated || !user) return [];
      try {
        const response = await apiClient.itinerary.list();
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch trip history:", error);
        return [];
      }
    },
    enabled: isAuthenticated && !!user,
  });

  // Filter trips
  const filteredTrips = React.useMemo(() => {
    let trips = [...itineraries];

    // Filter by status
    const now = new Date();
    if (filterStatus === "upcoming") {
      trips = trips.filter((trip: Itinerary) => {
        const startDate = trip.travel_dates?.start ? new Date(trip.travel_dates.start) : null;
        return startDate && startDate > now;
      });
    } else if (filterStatus === "past") {
      trips = trips.filter((trip: Itinerary) => {
        const endDate = trip.travel_dates?.end ? new Date(trip.travel_dates.end) : null;
        return endDate && endDate < now;
      });
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      trips = trips.filter((trip: Itinerary) => {
        const cities = trip.cities?.join(" ").toLowerCase() || "";
        return cities.includes(query);
      });
    }

    // Sort by date (most recent first)
    trips.sort((a: Itinerary, b: Itinerary) => {
      const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
      const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
      return dateB - dateA;
    });

    return trips;
  }, [itineraries, filterStatus, searchQuery]);

  if (!isAuthenticated) {
    return null;
  }

  const getTripStatus = (trip: Itinerary) => {
    const now = new Date();
    const startDate = trip.travel_dates?.start ? new Date(trip.travel_dates.start) : null;
    const endDate = trip.travel_dates?.end ? new Date(trip.travel_dates.end) : null;

    if (startDate && startDate > now) return "upcoming";
    if (endDate && endDate < now) return "past";
    if (startDate && endDate && startDate <= now && endDate >= now) return "ongoing";
    return "unknown";
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
              <h1 className="text-3xl font-bold text-gray-900">Trip History</h1>
              <p className="text-gray-600 mt-1">
                View your past and upcoming trips
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
                placeholder="Search trips..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div className="flex gap-2">
              {(["all", "upcoming", "past"] as const).map((status) => (
                <Button
                  key={status}
                  variant={filterStatus === status ? "default" : "outline"}
                  onClick={() => setFilterStatus(status)}
                  size="sm"
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Trips List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
          </div>
        ) : filteredTrips.length === 0 ? (
          <Card className="p-12 text-center">
            <CardContent>
              <div className="flex flex-col items-center">
                <Calendar className="w-16 h-16 text-gray-300 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {searchQuery ? "No trips found" : "No trip history yet"}
                </h3>
                <p className="text-gray-600 mb-6">
                  {searchQuery
                    ? "Try adjusting your search query"
                    : "Start planning your first trip to Sri Lanka"}
                </p>
                {!searchQuery && (
                  <Link href="/planner">
                    <Button className="bg-teal-500 hover:bg-teal-600 text-white">
                      Plan Your First Trip
                    </Button>
                  </Link>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredTrips.map((trip: Itinerary) => {
              const startDate = trip.travel_dates?.start
                ? new Date(trip.travel_dates.start)
                : null;
              const endDate = trip.travel_dates?.end
                ? new Date(trip.travel_dates.end)
                : null;
              const daysCount = trip.days?.length || 0;
              const status = getTripStatus(trip);

              const statusConfig = {
                upcoming: { label: "Upcoming", color: "bg-blue-100 text-blue-700" },
                ongoing: { label: "Ongoing", color: "bg-green-100 text-green-700" },
                past: { label: "Past", color: "bg-gray-100 text-gray-700" },
                unknown: { label: "Unknown", color: "bg-gray-100 text-gray-700" },
              };

              return (
                <Card key={trip.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="text-xl font-bold text-gray-900">
                            {trip.cities?.join(", ") || "Untitled Trip"}
                          </h3>
                          <Badge className={statusConfig[status as keyof typeof statusConfig].color}>
                            {statusConfig[status as keyof typeof statusConfig].label}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          {startDate && endDate && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Calendar className="w-4 h-4" />
                              <span>
                                {format(startDate, "MMM d")} - {format(endDate, "MMM d, yyyy")}
                              </span>
                            </div>
                          )}

                          {daysCount > 0 && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Clock className="w-4 h-4" />
                              <span>{daysCount} {daysCount === 1 ? "Day" : "Days"}</span>
                            </div>
                          )}

                          {trip.cities && trip.cities.length > 0 && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <MapPin className="w-4 h-4" />
                              <span>{trip.cities.length} {trip.cities.length === 1 ? "City" : "Cities"}</span>
                            </div>
                          )}
                        </div>

                        {trip.created_at && (
                          <p className="text-xs text-gray-500">
                            Created: {format(new Date(trip.created_at), "MMM d, yyyy")}
                          </p>
                        )}
                      </div>

                      <Link href={`/planner/${trip.id}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </Button>
                      </Link>
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


