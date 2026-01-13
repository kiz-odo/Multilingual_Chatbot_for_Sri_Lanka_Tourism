/**
 * Trip Store - Zustand state management for trip planning
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Destination {
    id: string;
    name: string;
    type: 'attraction' | 'hotel' | 'restaurant' | 'activity';
    location: {
        lat: number;
        lng: number;
        address: string;
    };
    duration?: number; // in hours
    cost?: number;
    notes?: string;
}

export interface DayPlan {
    day: number;
    date: Date;
    destinations: Destination[];
    totalCost: number;
    totalDuration: number;
}

export interface TripPlan {
    id: string;
    userId?: string;
    title: string;
    description?: string;
    destinations: string[]; // city names
    startDate: Date;
    endDate: Date;
    days: DayPlan[];
    budget: number;
    travelers: number;
    preferences: {
        interests?: string[];
        pace?: 'relaxed' | 'moderate' | 'fast';
        accommodation?: 'budget' | 'mid-range' | 'luxury';
    };
    status: 'draft' | 'planned' | 'active' | 'completed';
    createdAt: Date;
    updatedAt: Date;
}

interface TripStore {
    // State
    trips: TripPlan[];
    currentTrip: TripPlan | null;
    isCreatingTrip: boolean;

    // Actions
    setTrips: (trips: TripPlan[]) => void;
    setCurrentTrip: (trip: TripPlan | null) => void;
    createTrip: (tripData: Omit<TripPlan, 'id' | 'createdAt' | 'updatedAt'>) => TripPlan;
    updateTrip: (tripId: string, updates: Partial<TripPlan>) => void;
    deleteTrip: (tripId: string) => void;

    // Draft management
    saveDraft: (tripData: Partial<TripPlan>) => void;
    loadDraft: () => TripPlan | null;
    clearDraft: () => void;

    // Day plan management
    addDay: (tripId: string, day: DayPlan) => void;
    updateDay: (tripId: string, dayNumber: number, updates: Partial<DayPlan>) => void;
    removeDay: (tripId: string, dayNumber: number) => void;

    // Destination management
    addDestination: (tripId: string, dayNumber: number, destination: Destination) => void;
    removeDestination: (tripId: string, dayNumber: number, destinationId: string) => void;
    reorderDestinations: (tripId: string, dayNumber: number, destinationIds: string[]) => void;

    // Utility
    setIsCreatingTrip: (isCreating: boolean) => void;
    reset: () => void;
}

export const useTripStore = create<TripStore>()(
    persist(
        (set, get) => ({
            // Initial state
            trips: [],
            currentTrip: null,
            isCreatingTrip: false,

            // Trip actions
            setTrips: (trips) => set({ trips }),

            setCurrentTrip: (trip) => set({ currentTrip: trip }),

            createTrip: (tripData) => {
                const trip: TripPlan = {
                    ...tripData,
                    id: `trip-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    createdAt: new Date(),
                    updatedAt: new Date(),
                };

                set((state) => ({
                    trips: [trip, ...state.trips],
                    currentTrip: trip,
                }));

                return trip;
            },

            updateTrip: (tripId, updates) => set((state) => {
                const updatedTrips = state.trips.map((trip) =>
                    trip.id === tripId
                        ? { ...trip, ...updates, updatedAt: new Date() }
                        : trip
                );

                const updatedCurrentTrip =
                    state.currentTrip?.id === tripId
                        ? { ...state.currentTrip, ...updates, updatedAt: new Date() }
                        : state.currentTrip;

                return {
                    trips: updatedTrips,
                    currentTrip: updatedCurrentTrip,
                };
            }),

            deleteTrip: (tripId) => set((state) => ({
                trips: state.trips.filter((trip) => trip.id !== tripId),
                currentTrip: state.currentTrip?.id === tripId ? null : state.currentTrip,
            })),

            // Draft management
            saveDraft: (tripData) => {
                const draft = {
                    ...tripData,
                    status: 'draft' as const,
                };
                localStorage.setItem('trip-draft', JSON.stringify(draft));
            },

            loadDraft: () => {
                const draftStr = localStorage.getItem('trip-draft');
                if (draftStr) {
                    try {
                        return JSON.parse(draftStr);
                    } catch (e) {
                        return null;
                    }
                }
                return null;
            },

            clearDraft: () => {
                localStorage.removeItem('trip-draft');
            },

            // Day plan management
            addDay: (tripId, day) => {
                get().updateTrip(tripId, {
                    days: [...(get().trips.find((t) => t.id === tripId)?.days || []), day],
                });
            },

            updateDay: (tripId, dayNumber, updates) => {
                const trip = get().trips.find((t) => t.id === tripId);
                if (!trip) return;

                const updatedDays = trip.days.map((day) =>
                    day.day === dayNumber ? { ...day, ...updates } : day
                );

                get().updateTrip(tripId, { days: updatedDays });
            },

            removeDay: (tripId, dayNumber) => {
                const trip = get().trips.find((t) => t.id === tripId);
                if (!trip) return;

                const updatedDays = trip.days.filter((day) => day.day !== dayNumber);
                get().updateTrip(tripId, { days: updatedDays });
            },

            // Destination management
            addDestination: (tripId, dayNumber, destination) => {
                const trip = get().trips.find((t) => t.id === tripId);
                if (!trip) return;

                const updatedDays = trip.days.map((day) => {
                    if (day.day === dayNumber) {
                        const newDestinations = [...day.destinations, destination];
                        return {
                            ...day,
                            destinations: newDestinations,
                            totalCost: newDestinations.reduce((sum, d) => sum + (d.cost || 0), 0),
                            totalDuration: newDestinations.reduce((sum, d) => sum + (d.duration || 0), 0),
                        };
                    }
                    return day;
                });

                get().updateTrip(tripId, { days: updatedDays });
            },

            removeDestination: (tripId, dayNumber, destinationId) => {
                const trip = get().trips.find((t) => t.id === tripId);
                if (!trip) return;

                const updatedDays = trip.days.map((day) => {
                    if (day.day === dayNumber) {
                        const newDestinations = day.destinations.filter((d) => d.id !== destinationId);
                        return {
                            ...day,
                            destinations: newDestinations,
                            totalCost: newDestinations.reduce((sum, d) => sum + (d.cost || 0), 0),
                            totalDuration: newDestinations.reduce((sum, d) => sum + (d.duration || 0), 0),
                        };
                    }
                    return day;
                });

                get().updateTrip(tripId, { days: updatedDays });
            },

            reorderDestinations: (tripId, dayNumber, destinationIds) => {
                const trip = get().trips.find((t) => t.id === tripId);
                if (!trip) return;

                const updatedDays = trip.days.map((day) => {
                    if (day.day === dayNumber) {
                        const reorderedDestinations = destinationIds
                            .map((id) => day.destinations.find((d) => d.id === id))
                            .filter(Boolean) as Destination[];

                        return {
                            ...day,
                            destinations: reorderedDestinations,
                        };
                    }
                    return day;
                });

                get().updateTrip(tripId, { days: updatedDays });
            },

            // Utility
            setIsCreatingTrip: (isCreating) => set({ isCreatingTrip: isCreating }),

            reset: () => set({
                trips: [],
                currentTrip: null,
                isCreatingTrip: false,
            }),
        }),
        {
            name: 'trip-storage',
            partialize: (state) => ({
                trips: state.trips,
            }),
        }
    )
);

// Selectors
export const useCurrentTrip = () => {
    return useTripStore((state) => state.currentTrip);
};

export const useActiveTips = () => {
    return useTripStore((state) =>
        state.trips.filter((trip) => trip.status === 'active')
    );
};

export const usePlannedTrips = () => {
    return useTripStore((state) =>
        state.trips.filter((trip) => trip.status === 'planned')
    );
};
