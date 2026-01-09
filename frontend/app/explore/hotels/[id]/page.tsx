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
  Phone,
  Mail,
  Globe,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText, formatCurrency } from "@/lib/utils";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Hotel } from "@/types";

export default function HotelDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { currentLanguage } = useLanguageStore();
  const hotelId = params.id as string;

  const { data, isLoading, error } = useQuery({
    queryKey: ["hotel", hotelId, currentLanguage],
    queryFn: async () => {
      const response = await apiClient.hotels.get(hotelId, {
        language: currentLanguage,
      });
      return response.data;
    },
  });

  const hotel: Hotel = data;

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

  if (error || !hotel) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">
              Hotel not found or failed to load.
            </p>
            <Link href="/explore">
              <Button>Back to Explore</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const primaryImage = hotel.images?.[0];

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
                alt={hotel.name || "Hotel"}
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
                {getLocalizedText(hotel.description, currentLanguage)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Amenities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {hotel.amenities?.map((amenity, index) => (
                  <Badge key={index} variant="secondary">
                    {amenity}
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
                  <CardTitle className="text-2xl">{hotel.name}</CardTitle>
                  <CardDescription className="flex items-center mt-2">
                    <MapPin className="mr-1 h-4 w-4" />
                    {hotel.location?.city || hotel.location?.address}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {hotel.rating && (
                <div className="flex items-center space-x-2">
                  <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  <span className="font-semibold">{hotel.rating}</span>
                  <span className="text-muted-foreground">
                    ({hotel.review_count || 0} reviews)
                  </span>
                </div>
              )}

              {hotel.star_rating && (
                <div className="flex items-center space-x-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className={`h-4 w-4 ${
                        i < hotel.star_rating!
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-muted"
                      }`}
                    />
                  ))}
                  <span className="ml-2 text-sm text-muted-foreground">
                    {hotel.star_rating} Star Hotel
                  </span>
                </div>
              )}

              {hotel.price_range && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-muted-foreground" />
                  <span className="text-lg font-semibold">
                    {hotel.price_range}
                  </span>
                </div>
              )}

              <div className="pt-4 space-y-2">
                <Button className="w-full" size="lg">
                  Book Now
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

              {hotel.contact && (
                <div className="pt-4 border-t space-y-2">
                  {hotel.contact.phone && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <a href={`tel:${hotel.contact.phone}`} className="hover:underline">
                        {hotel.contact.phone}
                      </a>
                    </div>
                  )}
                  {hotel.contact.email && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <a href={`mailto:${hotel.contact.email}`} className="hover:underline">
                        {hotel.contact.email}
                      </a>
                    </div>
                  )}
                  {hotel.contact.website && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <a
                        href={hotel.contact.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline"
                      >
                        Visit Website
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






