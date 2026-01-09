"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  User,
  Heart,
  Calendar,
  MessageSquare,
  Settings,
  Edit,
  MapPin,
  Star,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { t, getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { getInitials } from "@/lib/utils";
import type { Attraction, Itinerary } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  const { data: userData } = useQuery({
    queryKey: ["user-profile"],
    queryFn: async () => {
      const response = await apiClient.users.getMe();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  const { data: savedAttractions } = useQuery({
    queryKey: ["saved-attractions"],
    queryFn: async () => {
      // Try to get user's favorite attractions
      try {
        // First get user profile to check for favorites
        const userResponse = await apiClient.users.getMe();
        const user = userResponse.data;
        // If user has favorite_attractions, fetch them
        if (user?.favorite_attractions && user.favorite_attractions.length > 0) {
          // Fetch each favorite attraction
          const favoritePromises = user.favorite_attractions.slice(0, 8).map((id: string) =>
            apiClient.attractions.get(id).catch(() => null)
          );
          const favorites = await Promise.all(favoritePromises);
          const validFavorites = favorites
            .filter(Boolean)
            .map((r: any) => r?.data || r)
            .filter(Boolean);
          return { items: validFavorites };
        }
        // Return empty if no favorites
        return { items: [] };
      } catch {
        // Return empty on error
        return { items: [] };
      }
    },
    enabled: isAuthenticated,
  });

  const { data: itineraries } = useQuery({
    queryKey: ["user-itineraries"],
    queryFn: async () => {
      try {
        const response = await apiClient.itinerary.getMyItineraries();
        return response.data;
      } catch {
        // Return empty array if endpoint not available or user has no itineraries
        return { items: [] };
      }
    },
    enabled: isAuthenticated,
  });

  if (!isAuthenticated || !user) {
    return null;
  }

  const displayUser = userData || user;
  const savedItems: Attraction[] = savedAttractions?.items || [];
  const userItineraries: Itinerary[] = itineraries?.items || [];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          {t("dashboard.title", currentLanguage)}
        </h1>
        <p className="text-muted-foreground mt-2">
          Welcome back, {displayUser.full_name || displayUser.username}!
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Profile Summary */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-4">
                <div className="h-16 w-16 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-2xl font-bold">
                  {getInitials(displayUser.full_name || displayUser.username)}
                </div>
                <div className="flex-1">
                  <CardTitle>{displayUser.full_name || displayUser.username}</CardTitle>
                  <CardDescription>{displayUser.email}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Link href="/dashboard/profile">
                <Button variant="outline" className="w-full">
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Profile
                </Button>
              </Link>
              <Link href="/dashboard/settings">
                <Button variant="ghost" className="w-full">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Button>
              </Link>
              <div className="pt-2 border-t space-y-2">
                <Link href="/dashboard/bookmarks">
                  <Button variant="ghost" className="w-full justify-start" size="sm">
                    <Heart className="mr-2 h-4 w-4" />
                    My Bookmarks
                  </Button>
                </Link>
                <Link href="/dashboard/history">
                  <Button variant="ghost" className="w-full justify-start" size="sm">
                    <Calendar className="mr-2 h-4 w-4" />
                    Trip History
                  </Button>
                </Link>
                <Link href="/dashboard/security">
                  <Button variant="ghost" className="w-full justify-start" size="sm">
                    <Settings className="mr-2 h-4 w-4" />
                    Security
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Saved Attractions */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Heart className="h-5 w-5" />
                    <span>{t("dashboard.saved", currentLanguage)}</span>
                  </CardTitle>
                  <CardDescription>
                    Your favorite attractions and places
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Link href="/dashboard/bookmarks">
                    <Button variant="ghost" size="sm">
                      View All →
                    </Button>
                  </Link>
                  <Link href="/explore">
                    <Button variant="ghost" size="sm">
                      Explore →
                    </Button>
                  </Link>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {savedItems.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Heart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No saved attractions yet</p>
                  <Link href="/explore">
                    <Button variant="outline" className="mt-4">
                      Explore Attractions
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {savedItems.map((attraction) => (
                    <Link
                      key={attraction.id}
                      href={`/explore/attractions/${attraction.id}`}
                      className="group"
                    >
                      <Card className="hover:shadow-lg transition-shadow">
                        <CardHeader>
                          <CardTitle className="text-lg line-clamp-1">
                            {getLocalizedText(attraction.name, currentLanguage)}
                          </CardTitle>
                          <CardDescription className="flex items-center space-x-2">
                            <MapPin className="h-3 w-3" />
                            <span>{attraction.location.city}</span>
                            {attraction.average_rating && (
                              <>
                                <span>•</span>
                                <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                                <span>{attraction.average_rating.toFixed(1)}</span>
                              </>
                            )}
                          </CardDescription>
                        </CardHeader>
                      </Card>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* My Itineraries */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Calendar className="h-5 w-5" />
                    <span>{t("dashboard.itineraries", currentLanguage)}</span>
                  </CardTitle>
                  <CardDescription>
                    Your planned trips and itineraries
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Link href="/planner/saved">
                    <Button variant="ghost" size="sm">
                      View All →
                    </Button>
                  </Link>
                  <Link href="/planner">
                    <Button variant="ghost" size="sm">
                      Create New →
                    </Button>
                  </Link>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {userItineraries.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No itineraries yet</p>
                  <Link href="/planner">
                    <Button variant="outline" className="mt-4">
                      Plan Your Trip
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {userItineraries.map((itinerary) => (
                    <Link
                      key={itinerary.id}
                      href={`/planner/${itinerary.id}`}
                      className="block"
                    >
                      <Card className="hover:shadow-lg transition-shadow">
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <CardTitle>
                              {itinerary.cities.join(", ")} Trip
                            </CardTitle>
                            <Badge variant="secondary">
                              {itinerary.days?.length || 0} Days
                            </Badge>
                          </div>
                          <CardDescription>
                            {new Date(itinerary.travel_dates.start).toLocaleDateString()} -{" "}
                            {new Date(itinerary.travel_dates.end).toLocaleDateString()}
                          </CardDescription>
                        </CardHeader>
                      </Card>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Chat History */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5" />
                    <span>{t("dashboard.chatHistory", currentLanguage)}</span>
                  </CardTitle>
                  <CardDescription>
                    Your recent conversations with the AI assistant
                  </CardDescription>
                </div>
                <Link href="/chat">
                  <Button variant="ghost" size="sm">
                    View All →
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No chat history yet</p>
                <Link href="/chat">
                  <Button variant="outline" className="mt-4">
                    Start Chatting
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


