/**
 * Error Handler - Centralized error handling utility
 */

import { AxiosError } from 'axios';

/**
 * Custom Application Error class
 */
export class AppError extends Error {
    constructor(
        public statusCode: number,
        public message: string,
        public code?: string,
        public details?: any
    ) {
        super(message);
        this.name = 'AppError';
        Object.setPrototypeOf(this, AppError.prototype);
    }
}

/**
 * API Error Response interface
 */
interface APIErrorResponse {
    message: string;
    code?: string;
    details?: any;
    errors?: Record<string, string[]>;
}

/**
 * Handle API errors from axios
 * @param error - Error object from axios
 * @returns AppError instance
 */
export const handleApiError = (error: unknown): AppError => {
    // Axios error with response
    if (error instanceof AxiosError && error.response) {
        const { status, data } = error.response;
        const errorData = data as APIErrorResponse;

        return new AppError(
            status,
            errorData.message || 'An error occurred',
            errorData.code,
            errorData.details || errorData.errors
        );
    }

    // Axios error without response (network error)
    if (error instanceof AxiosError && error.request) {
        return new AppError(
            0,
            'Network error - unable to reach the server',
            'NETWORK_ERROR'
        );
    }

    // Other axios errors
    if (error instanceof AxiosError) {
        return new AppError(
            500,
            error.message || 'An unexpected error occurred',
            'AXIOS_ERROR'
        );
    }

    // AppError instances
    if (error instanceof AppError) {
        return error;
    }

    // Generic errors
    if (error instanceof Error) {
        return new AppError(500, error.message, 'UNKNOWN_ERROR');
    }

    // Unknown error type
    return new AppError(500, 'An unexpected error occurred', 'UNKNOWN_ERROR');
};

/**
 * Get user-friendly error message based on status code
 * @param statusCode - HTTP status code
 * @param fallbackMessage - Fallback message if no specific message found
 * @returns User-friendly error message
 */
export const getUserFriendlyMessage = (
    statusCode: number,
    fallbackMessage?: string
): string => {
    const messages: Record<number, string> = {
        0: 'Unable to connect to the server. Please check your internet connection and try again.',
        400: 'Invalid request. Please check your input and try again.',
        401: 'You are not authorized. Please log in and try again.',
        403: 'You do not have permission to perform this action.',
        404: 'The requested resource was not found.',
        409: 'This action conflicts with existing data.',
        422: 'The data provided could not be processed. Please check and try again.',
        429: 'Too many requests. Please wait a moment and try again.',
        500: 'Server error. Please try again later.',
        502: 'Bad gateway. The server is temporarily unavailable.',
        503: 'Service unavailable. Please try again later.',
        504: 'Gateway timeout. The server took too long to respond.',
    };

    return messages[statusCode] || fallbackMessage || 'An unexpected error occurred';
};

/**
 * Log error (can be extended to send to monitoring service)
 * @param error - Error to log
 * @param context - Additional context about where the error occurred
 */
export const logError = (error: unknown, context?: string) => {
    const appError = handleApiError(error);

    console.error('Error:', {
        context,
        statusCode: appError.statusCode,
        message: appError.message,
        code: appError.code,
        details: appError.details,
        stack: appError.stack,
    });

    // TODO: Send to error tracking service (e.g., Sentry)
    // if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    //   Sentry.captureException(appError, { extra: { context } });
    // }
};

/**
 * Format validation errors from API
 * @param errors - Validation errors object from API
 * @returns Formatted error messages
 */
export const formatValidationErrors = (
    errors: Record<string, string[]>
): Record<string, string> => {
    const formatted: Record<string, string> = {};

    for (const [field, messages] of Object.entries(errors)) {
        formatted[field] = messages.join(', ');
    }

    return formatted;
};

/**
 * Check if error is a specific type
 * @param error - Error to check
 * @param code - Error code to match
 * @returns True if error matches the code
 */
export const isErrorCode = (error: unknown, code: string): boolean => {
    if (error instanceof AppError) {
        return error.code === code;
    }
    return false;
};

/**
 * Check if error is authentication error
 * @param error - Error to check
 * @returns True if error is 401 Unauthorized
 */
export const isAuthError = (error: unknown): boolean => {
    if (error instanceof AppError) {
        return error.statusCode === 401;
    }
    return false;
};

/**
 * Check if error is network error
 * @param error - Error to check
 * @returns True if error is network error
 */
export const isNetworkError = (error: unknown): boolean => {
    if (error instanceof AppError) {
        return error.statusCode === 0 || error.code === 'NETWORK_ERROR';
    }
    return false;
};

/**
 * Retry function with exponential backoff
 * @param fn - Function to retry
 * @param maxRetries - Maximum number of retries
 * @param baseDelay - Base delay in milliseconds
 * @returns Result of the function
 */
export const retryWithBackoff = async <T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
): Promise<T> => {
    let lastError: unknown;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            // Don't retry on auth errors or client errors
            if (error instanceof AppError) {
                if (error.statusCode >= 400 && error.statusCode < 500 && error.statusCode !== 429) {
                    throw error;
                }
            }

            // Wait before retrying (exponential backoff)
            if (attempt < maxRetries - 1) {
                const delay = baseDelay * Math.pow(2, attempt);
                await new Promise((resolve) => setTimeout(resolve, delay));
            }
        }
    }

    throw lastError;
};

/**
 * Create error toast message object
 * @param error - Error to create toast for
 * @returns Toast message object
 */
export const createErrorToast = (error: unknown) => {
    const appError = handleApiError(error);

    return {
        type: 'error' as const,
        title: getErrorTitle(appError.statusCode),
        message: getUserFriendlyMessage(appError.statusCode, appError.message),
    };
};

/**
 * Get error title based on status code
 * @param statusCode - HTTP status code
 * @returns Error title
 */
const getErrorTitle = (statusCode: number): string => {
    if (statusCode === 0) return 'Connection Error';
    if (statusCode >= 400 && statusCode < 500) return 'Request Error';
    if (statusCode >= 500) return 'Server Error';
    return 'Error';
};
