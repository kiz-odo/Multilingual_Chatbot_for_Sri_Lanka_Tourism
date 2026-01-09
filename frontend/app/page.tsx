"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { trackPageView } from "@/lib/analytics";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  MessageSquare,
  Compass,
  Calendar,
  MapPin,
  Heart,
  Sparkles,
  ArrowRight,
  Bot,
  Copy,
  Lock,
  BookOpen,
  Users,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { useAuthStore } from "@/store/auth-store";
import { getLocalizedText } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { Attraction } from "@/types";
import Image from "next/image";

export default function HomePage() {
  const { currentLanguage } = useLanguageStore();
  const { isAuthenticated, user } = useAuthStore();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    trackPageView("/");
  }, []);

  // Fetch featured/trending attractions
  const { data: attractionsData, isLoading } = useQuery({
    queryKey: ["attractions", "featured", currentLanguage],
    queryFn: async () => {
      try {
        // Try featured endpoint first
        const response = await apiClient.attractions.getFeatured({
          language: currentLanguage
        });
        const data = Array.isArray(response.data) ? response.data : [];
        return data.slice(0, 4);
      } catch {
        // Fallback to list if featured endpoint fails
        try {
          const response = await apiClient.attractions.list({
            featured_only: true,
            limit: 4,
            language: currentLanguage,
          } as any);
          return response.data?.items || [];
        } catch {
          return [];
        }
      }
    },
  });

  const featuredAttractions: Attraction[] = Array.isArray(attractionsData)
    ? attractionsData
    : attractionsData?.items || [];

  // Default destinations if API fails
  const defaultDestinations = [
    {
      id: "sigiriya",
      name: { en: "Sigiriya Rock Fortress", si: "සීගිරිය", ta: "சிகிரியா" },
      location: { city: "Central Province", province: "Central Province" },
      images: [{ url: "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&h=600&fit=crop" }],
    },
    {
      id: "mirissa",
      name: { en: "Mirissa Beach", si: "මිරිස්ස", ta: "மிரிசா" },
      location: { city: "South Coast", province: "Southern Province" },
      images: [{ url: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop" }],
    },
    {
      id: "nuwara-eliya",
      name: { en: "Nuwara Eliya", si: "නුවර එළිය", ta: "நுவரெலியா" },
      location: { city: "Hill Country", province: "Central Province" },
      images: [{ url: "https://images.unsplash.com/photo-1516026672322-600c59507334?w=800&h=600&fit=crop" }],
    },
    {
      id: "nine-arch",
      name: { en: "Nine Arch Bridge", si: "නව අංශ පාලම", ta: "ஒன்பது வளைவு பாலம்" },
      location: { city: "Uva Province", province: "Uva Province" },
      images: [{ url: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop" }],
    },
  ];

  const displayAttractions = featuredAttractions.length > 0
    ? featuredAttractions.slice(0, 4)
    : defaultDestinations;

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-animated-slow py-12 sm:py-20 lg:py-24">
        {/* Gradient Mesh Background */}
        <div className="absolute inset-0 bg-gradient-mesh opacity-50"></div>

        {/* Decorative Floating Elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-teal-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-cyan-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-green-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: '4s' }}></div>

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            {/* Left Side - Content */}
            <div
              className={`space-y-6 ${mounted ? 'animate-fade-in' : 'opacity-0'}`}
              style={{ animationDelay: '0.1s' }}
            >
              {/* Badge with Glassmorphism */}
              <div className="inline-flex items-center space-x-2 glass-white rounded-full px-6 py-3 text-sm font-bold shadow-glow animate-float-subtle">
                <Sparkles className="w-5 h-5 text-teal-600" />
                <span className="bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
                  MULTILINGUAL AI CHATBOT
                </span>
              </div>

              {/* Headline with Gradient Text */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
                <span className="text-gray-900">Explore Sri Lanka with an{" "}</span>
                <span className="gradient-text block mt-2 text-shadow-soft">AI Travel Assistant</span>
              </h1>

              {/* Subtitle */}
              <p className="text-lg sm:text-xl text-gray-700 leading-relaxed max-w-xl font-medium">
                Get instant personalized itineraries, safety tips, and cultural insights. Your 24/7 guide for the perfect island getaway.
              </p>

              {/* CTA Buttons with Enhanced Effects */}
              <div className="flex flex-wrap gap-4 pt-2">
                <Link href="/chat">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white font-semibold shadow-glow hover:shadow-intense transition-all duration-300 transform hover:scale-105 hover-lift"
                  >
                    <MessageSquare className="mr-2 h-5 w-5" />
                    Start Chat
                  </Button>
                </Link>
                <Link href="/explore">
                  <Button
                    size="lg"
                    className="glass-white border-2 border-white/40 backdrop-blur-custom font-semibold shadow-premium hover:shadow-glow transition-all duration-300 transform hover:scale-105"
                  >
                    <Compass className="mr-2 h-5 w-5 text-teal-600" />
                    <span className="text-gray-800">Explore Attractions</span>
                  </Button>
                </Link>
                <Link href="/planner">
                  <Button
                    size="lg"
                    className="glass-white border-2 border-white/40 backdrop-blur-custom font-semibold shadow-premium hover:shadow-glow transition-all duration-300 transform hover:scale-105"
                  >
                    <Calendar className="mr-2 h-5 w-5 text-teal-600" />
                    <span className="text-gray-800">Plan My Trip</span>
                  </Button>
                </Link>
              </div>

              {/* Social Proof */}
              <div className="flex items-center space-x-4 pt-4">
                <div className="flex -space-x-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-teal-500 border-3 border-white flex items-center justify-center text-white text-sm font-bold shadow-premium hover:scale-110 transition-transform cursor-default"
                      style={{ animationDelay: `${i * 0.2}s` }}
                    >
                      {String.fromCharCode(65 + i)}
                    </div>
                  ))}
                </div>
                <div className="text-sm text-gray-700">
                  <span className="font-bold text-gray-900 text-lg">+2k</span>{" "}
                  <span className="font-medium">2,000+ travelers helped this month</span>
                </div>
              </div>
            </div>

            {/* Right Side - Image with Chat Bubble */}
            <div
              className={`relative ${mounted ? 'animate-fade-in' : 'opacity-0'}`}
              style={{ animationDelay: '0.3s' }}
            >
              <div className="relative rounded-3xl overflow-hidden shadow-intense hover-lift">
                <div className="aspect-[4/3] relative">
                  <Image
                    src="https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&h=900&fit=crop"
                    alt="Sigiriya Rock Fortress"
                    fill
                    className="object-cover"
                    priority
                  />
                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent"></div>
                </div>

                {/* Chat Bubble Overlay with Glassmorphism */}
                <div className="absolute bottom-8 left-8 right-8 glass-white rounded-2xl shadow-intense p-6 animate-slide-up backdrop-blur-custom">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-glow">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-sm font-bold text-cyan-600 uppercase tracking-wide">AI Assistant</span>
                  </div>
                  <p className="text-gray-800 mb-4 leading-relaxed font-medium">
                    "Ayubowan! Ready to discover the pearl of the Indian Ocean? I can help you find hidden waterfalls in Ella or the best surf spots in Arugam Bay."
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <button className="px-4 py-2 glass hover:bg-white/30 rounded-xl text-sm font-semibold text-gray-800 transition-all hover:scale-105 shadow-sm hover:shadow-md">
                      Plan a 7-day trip
                    </button>
                    <button className="px-4 py-2 glass hover:bg-white/30 rounded-xl text-sm font-semibold text-gray-800 transition-all hover:scale-105 shadow-sm hover:shadow-md">
                      Visa info
                    </button>
                    <button className="px-4 py-2 glass hover:bg-white/30 rounded-xl text-sm font-semibold text-gray-800 transition-all hover:scale-105 shadow-sm hover:shadow-md">
                      Train schedules
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Your Personal Sri Lanka Expert Section */}
      <section className="py-16 sm:py-24 bg-white relative overflow-hidden">
        {/* Subtle Background Pattern */}
        <div className="absolute inset-0 bg-gradient-mesh opacity-30"></div>

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-12 animate-scale-in">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Your Personal <span className="gradient-text">Sri Lanka Expert</span>
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto font-medium">
              Whether you are looking for adventure, relaxation, or culture, our AI tools make planning effortless.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Instant Travel Chat */}
            <div className="group relative bg-gradient-to-br from-cyan-500 to-teal-500 rounded-3xl p-8 text-white shadow-glow hover:shadow-intense transition-all duration-500 transform hover:-translate-y-3 card-3d overflow-hidden">
              {/* Animated Background Pattern */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white rounded-full filter blur-3xl animate-float"></div>
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-white rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
              </div>

              <div className="relative z-10">
                <div className="w-16 h-16 glass-white rounded-2xl flex items-center justify-center mb-6 backdrop-blur-sm shadow-premium group-hover:scale-110 transition-transform duration-300">
                  <MessageSquare className="w-8 h-8 text-cyan-500" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-shadow-soft">Instant Travel Chat</h3>
                <p className="text-white/95 mb-6 leading-relaxed">
                  Ask about weather, transport, or local customs in English, Sinhala, or Tamil. Get accurate, real-time answers instantly.
                </p>
                <Link href="/chat">
                  <span className="inline-flex items-center text-white font-bold hover:underline cursor-pointer group-hover:translate-x-2 transition-transform duration-300">
                    Start chatting <ArrowRight className="ml-2 w-5 h-5" />
                  </span>
                </Link>
              </div>
            </div>

            {/* Smart Itinerary Planner */}
            <div className="group relative bg-gradient-to-br from-teal-500 to-green-500 rounded-3xl p-8 text-white shadow-glow-green hover:shadow-intense transition-all duration-500 transform hover:-translate-y-3 card-3d overflow-hidden">
              {/* Animated Background Pattern */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500">
                <div className="absolute top-0 left-0 w-32 h-32 bg-white rounded-full filter blur-3xl animate-float"></div>
                <div className="absolute bottom-0 right-0 w-32 h-32 bg-white rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
              </div>

              <div className="relative z-10">
                <div className="w-16 h-16 glass-white rounded-2xl flex items-center justify-center mb-6 backdrop-blur-sm shadow-premium group-hover:scale-110 transition-transform duration-300">
                  <BookOpen className="w-8 h-8 text-teal-500" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-shadow-soft">Smart Itinerary Planner</h3>
                <p className="text-white/95 mb-6 leading-relaxed">
                  Tell us your dates and interests. We'll generate a day-by-day plan optimized for travel times and your budget.
                </p>
                <Link href="/planner">
                  <span className="inline-flex items-center text-white font-bold hover:underline cursor-pointer group-hover:translate-x-2 transition-transform duration-300">
                    Plan trip <ArrowRight className="ml-2 w-5 h-5" />
                  </span>
                </Link>
              </div>
            </div>

            {/* Cultural & Safety Guide */}
            <div className="group relative bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl p-8 text-white shadow-glow hover:shadow-intense transition-all duration-500 transform hover:-translate-y-3 card-3d overflow-hidden">
              {/* Animated Background Pattern */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white rounded-full filter blur-3xl animate-float"></div>
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-white rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
              </div>

              <div className="relative z-10">
                <div className="w-16 h-16 glass-white rounded-2xl flex items-center justify-center mb-6 backdrop-blur-sm shadow-premium group-hover:scale-110 transition-transform duration-300">
                  <Lock className="w-8 h-8 text-emerald-500" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-shadow-soft">Cultural & Safety Guide</h3>
                <p className="text-white/95 mb-6 leading-relaxed">
                  Navigate Sri Lanka respectfully with etiquette tips and stay safe with real-time alerts and emergency contacts.
                </p>
                <Link href="/safety">
                  <span className="inline-flex items-center text-white font-bold hover:underline cursor-pointer group-hover:translate-x-2 transition-transform duration-300">
                    View guides <ArrowRight className="ml-2 w-5 h-5" />
                  </span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trending Destinations Section */}
      <section className="py-16 sm:py-24 bg-gradient-to-b from-gray-50 to-white relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float-subtle"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-teal-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float-subtle" style={{ animationDelay: '3s' }}></div>

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="flex items-center justify-between mb-12">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                Trending <span className="gradient-text">Destinations</span>
              </h2>
              <p className="text-gray-600 font-medium">Most visited places this season</p>
            </div>
            <Link href="/explore">
              <Button variant="ghost" className="text-cyan-600 hover:text-cyan-700 font-semibold hover:bg-cyan-50">
                View all places <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>

          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white rounded-3xl overflow-hidden shadow-premium">
                  <div className="h-64 bg-gray-200 animate-shimmer" />
                  <div className="p-5 space-y-3">
                    <div className="h-5 bg-gray-200 rounded-lg w-3/4 animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded-lg w-1/2 animate-pulse" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {displayAttractions.map((attraction, index) => {
                const name = getLocalizedText(attraction.name, currentLanguage) ||
                  (typeof attraction.name === 'string' ? attraction.name : attraction.name?.en || '');
                const location = attraction.location?.city || attraction.location?.province || '';
                const imageUrl = attraction.images?.[0]?.url ||
                  (attraction.id === 'sigiriya' ? 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&h=600&fit=crop' :
                    attraction.id === 'mirissa' ? 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop' :
                      attraction.id === 'nuwara-eliya' ? 'https://images.unsplash.com/photo-1516026672322-600c59507334?w=800&h=600&fit=crop' :
                        'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop');

                return (
                  <Link
                    key={attraction.id}
                    href={`/explore/attractions/${attraction.id}`}
                    className="group"
                  >
                    <div
                      className="relative bg-white rounded-3xl overflow-hidden shadow-premium hover:shadow-intense transition-all duration-500 transform hover:-translate-y-3 card-3d"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="relative h-64 overflow-hidden">
                        <Image
                          src={imageUrl}
                          alt={name}
                          fill
                          className="object-cover group-hover:scale-110 transition-transform duration-700"
                        />
                        {/* Gradient Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-80 group-hover:opacity-90 transition-opacity duration-300"></div>

                        {/* Favorite Button with Glassmorphism */}
                        <div className="absolute top-4 right-4">
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                            }}
                            className="w-11 h-11 rounded-full glass-white backdrop-blur-custom flex items-center justify-center hover:scale-110 transition-all shadow-premium hover:shadow-glow"
                          >
                            <Heart className="w-5 h-5 text-red-500" />
                          </button>
                        </div>

                        {/* Location Badge */}
                        <div className="absolute bottom-4 left-4">
                          <Badge className="glass-white backdrop-blur-custom text-white font-bold text-xs px-3 py-1.5 shadow-premium">
                            {location.toUpperCase()}
                          </Badge>
                        </div>
                      </div>

                      {/* Card Content */}
                      <div className="p-5 relative">
                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-cyan-600 transition-colors duration-300 mb-1">
                          {name}
                        </h3>
                        <div className="flex items-center text-sm text-gray-500">
                          <MapPin className="w-4 h-4 mr-1" />
                          <span>{location}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Floating Chat Button with Pulse Glow */}
      <Link
        href="/chat"
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gradient-to-br from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white rounded-full shadow-glow flex items-center justify-center hover:scale-110 transition-all duration-300 animate-pulse-glow"
        aria-label="Start chat"
      >
        <MessageSquare className="w-7 h-7" />
      </Link>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.8s ease-out forwards;
        }

        .animate-slide-up {
          animation: slide-up 0.6s ease-out 0.5s forwards;
          opacity: 0;
        }

        .animate-bounce-slow {
          animation: bounce-slow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
