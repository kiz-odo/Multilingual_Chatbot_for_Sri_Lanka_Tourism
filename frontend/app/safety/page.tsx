"use client";

import * as React from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangle,
  Phone,
  MapPin,
  Shield,
  Info,
  Flame,
  Flag,
  Ambulance,
  Navigation,
  Clock,
  Search,
  ChevronRight,
  ChevronLeft,
  Home,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import Link from "next/link";
import Image from "next/image";

interface Advisory {
  id: string;
  type: "warning" | "traffic" | "health";
  title: string;
  location: string;
  description: string;
  updated_at: string;
  severity: "low" | "medium" | "high";
}

interface SafetyTip {
  id: string;
  number: number;
  title: string;
  description: string;
  category: string;
  image_url?: string;
}

export default function SafetyPage() {
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const [locationShared, setLocationShared] = React.useState(true);
  const [sosPressStart, setSosPressStart] = React.useState<number | null>(null);
  const [currentTipIndex, setCurrentTipIndex] = React.useState(13); // Start at tip #14
  const sosButtonRef = React.useRef<HTMLButtonElement>(null);

  // Fetch active advisories
  const { data: advisoriesData } = useQuery({
    queryKey: ["safety-advisories"],
    queryFn: async () => {
      try {
        const response = await apiClient.safety.getAlerts({ active_only: true });
        return response.data || [];
      } catch {
        // Return mock data if API fails
        return [
          {
            id: "1",
            type: "warning",
            title: "Heavy Rain Warning",
            location: "South-Western Coastal Areas",
            description: "Heavy showers above 100mm are likely. Avoid sea bathing in these areas.",
            updated_at: new Date(Date.now() - 10 * 60000).toISOString(),
          },
          {
            id: "2",
            type: "traffic",
            title: "Traffic Update",
            location: "Colombo Fort Area",
            description: "Road diversions in place due to a local procession. Expect delays of 20-30 mins.",
            updated_at: new Date(Date.now() - 60 * 60000).toISOString(),
          },
          {
            id: "3",
            type: "health",
            title: "Dengue Prevention",
            location: "Island-wide",
            description: "Travelers are advised to use mosquito repellent during dawn and dusk hours.",
            updated_at: new Date(Date.now() - 5 * 60 * 60000).toISOString(),
          },
        ];
      }
    },
  });

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
            id: "14",
            number: 14,
            title: "Ocean Safety",
            description: "Always swim in designated areas monitored by lifeguards. Look for red and yellow flags.",
            category: "Water Safety",
          },
        ];
      }
    },
  });

  // Fetch emergency numbers
  const { data: emergencyNumbers } = useQuery({
    queryKey: ["emergency-numbers"],
    queryFn: async () => {
      try {
        const response = await apiClient.safety.getEmergencyNumbers();
        return response.data || {};
      } catch {
        return {
          police: "119",
          ambulance: "1990",
          fire: "110",
          tourist_police: "1912",
        };
      }
    },
  });

  // Get current location
  const getCurrentLocation = React.useCallback((): Promise<{ lat: number; lng: number; address?: string }> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocation not supported"));
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        reject
      );
    });
  }, []);

  // SOS mutation
  const sosMutation = useMutation({
    mutationFn: async () => {
      if (!user) throw new Error("User not authenticated");
      
      const location = await getCurrentLocation();
      return apiClient.safety.sos({
        user_id: user.id,
        emergency_type: "general",
        description: "Emergency SOS activated via Safety Center",
        severity: 5,
        location: {
          latitude: location.lat,
          longitude: location.lng,
          city: "Unknown",
        },
      });
    },
    onSuccess: () => {
      alert("Emergency SOS activated! Help is on the way. Tourist Police: 1912");
    },
    onError: (error) => {
      console.error("SOS error:", error);
      alert("Failed to activate SOS. Please call 1912 directly.");
    },
  });

  // Handle SOS button press (3 seconds)
  const handleSOSPressStart = () => {
    setSosPressStart(Date.now());
  };

  const handleSOSPressEnd = () => {
    if (sosPressStart) {
      const pressDuration = Date.now() - sosPressStart;
      if (pressDuration >= 3000) {
        // 3 seconds pressed
        if (isAuthenticated && user) {
          sosMutation.mutate();
        } else {
          alert("Please login to use SOS feature");
        }
      }
      setSosPressStart(null);
    }
  };

  // Toggle location sharing
  const toggleLocationSharing = async () => {
    if (!isAuthenticated || !user) {
      alert("Please login to enable location sharing");
      return;
    }

    if (!locationShared) {
      try {
        const location = await getCurrentLocation();
        await apiClient.safety.startLocationSharing({
          shared_with: [],
          duration_hours: 24,
          current_location: {
            latitude: location.lat,
            longitude: location.lng,
            city: "Unknown",
          },
          enable_auto_check_in: true,
        });
        setLocationShared(true);
      } catch (error) {
        console.error("Location sharing error:", error);
        alert("Failed to enable location sharing");
      }
    } else {
      setLocationShared(false);
    }
  };

  // Format advisory type
  const getAdvisoryType = (advisory: any): Advisory["type"] => {
    const type = advisory.type?.toLowerCase() || advisory.alert_type?.toLowerCase() || advisory.title?.toLowerCase() || "";
    if (type.includes("rain") || type.includes("weather") || type.includes("warning")) return "warning";
    if (type.includes("traffic") || type.includes("road")) return "traffic";
    return "health";
  };

  // Format time ago
  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 60) return `${diffMins} mins ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    return `${Math.floor(diffHours / 24)} days ago`;
  };

  const advisories: Advisory[] = (advisoriesData || []).slice(0, 3).map((adv: any, idx: number) => ({
    id: adv.id || `adv-${idx}`,
    type: getAdvisoryType(adv),
    title: adv.title || adv.alert_type || "Advisory",
    location: adv.location || adv.area || "Sri Lanka",
    description: adv.description || adv.message || "",
    updated_at: adv.updated_at || adv.created_at || new Date().toISOString(),
    severity: adv.severity || "medium",
  }));

  const safetyTips: SafetyTip[] = (safetyTipsData || []).map((tip: any, idx: number) => ({
    id: tip.id || `tip-${idx}`,
    number: tip.number || idx + 1,
    title: tip.title || `Safety Tip ${idx + 1}`,
    description: tip.description || tip.content || "",
    category: tip.category || "General",
    image_url: tip.image_url,
  }));

  const currentTip = safetyTips[currentTipIndex] || safetyTips[0];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
          <Link href="/" className="hover:text-gray-900 flex items-center gap-1">
            <Home className="w-4 h-4" />
            Home
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">Safety Center</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">Safety Center</h1>
            <p className="text-gray-600 text-lg max-w-2xl">
              Your intelligent companion for a safe journey in Sri Lanka. Connect instantly with emergency services and stay informed.
            </p>
          </div>
          <div className="flex items-center space-x-2 text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium">System Operational</span>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Need Immediate Assistance - SOS Button */}
            <Card className="relative overflow-hidden">
              <CardContent className="p-8">
                <div className="flex flex-col items-center text-center">
                  {/* Shield Icon Background */}
                  <div className="absolute inset-0 flex items-center justify-center opacity-5">
                    <Shield className="w-64 h-64 text-gray-400" />
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-900 mb-6">Need Immediate Assistance?</h3>
                  
                  {/* SOS Button */}
                  <div className="relative z-10 mb-4">
                    <button
                      ref={sosButtonRef}
                      onMouseDown={handleSOSPressStart}
                      onMouseUp={handleSOSPressEnd}
                      onMouseLeave={handleSOSPressEnd}
                      onTouchStart={handleSOSPressStart}
                      onTouchEnd={handleSOSPressEnd}
                      className="w-32 h-32 rounded-full bg-red-600 hover:bg-red-700 active:bg-red-800 text-white flex flex-col items-center justify-center shadow-xl transition-all duration-300 transform active:scale-95"
                      aria-label="Emergency SOS - Press and hold for 3 seconds"
                    >
                      <span className="text-sm font-bold mb-1">SOS</span>
                      <span className="text-3xl font-bold">1912</span>
                      <span className="text-xs mt-1">PRESS 3S</span>
                    </button>
                  </div>
                  
                  <p className="text-sm text-gray-600">
                    Automatically shares location with Tourist Police
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Location Sharing */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Location Sharing</h3>
                    <p className="text-sm text-gray-500">Visible to verified contacts only</p>
                  </div>
                  <button
                    onClick={toggleLocationSharing}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      locationShared ? "bg-blue-600" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        locationShared ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
                
                {locationShared && (
                  <div className="mt-4 relative h-48 bg-gray-100 rounded-lg overflow-hidden">
                    {/* Map placeholder */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <MapPin className="w-8 h-8 text-green-600 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">Near Galle Face Green, Colombo 03</p>
                      </div>
                    </div>
                    {/* Target icon overlay */}
                    <div className="absolute bottom-3 right-3">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <Navigation className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Emergency Contact Numbers */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Emergency Contact Numbers</h2>
              <div className="grid grid-cols-2 gap-4">
                {/* Police Emergency */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <Shield className="w-6 h-6 text-blue-600" />
                      </div>
                      <a href={`tel:${emergencyNumbers?.police || "119"}`}>
                        <Phone className="w-5 h-5 text-gray-600 hover:text-blue-600 cursor-pointer" />
                      </a>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">Police Emergency</h3>
                    <p className="text-2xl font-bold text-gray-900">{emergencyNumbers?.police || "119"}</p>
                  </CardContent>
                </Card>

                {/* Ambulance */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                        <Ambulance className="w-6 h-6 text-green-600" />
                      </div>
                      <a href={`tel:${emergencyNumbers?.ambulance || "1990"}`}>
                        <Phone className="w-5 h-5 text-gray-600 hover:text-green-600 cursor-pointer" />
                      </a>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">Ambulance</h3>
                    <p className="text-2xl font-bold text-gray-900">{emergencyNumbers?.ambulance || "1990"}</p>
                  </CardContent>
                </Card>

                {/* Fire & Rescue */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
                        <Flame className="w-6 h-6 text-orange-600" />
                      </div>
                      <a href={`tel:${emergencyNumbers?.fire || "110"}`}>
                        <Phone className="w-5 h-5 text-gray-600 hover:text-orange-600 cursor-pointer" />
                      </a>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">Fire & Rescue</h3>
                    <p className="text-2xl font-bold text-gray-900">{emergencyNumbers?.fire || "110"}</p>
                  </CardContent>
                </Card>

                {/* Foreign Mission */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                        <Flag className="w-6 h-6 text-purple-600" />
                      </div>
                      <Link href="/safety/embassy">
                        <Search className="w-5 h-5 text-gray-600 hover:text-purple-600 cursor-pointer" />
                      </Link>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">Foreign Mission</h3>
                    <p className="text-lg font-medium text-gray-700">Find Embassy</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Active Advisories */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Active Advisories</h2>
                <Link href="/safety/advisories" className="text-sm text-blue-600 hover:underline">
                  View All History
                </Link>
              </div>
              <div className="space-y-3">
                {advisories.map((advisory) => (
                  <Card
                    key={advisory.id}
                    className="border-l-4 bg-white"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <div
                          className={`flex-shrink-0 ${
                            advisory.type === "warning"
                              ? "text-red-500"
                              : advisory.type === "traffic"
                              ? "text-orange-500"
                              : "text-blue-500"
                          }`}
                        >
                          {advisory.type === "warning" && <AlertTriangle className="w-5 h-5" />}
                          {advisory.type === "traffic" && (
                            <div className="w-5 h-5 flex flex-col items-center justify-between">
                              <div className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                              <div className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                              <div className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                            </div>
                          )}
                          {advisory.type === "health" && <Info className="w-5 h-5" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 text-sm mb-1">{advisory.location}</h3>
                          <p className="text-sm text-gray-600 mb-2">{advisory.description}</p>
                          <p className="text-xs text-gray-500 flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>Updated: {getTimeAgo(advisory.updated_at)}</span>
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                {advisories.length === 0 && (
                  <Card>
                    <CardContent className="p-4 text-center text-gray-500">
                      <p className="text-sm">No active advisories</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>

            {/* Official Safety Partner */}
            <Card>
              <CardContent className="p-6 text-center">
                <h3 className="text-xs font-semibold uppercase text-gray-500 mb-4">
                  Official Safety Partner
                </h3>
                <div className="flex items-center justify-center space-x-4 mb-3">
                  <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                    <Shield className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                    <Shield className="w-8 h-8 text-gray-400" />
                  </div>
                </div>
                <p className="text-xs text-gray-500">Sri Lanka Tourism</p>
                <p className="text-xs text-gray-500">Tourist Police</p>
              </CardContent>
            </Card>

            {/* Safety Tip */}
            {currentTip && (
              <Card className="relative overflow-hidden bg-gradient-to-br from-teal-500 to-blue-600 text-white">
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute bottom-0 right-0 w-32 h-32 bg-white rounded-full -mr-16 -mb-16" />
                </div>
                <CardContent className="p-6 relative z-10">
                  <Badge className="mb-3 bg-white/20 text-white border-white/30 text-xs">
                    Safety Tip #{currentTip.number}
                  </Badge>
                  <h3 className="text-xl font-bold mb-2">{currentTip.title}</h3>
                  <p className="text-sm text-white/90 mb-4">{currentTip.description}</p>
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
                    <div className="flex gap-1">
                      <button
                        onClick={() =>
                          setCurrentTipIndex((prev) => (prev - 1 + safetyTips.length) % safetyTips.length)
                        }
                        className="text-white/80 hover:text-white"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() =>
                          setCurrentTipIndex((prev) => (prev + 1) % safetyTips.length)
                        }
                        className="text-white/80 hover:text-white"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
