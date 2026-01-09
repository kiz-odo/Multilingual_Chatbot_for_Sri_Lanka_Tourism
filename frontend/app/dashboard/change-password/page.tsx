"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Lock, CheckCircle2 } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";

const changePasswordSchema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export default function ChangePasswordPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const [success, setSuccess] = React.useState(false);

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
  });

  const newPassword = watch("newPassword");

  const getPasswordStrength = (password: string): {
    strength: "weak" | "medium" | "strong";
    message: string;
  } => {
    if (password.length < 8) {
      return { strength: "weak", message: "Too short" };
    }
    if (password.length < 12) {
      return { strength: "medium", message: "Medium" };
    }
    if (/[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) {
      return { strength: "strong", message: "Strong" };
    }
    return { strength: "medium", message: "Medium" };
  };

  const passwordStrength = newPassword ? getPasswordStrength(newPassword) : null;

  const changePasswordMutation = useMutation({
    mutationFn: async (data: ChangePasswordFormData) => {
      await apiClient.auth.changePassword(data.currentPassword, data.newPassword);
    },
    onSuccess: () => {
      setSuccess(true);
    },
    onError: (error: any) => {
      alert(error.response?.data?.error?.message || "Failed to change password");
    },
  });

  const onSubmit = (data: ChangePasswordFormData) => {
    changePasswordMutation.mutate(data);
  };

  if (!isAuthenticated) {
    return null;
  }

  if (success) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mx-auto max-w-md">
          <Card>
            <CardHeader className="space-y-1 text-center">
              <div className="mx-auto mb-4 rounded-full bg-green-100 p-3">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
              <CardTitle className="text-2xl font-bold">
                Password Changed Successfully
              </CardTitle>
              <CardDescription>
                Your password has been updated. Please use your new password to log in.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => router.push("/dashboard")}
                className="w-full"
              >
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
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

      <div className="mx-auto max-w-md">
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold flex items-center space-x-2">
              <Lock className="h-5 w-5" />
              <span>Change Password</span>
            </CardTitle>
            <CardDescription>
              Update your password to keep your account secure
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                id="currentPassword"
                label="Current Password"
                type="password"
                autoComplete="current-password"
                {...register("currentPassword")}
                error={errors.currentPassword?.message}
                aria-required="true"
              />

              <div className="space-y-2">
                <Input
                  id="newPassword"
                  label="New Password"
                  type="password"
                  autoComplete="new-password"
                  {...register("newPassword")}
                  error={errors.newPassword?.message}
                  aria-required="true"
                />
                {passwordStrength && (
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Password strength:</span>
                      <span
                        className={`font-medium ${
                          passwordStrength.strength === "strong"
                            ? "text-green-600"
                            : passwordStrength.strength === "medium"
                            ? "text-yellow-600"
                            : "text-red-600"
                        }`}
                      >
                        {passwordStrength.message}
                      </span>
                    </div>
                    <div className="h-1 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          passwordStrength.strength === "strong"
                            ? "bg-green-600 w-full"
                            : passwordStrength.strength === "medium"
                            ? "bg-yellow-600 w-2/3"
                            : "bg-red-600 w-1/3"
                        }`}
                      />
                    </div>
                  </div>
                )}
              </div>

              <Input
                id="confirmPassword"
                label="Confirm New Password"
                type="password"
                autoComplete="new-password"
                {...register("confirmPassword")}
                error={errors.confirmPassword?.message}
                aria-required="true"
              />

              <Button
                type="submit"
                className="w-full"
                isLoading={changePasswordMutation.isPending}
                disabled={changePasswordMutation.isPending}
              >
                Change Password
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}






