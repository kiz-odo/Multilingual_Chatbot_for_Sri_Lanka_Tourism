"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  MapPin,
  Star,
  Clock,
  DollarSign,
  ArrowLeft,
  Share2,
  Heart,
  Navigation,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { useAuthStore } from "@/store/auth-store";
import { getLocalizedText, formatCurrency } from "@/lib/utils";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import type { Attraction } from "@/types";

export default function AttractionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { currentLanguage } = useLanguageStore();
  const { isAuthenticated } = useAuthStore();
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const attractionId = params.id as string;
  const [isFavorite, setIsFavorite] = React.useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["attraction", attractionId, currentLanguage],
    queryFn: async () => {
      const response = await apiClient.attractions.get(attractionId, {
        language: currentLanguage,
      });
      return response.data;
    },
  });

  // Check if attraction is in favorites
  const { data: userData } = useQuery({
    queryKey: ["user-profile"],
    queryFn: async () => {
      if (!isAuthenticated) return null;
      const response = await apiClient.users.getMe();
      return response.data;
    },
    enabled: isAuthenticated,
    onSuccess: (data) => {
      if (data?.favorite_attractions?.includes(attractionId)) {
        setIsFavorite(true);
      }
    },
  });

  // Add to favorites mutation
  const addFavoriteMutation = useMutation({
    mutationFn: async () => {
      await apiClient.users.addFavoriteAttraction(attractionId);
    },
    onSuccess: () => {
      setIsFavorite(true);
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      queryClient.invalidateQueries({ queryKey: ["saved-attractions"] });
      addToast({
        type: "success",
        message: "Added to favorites",
      });
    },
    onError: () => {
      addToast({
        type: "error",
        message: "Failed to add to favorites",
      });
    },
  });

  // Remove from favorites mutation
  const removeFavoriteMutation = useMutation({
    mutationFn: async () => {
      await apiClient.users.removeFavoriteAttraction(attractionId);
    },
    onSuccess: () => {
      setIsFavorite(false);
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      queryClient.invalidateQueries({ queryKey: ["saved-attractions"] });
      addToast({
        type: "success",
        message: "Removed from favorites",
      });
    },
    onError: () => {
      addToast({
        type: "error",
        message: "Failed to remove from favorites",
      });
    },
  });

  const handleFavoriteToggle = () => {
    if (!isAuthenticated) {
      addToast({
        type: "error",
        message: "Please login to add favorites",
      });
      router.push("/auth/login");
      return;
    }

    if (isFavorite) {
      removeFavoriteMutation.mutate();
    } else {
      addFavoriteMutation.mutate();
    }
  };

  const handleShare = async () => {
    const shareData = {
      title: getLocalizedText(attraction.name, currentLanguage),
      text: getLocalizedText(attraction.description, currentLanguage)?.substring(0, 200),
      url: typeof window !== "undefined" ? window.location.href : "",
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // Fallback: Copy to clipboard
        await navigator.clipboard.writeText(shareData.url);
        addToast({
          type: "success",
          message: "Link copied to clipboard!",
        });
      }
    } catch (error: any) {
      if (error.name !== "AbortError") {
        // Fallback: Copy to clipboard
        try {
          await navigator.clipboard.writeText(shareData.url);
          addToast({
            type: "success",
            message: "Link copied to clipboard!",
          });
        } catch (clipboardError) {
          addToast({
            type: "error",
            message: "Failed to share",
          });
        }
      }
    }
  };

  const attraction: Attraction = data;

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-1/4" />
          <div className="h-96 bg-muted rounded-2xl" />
          <div className="h-32 bg-muted rounded" />
        </div>
      </div>
    );
  }

  if (error || !attraction) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">
              Attraction not found or failed to load.
            </p>
            <Link href="/explore">
              <Button>Back to Explore</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const primaryImage = attraction.images?.find((img) => img.is_primary) || attraction.images?.[0];
  const otherImages = attraction.images?.filter((img) => !img.is_primary) || [];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <Button
        variant="ghost"
        onClick={() => router.back()}
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Image Gallery */}
          <div className="space-y-4">
            {primaryImage && (
              <div className="relative h-96 w-full overflow-hidden rounded-2xl">
                <Image
                  src={primaryImage.url}
                  alt={getLocalizedText(primaryImage.alt_text, currentLanguage) || getLocalizedText(attraction.name, currentLanguage)}
                  fill
                  className="object-cover"
                  priority
                />
              </div>
            )}
            {otherImages.length > 0 && (
              <div className="grid grid-cols-4 gap-4">
                {otherImages.slice(0, 4).map((image, idx) => (
                  <div
                    key={idx}
                    className="relative h-24 w-full overflow-hidden rounded-lg"
                  >
                    <Image
                      src={image.url}
                      alt={getLocalizedText(image.alt_text, currentLanguage) || `${getLocalizedText(attraction.name, currentLanguage)} - Image ${idx + 2}`}
                      fill
                      className="object-cover"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Description */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-3xl mb-2">
                    {getLocalizedText(attraction.name, currentLanguage)}
                  </CardTitle>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <MapPin className="h-4 w-4" />
                      <span>{attraction.location.city}, {attraction.location.province}</span>
                    </div>
                    {attraction.average_rating && (
                      <div className="flex items-center space-x-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span>{attraction.average_rating.toFixed(1)}</span>
                        <span>({attraction.total_reviews || 0} reviews)</span>
                      </div>
                    )}
                    {attraction.estimated_visit_duration && (
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{attraction.estimated_visit_duration}</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant={isFavorite ? "default" : "outline"}
                    size="sm"
                    onClick={handleFavoriteToggle}
                    disabled={addFavoriteMutation.isPending || removeFavoriteMutation.isPending}
                    className={isFavorite ? "bg-red-500 hover:bg-red-600" : ""}
                  >
                    <Heart className={`h-4 w-4 ${isFavorite ? "fill-white" : ""}`} />
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleShare}>
                    <Share2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">About</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">
                    {getLocalizedText(attraction.description, currentLanguage)}
                  </p>
                </div>

                {attraction.category && (
                  <div>
                    <h3 className="font-semibold mb-2">Category</h3>
                    <Badge variant="secondary">{attraction.category}</Badge>
                  </div>
                )}

                {attraction.pricing && attraction.pricing.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2 flex items-center space-x-2">
                      <DollarSign className="h-4 w-4" />
                      <span>Pricing</span>
                    </h3>
                    <div className="space-y-2">
                      {attraction.pricing.map((price, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 rounded-lg bg-muted"
                        >
                          <span className="text-sm capitalize">
                            {price.category.replace("_", " ")}
                          </span>
                          <span className="font-semibold">
                            {formatCurrency(price.price, price.currency)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Location Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Navigation className="h-5 w-5" />
                <span>Location</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm">{attraction.location.address}</p>
                <p className="text-sm text-muted-foreground">
                  {attraction.location.city}, {attraction.location.province}
                </p>
                {attraction.location.coordinates && (
                  <Button
                    variant="outline"
                    className="w-full mt-4"
                    onClick={() => {
                      const [lng, lat] = attraction.location.coordinates;
                      window.open(
                        `https://www.google.com/maps?q=${lat},${lng}`,
                        "_blank"
                      );
                    }}
                  >
                    Open in Maps
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href={`/chat?message=Tell me about ${getLocalizedText(attraction.name, currentLanguage)}`}>
                <Button className="w-full" variant="outline">
                  Ask AI About This
                </Button>
              </Link>
              <Link href={`/planner?city=${attraction.location.city}`}>
                <Button className="w-full" variant="outline">
                  Add to Itinerary
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


