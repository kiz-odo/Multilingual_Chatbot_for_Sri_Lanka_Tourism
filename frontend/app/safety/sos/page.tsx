"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Shield,
  Phone,
  MapPin,
  Navigation,
  AlertTriangle,
  ChevronLeft,
  Home,
  CheckCircle,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import { useRouter } from "next/navigation";

export default function SOSPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const [locationShared, setLocationShared] = React.useState(false);
  const [sosPressStart, setSosPressStart] = React.useState<number | null>(null);
  const [sosActivated, setSosActivated] = React.useState(false);
  const sosButtonRef = React.useRef<HTMLButtonElement>(null);

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
      setSosActivated(true);
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
          router.push("/auth/login");
        }
      }
      setSosPressStart(null);
    }
  };

  // Toggle location sharing
  const toggleLocationSharing = async () => {
    if (!isAuthenticated || !user) {
      alert("Please login to enable location sharing");
      router.push("/auth/login");
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
          <span className="text-gray-900 font-medium">SOS Emergency</span>
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
              <h1 className="text-4xl font-bold text-gray-900">SOS Emergency</h1>
              <p className="text-gray-600 mt-2">
                Press and hold for 3 seconds to activate emergency SOS
              </p>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* SOS Button */}
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
                    disabled={sosActivated}
                    className={`w-32 h-32 rounded-full text-white flex flex-col items-center justify-center shadow-xl transition-all duration-300 transform active:scale-95 ${
                      sosActivated
                        ? "bg-green-600"
                        : "bg-red-600 hover:bg-red-700 active:bg-red-800"
                    }`}
                    aria-label="Emergency SOS - Press and hold for 3 seconds"
                  >
                    {sosActivated ? (
                      <>
                        <CheckCircle className="w-8 h-8 mb-2" />
                        <span className="text-sm font-bold">ACTIVATED</span>
                      </>
                    ) : (
                      <>
                        <span className="text-sm font-bold mb-1">SOS</span>
                        <span className="text-3xl font-bold">1912</span>
                        <span className="text-xs mt-1">PRESS 3S</span>
                      </>
                    )}
                  </button>
                </div>
                
                <p className="text-sm text-gray-600 mb-4">
                  {sosActivated
                    ? "Help has been notified. Tourist Police will contact you shortly."
                    : "Automatically shares location with Tourist Police"}
                </p>

                {!isAuthenticated && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      Please login to use SOS feature
                    </p>
                    <Link href="/auth/login">
                      <Button size="sm" className="mt-2">
                        Login
                      </Button>
                    </Link>
                  </div>
                )}
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
                  disabled={!isAuthenticated}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    locationShared ? "bg-blue-600" : "bg-gray-300"
                  } ${!isAuthenticated ? "opacity-50 cursor-not-allowed" : ""}`}
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
                      <p className="text-sm text-gray-600">Location shared</p>
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
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-orange-500" />
                  Quick Emergency Numbers
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <a href="tel:1912" className="text-center p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                    <div className="text-2xl font-bold text-red-600 mb-1">1912</div>
                    <div className="text-sm text-gray-600">Tourist Police</div>
                  </a>
                  <a href="tel:119" className="text-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                    <div className="text-2xl font-bold text-blue-600 mb-1">119</div>
                    <div className="text-sm text-gray-600">Police</div>
                  </a>
                  <a href="tel:1990" className="text-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                    <div className="text-2xl font-bold text-green-600 mb-1">1990</div>
                    <div className="text-sm text-gray-600">Ambulance</div>
                  </a>
                  <a href="tel:110" className="text-center p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors">
                    <div className="text-2xl font-bold text-orange-600 mb-1">110</div>
                    <div className="text-sm text-gray-600">Fire</div>
                  </a>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}


