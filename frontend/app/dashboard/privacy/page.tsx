"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Shield, Eye, EyeOff, Lock, Globe, Users } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { useToast } from "@/hooks/use-toast";
import apiClient from "@/lib/api-client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export default function PrivacyPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  // Fetch privacy settings
  const { data: privacySettings } = useQuery({
    queryKey: ["privacy-settings", user?.id],
    queryFn: async () => {
      try {
        const response = await apiClient.users.getMe();
        return {
          profile_visibility: response.data.profile_visibility || "public",
          location_sharing: response.data.location_sharing || false,
          data_collection: response.data.data_collection || true,
          analytics: response.data.analytics || true,
        };
      } catch {
        return {
          profile_visibility: "public",
          location_sharing: false,
          data_collection: true,
          analytics: true,
        };
      }
    },
    enabled: isAuthenticated && !!user,
  });

  // Update privacy settings mutation
  const updatePrivacyMutation = useMutation({
    mutationFn: async (settings: any) => {
      await apiClient.users.updateMe(settings);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["privacy-settings", user?.id] });
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      addToast({
        title: "Success",
        description: "Privacy settings updated successfully",
        variant: "success",
      });
    },
    onError: () => {
      addToast({
        title: "Error",
        description: "Failed to update privacy settings",
        variant: "error",
      });
    },
  });

  const handleToggle = (setting: string, value: any) => {
    updatePrivacyMutation.mutate({
      [setting]: value,
    });
  };

  if (!isAuthenticated) {
    return null;
  }

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

      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Privacy Settings</h1>
          <p className="text-muted-foreground mt-2">
            Control your privacy and data sharing preferences
          </p>
        </div>

        {/* Profile Visibility */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5" />
              <span>Profile Visibility</span>
            </CardTitle>
            <CardDescription>
              Control who can see your profile information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="visibility"
                  value="public"
                  checked={privacySettings?.profile_visibility === "public"}
                  onChange={() => handleToggle("profile_visibility", "public")}
                  className="w-4 h-4"
                />
                <div>
                  <p className="font-medium">Public</p>
                  <p className="text-sm text-muted-foreground">
                    Anyone can see your profile
                  </p>
                </div>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="visibility"
                  value="private"
                  checked={privacySettings?.profile_visibility === "private"}
                  onChange={() => handleToggle("profile_visibility", "private")}
                  className="w-4 h-4"
                />
                <div>
                  <p className="font-medium">Private</p>
                  <p className="text-sm text-muted-foreground">
                    Only you can see your profile
                  </p>
                </div>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Location Sharing */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5" />
              <span>Location Sharing</span>
            </CardTitle>
            <CardDescription>
              Control location data sharing for safety features
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Share Location</p>
                <p className="text-sm text-muted-foreground">
                  Allow location sharing for emergency services and trip planning
                </p>
              </div>
              <button
                onClick={() => handleToggle("location_sharing", !privacySettings?.location_sharing)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  privacySettings?.location_sharing ? "bg-blue-600" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    privacySettings?.location_sharing ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Data Collection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>Data Collection</span>
            </CardTitle>
            <CardDescription>
              Control how your data is used to improve services
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Analytics & Usage Data</p>
                <p className="text-sm text-muted-foreground">
                  Help improve our services by sharing anonymous usage data
                </p>
              </div>
              <button
                onClick={() => handleToggle("analytics", !privacySettings?.analytics)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  privacySettings?.analytics ? "bg-blue-600" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    privacySettings?.analytics ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Personalized Recommendations</p>
                <p className="text-sm text-muted-foreground">
                  Use your data to provide personalized travel recommendations
                </p>
              </div>
              <button
                onClick={() => handleToggle("data_collection", !privacySettings?.data_collection)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  privacySettings?.data_collection ? "bg-blue-600" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    privacySettings?.data_collection ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Lock className="h-5 w-5" />
              <span>Data Management</span>
            </CardTitle>
            <CardDescription>
              Manage your personal data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" className="w-full justify-start">
              Download My Data
            </Button>
            <Button variant="outline" className="w-full justify-start">
              Clear Search History
            </Button>
            <Button variant="outline" className="w-full justify-start">
              Clear Chat History
            </Button>
          </CardContent>
        </Card>

        {/* Privacy Policy Link */}
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <p className="text-sm text-blue-900">
              <strong>Your Privacy Matters</strong>
              <br />
              We are committed to protecting your privacy. Read our{" "}
              <Link href="/privacy-policy" className="underline hover:text-blue-700">
                Privacy Policy
              </Link>{" "}
              to learn more about how we collect, use, and protect your data.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


