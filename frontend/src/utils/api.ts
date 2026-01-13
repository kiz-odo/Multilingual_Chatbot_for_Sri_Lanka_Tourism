/**
 * API Client - Additional API integrations
 * Speech, Landmark, Notification, and Admin APIs
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

/**
 * Speech API - Voice interactions
 */
export const speechAPI = {
    /**
     * Convert speech audio to text
     * @param audioBlob - Audio file to transcribe
     * @param language - Language code (en, si, ta, etc.)
     */
    speechToText: async (audioBlob: Blob, language?: string) => {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');
        if (language) {
            formData.append('language', language);
        }

        const response = await api.post('/api/v1/speech/speech-to-text', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    /**
     * Convert text to speech audio
     * @param text - Text to convert
     * @param language - Language code (en, si, ta, etc.)
     */
    textToSpeech: async (text: string, language: string = 'en') => {
        const formData = new FormData();
        formData.append('text', text);
        formData.append('language', language);

        const response = await api.post('/api/v1/speech/text-to-speech', formData, {
            responseType: 'blob',
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    /**
     * Get supported languages for speech services
     */
    getSupportedLanguages: async () => {
        const response = await api.get('/api/v1/speech/supported-languages');
        return response.data;
    },

    /**
     * Analyze sentiment from audio
     * @param audioBlob - Audio file to analyze
     */
    analyzeSentiment: async (audioBlob: Blob) => {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');

        const response = await api.post('/api/v1/speech/analyze-sentiment', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
};

/**
 * Landmark API - Image recognition
 */
export const landmarkAPI = {
    /**
     * Recognize landmark from image
     * @param imageFile - Image file to analyze
     */
    recognize: async (imageFile: File) => {
        const formData = new FormData();
        formData.append('image', imageFile);

        const response = await api.post('/api/v1/landmarks/recognize', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    /**
     * Get popular landmarks
     */
    getPopular: async () => {
        const response = await api.get('/api/v1/landmarks/popular');
        return response.data;
    },
};

/**
 * Notification API - Real-time notifications
 */
export const notificationAPI = {
    /**
     * Get user notifications
     */
    getNotifications: async () => {
        const response = await api.get('/api/v1/users/notifications');
        return response.data;
    },

    /**
     * Mark notification as read
     * @param notificationId - ID of notification to mark
     */
    markAsRead: async (notificationId: string) => {
        const response = await api.put(`/api/v1/users/notifications/${notificationId}/read`);
        return response.data;
    },

    /**
     * Mark all notifications as read
     */
    markAllAsRead: async () => {
        const response = await api.put('/api/v1/users/notifications/mark-all-read');
        return response.data;
    },

    /**
     * Delete notification
     * @param notificationId - ID of notification to delete
     */
    deleteNotification: async (notificationId: string) => {
        const response = await api.delete(`/api/v1/users/notifications/${notificationId}`);
        return response.data;
    },
};

/**
 * Admin API - Admin panel operations
 */
export const adminAPI = {
    /**
     * Get all users (admin only)
     */
    getUsers: async (page: number = 1, limit: number = 50) => {
        const response = await api.get('/api/v1/admin/users', {
            params: { page, limit },
        });
        return response.data;
    },

    /**
     * Get user details (admin only)
     * @param userId - ID of user
     */
    getUserDetails: async (userId: string) => {
        const response = await api.get(`/api/v1/admin/users/${userId}`);
        return response.data;
    },

    /**
     * Update user (admin only)
     * @param userId - ID of user
     * @param data - User data to update
     */
    updateUser: async (userId: string, data: any) => {
        const response = await api.put(`/api/v1/admin/users/${userId}`, data);
        return response.data;
    },

    /**
     * Delete user (admin only)
     * @param userId - ID of user
     */
    deleteUser: async (userId: string) => {
        const response = await api.delete(`/api/v1/admin/users/${userId}`);
        return response.data;
    },

    /**
     * Get system statistics (admin only)
     */
    getStatistics: async () => {
        const response = await api.get('/api/v1/admin/statistics');
        return response.data;
    },

    /**
     * Get analytics data (admin only)
     */
    getAnalytics: async (startDate?: string, endDate?: string) => {
        const response = await api.get('/api/v1/admin/analytics', {
            params: { start_date: startDate, end_date: endDate },
        });
        return response.data;
    },
};

/**
 * Forum API - Community forum
 */
export const forumAPI = {
    /**
     * Get forum posts
     */
    getPosts: async (page: number = 1, limit: number = 20) => {
        const response = await api.get('/api/v1/forum/posts', {
            params: { page, limit },
        });
        return response.data;
    },

    /**
     * Create new post
     * @param data - Post data
     */
    createPost: async (data: { title: string; content: string; category?: string }) => {
        const response = await api.post('/api/v1/forum/posts', data);
        return response.data;
    },

    /**
     * Get post by ID
     * @param postId - ID of post
     */
    getPost: async (postId: string) => {
        const response = await api.get(`/api/v1/forum/posts/${postId}`);
        return response.data;
    },

    /**
     * Reply to post
     * @param postId - ID of post
     * @param content - Reply content
     */
    replyToPost: async (postId: string, content: string) => {
        const response = await api.post(`/api/v1/forum/posts/${postId}/reply`, { content });
        return response.data;
    },

    /**
     * Delete post
     * @param postId - ID of post
     */
    deletePost: async (postId: string) => {
        const response = await api.delete(`/api/v1/forum/posts/${postId}`);
        return response.data;
    },
};

/**
 * Challenges API - Gamification
 */
export const challengesAPI = {
    /**
     * Get all challenges
     */
    getChallenges: async () => {
        const response = await api.get('/api/v1/challenges');
        return response.data;
    },

    /**
     * Get user challenges progress
     */
    getUserChallenges: async () => {
        const response = await api.get('/api/v1/challenges/user');
        return response.data;
    },

    /**
     * Update challenge progress
     * @param challengeId - ID of challenge
     * @param progress - Progress data
     */
    updateProgress: async (challengeId: string, progress: any) => {
        const response = await api.put(`/api/v1/challenges/${challengeId}/progress`, progress);
        return response.data;
    },

    /**
     * Claim challenge reward
     * @param challengeId - ID of challenge
     */
    claimReward: async (challengeId: string) => {
        const response = await api.post(`/api/v1/challenges/${challengeId}/claim`);
        return response.data;
    },
};

export default api;
