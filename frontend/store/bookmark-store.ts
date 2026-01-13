/**
 * Bookmark Store - Zustand state management for saved places
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type BookmarkType = 'attraction' | 'hotel' | 'restaurant' | 'event' | 'activity';

export interface Bookmark {
    id: string;
    itemId: string; // ID of the bookmarked item
    type: BookmarkType;
    name: string;
    description?: string;
    image?: string;
    location?: {
        lat: number;
        lng: number;
        address: string;
    };
    rating?: number;
    tags?: string[];
    notes?: string;
    createdAt: Date;
}

interface BookmarkStore {
    // State
    bookmarks: Bookmark[];

    // Actions
    setBookmarks: (bookmarks: Bookmark[]) => void;
    addBookmark: (bookmark: Omit<Bookmark, 'id' | 'createdAt'>) => void;
    removeBookmark: (bookmarkId: string) => void;
    updateBookmark: (bookmarkId: string, updates: Partial<Bookmark>) => void;
    isBookmarked: (itemId: string) => boolean;
    getBookmark: (itemId: string) => Bookmark | undefined;
    clearBookmarks: () => void;

    // Filter and sort
    getBookmarksByType: (type: BookmarkType) => Bookmark[];
    searchBookmarks: (query: string) => Bookmark[];
}

export const useBookmarkStore = create<BookmarkStore>()(
    persist(
        (set, get) => ({
            // Initial state
            bookmarks: [],

            // Actions
            setBookmarks: (bookmarks) => set({ bookmarks }),

            addBookmark: (bookmarkData) => {
                // Check if already bookmarked
                if (get().isBookmarked(bookmarkData.itemId)) {
                    console.warn('Item already bookmarked');
                    return;
                }

                const bookmark: Bookmark = {
                    ...bookmarkData,
                    id: `bookmark-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    createdAt: new Date(),
                };

                set((state) => ({
                    bookmarks: [bookmark, ...state.bookmarks],
                }));
            },

            removeBookmark: (bookmarkId) => set((state) => ({
                bookmarks: state.bookmarks.filter((b) => b.id !== bookmarkId),
            })),

            updateBookmark: (bookmarkId, updates) => set((state) => ({
                bookmarks: state.bookmarks.map((b) =>
                    b.id === bookmarkId ? { ...b, ...updates } : b
                ),
            })),

            isBookmarked: (itemId) => {
                return get().bookmarks.some((b) => b.itemId === itemId);
            },

            getBookmark: (itemId) => {
                return get().bookmarks.find((b) => b.itemId === itemId);
            },

            clearBookmarks: () => set({ bookmarks: [] }),

            // Filter and sort
            getBookmarksByType: (type) => {
                return get().bookmarks.filter((b) => b.type === type);
            },

            searchBookmarks: (query) => {
                const lowerQuery = query.toLowerCase();
                return get().bookmarks.filter(
                    (b) =>
                        b.name.toLowerCase().includes(lowerQuery) ||
                        b.description?.toLowerCase().includes(lowerQuery) ||
                        b.tags?.some((tag) => tag.toLowerCase().includes(lowerQuery))
                );
            },
        }),
        {
            name: 'bookmark-storage',
        }
    )
);

// Selectors
export const useBookmarkCount = () => {
    return useBookmarkStore((state) => state.bookmarks.length);
};

export const useAttractionBookmarks = () => {
    return useBookmarkStore((state) => state.getBookmarksByType('attraction'));
};

export const useHotelBookmarks = () => {
    return useBookmarkStore((state) => state.getBookmarksByType('hotel'));
};

export const useRestaurantBookmarks = () => {
    return useBookmarkStore((state) => state.getBookmarksByType('restaurant'));
};
