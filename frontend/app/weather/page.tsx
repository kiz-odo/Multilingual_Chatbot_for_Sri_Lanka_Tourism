"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Cloud,
  Sun,
  CloudRain,
  Wind,
  Droplets,
  Thermometer,
  Sunrise,
  Sunset,
  MapPin,
  RefreshCw,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Weather, WeatherForecast } from "@/types";

const weatherIcons: Record<string, React.ReactNode> = {
  clear: <Sun className="h-12 w-12 text-yellow-500" />,
  sunny: <Sun className="h-12 w-12 text-yellow-500" />,
  clouds: <Cloud className="h-12 w-12 text-gray-400" />,
  cloudy: <Cloud className="h-12 w-12 text-gray-400" />,
  rain: <CloudRain className="h-12 w-12 text-blue-500" />,
  drizzle: <CloudRain className="h-12 w-12 text-blue-400" />,
  thunderstorm: <CloudRain className="h-12 w-12 text-purple-500" />,
};

const cities = [
  { name: "Colombo", emoji: "🏙️" },
  { name: "Kandy", emoji: "🏔️" },
  { name: "Galle", emoji: "🏖️" },
  { name: "Jaffna", emoji: "🌴" },
  { name: "Nuwara Eliya", emoji: "🌿" },
  { name: "Trincomalee", emoji: "🌊" },
  { name: "Anuradhapura", emoji: "🏛️" },
  { name: "Sigiriya", emoji: "🗿" },
];

