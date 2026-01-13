/**
 * useMediaQuery - Responsive breakpoint detection
 */

import { useState, useEffect } from 'react';

export function useMediaQuery(query: string): boolean {
    const [matches, setMatches] = useState<boolean>(false);

    useEffect(() => {
        // Check if window is available (client-side)
        if (typeof window === 'undefined') {
            return;
        }

        const media = window.matchMedia(query);

        // Update initial state
        setMatches(media.matches);

        // Create listener
        const listener = (event: MediaQueryListEvent) => {
            setMatches(event.matches);
        };

        // Add listener (use deprecated addListener for older browsers)
        if (media.addEventListener) {
            media.addEventListener('change', listener);
        } else {
            // @ts-ignore - for older browsers
            media.addListener(listener);
        }

        // Cleanup
        return () => {
            if (media.removeEventListener) {
                media.removeEventListener('change', listener);
            } else {
                // @ts-ignore - for older browsers
                media.removeListener(listener);
            }
        };
    }, [query]);

    return matches;
}

// Predefined breakpoint hooks
export const useIsMobile = () => useMediaQuery('(max-width: 768px)');
export const useIsTablet = () => useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
export const useIsDesktop = () => useMediaQuery('(min-width: 1025px)');
export const useIsSmallScreen = () => useMediaQuery('(max-width: 640px)');
export const useIsLargeScreen = () => useMediaQuery('(min-width: 1280px)');
