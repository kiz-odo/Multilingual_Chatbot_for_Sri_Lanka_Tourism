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
  Home,
  Mail, 
  Lock, 
  Eye, 
  EyeOff,
  Globe,
  ChevronDown,
  ArrowRight,
  MapPin,
  Star
} from "lucide-react";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const [error, setError] = React.useState<string | null>(null);
  const [showPassword, setShowPassword] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      // Backend accepts username or email, so we can use email as username
      await login(data.email, data.password);
      
      // Handle remember me - store in localStorage if checked
      if (data.rememberMe) {
        localStorage.setItem("rememberMe", "true");
      } else {
        localStorage.removeItem("rememberMe");
      }
      
      router.push("/dashboard");
    } catch (err: any) {
      // Check for network errors
      if (err.code === "ERR_NETWORK" || err.message === "Network Error" || err.message?.includes("Unable to connect")) {
        setError(
          "Unable to connect to the server. Please check your internet connection and ensure the backend server is running. If the problem persists, please try again later."
        );
      } else if (err.response?.status === 401 || err.response?.status === 403) {
        // Authentication errors
        const errorMessage = err.response?.data?.detail || 
                            err.response?.data?.error?.message ||
                            "Invalid email or password. Please check your credentials and try again.";
        setError(errorMessage);
      } else if (err.response?.status >= 500) {
        // Server errors
        setError("Server error occurred. Please try again later or contact support if the problem persists.");
      } else {
        // Other errors
        const errorMessage = err.response?.data?.detail || 
                            err.response?.data?.error?.message ||
                            "An error occurred. Please try again.";
        setError(errorMessage);
      }
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Side - Login Form (50% width) */}
      <div className="w-full lg:w-1/2 flex flex-col bg-gray-900 text-white">
        {/* Header */}
        <div className="flex items-center justify-between p-6">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-lg bg-teal-500 flex items-center justify-center">
              <Home className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold">Sri Lanka AI</span>
          </div>

          {/* Language Selector */}
          <button className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors">
            <Globe className="w-4 h-4" />
            <span className="text-sm">English</span>
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>

        {/* Form Container */}
        <div className="flex-1 flex items-center justify-center px-8 pb-8">
          <div className="w-full max-w-md">
            {/* Welcome Message */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold mb-3">Welcome Back</h1>
              <p className="text-gray-400 text-lg">
                Log in to continue planning your perfect Sri Lankan adventure with your personal AI assistant.
              </p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {error && (
                <div
                  className="rounded-lg bg-red-500/10 border border-red-500/50 p-4 text-sm text-red-400"
                  role="alert"
                >
                  <div className="flex items-start space-x-2">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium mb-1">Login Failed</p>
                      <p className="text-red-300">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Email Address */}
              <div>
                <label className="block text-sm font-medium mb-2">
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
                    className="block w-full pl-10 pr-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                  />
                </div>
                {errors.email && (
                  <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
                )}
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium">
                    Password
                  </label>
                  <Link
                    href="/auth/forgot-password"
                    className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    {...register("password")}
                    className="block w-full pl-10 pr-10 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
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
                  <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
                )}
              </div>

              {/* Remember Me */}
              <div className="flex items-center">
                <input
                  id="rememberMe"
                  type="checkbox"
                  {...register("rememberMe")}
                  className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-gray-900"
                />
                <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-300">
                  Remember me for 30 days
                </label>
              </div>

              {/* Login Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Log In</span>
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>

            {/* Social Login Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-gray-900 text-gray-400">Or continue with</span>
              </div>
            </div>

            {/* Social Login Buttons */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <button
                type="button"
                className="flex items-center justify-center px-4 py-3 bg-white rounded-lg hover:bg-gray-100 transition-colors"
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
                className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
                <span className="text-sm font-medium">Facebook</span>
              </button>
            </div>

            {/* Registration Link */}
            <div className="text-center">
              <p className="text-sm text-gray-400">
                Don't have an account?{" "}
                <Link href="/auth/register" className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
                  Register Now
                </Link>
              </p>
            </div>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-gray-800">
              <div className="flex items-center justify-center space-x-2 text-xs text-gray-500">
                <Link href="/privacy" className="hover:text-gray-400 transition-colors">
                  Privacy Policy
                </Link>
                <span>•</span>
                <Link href="/terms" className="hover:text-gray-400 transition-colors">
                  Terms of Service
                </Link>
                <span>•</span>
                <span>© 2024 Sri Lanka AI Tourism</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Promotional Image (50% width) */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-teal-900 to-green-900">
        {/* Background Image - Nine Arches Bridge */}
        <div className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1200&h=800&fit=crop')",
          }}
        />
        
        {/* Dark Overlay */}
        <div className="absolute inset-0 bg-black/40"></div>
        
        {/* Overlay Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          {/* Top - Location Tag */}
          <div className="flex justify-end">
            <div className="flex items-center space-x-2 bg-black/60 backdrop-blur-sm rounded-lg px-4 py-2">
              <MapPin className="w-4 h-4" />
              <span className="text-sm font-medium">Nine Arches Bridge, Ella</span>
            </div>
          </div>

          {/* Middle - Content */}
          <div className="space-y-6">
            {/* Featured Destination Badge */}
            <div className="inline-flex items-center space-x-2 bg-black/60 backdrop-blur-sm rounded-lg px-4 py-2 w-fit">
              <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
              <span className="text-sm font-medium">Featured Destination</span>
            </div>

            {/* Headline */}
            <h2 className="text-5xl font-bold leading-tight">
              Discover the magic of Sri Lanka
            </h2>
            
            {/* Description */}
            <p className="text-lg text-white/90 max-w-md leading-relaxed">
              Let our advanced AI guide you through ancient cities, pristine beaches, and misty mountains. Your journey begins here.
            </p>
          </div>

          {/* Bottom - Social Proof */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="flex -space-x-2">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full bg-white/20 border-2 border-white/30 flex items-center justify-center text-xs font-bold"
                  >
                    {String.fromCharCode(65 + i)}
                  </div>
                ))}
                <div className="w-10 h-10 rounded-full bg-cyan-500 border-2 border-white/30 flex items-center justify-center text-xs font-bold">
                  2k+
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
            </div>
            <p className="text-sm text-white/80">Trusted by travelers</p>
          </div>
        </div>
      </div>
    </div>
  );
}
