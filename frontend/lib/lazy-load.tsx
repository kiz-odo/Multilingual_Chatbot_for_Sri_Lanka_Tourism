"use client";

import * as React from "react";
import dynamic from "next/dynamic";

// Lazy load heavy components
export const LazyImageUpload = dynamic(
  () => import("@/components/features/image-upload").then((mod) => ({ default: mod.ImageUpload })),
  {
    loading: () => <div className="p-4 text-center text-gray-500">Loading image upload...</div>,
    ssr: false,
  }
);

export const LazyVoiceInput = dynamic(
  () => import("@/components/features/voice-input").then((mod) => ({ default: mod.VoiceInput })),
  {
    loading: () => <div className="p-2 text-gray-500">Loading voice input...</div>,
    ssr: false,
  }
);

export const LazyMapView = dynamic(
  () => import("@/components/features/map-view").then((mod) => ({ default: mod.MapView })),
  {
    loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">Loading map...</div>,
    ssr: false,
  }
);

export const LazyWeatherWidget = dynamic(
  () => import("@/components/features/weather-widget").then((mod) => ({ default: mod.WeatherWidget })),
  {
    loading: () => <div className="p-4 bg-gray-100 rounded-lg">Loading weather...</div>,
    ssr: false,
  }
);

export const LazyCurrencyConverter = dynamic(
  () => import("@/components/features/currency-converter").then((mod) => ({ default: mod.CurrencyConverter })),
  {
    loading: () => <div className="p-4 bg-gray-100 rounded-lg">Loading currency converter...</div>,
    ssr: false,
  }
);






