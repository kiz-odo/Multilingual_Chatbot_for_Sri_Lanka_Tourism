"use client";

import * as React from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Calendar,
  MapPin,
  Clock,
  DollarSign,
  ArrowLeft,
  Download,
  Share2,
  Edit,
  Trash2,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { formatDate } from "@/lib/utils";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { useAuthStore } from "@/store/auth-store";
import { useToast } from "@/hooks/use-toast";

export default function ItineraryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { currentLanguage } = useLanguageStore();
  const { user } = useAuthStore();
  const { addToast } = useToast();
  const itineraryId = params.id as string;

  const { data: itinerary, isLoading, error } = useQuery({
    queryKey: ["itinerary", itineraryId],
    queryFn: async () => {
      const response = await apiClient.itinerary.get(itineraryId);
      return response.data;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async () => {
      await apiClient.itinerary.delete(itineraryId);
    },
    onSuccess: () => {
      router.push("/planner");
    },
  });

  const exportPDFMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.itinerary.exportPDF(itineraryId);
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `itinerary-${itineraryId}.pdf`;
      a.click();
    },
  });

  const handleShare = async () => {
    const shareData = {
      title: itinerary.title || "My Sri Lanka Itinerary",
      text: `Check out my ${itinerary.duration_days || ""} day itinerary for Sri Lanka!`,
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

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-1/4" />
          <div className="h-96 bg-muted rounded-2xl" />
        </div>
      </div>
    );
  }

  if (error || !itinerary) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">
              Itinerary not found or failed to load.
            </p>
            <Link href="/planner">
              <Button>Back to Planner</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => exportPDFMutation.mutate()}
            disabled={exportPDFMutation.isPending}
          >
            <Download className="mr-2 h-4 w-4" />
            Export PDF
          </Button>
          <Button variant="outline" onClick={handleShare}>
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
          {user && (
            <>
              <Button variant="outline">
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
              <Button
                variant="destructive"
                onClick={() => {
                  if (confirm("Are you sure you want to delete this itinerary?")) {
                    deleteMutation.mutate();
                  }
                }}
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-3xl">{itinerary.title || "My Itinerary"}</CardTitle>
          <CardDescription>
            {itinerary.destination && (
              <div className="flex items-center space-x-2 mt-2">
                <MapPin className="h-4 w-4" />
                <span>{itinerary.destination}</span>
              </div>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {itinerary.start_date && (
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Start Date</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(itinerary.start_date)}
                  </p>
                </div>
              </div>
            )}
            {itinerary.end_date && (
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">End Date</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(itinerary.end_date)}
                  </p>
                </div>
              </div>
            )}
            {itinerary.budget && (
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Budget</p>
                  <p className="text-sm text-muted-foreground">
                    {itinerary.budget}
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {itinerary.days && (
        <div className="space-y-6">
          {itinerary.days.map((day: any, index: number) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle>Day {index + 1}</CardTitle>
                {day.date && (
                  <CardDescription>{formatDate(day.date)}</CardDescription>
                )}
              </CardHeader>
              <CardContent>
                {day.activities && day.activities.length > 0 ? (
                  <div className="space-y-4">
                    {day.activities.map((activity: any, actIndex: number) => (
                      <div key={actIndex} className="border-l-4 border-primary pl-4 py-2">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold">{activity.name || activity.title}</h4>
                            {activity.time && (
                              <div className="flex items-center space-x-1 text-sm text-muted-foreground mt-1">
                                <Clock className="h-3 w-3" />
                                <span>{activity.time}</span>
                              </div>
                            )}
                            {activity.description && (
                              <p className="text-sm text-muted-foreground mt-2">
                                {activity.description}
                              </p>
                            )}
                            {activity.location && (
                              <div className="flex items-center space-x-1 text-sm text-muted-foreground mt-1">
                                <MapPin className="h-3 w-3" />
                                <span>{activity.location}</span>
                              </div>
                            )}
                          </div>
                          {activity.cost && (
                            <Badge variant="secondary">{activity.cost}</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No activities planned for this day.</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}


