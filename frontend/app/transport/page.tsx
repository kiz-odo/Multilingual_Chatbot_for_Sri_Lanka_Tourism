"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, MapPin, Clock, DollarSign, Bus, Train, Car, Plane } from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";

const transportIcons = {
  bus: Bus,
  train: Train,
  car: Car,
  plane: Plane,
};

export default function TransportPage() {
  const { currentLanguage } = useLanguageStore();
  const [origin, setOrigin] = React.useState("");
  const [destination, setDestination] = React.useState("");
  const [transportType, setTransportType] = React.useState<string>("");

  const { data: transportList, isLoading } = useQuery({
    queryKey: ["transport", currentLanguage],
    queryFn: async () => {
      const response = await apiClient.transport.list();
      return response.data;
    },
  });

  const { data: searchResults, refetch: searchTransport } = useQuery({
    queryKey: ["transport-search", origin, destination, transportType],
    queryFn: async () => {
      const response = await apiClient.transport.search({
        origin,
        destination,
        transport_type: transportType || undefined,
      });
      return response.data;
    },
    enabled: false,
  });

  const handleSearch = () => {
    if (origin && destination) {
      searchTransport();
    }
  };

  const displayData = searchResults || transportList || [];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Transport Options</h1>
        <p className="text-muted-foreground">
          Find the best way to travel around Sri Lanka
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Search Transport</CardTitle>
          <CardDescription>
            Find transport options between locations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <Input
              placeholder="Origin"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
            />
            <Input
              placeholder="Destination"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            />
            <Select
              options={[
                { value: "", label: "All Types" },
                { value: "bus", label: "Bus" },
                { value: "train", label: "Train" },
                { value: "car", label: "Car" },
                { value: "plane", label: "Plane" },
              ]}
              value={transportType}
              onChange={(e) => setTransportType(e.target.value)}
            />
            <Button onClick={handleSearch}>
              <Search className="mr-2 h-4 w-4" />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {displayData.map((transport: any) => {
            const Icon = transportIcons[transport.transport_type as keyof typeof transportIcons] || Bus;
            return (
              <Card key={transport.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Icon className="h-5 w-5" />
                      <CardTitle>{transport.name}</CardTitle>
                    </div>
                    <Badge variant="secondary">{transport.transport_type}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {transport.origin && transport.destination && (
                    <div className="space-y-1">
                      <div className="flex items-center text-sm text-muted-foreground">
                        <MapPin className="mr-1 h-3 w-3" />
                        {transport.origin} → {transport.destination}
                      </div>
                    </div>
                  )}
                  {transport.duration && (
                    <div className="flex items-center text-sm">
                      <Clock className="mr-1 h-4 w-4 text-muted-foreground" />
                      {transport.duration}
                    </div>
                  )}
                  {transport.price && (
                    <div className="flex items-center text-sm font-semibold">
                      <DollarSign className="mr-1 h-4 w-4 text-muted-foreground" />
                      {transport.price}
                    </div>
                  )}
                  <Button variant="outline" className="w-full mt-4">
                    View Details
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}






