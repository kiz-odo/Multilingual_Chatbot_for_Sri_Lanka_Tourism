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
import Link from "next/link";
import { ArrowLeft, Shield, Lock, Key, Smartphone, AlertTriangle } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

const passwordSchema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newPassword: z.string().min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string().min(8, "Password must be at least 8 characters"),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type PasswordFormData = z.infer<typeof passwordSchema>;

export default function SecurityPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const { addToast } = useToast();

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  // Fetch user security settings
  const { data: securityData } = useQuery({
    queryKey: ["user-security"],
    queryFn: async () => {
      const response = await apiClient.users.getMe();
      return {
        mfa_enabled: response.data.mfa_enabled || false,
        last_password_change: response.data.last_password_change,
        active_sessions: [],
      };
    },
    enabled: isAuthenticated,
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: async (data: PasswordFormData) => {
      await apiClient.auth.changePassword({
        current_password: data.currentPassword,
        new_password: data.newPassword,
      });
    },
    onSuccess: () => {
      addToast({
        title: "Success",
        description: "Password changed successfully",
        variant: "success",
      });
      reset();
    },
    onError: (error: any) => {
      addToast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to change password",
        variant: "error",
      });
    },
  });

  const onSubmit = (data: PasswordFormData) => {
    changePasswordMutation.mutate(data);
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
          <h1 className="text-3xl font-bold tracking-tight">Security Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account security and authentication settings
          </p>
        </div>

        {/* Change Password */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Lock className="h-5 w-5" />
              <span>Change Password</span>
            </CardTitle>
            <CardDescription>
              Update your account password to keep your account secure
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Current Password</label>
                <Input
                  type="password"
                  {...register("currentPassword")}
                  className={errors.currentPassword ? "border-red-500" : ""}
                />
                {errors.currentPassword && (
                  <p className="mt-1 text-sm text-red-600">{errors.currentPassword.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">New Password</label>
                <Input
                  type="password"
                  {...register("newPassword")}
                  className={errors.newPassword ? "border-red-500" : ""}
                />
                {errors.newPassword && (
                  <p className="mt-1 text-sm text-red-600">{errors.newPassword.message}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Password must be at least 8 characters long
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Confirm New Password</label>
                <Input
                  type="password"
                  {...register("confirmPassword")}
                  className={errors.confirmPassword ? "border-red-500" : ""}
                />
                {errors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting || changePasswordMutation.isPending}
                className="w-full"
              >
                {isSubmitting || changePasswordMutation.isPending ? "Changing..." : "Change Password"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Multi-Factor Authentication */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Smartphone className="h-5 w-5" />
              <span>Multi-Factor Authentication</span>
            </CardTitle>
            <CardDescription>
              Add an extra layer of security to your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">MFA Status</p>
                <p className="text-sm text-muted-foreground">
                  {securityData?.mfa_enabled ? "Enabled" : "Disabled"}
                </p>
              </div>
              <Link href="/dashboard/settings/mfa">
                <Button variant="outline">
                  {securityData?.mfa_enabled ? "Manage MFA" : "Enable MFA"}
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Active Sessions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Key className="h-5 w-5" />
              <span>Active Sessions</span>
            </CardTitle>
            <CardDescription>
              Manage devices where you're currently logged in
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {securityData?.active_sessions && securityData.active_sessions.length > 0 ? (
                securityData.active_sessions.map((session: any) => (
                  <div key={session.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{session.device || "Unknown Device"}</p>
                      <p className="text-sm text-muted-foreground">{session.location || "Unknown Location"}</p>
                      <p className="text-xs text-muted-foreground">Last active: {session.last_active}</p>
                    </div>
                    <Button variant="ghost" size="sm" className="text-red-600">
                      Revoke
                    </Button>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No active sessions found</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Security Recommendations */}
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-yellow-900">
              <AlertTriangle className="h-5 w-5" />
              <span>Security Recommendations</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-yellow-900">
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Use a strong, unique password that you don't use elsewhere</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Enable multi-factor authentication for added security</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Review and revoke access from devices you no longer use</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Change your password regularly, especially if you suspect a breach</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

