"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { 
  Compass, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff,
  RotateCcw,
  Sparkles,
  ArrowRight
} from "lucide-react";

const registerSchema = z
  .object({
    email: z.string().email("Invalid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser, isLoading } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const [error, setError] = React.useState<string | null>(null);
  const [showPassword, setShowPassword] = React.useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      // Generate username from email (remove @ and everything after)
      const username = data.email.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_").toLowerCase();
      // Ensure username is at least 3 characters
      const finalUsername = username.length >= 3 ? username : `user_${Date.now()}`;
      
      await registerUser({
        username: finalUsername,
        email: data.email,
        password: data.password,
      });
      router.push("/dashboard");
    } catch (err: any) {
      // Check for network errors
      if (err.code === "ERR_NETWORK" || err.message === "Network Error" || err.message?.includes("Unable to connect")) {
        setError(
          "Unable to connect to the server. Please check your internet connection and ensure the backend server is running. If the problem persists, please try again later."
        );
      } else if (err.response?.status === 400 || err.response?.status === 409) {
        // Validation or conflict errors
        const errorMessage = err.response?.data?.detail || 
                            err.response?.data?.error?.message ||
                            "Registration failed. Please check your information and try again.";
        setError(errorMessage);
      } else if (err.response?.status >= 500) {
        // Server errors
        setError("Server error occurred. Please try again later or contact support if the problem persists.");
      } else {
        // Other errors
        const errorMessage = err.response?.data?.detail || 
                            err.response?.data?.error?.message || 
                            "Registration failed. Please try again.";
        setError(errorMessage);
      }
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Side - Hero Image (50% width) */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
        {/* Background Image - Tea Plantations */}
        <div className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1516026672322-600c59507334?w=1200&h=800&fit=crop')",
          }}
        />
        
        {/* Dark Overlay */}
        <div className="absolute inset-0 bg-black/50"></div>
        
        {/* Overlay Content */}
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          {/* AI Powered Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-2 w-fit mb-6">
            <Sparkles className="w-4 h-4 text-teal-600" />
            <span className="text-sm font-bold text-gray-900">AI POWERED</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl font-bold mb-4 leading-tight">
            Your Personal Guide to Paradise
          </h1>
          
          {/* Description */}
          <p className="text-lg text-white/90 max-w-md leading-relaxed">
            Discover hidden gems, local favorites, and cultural treasures with the Sri Lanka Travel Buddy.
          </p>
        </div>
      </div>

      {/* Right Side - Register Form (50% width) */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-100">
        <div className="w-full max-w-md">
          {/* Logo & Heading */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center space-x-3 mb-6">
              <div className="w-12 h-12 rounded-full bg-teal-500 flex items-center justify-center">
                <Compass className="w-7 h-7 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900">Travel Buddy</span>
            </div>
            
            <h2 className="text-3xl font-bold mb-2 text-gray-900">Create Account</h2>
            <p className="text-teal-600">Start your adventure in just a few seconds.</p>
          </div>

          {/* Social Login Buttons */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              type="button"
              className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-white transition-colors bg-white shadow-sm"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC04"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="text-sm font-medium text-gray-900">Google</span>
            </button>

            <button
              type="button"
              className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
              <span className="text-sm font-medium">Facebook</span>
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-slate-100 text-gray-500">OR</span>
            </div>
          </div>

          {/* Register Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-teal-500" />
                </div>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="hello@example.com"
                  {...register("email")}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white text-gray-900 placeholder:text-gray-400"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-teal-500" />
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="••••••••"
                  {...register("password")}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white text-gray-900 placeholder:text-gray-400"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-teal-500" />
                  ) : (
                    <Eye className="h-5 w-5 text-teal-500" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <RotateCcw className="h-5 w-5 text-teal-500" />
                </div>
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="••••••••"
                  {...register("confirmPassword")}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white text-gray-900 placeholder:text-gray-400"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-teal-500" />
                  ) : (
                    <Eye className="h-5 w-5 text-teal-500" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Sign Up Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600 text-white font-bold py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign Up</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Footer Links */}
          <div className="mt-6 text-center space-y-2">
            <p className="text-sm text-gray-600">
              Already a member?{" "}
              <Link href="/auth/login" className="text-teal-600 font-medium hover:text-teal-700">
                Login
              </Link>
            </p>
            <div className="flex items-center justify-center space-x-2 text-xs text-gray-500">
              <Link href="/privacy" className="hover:text-gray-700">Privacy Policy</Link>
              <span>•</span>
              <Link href="/terms" className="hover:text-gray-700">Terms of Service</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
