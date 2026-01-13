"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ChevronLeft,
  ChevronRight,
  Home,
  Shield,
  AlertTriangle,
  Info,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";

interface SafetyTip {
  id: string;
  number: number;
  title: string;
  description: string;
  category: string;
  image_url?: string;
}

export default function SafetyTipsPage() {
  const { currentLanguage } = useLanguageStore();
  const [currentTipIndex, setCurrentTipIndex] = React.useState(0);

  // Fetch safety tips
  const { data: safetyTipsData } = useQuery({
    queryKey: ["safety-tips"],
    queryFn: async () => {
      try {
        const response = await apiClient.safety.getTips();
        return response.data || [];
      } catch {
        // Return mock data if API fails
        return [
          {
            id: "1",
            number: 1,
            title: "Ocean Safety",
            description: "Always swim in designated areas monitored by lifeguards. Look for red and yellow flags.",
            category: "Water Safety",
          },
          {
            id: "2",
            number: 2,
            title: "Stay Hydrated",
            description: "Sri Lanka's tropical climate requires constant hydration. Carry water and drink regularly.",
            category: "Health",
          },
          {
            id: "3",
            number: 3,
            title: "Respect Local Customs",
            description: "Dress modestly when visiting temples. Remove shoes and hats before entering religious sites.",
            category: "Cultural",
          },
          {
            id: "4",
            number: 4,
            title: "Wildlife Encounters",
            description: "Maintain safe distance from wildlife. Never feed or approach wild animals.",
            category: "Wildlife",
          },
          {
            id: "5",
            number: 5,
            title: "Road Safety",
            description: "Traffic drives on the left. Be cautious when crossing roads, especially in busy areas.",
            category: "Transport",
          },
        ];
      }
    },
  });

  const safetyTips: SafetyTip[] = (safetyTipsData || []).map((tip: any, idx: number) => ({
    id: tip.id || `tip-${idx}`,
    number: tip.number || idx + 1,
    title: tip.title || `Safety Tip ${idx + 1}`,
    description: tip.description || tip.content || "",
    category: tip.category || "General",
    image_url: tip.image_url,
  }));

  const currentTip = safetyTips[currentTipIndex] || safetyTips[0];

  const nextTip = () => {
    setCurrentTipIndex((prev) => (prev + 1) % safetyTips.length);
  };

  const prevTip = () => {
    setCurrentTipIndex((prev) => (prev - 1 + safetyTips.length) % safetyTips.length);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "Water Safety": "bg-blue-100 text-blue-700",
      Health: "bg-green-100 text-green-700",
      Cultural: "bg-purple-100 text-purple-700",
      Wildlife: "bg-orange-100 text-orange-700",
      Transport: "bg-red-100 text-red-700",
      General: "bg-gray-100 text-gray-700",
    };
    return colors[category] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
          <Link href="/" className="hover:text-gray-900 flex items-center gap-1">
            <Home className="w-4 h-4" />
            Home
          </Link>
          <span>/</span>
          <Link href="/safety" className="hover:text-gray-900">
            Safety
          </Link>
          <span>/</span>
          <span className="text-gray-900 font-medium">Safety Tips</span>
        </div>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Link href="/safety">
              <Button variant="ghost" className="p-2">
                <ChevronLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Safety Tips</h1>
              <p className="text-gray-600 mt-2">
                Essential safety information for your journey in Sri Lanka
              </p>
            </div>
          </div>
        </div>

        {safetyTips.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Info className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No safety tips available at the moment</p>
            </CardContent>
          </Card>
        ) : (
          <div className="max-w-4xl mx-auto">
            {/* Main Tip Card */}
            <Card className="relative overflow-hidden bg-gradient-to-br from-teal-500 to-blue-600 text-white mb-6">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute bottom-0 right-0 w-32 h-32 bg-white rounded-full -mr-16 -mb-16" />
              </div>
              <CardContent className="p-8 relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <Badge className="bg-white/20 text-white border-white/30 text-xs">
                    Tip #{currentTip.number} of {safetyTips.length}
                  </Badge>
                  <Badge className={`${getCategoryColor(currentTip.category)} text-xs`}>
                    {currentTip.category}
                  </Badge>
                </div>
                
                {currentTip.image_url && (
                  <div className="relative h-64 rounded-lg overflow-hidden mb-6">
                    <Image
                      src={currentTip.image_url}
                      alt={currentTip.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                )}

                <h2 className="text-3xl font-bold mb-4">{currentTip.title}</h2>
                <p className="text-lg text-white/90 mb-6">{currentTip.description}</p>

                {/* Navigation */}
                <div className="flex items-center justify-between">
                  <div className="flex space-x-1">
                    {safetyTips.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => setCurrentTipIndex(idx)}
                        className={`w-2 h-2 rounded-full transition-colors ${
                          idx === currentTipIndex ? "bg-white" : "bg-white/30"
                        }`}
                        aria-label={`Go to tip ${idx + 1}`}
                      />
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      onClick={prevTip}
                      className="text-white hover:bg-white/20"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={nextTip}
                      className="text-white hover:bg-white/20"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* All Tips Grid */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">All Safety Tips</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {safetyTips.map((tip, idx) => (
                  <Card
                    key={tip.id}
                    className={`cursor-pointer hover:shadow-lg transition-all ${
                      idx === currentTipIndex ? "ring-2 ring-teal-500" : ""
                    }`}
                    onClick={() => setCurrentTipIndex(idx)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <Badge className="bg-teal-100 text-teal-700 text-xs">
                          #{tip.number}
                        </Badge>
                        <Badge className={`${getCategoryColor(tip.category)} text-xs`}>
                          {tip.category}
                        </Badge>
                      </div>
                      <h4 className="font-semibold text-gray-900 mb-2">{tip.title}</h4>
                      <p className="text-sm text-gray-600 line-clamp-3">{tip.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


