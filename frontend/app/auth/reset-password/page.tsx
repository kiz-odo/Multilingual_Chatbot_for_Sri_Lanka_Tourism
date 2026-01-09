"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { Compass, CheckCircle2, Lock, Eye, EyeOff, Mail, HelpCircle } from "lucide-react";

const resetPasswordSchema = z
  .object({
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { currentLanguage } = useLanguageStore();
  const [success, setSuccess] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const token = searchParams.get("token");

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const newPassword = watch("password");

  const getPasswordStrength = (password: string): {
    strength: "weak" | "medium" | "strong";
    message: string;
    width: string;
    color: string;
  } => {
    if (password.length < 8) {
      return { strength: "weak", message: "Too short", width: "w-1/3", color: "bg-red-500" };
    }
    if (password.length < 12) {
      return { strength: "medium", message: "Medium", width: "w-2/3", color: "bg-yellow-500" };
    }
    if (/[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) {
      return { strength: "strong", message: "Strong", width: "w-full", color: "bg-green-500" };
    }
    return { strength: "medium", message: "Medium", width: "w-2/3", color: "bg-yellow-500" };
  };

  const passwordStrength = newPassword ? getPasswordStrength(newPassword) : null;

  const resetPasswordMutation = useMutation({
    mutationFn: async (data: ResetPasswordFormData) => {
      if (!token) {
        throw new Error("Reset token is missing");
      }
      const response = await apiClient.auth.resetPassword(token, data.password);
      return response.data;
    },
    onSuccess: () => {
      setSuccess(true);
      setError(null);
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error?.message || 
                          "Failed to reset password. The token may be invalid or expired.";
      setError(errorMessage);
    },
  });

  const onSubmit = (data: ResetPasswordFormData) => {
    setError(null);
    resetPasswordMutation.mutate(data);
  };

  if (!token) {
    return (
      <div className="flex h-screen overflow-hidden">
        {/* Left Side - Hero Image */}
        <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
          <div className="absolute inset-0 bg-cover bg-center opacity-80"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&h=800&fit=crop')",
            }}
          />
          <div className="relative z-10 flex flex-col justify-between p-12 text-white">
            <div />
            <div>
              <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-6">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="text-sm font-medium">Discover the wonder of Asia</span>
              </div>
              <p className="text-lg text-white/90 max-w-md">
                Join thousands of travelers exploring the pristine beaches, timeless ruins, and welcoming people of Sri Lanka.
              </p>
            </div>
            <div />
          </div>
        </div>

        {/* Right Side - Error Message */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
          <div className="w-full max-w-md">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-cyan-500 flex items-center justify-center">
                  <Compass className="w-7 h-7 text-white" />
                </div>
                <span className="text-2xl font-bold text-gray-800">Sri Lanka Tourism Chatbot</span>
              </div>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Invalid Reset Link</h2>
              <p className="text-gray-600 mb-6">
                The password reset link is invalid or missing a token.
              </p>
              <Link href="/auth/forgot-password">
                <Button className="w-full bg-cyan-500 hover:bg-cyan-600 text-white">
                  Request New Reset Link
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="flex h-screen overflow-hidden">
        {/* Left Side - Hero Image */}
        <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
          <div className="absolute inset-0 bg-cover bg-center opacity-80"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&h=800&fit=crop')",
            }}
          />
          <div className="relative z-10 flex flex-col justify-between p-12 text-white">
            <div />
            <div>
              <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-6">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="text-sm font-medium">Discover the wonder of Asia</span>
              </div>
              <p className="text-lg text-white/90 max-w-md">
                Join thousands of travelers exploring the pristine beaches, timeless ruins, and welcoming people of Sri Lanka.
              </p>
            </div>
            <div />
          </div>
        </div>

        {/* Right Side - Success Message */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
          <div className="w-full max-w-md">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-cyan-500 flex items-center justify-center">
                  <Compass className="w-7 h-7 text-white" />
                </div>
                <span className="text-2xl font-bold text-gray-800">Sri Lanka Tourism Chatbot</span>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Password Reset Successful</h2>
              <p className="text-gray-600 mb-6">
                Your password has been reset successfully. You can now log in with your new password.
              </p>
              <Link href="/auth/login">
                <Button className="w-full bg-cyan-500 hover:bg-cyan-600 text-white">
                  Go to Login
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Side - Hero Image with Sigiriya */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
        {/* Background Image - Sigiriya */}
        <div className="absolute inset-0 bg-cover bg-center opacity-80"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&h=800&fit=crop')",
          }}
        />
        
        {/* Overlay Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          {/* Empty space for top */}
          <div />
          
          {/* Hero Text */}
          <div>
            <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-6">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-sm font-medium">Discover the wonder of Asia</span>
            </div>
            <p className="text-lg text-white/90 max-w-md">
              Join thousands of travelers exploring the pristine beaches, timeless ruins, and welcoming people of Sri Lanka.
            </p>
          </div>

          {/* Empty space for bottom */}
          <div />
        </div>
      </div>

      {/* Right Side - Reset Password Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          {/* Logo & Heading */}
          <div className="mb-8">
            <div className="inline-flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 rounded-full bg-cyan-500 flex items-center justify-center">
                <Compass className="w-7 h-7 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-800">Sri Lanka Tourism Chatbot</span>
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Reset your password</h1>
            <p className="text-gray-600">
              Don't worry, it happens. Please enter your new password below.
            </p>
          </div>

          {/* Reset Password Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {error && (
              <div
                className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800"
                role="alert"
              >
                {error}
              </div>
            )}

            {/* New Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="Enter your new password"
                  {...register("password")}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
              {passwordStrength && (
                <div className="mt-2 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Password strength:</span>
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
                  <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${passwordStrength.width} ${passwordStrength.color}`}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="Confirm your new password"
                  {...register("confirmPassword")}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Reset Password Button */}
            <button
              type="submit"
              disabled={resetPasswordMutation.isPending}
              className="w-full bg-cyan-500 hover:bg-cyan-600 text-white font-medium py-3 rounded-lg transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {resetPasswordMutation.isPending ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                "Reset Password"
              )}
            </button>
          </form>

          {/* Footer Links */}
          <div className="mt-6 space-y-3">
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Remember your password?{" "}
                <Link href="/auth/login" className="text-cyan-600 font-medium hover:text-cyan-700">
                  Log in
                </Link>
              </p>
            </div>
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
              <HelpCircle className="w-4 h-4" />
              <Link href="/support" className="hover:text-gray-700">
                Contact Support
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

