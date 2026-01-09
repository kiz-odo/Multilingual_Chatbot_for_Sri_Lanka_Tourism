"use client";

import * as React from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";
import { 
  MessageSquare, 
  Mail, 
  HelpCircle,
  Search
} from "lucide-react";

const forgotPasswordSchema = z.object({
  email: z.string().email("Invalid email address"),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const { currentLanguage } = useLanguageStore();
  const [emailSent, setEmailSent] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const forgotPasswordMutation = useMutation({
    mutationFn: async (email: string) => {
      const response = await apiClient.auth.forgotPassword(email);
      return response.data;
    },
    onSuccess: () => {
      setEmailSent(true);
      setError(null);
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.error?.message || 
                          "Failed to send reset email. Please try again.";
      setError(errorMessage);
    },
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setError(null);
    forgotPasswordMutation.mutate(data.email);
  };

  if (emailSent) {
    return (
      <div className="flex h-screen overflow-hidden">
        {/* Left Side - Hero Image (50% width) */}
        <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
          <div className="absolute inset-0 bg-cover bg-center opacity-80"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&h=800&fit=crop')",
            }}
          />
          <div className="relative z-10 flex flex-col justify-end p-12 text-white">
            <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-6">
              <Search className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-medium">Discover the wonder of Asia</span>
            </div>
            <p className="text-lg text-white/90 max-w-md">
              Join thousands of travelers exploring the pristine beaches, timeless ruins, and welcoming people of Sri Lanka.
            </p>
          </div>
        </div>

        {/* Right Side - Success Message (50% width) */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
          <div className="w-full max-w-md">
            <div className="mb-8">
              <div className="inline-flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-cyan-500 flex items-center justify-center">
                  <MessageSquare className="w-7 h-7 text-white" />
                </div>
                <span className="text-2xl font-bold text-gray-900">Sri Lanka Tourism Chatbot</span>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email</h2>
              <p className="text-gray-600 mb-6">
                We've sent a password reset link to your email address. Please check your inbox and follow the instructions to reset your password.
              </p>
              <div className="space-y-3">
                <button
                  onClick={() => setEmailSent(false)}
                  className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Try Again
                </button>
                <Link href="/auth/login">
                  <button className="w-full px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors">
                    Back to Login
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Side - Hero Image (50% width) */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
        {/* Background Image - Sigiriya */}
        <div className="absolute inset-0 bg-cover bg-center opacity-80"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&h=800&fit=crop')",
          }}
        />
        
        {/* Overlay Content */}
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          {/* Text Overlay */}
          <div>
            <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-6">
              <Search className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-medium">Discover the wonder of Asia</span>
            </div>
            <p className="text-lg text-white/90 max-w-md">
              Join thousands of travelers exploring the pristine beaches, timeless ruins, and welcoming people of Sri Lanka.
            </p>
          </div>
        </div>
      </div>

      {/* Right Side - Forgot Password Form (50% width) */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="mb-8">
            <div className="inline-flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 rounded-full bg-cyan-500 flex items-center justify-center">
                <MessageSquare className="w-7 h-7 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900">Sri Lanka Tourism Chatbot</span>
            </div>
          </div>

          {/* Main Content */}
          <div className="space-y-6">
            {/* Title */}
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Reset your password
              </h1>
              <p className="text-gray-600">
                Don't worry, it happens. Please enter the email address linked to your account.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {error && (
                <div
                  className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800"
                  role="alert"
                >
                  {error}
                </div>
              )}

              {/* Email Address */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    placeholder="name@example.com"
                    {...register("email")}
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                  />
                </div>
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>

              {/* Send Reset Link Button */}
              <button
                type="submit"
                disabled={forgotPasswordMutation.isPending}
                className="w-full bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {forgotPasswordMutation.isPending ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  "Send Reset Link"
                )}
              </button>
            </form>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Remember your password?{" "}
                <Link href="/auth/login" className="text-cyan-500 font-bold hover:text-cyan-600 transition-colors">
                  Log in
                </Link>
              </p>
            </div>

            {/* Support Link */}
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500 pt-4 border-t border-gray-200">
              <HelpCircle className="w-4 h-4" />
              <Link href="/support" className="hover:text-gray-700 transition-colors">
                Contact Support
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
