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
  Calendar,
  Clock,
  DollarSign,
  ArrowLeft,
  Share2,
  Heart,
  Users,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { getLocalizedText, formatDate } from "@/lib/utils";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Event } from "@/types";

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { currentLanguage } = useLanguageStore();
  const eventId = params.id as string;

  const { data, isLoading, error } = useQuery({
    queryKey: ["event", eventId, currentLanguage],
    queryFn: async () => {
      const response = await apiClient.events.get(eventId);
      return response.data;
    },
  });

  const event: Event = data;

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

  if (error || !event) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">
              Event not found or failed to load.
            </p>
            <Link href="/explore">
              <Button>Back to Explore</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const primaryImage = event.image_url;

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
                alt={event.title || "Event"}
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
              <p className="text-muted-foreground whitespace-pre-line">
                {getLocalizedText(event.description, currentLanguage)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Event Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {event.start_date && (
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Start Date</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(event.start_date)}
                    </p>
                  </div>
                </div>
              )}
              {event.end_date && (
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">End Date</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(event.end_date)}
                    </p>
                  </div>
                </div>
              )}
              {event.location && (
                <div className="flex items-center space-x-2">
                  <MapPin className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">
                      {event.location}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{event.title}</CardTitle>
                  {event.category && (
                    <CardDescription className="mt-2">
                      <Badge variant="secondary">{event.category}</Badge>
                    </CardDescription>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {event.price && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-muted-foreground" />
                  <span className="text-lg font-semibold">
                    {event.price === 0 ? "Free" : formatCurrency(event.price)}
                  </span>
                </div>
              )}

              {event.status && (
                <Badge
                  variant={
                    event.status === "upcoming"
                      ? "default"
                      : event.status === "ongoing"
                      ? "secondary"
                      : "outline"
                  }
                >
                  {event.status}
                </Badge>
              )}

              <div className="pt-4 space-y-2">
                <Button className="w-full" size="lg">
                  Get Tickets
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
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}






