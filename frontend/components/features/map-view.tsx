"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin } from "lucide-react";

export interface MapViewProps {
  lat: number;
  lng: number;
  zoom?: number;
  markers?: Array<{ lat: number; lng: number; label?: string }>;
  className?: string;
  height?: string;
}

export function MapView({
  lat,
  lng,
  zoom: _zoom = 13,
  markers: _markers = [],
  className,
  height = "400px",
}: MapViewProps) {
  // Note: zoom and markers are available for future map library integration
  void _zoom;
  void _markers;
  const mapRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (!mapRef.current) return;

    // Create a simple map using OpenStreetMap or Google Maps embed
    // For production, you would use a proper map library like Leaflet or Google Maps
    const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${
      lng - 0.01
    },${lat - 0.01},${lng + 0.01},${lat + 0.01}&layer=mapnik&marker=${lat},${lng}`;

    mapRef.current.innerHTML = `
      <iframe
        width="100%"
        height="${height}"
        frameborder="0"
        scrolling="no"
        marginheight="0"
        marginwidth="0"
        src="${mapUrl}"
        style="border: 1px solid #ccc; border-radius: 8px;"
      ></iframe>
    `;
  }, [lat, lng, height]);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <MapPin className="h-5 w-5" />
          <span>Location</span>
        </CardTitle>
        <CardDescription>
          {lat.toFixed(4)}, {lng.toFixed(4)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div ref={mapRef} className="w-full" />
        <p className="text-xs text-muted-foreground mt-2">
          Interactive map view. Click to open in full screen.
        </p>
      </CardContent>
    </Card>
  );
}