export default function WeatherPage() {
  const { currentLanguage } = useLanguageStore();
  const [selectedCity, setSelectedCity] = React.useState("Colombo");

  const { data: currentWeather, isLoading: isLoadingCurrent, refetch: refetchCurrent } = useQuery({
    queryKey: ["weather-current", selectedCity],
    queryFn: async () => {
      const response = await apiClient.weather.getCurrent({ city: selectedCity });
      return response.data;
    },
  });

  const { data: forecast, isLoading: isLoadingForecast } = useQuery({
    queryKey: ["weather-forecast", selectedCity],
    queryFn: async () => {
      const response = await apiClient.weather.getForecast({ city: selectedCity, days: 7 });
      return response.data;
    },
  });

  const { data: recommendations } = useQuery({
    queryKey: ["weather-recommendations", selectedCity],
    queryFn: async () => {
      const response = await apiClient.weather.getRecommendations({ city: selectedCity });
      return response.data;
    },
  });

  const getWeatherIcon = (description: string) => {
    const key = Object.keys(weatherIcons).find((k) =>
      description?.toLowerCase().includes(k)
    );
    return key ? weatherIcons[key] : <Sun className="h-12 w-12 text-yellow-500" />;
  };

  const weather: Weather | null = currentWeather;
  const forecastData: WeatherForecast | null = forecast;

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="relative mb-8 rounded-3xl bg-gradient-to-r from-sky-400 via-blue-500 to-indigo-500 p-8 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/10" />
        <div className="relative z-10">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-2">
            Sri Lanka Weather
          </h1>
          <p className="text-white/90 max-w-2xl">
            Plan your perfect trip with real-time weather updates for major cities across Sri Lanka
          </p>
        </div>
        <div className="absolute right-8 top-8 opacity-30">
          <Sun className="h-32 w-32" />
        </div>
      </div>

      {/* City Selector */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Select a City</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {cities.map((city) => (
            <Button
              key={city.name}
              variant={selectedCity === city.name ? "default" : "outline"}
              className="h-auto py-3 flex-col gap-1"
              onClick={() => setSelectedCity(city.name)}
            >
              <span className="text-xl">{city.emoji}</span>
              <span className="text-xs">{city.name}</span>
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Current Weather */}
        <div className="lg:col-span-2">
          <Card className="overflow-hidden">
            <div className="bg-gradient-to-br from-blue-500 to-sky-400 p-6 text-white">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  <span className="text-xl font-semibold">{selectedCity}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-white hover:bg-white/20"
                  onClick={() => refetchCurrent()}
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Refresh
                </Button>
              </div>

              {isLoadingCurrent ? (
                <div className="flex items-center justify-center py-12">
                  <RefreshCw className="h-8 w-8 animate-spin" />
                </div>
              ) : weather ? (
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-6xl font-bold mb-2">
                      {Math.round(weather.temperature)}°C
                    </div>
                    <p className="text-lg capitalize">{weather.description}</p>
                    {weather.feels_like && (
                      <p className="text-sm text-white/80">
                        Feels like {Math.round(weather.feels_like)}°C
                      </p>
                    )}
                  </div>
                  <div className="text-white/90">
                    {getWeatherIcon(weather.description)}
                  </div>
                </div>
              ) : (
                <p className="text-center py-8">Weather data unavailable</p>
              )}
            </div>

            {weather && (
              <CardContent className="p-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted">
                    <Droplets className="h-5 w-5 text-blue-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Humidity</p>
                      <p className="font-semibold">{weather.humidity || "--"}%</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted">
                    <Wind className="h-5 w-5 text-teal-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Wind</p>
                      <p className="font-semibold">{weather.wind_speed || "--"} km/h</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted">
                    <Sunrise className="h-5 w-5 text-orange-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Sunrise</p>
                      <p className="font-semibold">{weather.sunrise || "6:00 AM"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted">
                    <Sunset className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Sunset</p>
                      <p className="font-semibold">{weather.sunset || "6:00 PM"}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* 7-Day Forecast */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>7-Day Forecast</CardTitle>
              <CardDescription>Weather outlook for {selectedCity}</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingForecast ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : forecastData?.forecast ? (
                <div className="grid grid-cols-7 gap-2">
                  {forecastData.forecast.slice(0, 7).map((day, idx) => (
                    <div
                      key={idx}
                      className="text-center p-3 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
                    >
                      <p className="text-xs text-muted-foreground mb-2">
                        {new Date(day.date).toLocaleDateString("en", { weekday: "short" })}
                      </p>
                      <div className="flex justify-center mb-2">
                        {getWeatherIcon(day.description)}
                      </div>
                      <p className="text-sm font-semibold">{Math.round(day.temperature_high)}°</p>
                      <p className="text-xs text-muted-foreground">{Math.round(day.temperature_low)}°</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-7 gap-2">
                  {[...Array(7)].map((_, idx) => (
                    <div key={idx} className="text-center p-3 rounded-lg bg-muted">
                      <p className="text-xs text-muted-foreground mb-2">
                        {new Date(Date.now() + idx * 86400000).toLocaleDateString("en", { weekday: "short" })}
                      </p>
                      <Sun className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                      <p className="text-sm font-semibold">{28 + Math.floor(Math.random() * 4)}°</p>
                      <p className="text-xs text-muted-foreground">{22 + Math.floor(Math.random() * 3)}°</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Travel Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Thermometer className="h-5 w-5" />
                Travel Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {recommendations ? (
                recommendations.map((tip: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-muted">
                    <p className="text-sm">{tip.message || tip}</p>
                  </div>
                ))
              ) : (
                <>
                  <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                    <p className="text-sm font-medium text-blue-700 dark:text-blue-300">
                      💧 Stay Hydrated
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Tropical climate requires drinking plenty of water
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                    <p className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                      ☀️ Sun Protection
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Use SPF 50+ sunscreen, especially at beaches
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                    <p className="text-sm font-medium text-green-700 dark:text-green-300">
                      🌧️ Monsoon Awareness
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Check seasonal patterns for your destination
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Best Time to Visit */}
          <Card>
            <CardHeader>
              <CardTitle>Best Time to Visit</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-2 rounded bg-muted">
                  <span className="text-sm">West Coast</span>
                  <Badge variant="secondary">Nov - Apr</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted">
                  <span className="text-sm">East Coast</span>
                  <Badge variant="secondary">May - Sep</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted">
                  <span className="text-sm">Hill Country</span>
                  <Badge variant="secondary">Jan - Apr</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted">
                  <span className="text-sm">Cultural Triangle</span>
                  <Badge variant="secondary">Year Round</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
