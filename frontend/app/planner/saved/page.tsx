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
  Calendar,
  MapPin,
  Clock,
  ArrowLeft,
  Trash2,
  Eye,
  Plus,
  Search,
  Filter,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import { format } from "date-fns";
import { useToast } from "@/hooks/use-toast";
import type { Itinerary } from "@/types";

export default function SavedTripsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = React.useState("");

  // Redirect if not authenticated
  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  // Fetch saved itineraries
  const { data: itineraries = [], isLoading } = useQuery({
    queryKey: ["itineraries", user?.id],
    queryFn: async () => {
      if (!isAuthenticated || !user) return [];
      try {
        const response = await apiClient.itinerary.list();
        return response.data || [];
      } catch (error) {
        console.error("Failed to fetch itineraries:", error);
        return [];
      }
    },
    enabled: isAuthenticated && !!user,
  });

  // Delete itinerary mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.itinerary.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["itineraries", user?.id] });
      addToast({
        title: "Success",
        description: "Itinerary deleted successfully",
        variant: "success",
      });
    },
    onError: () => {
      addToast({
        title: "Error",
        description: "Failed to delete itinerary",
        variant: "error",
      });
    },
  });

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this itinerary?")) {
      deleteMutation.mutate(id);
    }
  };

  // Filter itineraries by search query
  const filteredItineraries = React.useMemo(() => {
    if (!searchQuery.trim()) return itineraries;
    const query = searchQuery.toLowerCase();
    return itineraries.filter((itinerary: Itinerary) => {
      const cities = itinerary.cities?.join(" ").toLowerCase() || "";
      return cities.includes(query);
    });
  }, [itineraries, searchQuery]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                className="p-2"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">My Saved Trips</h1>
                <p className="text-gray-600 mt-1">
                  Manage and view your saved travel itineraries
                </p>
              </div>
            </div>
            <Link href="/planner">
              <Button className="bg-teal-500 hover:bg-teal-600 text-white">
                <Plus className="w-4 h-4 mr-2" />
                Create New Trip
              </Button>
            </Link>
          </div>

          {/* Search and Filter */}
          <div className="flex gap-4 mt-6">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by city or destination..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>
        </div>

        {/* Itineraries Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
          </div>
        ) : filteredItineraries.length === 0 ? (
          <Card className="p-12 text-center">
            <CardContent>
              <div className="flex flex-col items-center">
                <Calendar className="w-16 h-16 text-gray-300 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {searchQuery ? "No trips found" : "No saved trips yet"}
                </h3>
                <p className="text-gray-600 mb-6">
                  {searchQuery
                    ? "Try adjusting your search query"
                    : "Start planning your first trip to Sri Lanka"}
                </p>
                {!searchQuery && (
                  <Link href="/planner">
                    <Button className="bg-teal-500 hover:bg-teal-600 text-white">
                      <Plus className="w-4 h-4 mr-2" />
                      Create Your First Trip
                    </Button>
                  </Link>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItineraries.map((itinerary: Itinerary) => {
              const startDate = itinerary.travel_dates?.start
                ? new Date(itinerary.travel_dates.start)
                : null;
              const endDate = itinerary.travel_dates?.end
                ? new Date(itinerary.travel_dates.end)
                : null;
              const daysCount = itinerary.days?.length || 0;

              return (
                <Card
                  key={itinerary.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => router.push(`/planner/${itinerary.id}`)}
                >
                  <CardContent className="p-6">
                    {/* Image */}
                    <div className="relative h-48 rounded-lg overflow-hidden mb-4 bg-gradient-to-br from-teal-400 to-blue-500">
                      {itinerary.days?.[0]?.activities?.[0]?.location && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <MapPin className="w-16 h-16 text-white/30" />
                        </div>
                      )}
                      <Badge className="absolute top-3 right-3 bg-white/90 text-gray-900">
                        {daysCount} {daysCount === 1 ? "Day" : "Days"}
                      </Badge>
                    </div>

                    {/* Content */}
                    <div className="space-y-3">
                      <h3 className="text-lg font-bold text-gray-900 line-clamp-2">
                        {itinerary.cities?.join(", ") || "Untitled Trip"}
                      </h3>

                      {/* Dates */}
                      {startDate && endDate && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {format(startDate, "MMM d")} - {format(endDate, "MMM d, yyyy")}
                          </span>
                        </div>
                      )}

                      {/* Cities */}
                      {itinerary.cities && itinerary.cities.length > 0 && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <MapPin className="w-4 h-4" />
                          <span className="line-clamp-1">
                            {itinerary.cities.slice(0, 2).join(", ")}
                            {itinerary.cities.length > 2 && ` +${itinerary.cities.length - 2}`}
                          </span>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                        <Link
                          href={`/planner/${itinerary.id}`}
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4 mr-2" />
                            View
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleDelete(itinerary.id, e)}
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

