/**
 * useGeolocation - Get user's current location
 */

import { useState, useEffect } from 'react';

interface GeolocationState {
    latitude: number | null;
    longitude: number | null;
    accuracy: number | null;
    error: string | null;
    loading: boolean;
}

export const useGeolocation = (options?: PositionOptions) => {
    const [state, setState] = useState<GeolocationState>({
        latitude: null,
        longitude: null,
        accuracy: null,
        error: null,
        loading: true,
    });

    useEffect(() => {
        if (!navigator.geolocation) {
            setState((prev) => ({
                ...prev,
                error: 'Geolocation is not supported by your browser',
                loading: false,
            }));
            return;
        }

        const handleSuccess = (position: GeolocationPosition) => {
            setState({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                error: null,
                loading: false,
            });
        };

        const handleError = (error: GeolocationPositionError) => {
            let errorMessage = 'An error occurred while getting location';

            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = 'Location permission denied';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = 'Location information unavailable';
                    break;
                case error.TIMEOUT:
                    errorMessage = 'Location request timed out';
                    break;
            }

            setState((prev) => ({
                ...prev,
                error: errorMessage,
                loading: false,
            }));
        };

        navigator.geolocation.getCurrentPosition(handleSuccess, handleError, options);
    }, [options]);

    return state;
};
