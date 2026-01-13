"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Phone,
  Shield,
  Ambulance,
  Flame,
  Flag,
  MapPin,
  Clock,
  ChevronLeft,
  Home,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import apiClient from "@/lib/api-client";

export default function EmergencyContactsPage() {
  const { currentLanguage } = useLanguageStore();

  // Fetch emergency numbers
  const { data: emergencyNumbers } = useQuery({
    queryKey: ["emergency-numbers"],
    queryFn: async () => {
      try {
        const response = await apiClient.safety.getEmergencyNumbers();
        return response.data || {};
      } catch {
        return {
          police: "119",
          ambulance: "1990",
          fire: "110",
          tourist_police: "1912",
        };
      }
    },
  });

  // Fetch embassy contacts
  const { data: embassies = [] } = useQuery({
    queryKey: ["embassies"],
    queryFn: async () => {
      try {
        const response = await apiClient.safety.getEmbassies();
        return response.data || [];
      } catch {
        return [
          {
            id: "1",
            country: "United States",
            name: "U.S. Embassy",
            phone: "+94 11 202-8500",
            address: "210 Galle Road, Colombo 03",
          },
          {
            id: "2",
            country: "United Kingdom",
            name: "British High Commission",
            phone: "+94 11 539-0639",
            address: "389 Bauddhaloka Mawatha, Colombo 07",
          },
        ];
      }
    },
  });

  const emergencyServices = [
    {
      id: "police",
      title: "Police Emergency",
      number: emergencyNumbers?.police || "119",
      icon: Shield,
      color: "blue",
      description: "For all police emergencies",
    },
    {
      id: "ambulance",
      title: "Ambulance",
      number: emergencyNumbers?.ambulance || "1990",
      icon: Ambulance,
      color: "green",
      description: "Medical emergencies",
    },
    {
      id: "fire",
      title: "Fire & Rescue",
      number: emergencyNumbers?.fire || "110",
      icon: Flame,
      color: "orange",
      description: "Fire emergencies",
    },
    {
      id: "tourist",
      title: "Tourist Police",
      number: emergencyNumbers?.tourist_police || "1912",
      icon: Shield,
      color: "purple",
      description: "Tourist assistance",
    },
  ];

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
          <span className="text-gray-900 font-medium">Emergency Contacts</span>
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
              <h1 className="text-4xl font-bold text-gray-900">Emergency Contacts</h1>
              <p className="text-gray-600 mt-2">
                Quick access to emergency services and embassy contacts
              </p>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Emergency Services */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Emergency Services</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {emergencyServices.map((service) => {
                const Icon = service.icon;
                const colorClasses = {
                  blue: "bg-blue-100 text-blue-600",
                  green: "bg-green-100 text-green-600",
                  orange: "bg-orange-100 text-orange-600",
                  purple: "bg-purple-100 text-purple-600",
                };

                return (
                  <Card key={service.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className={`w-12 h-12 rounded-full ${colorClasses[service.color as keyof typeof colorClasses]} flex items-center justify-center`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <a href={`tel:${service.number}`}>
                          <Button variant="ghost" size="sm" className="p-2">
                            <Phone className="w-5 h-5" />
                          </Button>
                        </a>
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-1">{service.title}</h3>
                      <p className="text-2xl font-bold text-gray-900 mb-2">{service.number}</p>
                      <p className="text-sm text-gray-600">{service.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Embassy Contacts */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Embassy Contacts</h2>
            <div className="space-y-4">
              {embassies.length > 0 ? (
                embassies.map((embassy: any) => (
                  <Card key={embassy.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Flag className="w-5 h-5 text-gray-400" />
                            <h3 className="font-semibold text-gray-900">{embassy.name}</h3>
                          </div>
                          <p className="text-sm text-gray-600 mb-3">{embassy.country}</p>
                          {embassy.address && (
                            <div className="flex items-start gap-2 mb-3 text-sm text-gray-600">
                              <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
                              <span>{embassy.address}</span>
                            </div>
                          )}
                          {embassy.phone && (
                            <a
                              href={`tel:${embassy.phone.replace(/\s/g, "")}`}
                              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
                            >
                              <Phone className="w-4 h-4" />
                              <span>{embassy.phone}</span>
                            </a>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="p-6 text-center text-gray-500">
                    <p>Embassy information will be available soon</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>

        {/* Additional Resources */}
        <div className="mt-12">
          <Card className="bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
            <CardContent className="p-6">
              <h3 className="font-bold text-gray-900 mb-2">Important Reminder</h3>
              <p className="text-gray-700 text-sm">
                In case of any emergency, dial the appropriate number immediately. For tourist-specific
                assistance, contact Tourist Police at 1912. Always keep your location sharing enabled when
                traveling in unfamiliar areas.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


