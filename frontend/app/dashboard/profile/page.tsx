"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Save, User, Mail, Lock } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { getInitials } from "@/lib/utils";

const profileSchema = z.object({
  full_name: z.string().optional(),
  email: z.string().email("Invalid email address").optional(),
  preferences: z.object({
    preferred_language: z.string().optional(),
    interests: z.array(z.string()).optional(),
  }).optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export default function ProfilePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  const { data: userData, isLoading } = useQuery({
    queryKey: ["user-profile"],
    queryFn: async () => {
      const response = await apiClient.users.getMe();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: userData?.full_name || "",
      email: userData?.email || "",
    },
  });

  React.useEffect(() => {
    if (userData) {
      reset({
        full_name: userData.full_name || "",
        email: userData.email || "",
        preferences: userData.preferences || {},
      });
    }
  }, [userData, reset]);

  const updateMutation = useMutation({
    mutationFn: async (data: ProfileFormData) => {
      const response = await apiClient.users.updateMe(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      useAuthStore.getState().refreshUser();
      alert("Profile updated successfully!");
    },
    onError: (error: any) => {
      alert(error.response?.data?.error?.message || "Failed to update profile");
    },
  });

  const onSubmit = (data: ProfileFormData) => {
    updateMutation.mutate(data);
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-1/4" />
          <div className="h-64 bg-muted rounded" />
        </div>
      </div>
    );
  }

  const displayUser = userData || user;

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

      <div className="mx-auto max-w-2xl">
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-4 mb-4">
              <div className="h-16 w-16 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-2xl font-bold">
                {getInitials(displayUser.full_name || displayUser.username)}
              </div>
              <div>
                <CardTitle>{displayUser.full_name || displayUser.username}</CardTitle>
                <CardDescription>{displayUser.email}</CardDescription>
              </div>
            </div>
            <CardTitle>Edit Profile</CardTitle>
            <CardDescription>
              Update your personal information and preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>Full Name</span>
                </label>
                <Input
                  {...register("full_name")}
                  placeholder="Enter your full name"
                  error={errors.full_name?.message}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>Email</span>
                </label>
                <Input
                  type="email"
                  {...register("email")}
                  placeholder="Enter your email"
                  error={errors.email?.message}
                />
              </div>

              <div className="pt-4 border-t">
                <Link href="/dashboard/change-password">
                  <Button variant="outline" type="button" className="w-full">
                    <Lock className="mr-2 h-4 w-4" />
                    Change Password
                  </Button>
                </Link>
              </div>

              <div className="flex space-x-4">
                <Button
                  type="submit"
                  isLoading={updateMutation.isPending}
                  disabled={updateMutation.isPending}
                  className="flex-1"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}






