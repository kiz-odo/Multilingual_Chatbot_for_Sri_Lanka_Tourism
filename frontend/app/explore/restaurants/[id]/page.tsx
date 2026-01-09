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
  Phone,
  Mail,
  UtensilsCrossed,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText, formatCurrency } from "@/lib/utils";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Restaurant } from "@/types";

export default function RestaurantDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { currentLanguage } = useLanguageStore();
  const restaurantId = params.id as string;

  const { data, isLoading, error } = useQuery({
    queryKey: ["restaurant", restaurantId, currentLanguage],
    queryFn: async () => {
      const response = await apiClient.restaurants.get(restaurantId, {
        language: currentLanguage,
      });
      return response.data;
    },
  });

  const restaurant: Restaurant = data;

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

  if (error || !restaurant) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">
              Restaurant not found or failed to load.
            </p>
            <Link href="/explore">
              <Button>Back to Explore</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const primaryImage = restaurant.images?.[0];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.back()}
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {primaryImage && (
            <div className="relative h-96 rounded-2xl overflow-hidden">
              <Image
                src={primaryImage}
                alt={restaurant.name || "Restaurant"}
                fill
                className="object-cover"
              />
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>About</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {getLocalizedText(restaurant.description, currentLanguage)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cuisine & Specialties</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {restaurant.cuisine_type && (
                  <Badge variant="secondary">
                    <UtensilsCrossed className="mr-1 h-3 w-3" />
                    {restaurant.cuisine_type}
                  </Badge>
                )}
                {restaurant.specialties?.map((specialty, index) => (
                  <Badge key={index} variant="outline">
                    {specialty}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{restaurant.name}</CardTitle>
                  <CardDescription className="flex items-center mt-2">
                    <MapPin className="mr-1 h-4 w-4" />
                    {restaurant.location?.city || restaurant.location?.address}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {restaurant.rating && (
                <div className="flex items-center space-x-2">
                  <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  <span className="font-semibold">{restaurant.rating}</span>
                  <span className="text-muted-foreground">
                    ({restaurant.review_count || 0} reviews)
                  </span>
                </div>
              )}

              {restaurant.price_range && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-muted-foreground" />
                  <span className="text-lg font-semibold">
                    {restaurant.price_range}
                  </span>
                </div>
              )}

              {restaurant.opening_hours && (
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <span className="text-sm">
                    {restaurant.opening_hours}
                  </span>
                </div>
              )}

              <div className="pt-4 space-y-2">
                <Button className="w-full" size="lg">
                  Make Reservation
                </Button>
                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1">
                    <Heart className="mr-2 h-4 w-4" />
                    Save
                  </Button>
                  <Button variant="outline" className="flex-1">
                    <Share2 className="mr-2 h-4 w-4" />
                    Share
                  </Button>
                </div>
              </div>

              {restaurant.contact && (
                <div className="pt-4 border-t space-y-2">
                  {restaurant.contact.phone && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <a href={`tel:${restaurant.contact.phone}`} className="hover:underline">
                        {restaurant.contact.phone}
                      </a>
                    </div>
                  )}
                  {restaurant.contact.email && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <a href={`mailto:${restaurant.contact.email}`} className="hover:underline">
                        {restaurant.contact.email}
                      </a>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}






