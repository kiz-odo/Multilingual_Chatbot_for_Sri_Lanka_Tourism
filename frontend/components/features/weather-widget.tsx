"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Cloud, Sun, CloudRain, CloudSnow, Wind, Droplets } from "lucide-react";
import apiClient from "@/lib/api-client";

export interface WeatherWidgetProps {
  city?: string;
  lat?: number;
  lng?: number;
  className?: string;
}

const weatherIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  clear: Sun,
  sunny: Sun,
  cloudy: Cloud,
  rain: CloudRain,
  snow: CloudSnow,
};

export function WeatherWidget({ city, lat, lng, className }: WeatherWidgetProps) {
  const { data: weather, isLoading } = useQuery({
    queryKey: ["weather", city, lat, lng],
    queryFn: async () => {
      const response = await apiClient.weather.getCurrent({
        city,
        lat,
        lng,
      });
      return response.data;
    },
    enabled: !!(city || (lat && lng)),
  });

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="py-6">
          <div className="animate-pulse space-y-2">
            <div className="h-4 bg-muted rounded w-3/4" />
            <div className="h-8 bg-muted rounded w-1/2" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!weather) return null;

  const Icon = weatherIcons[weather.condition?.toLowerCase() || ""] || Cloud;
  const temperature = weather.temperature || weather.temp;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-lg">Weather</CardTitle>
        {weather.location && (
          <CardDescription>{weather.location}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Icon className="h-12 w-12 text-primary" />
            <div>
              <div className="text-3xl font-bold">
                {temperature ? `${Math.round(temperature)}°` : "N/A"}
              </div>
              {weather.condition && (
                <div className="text-sm text-muted-foreground capitalize">
                  {weather.condition}
                </div>
              )}
            </div>
          </div>
        </div>
        {weather.humidity !== undefined && (
          <div className="mt-4 flex items-center space-x-4 text-sm text-muted-foreground">
            {weather.humidity !== undefined && (
              <div className="flex items-center space-x-1">
                <Droplets className="h-4 w-4" />
                <span>{weather.humidity}%</span>
              </div>
            )}
            {weather.wind_speed !== undefined && (
              <div className="flex items-center space-x-1">
                <Wind className="h-4 w-4" />
                <span>{weather.wind_speed} km/h</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}






