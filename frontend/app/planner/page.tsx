"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Search,
  X,
  Mountain,
  Building2,
  Umbrella,
  UtensilsCrossed,
  FileText,
  Calendar as CalendarIcon,
  MapPin,
  Plane,
  Train,
  Clock,
  DollarSign,
  Plus,
  MessageCircle,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import apiClient from "@/lib/api-client";
import { format, addDays, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isSameMonth, getDay } from "date-fns";

type BudgetLevel = "standard" | "balanced" | "luxury";
type TravelStyle = "adventure" | "culture" | "relax" | "food";

export default function PlannerPage() {
  const { user, isAuthenticated } = useAuthStore();
  const [selectedCities, setSelectedCities] = React.useState<string[]>(["Colombo", "Sigiriya"]);
  const [cityInput, setCityInput] = React.useState("");
  const [selectedDates, setSelectedDates] = React.useState<Date[]>([]);
  const [currentMonth, setCurrentMonth] = React.useState(new Date());
  const [budgetLevel, setBudgetLevel] = React.useState<BudgetLevel>("balanced");
  const [travelStyle, setTravelStyle] = React.useState<TravelStyle>("adventure");
  const [generatedItinerary, setGeneratedItinerary] = React.useState<any>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);

  // Calendar helpers
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });
  
  // Get first day of month to align calendar grid
  const firstDayOfMonth = getDay(monthStart);
  const emptyDays = Array(firstDayOfMonth).fill(null);

  const handleDateClick = (date: Date) => {
    if (isSameMonth(date, currentMonth)) {
      setSelectedDates((prev) => {
        const exists = prev.find((d) => isSameDay(d, date));
        if (exists) {
          return prev.filter((d) => !isSameDay(d, date));
        }
        return [...prev, date].sort((a, b) => a.getTime() - b.getTime());
      });
    }
  };

  const addCity = () => {
    if (cityInput.trim() && !selectedCities.includes(cityInput.trim())) {
      setSelectedCities([...selectedCities, cityInput.trim()]);
      setCityInput("");
    }
  };

  const removeCity = (city: string) => {
    setSelectedCities(selectedCities.filter((c) => c !== city));
  };

  const generateItinerary = async () => {
    if (selectedCities.length === 0 || selectedDates.length < 2) {
      alert("Please select at least one city and travel dates");
      return;
    }

    setIsGenerating(true);
    try {
      const startDate = selectedDates[0];
      const endDate = selectedDates[selectedDates.length - 1];
      const durationDays = selectedDates.length;

      // Map travel style to backend interests
      const interestsMap: Record<TravelStyle, string[]> = {
        adventure: ["adventure", "hiking", "nature"],
        culture: ["culture", "history", "temple"],
        relax: ["relaxation", "beach", "spa"],
        food: ["food", "culinary", "restaurant"],
      };

      const response = await apiClient.itinerary.generate({
        destination: selectedCities[0],
        duration_days: durationDays,
        start_date: format(startDate, "yyyy-MM-dd"),
        budget_level: budgetLevel,
        interests: interestsMap[travelStyle],
        travelers_count: 1,
        cities: selectedCities,
      } as any);

      setGeneratedItinerary(response.data || response);
    } catch (error) {
      console.error("Failed to generate itinerary:", error);
      // For demo, create mock itinerary
      setGeneratedItinerary(createMockItinerary());
    } finally {
      setIsGenerating(false);
    }
  };

  const createMockItinerary = () => {
    const startDate = selectedDates[0];
    return {
      id: "mock-1",
      days: [
        {
          day: 1,
          date: format(startDate, "yyyy-MM-dd"),
          title: "Arrival in Colombo & City Tour",
          activities: [
            {
              time: "09:00 AM",
              title: "Arrival",
              description: "Land at Bandaranaike International Airport. Meet your driver and enjoy a fresh king coconut drink.",
              icon: "plane",
            },
            {
              time: "02:00 PM",
              title: "Gangaramaya Temple",
              description: "Visit one of the most important temples in Colombo, mixing modern architecture and cultural essence.",
              icon: "temple",
            },
          ],
          image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
        },
        {
          day: 2,
          date: format(addDays(startDate, 1), "yyyy-MM-dd"),
          title: "Train to Kandy & Sacred Relics",
          activities: [
            {
              time: "08:30 AM",
              title: "Scenic Train Ride",
              description: "Experience one of the most beautiful train journeys in the world through lush tea estates.",
              icon: "train",
              duration: "3h 15m",
              cost: "~$12 USD",
            },
          ],
          image: "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&q=80",
        },
        {
          day: 3,
          date: format(addDays(startDate, 2), "yyyy-MM-dd"),
          title: "Sigiriya Rock Fortress",
          activities: [
            {
              time: "06:00 AM",
              title: "Sigiriya Rock Fortress",
              description: "Early morning climb to avoid the heat. Explore the ancient water gardens and frescoes atop the Lion Rock.",
              icon: "mountain",
            },
          ],
          image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
        },
      ],
      cities: selectedCities,
      travelStyle: travelStyle,
    };
  };

  const getActivityIcon = (iconName: string) => {
    const icons: Record<string, React.ReactNode> = {
      plane: <Plane className="w-4 h-4" />,
      train: <Train className="w-4 h-4" />,
      temple: <Building2 className="w-4 h-4" />,
      mountain: <Mountain className="w-4 h-4" />,
    };
    return icons[iconName] || <MapPin className="w-4 h-4" />;
  };

  const handlePDFExport = async () => {
    if (!generatedItinerary?.id) return;
    try {
      const response = await apiClient.itinerary.exportPDF(generatedItinerary.id);
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `itinerary-${generatedItinerary.id}.pdf`;
      a.click();
    } catch (error) {
      console.error("Failed to export PDF:", error);
    }
  };

  const handleCalendarSync = async () => {
    if (!generatedItinerary?.id) return;
    try {
      const response = await apiClient.itinerary.exportCalendarICS(generatedItinerary.id);
      const blob = new Blob([response.data], { type: "text/calendar" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `itinerary-${generatedItinerary.id}.ics`;
      a.click();
    } catch (error) {
      console.error("Failed to sync calendar:", error);
    }
  };

  const getTravelStyleSummary = () => {
    const styles = travelStyle === "adventure" ? "Adventure" : travelStyle === "culture" ? "Culture" : travelStyle === "relax" ? "Relax" : "Food";
    return styles;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative h-[400px] md:h-[500px] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1920&q=80"
            alt="Sigiriya Rock Fortress"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60" />
        </div>

        <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 text-center">
          <Button
            variant="outline"
            className="mb-4 bg-white/10 backdrop-blur-sm border-white/30 text-white hover:bg-white/20"
          >
            EXPLORE THE TROPICS
          </Button>
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4">
            Plan Your Island Escape
          </h1>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl">
            Experience the warmth of Sri Lanka with a perfectly curated itinerary powered by AI
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative -mt-20 md:-mt-32 px-4 md:px-8 lg:px-12 pb-12">
        <div className="grid lg:grid-cols-2 gap-4 md:gap-6 max-w-7xl mx-auto">
          {/* Left Panel - Trip Details */}
          <div className="bg-white rounded-2xl shadow-xl p-4 md:p-6 lg:p-8 z-10">
            <h2 className="text-2xl font-bold mb-6">Trip Details</h2>

            {/* City Search */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Where do you want to go?
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={cityInput}
                  onChange={(e) => setCityInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addCity();
                    }
                  }}
                  placeholder="Search cities (e.g. Kandy, Galle, Ella)"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              {selectedCities.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {selectedCities.map((city) => (
                    <Badge
                      key={city}
                      className="bg-teal-500 text-white px-3 py-1 flex items-center gap-2"
                    >
                      {city}
                      <button
                        onClick={() => removeCity(city)}
                        className="hover:bg-teal-600 rounded-full p-0.5"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Calendar */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Travel Dates
              </label>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <button
                    onClick={() =>
                      setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))
                    }
                    className="p-2 hover:bg-gray-100 rounded"
                  >
                    ←
                  </button>
                  <h3 className="font-semibold">
                    {format(currentMonth, "MMMM yyyy")}
                  </h3>
                  <button
                    onClick={() =>
                      setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))
                    }
                    className="p-2 hover:bg-gray-100 rounded"
                  >
                    →
                  </button>
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                    <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
                      {day}
                    </div>
                  ))}
                  {emptyDays.map((_, idx) => (
                    <div key={`empty-${idx}`} className="p-2" />
                  ))}
                  {daysInMonth.map((date, idx) => {
                    const isSelected = selectedDates.some((d) => isSameDay(d, date));
                    const isCurrentMonth = isSameMonth(date, currentMonth);
                    return (
                      <button
                        key={idx}
                        onClick={() => handleDateClick(date)}
                        className={`p-2 rounded text-sm ${
                          isSelected
                            ? "bg-teal-500 text-white"
                            : isCurrentMonth
                            ? "hover:bg-gray-100"
                            : "text-gray-300"
                        }`}
                        disabled={!isCurrentMonth}
                      >
                        {format(date, "d")}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Budget Slider */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Budget Range
              </label>
              <div className="relative">
                <div className="flex justify-between text-xs text-gray-500 mb-2">
                  <span>Standard</span>
                  <span>Balanced</span>
                  <span>Luxury</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="2"
                  value={budgetLevel === "standard" ? 0 : budgetLevel === "balanced" ? 1 : 2}
                  onChange={(e) => {
                    const val = parseInt(e.target.value);
                    setBudgetLevel(val === 0 ? "standard" : val === 1 ? "balanced" : "luxury");
                  }}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-500"
                />
                <div className="flex justify-center mt-2">
                  <Badge className="bg-teal-500 text-white">
                    {budgetLevel === "standard" ? "Standard" : budgetLevel === "balanced" ? "Mid-Range" : "Luxury"}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Travel Style */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Travel Style
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: "adventure", label: "Adventure", icon: Mountain },
                  { id: "culture", label: "Culture", icon: Building2 },
                  { id: "relax", label: "Relax", icon: Umbrella },
                  { id: "food", label: "Food", icon: UtensilsCrossed },
                ].map((style) => {
                  const Icon = style.icon;
                  const isSelected = travelStyle === style.id;
                  return (
                    <button
                      key={style.id}
                      onClick={() => setTravelStyle(style.id as TravelStyle)}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        isSelected
                          ? "border-teal-500 bg-teal-50 text-teal-700"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <Icon className={`w-6 h-6 mx-auto mb-2 ${isSelected ? "text-teal-600" : "text-gray-400"}`} />
                      <span className="text-sm font-medium">{style.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Generate Button */}
            <Button
              onClick={generateItinerary}
              disabled={isGenerating || selectedCities.length === 0 || selectedDates.length < 2}
              className="w-full bg-gradient-to-r from-teal-500 to-green-500 hover:from-teal-600 hover:to-green-600 text-white py-3 text-lg font-semibold"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              {isGenerating ? "Generating..." : "Generate AI Itinerary"}
            </Button>
          </div>

          {/* Right Panel - Itinerary Display */}
          <div className="bg-white rounded-2xl shadow-xl p-4 md:p-6 lg:p-8 z-10">
            {generatedItinerary ? (
              <>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold mb-1">Your Customized Itinerary</h2>
                    <p className="text-gray-600">
                      {generatedItinerary.days?.length || 0} Days • {selectedCities.length} Cities • {getTravelStyleSummary()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handlePDFExport}>
                      <FileText className="w-4 h-4 mr-2" />
                      PDF
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleCalendarSync}>
                      <CalendarIcon className="w-4 h-4 mr-2" />
                      Sync
                    </Button>
                  </div>
                </div>

                <div className="space-y-8">
                  {generatedItinerary.days?.map((day: any, idx: number) => (
                    <div key={idx} className="relative">
                      {/* Timeline Line */}
                      {idx < (generatedItinerary.days?.length || 0) - 1 && (
                        <div className="absolute left-5 md:left-6 top-16 md:top-20 bottom-0 w-0.5 bg-teal-200" />
                      )}

                      <div className="flex gap-4">
                        {/* Timeline Dot */}
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-teal-500 flex items-center justify-center text-white font-bold z-10 relative text-sm md:text-base">
                            {day.day || idx + 1}
                          </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 pb-8">
                          {day.image && (
                            <div className="relative h-48 md:h-64 rounded-lg overflow-hidden mb-4">
                              <Image
                                src={day.image}
                                alt={day.title || `Day ${day.day || idx + 1}`}
                                fill
                                className="object-cover"
                              />
                            </div>
                          )}

                          <Badge className="bg-green-500 text-white mb-3">
                            DAY {String(day.day || idx + 1).padStart(2, "0")}
                          </Badge>

                          <h3 className="text-xl font-bold mb-4">{day.title || `Day ${day.day || idx + 1}`}</h3>

                          <div className="space-y-4">
                            {day.activities?.map((activity: any, actIdx: number) => (
                              <div key={actIdx} className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 mt-1">
                                  {getActivityIcon(activity.icon || "map")}
                                </div>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-semibold text-gray-900">{activity.time}</span>
                                    <span className="text-gray-700">-</span>
                                    <span className="font-medium text-gray-900">{activity.title}</span>
                                  </div>
                                  <p className="text-gray-600 text-sm mb-2">{activity.description}</p>
                                  {(activity.duration || activity.cost) && (
                                    <div className="flex gap-4 text-xs text-gray-500">
                                      {activity.duration && (
                                        <div className="flex items-center gap-1">
                                          <Clock className="w-3 h-3" />
                                          {activity.duration}
                                        </div>
                                      )}
                                      {activity.cost && (
                                        <div className="flex items-center gap-1">
                                          <DollarSign className="w-3 h-3" />
                                          {activity.cost}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>

                          {idx === (generatedItinerary.days?.length || 0) - 1 && (
                            <div className="mt-6 border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                              <Plus className="w-6 h-6 text-gray-400 mx-auto mb-2" />
                              <p className="text-gray-500 text-sm">Add Activity</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full min-h-[400px] text-center">
                <div>
                  <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">No Itinerary Yet</h3>
                  <p className="text-gray-500">
                    Fill in your trip details and generate your personalized AI itinerary
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Floating AI Assistant Button */}
      <Link href="/chat">
        <button className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all z-50">
          <MessageCircle className="w-6 h-6" />
          <span className="sr-only">Ask AI Assistant</span>
        </button>
      </Link>
    </div>
  );
}
