import axios, { AxiosInstance, AxiosError } from "axios";

// In browser, use relative URLs which will be proxied by Next.js rewrites
// In server-side, use direct backend URL
const isServer = typeof window === "undefined";
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
// Use relative URLs in browser to leverage Next.js proxy and avoid CORS issues
const API_BASE_URL = isServer ? `${BACKEND_URL}/api/v1` : "/api/v1";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 150000, // 150 seconds (2.5 minutes) for AI responses - increased to accommodate 90s backend timeout
      withCredentials: !isServer, // Enable credentials only in browser
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        // Handle network errors
        if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
          const networkError = new Error(
            `Cannot connect to backend server. Please ensure the backend is running on port 8001.`
          ) as AxiosError;
          networkError.code = error.code;
          return Promise.reject(networkError);
        }

        // Handle timeout errors
        if (error.code === "ECONNABORTED") {
          const requestUrl = error.config?.url || "unknown endpoint";
          const isChatRequest = requestUrl.includes("/chat/");

          console.error(
            `Request Timeout: API server took too long to respond for ${requestUrl}`,
            isChatRequest
              ? "\nNote: AI chat responses can take longer. Please wait or try again."
              : ""
          );

          const timeoutError = new Error(
            isChatRequest
              ? "The AI is still processing your request. This can happen with complex questions that require searching multiple sources. Please wait a moment and try again, or try asking a simpler question."
              : "Request timeout: The API server took too long to respond. Please try again."
          ) as AxiosError;
          timeoutError.code = error.code;
          timeoutError.message = timeoutError.message;
          return Promise.reject(timeoutError);
        }

        // Handle connection refused errors
        if (error.code === "ECONNREFUSED" || error.code === "ERR_CONNECTION_REFUSED") {
          console.error(
            `Connection Refused: API server at ${API_BASE_URL} is not accepting connections`,
            "\nPlease start the backend server"
          );
          const connectionError = new Error(
            `Connection refused: The API server at ${API_BASE_URL} is not running. Please start the backend server.`
          ) as AxiosError;
          connectionError.code = error.code;
          return Promise.reject(connectionError);
        }

        // Handle 401 Unauthorized
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          if (typeof window !== "undefined") {
            window.location.href = "/auth/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("auth_token");
  }

  private clearToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
  }

  setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("auth_token", token);
  }

  clearAuth(): void {
    this.clearToken();
  }

  // Auth endpoints
  auth = {
    register: (data: {
      username: string;
      email: string;
      password: string;
      full_name?: string;
      preferences?: any;
    }) => this.client.post("/auth/register", data),

    login: (username: string, password: string) =>
      this.client.post(
        "/auth/login",
        new URLSearchParams({ username, password }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      ),

    logout: () => this.client.post("/auth/logout"),

    refresh: () => this.client.post("/auth/refresh"),

    forgotPassword: (email: string) =>
      this.client.post("/auth/forgot-password", { email }),

    resetPassword: (token: string, newPassword: string) =>
      this.client.post("/auth/reset-password", { token, new_password: newPassword }),

    changePassword: (currentPassword: string, newPassword: string) =>
      this.client.post("/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      }),

    verifyToken: (token: string) =>
      this.client.get("/auth/verify-token", { params: { token } }),

    enableMFA: () => this.client.post("/auth/enable-mfa"),

    verifyMFA: (code: string) =>
      this.client.post("/auth/verify-mfa", { code }),

    disableMFA: () => this.client.post("/auth/disable-mfa"),

    getMe: () => this.client.get("/auth/me"),

    updateMe: (data: any) => this.client.put("/auth/me", data),
  };

  // User endpoints
  users = {
    getMe: () => this.client.get("/users/me"),
    updateMe: (data: any) => this.client.put("/users/me", data),
    deleteMe: () => this.client.delete("/users/me"),
    deleteMyData: () => this.client.delete("/users/me/data"),
    getBadges: () => this.client.get("/users/me/badges"),
    addFavoriteAttraction: (attractionId: string) =>
      this.client.post(`/users/me/favorites/attractions/${attractionId}`),
    removeFavoriteAttraction: (attractionId: string) =>
      this.client.delete(`/users/me/favorites/attractions/${attractionId}`),
    markVisited: (placeId: string) =>
      this.client.post(`/users/me/visited/${placeId}`),
    getStats: () => this.client.get("/users/me/stats"),
    exportData: () => this.client.get("/users/me/export"),
    downloadExport: () => this.client.get("/users/me/export/download", { responseType: "blob" }),
  };

  // Chat endpoints
  chat = {
    sendMessage: (data: {
      message: string;
      language?: string;
      session_id?: string;
    }) => this.client.post("/chat/message", {
      ...data,
      message_type: "text"
    }, {
      timeout: 150000, // 150 seconds (2.5 minutes) for AI chat responses
      headers: {
        "X-Request-Timeout": "150", // Tell backend to allow 150 seconds
      },
    }),

    sendVoice: (audio: File | Blob, data: { user_id: string; language?: string }) => {
      const formData = new FormData();
      formData.append("audio", audio);
      formData.append("user_id", data.user_id);
      if (data.language) formData.append("language", data.language);
      return this.client.post("/chat/voice", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000, // 2 minutes for voice processing
      });
    },

    detectLanguage: (message: string) =>
      this.client.post("/chat/detect-language", { message }),

    getConversations: () => this.client.get("/chat/conversations"),

    getConversation: (conversationId: string) =>
      this.client.get(`/chat/conversations/${conversationId}`),

    deleteConversation: (conversationId: string) =>
      this.client.delete(`/chat/conversations/${conversationId}`),

    getHistory: (userId: string, params?: { limit?: number; offset?: number }) =>
      this.client.get(`/chat/history/${userId}`, { params }),

    getAllHistory: () => this.client.get("/chat/history"),

    clearAllHistory: () => this.client.delete("/chat/history"),

    clearHistory: (userId: string) =>
      this.client.delete(`/chat/history/${userId}`),

    getSuggestions: () => this.client.get("/chat/suggestions"),

    getSupportedLanguages: () => this.client.get("/chat/supported-languages"),

    setContext: (data: { user_id: string; context: any }) =>
      this.client.post("/chat/context", data),

    uploadImage: (image: File | Blob, data: { user_id: string; language?: string }) => {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("user_id", data.user_id);
      if (data.language) formData.append("language", data.language);
      return this.client.post("/chat/upload-image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000, // 2 minutes for image processing with AI
      });
    },

    uploadAudio: (audio: File | Blob, data: { user_id: string; language?: string }) => {
      const formData = new FormData();
      formData.append("audio", audio);
      formData.append("user_id", data.user_id);
      if (data.language) formData.append("language", data.language);
      return this.client.post("/chat/upload-audio", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000, // 2 minutes for audio processing with AI
      });
    },

    submitFeedback: (data: {
      message_id: string;
      user_id: string;
      rating: number;
      feedback?: string;
      feedback_type?: string;
    }) => this.client.post("/chat/feedback", data),
  };

  // Attractions endpoints
  attractions = {
    list: (params?: {
      skip?: number;
      limit?: number;
      category?: string;
      city?: string;
      province?: string;
      featured_only?: boolean;
      language?: string;
    }) => this.client.get("/attractions/", { params }),

    get: (id: string, params?: { language?: string }) =>
      this.client.get(`/attractions/${id}`, { params }),

    search: (params: {
      q?: string;
      category?: string;
      city?: string;
      province?: string;
      min_rating?: number;
      max_price?: number;
      language?: string;
    }) => this.client.get("/attractions/search", { params }),

    getCategories: () => this.client.get("/attractions/categories"),

    getFeatured: (params?: { language?: string }) =>
      this.client.get("/attractions/featured", { params }),

    getPopular: (params?: { language?: string }) =>
      this.client.get("/attractions/popular", { params }),

    nearby: (params: {
      lat: number;
      lng: number;
      radius?: number;
      limit?: number;
    }) => this.client.get("/attractions/nearby", { params }),

    getReviews: (id: string, params?: { skip?: number; limit?: number }) =>
      this.client.get(`/attractions/${id}/reviews`, { params }),

    addReview: (id: string, data: { rating: number; comment: string }) =>
      this.client.post(`/attractions/${id}/reviews`, data),

    addFavorite: (id: string) =>
      this.client.post(`/attractions/${id}/favorite`),

    removeFavorite: (id: string) =>
      this.client.delete(`/attractions/${id}/favorite`),

    create: (data: any) => this.client.post("/attractions/", data),
  };

  // Hotels endpoints
  hotels = {
    list: (params?: {
      skip?: number;
      limit?: number;
      city?: string;
      star_rating?: number;
      language?: string;
    }) => this.client.get("/hotels/", { params }),

    get: (id: string, params?: { language?: string }) =>
      this.client.get(`/hotels/${id}`, { params }),

    search: (params: {
      check_in?: string;
      check_out?: string;
      guests?: number;
      city?: string;
      star_rating?: number;
      max_price?: number;
    }) => this.client.get("/hotels/search", { params }),
  };

  // Restaurants endpoints
  restaurants = {
    list: (params?: {
      skip?: number;
      limit?: number;
      cuisine_type?: string;
      city?: string;
      price_range?: string;
      language?: string;
    }) => this.client.get("/restaurants/", { params }),

    get: (id: string, params?: { language?: string }) =>
      this.client.get(`/restaurants/${id}`, { params }),

    search: (params: {
      q?: string;
      cuisine_type?: string;
      city?: string;
    }) => this.client.get("/restaurants/search", { params }),
  };

  // Transport endpoints
  transport = {
    list: (params?: {
      skip?: number;
      limit?: number;
      transport_type?: string;
      origin?: string;
      destination?: string;
      language?: string;
    }) => this.client.get("/transport/", { params }),

    get: (id: string) => this.client.get(`/transport/${id}`),

    search: (params: {
      origin?: string;
      destination?: string;
      transport_type?: string;
      date?: string;
    }) => this.client.get("/transport/search", { params }),

    searchRoutes: (params: {
      origin?: string;
      destination?: string;
      transport_type?: string;
      date?: string;
    }) => this.client.get("/transport/search", { params }), // Alias
  };

  // Events endpoints
  events = {
    list: (params?: {
      category?: string;
      start_date?: string;
      end_date?: string;
      date_from?: string;
      date_to?: string;
      city?: string;
      status?: string;
      limit?: number;
      language?: string;
    }) => this.client.get("/events/", { params }),

    get: (id: string) => this.client.get(`/events/${id}`),

    search: (params: { q?: string; city?: string; date_from?: string; date_to?: string; category?: string }) =>
      this.client.get("/events/search", { params }),
  };

  // Itinerary endpoints
  itinerary = {
    generate: (data: {
      destination?: string;
      duration_days?: number;
      budget_level?: string;
      interests?: string[];
      start_date?: string;
      travelers_count?: number;
      custom_requirements?: string;
      travel_dates?: { start: string; end: string };
      cities?: string[];
      budget?: number;
      preferences?: string[];
    }) => this.client.post("/itinerary/generate", data),

    create: (data: {
      travel_dates: { start: string; end: string };
      cities: string[];
      budget?: number;
      preferences?: string[];
    }) => this.client.post("/itinerary/generate", data), // Alias for generate

    getMyItineraries: () => this.client.get("/itinerary/my-itineraries"),

    get: (id: string) => this.client.get(`/itinerary/${id}`),

    getByShareToken: (token: string) =>
      this.client.get(`/itinerary/share/${token}`),

    update: (id: string, data: any) =>
      this.client.put(`/itinerary/${id}`, data),

    delete: (id: string) => this.client.delete(`/itinerary/${id}`),

    book: (id: string, data: any) =>
      this.client.post(`/itinerary/${id}/book`, data),

    exportPDF: (id: string) =>
      this.client.post(`/itinerary/${id}/export/pdf`, {}, { responseType: "blob" }),

    exportCalendarICS: (id: string) =>
      this.client.post(`/itinerary/${id}/export/calendar/ics`, {}, { responseType: "blob" }),

    exportCalendarGoogle: (id: string) =>
      this.client.post(`/itinerary/${id}/export/calendar/google`, {}),

    exportCalendar: (id: string) =>
      this.client.post(`/itinerary/${id}/export/calendar/ics`, {}, { responseType: "blob" }), // Alias
  };

  // Recommendations endpoints
  recommendations = {
    get: (data: {
      user_id: string;
      preferences?: string[];
      location?: [number, number];
      limit?: number;
    }) => this.client.post("/recommendations", data),

    getSimilar: (resourceType: string, resourceId: string, params?: { limit?: number }) =>
      this.client.get(`/recommendations/similar/${resourceType}/${resourceId}`, { params }),

    getAttractions: (params?: { user_id?: string; location?: [number, number]; limit?: number }) =>
      this.client.get("/recommendations/attractions", { params }),

    getItineraries: (params?: { user_id?: string; limit?: number }) =>
      this.client.get("/recommendations/itineraries", { params }),

    getBasedOnLocation: (params: { lat: number; lng: number; radius?: number; limit?: number }) =>
      this.client.get("/recommendations/based-on-location", { params }),
  };

  // Maps endpoints
  maps = {
    geocode: (address: string) =>
      this.client.post("/maps/geocode", { address }),

    reverseGeocode: (lat: number, lng: number) =>
      this.client.post("/maps/reverse-geocode", { lat, lng }),

    searchPlaces: (params: {
      query: string;
      location?: { lat: number; lng: number };
      radius?: number;
      type?: string;
    }) => this.client.post("/maps/search-places", params),

    getPlace: (placeId: string) =>
      this.client.get(`/maps/place/${placeId}`),

    getDirections: (params: {
      origin: string;
      destination: string;
      mode?: string;
    }) => this.client.post("/maps/directions", params),

    getNearby: (params: {
      lat: number;
      lng: number;
      type?: string;
      radius?: number;
    }) => this.client.get("/maps/nearby", { params }),

    getNearbyAttractions: (params: {
      lat: number;
      lng: number;
      radius?: number;
    }) => this.client.get("/maps/nearby-attractions", { params }),

    getNearbyRestaurants: (params: {
      lat: number;
      lng: number;
      radius?: number;
    }) => this.client.get("/maps/nearby-restaurants", { params }),

    getNearbyHotels: (params: {
      lat: number;
      lng: number;
      radius?: number;
    }) => this.client.get("/maps/nearby-hotels", { params }),

    getDistanceMatrix: (params: {
      origins: Array<{ lat: number; lng: number } | string>;
      destinations: Array<{ lat: number; lng: number } | string>;
      mode?: string;
    }) => this.client.post("/maps/distance-matrix", params),
  };

  // Weather endpoints
  weather = {
    getCurrent: (params: { city?: string; lat?: number; lng?: number }) =>
      this.client.get("/weather/current", { params }),

    get: (city: string) => this.client.get(`/weather/current?city=${city}`), // Alias

    getForecast: (params: { city?: string; days?: number }) =>
      this.client.get("/weather/forecast", { params }),

    getAlerts: (params?: { city?: string }) =>
      this.client.get("/weather/alerts", { params }),

    getSummary: (params?: { city?: string }) =>
      this.client.get("/weather/summary", { params }),

    getCities: () => this.client.get("/weather/cities"),

    getRecommendations: (params?: { city?: string; activity?: string }) =>
      this.client.get("/weather/recommendations", { params }),

    getIcon: (iconCode: string) =>
      this.client.get(`/weather/icon/${iconCode}`, { responseType: "blob" }),
  };

  // Currency endpoints
  currency = {
    convert: (params: {
      amount: number;
      from: string;
      to: string;
    }) => this.client.post("/currency/convert", params),

    getRates: (params?: { base?: string }) =>
      this.client.get("/currency/rates", { params }),

    getSriLankaRates: () => this.client.get("/currency/sri-lanka-rates"),

    getCurrencies: () => this.client.get("/currency/currencies"),

    getCurrencyInfo: (code: string) =>
      this.client.get(`/currency/currency/${code}`),

    getRecommendations: (params?: { amount?: number; from?: string }) =>
      this.client.get("/currency/recommendations", { params }),

    getSummary: () => this.client.get("/currency/summary"),

    format: (amount: number, currency: string) =>
      this.client.get(`/currency/format/${amount}`, { params: { currency } }),

    check: (code: string) => this.client.get(`/currency/check/${code}`),
  };

  // Landmarks endpoints
  landmarks = {
    recognize: (image: File | Blob, params?: { language?: string }) => {
      const formData = new FormData();
      formData.append("image", image);
      return this.client.post("/landmarks/recognize", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        params,
      });
    },

    getNearby: (params: { lat: number; lng: number; radius?: number; limit?: number }) =>
      this.client.get("/landmarks/nearby", { params }),

    getSimilar: (landmarkId: string, params?: { limit?: number }) =>
      this.client.get(`/landmarks/similar/${landmarkId}`, { params }),
  };

  // Emergency endpoints
  emergency = {
    list: (params?: { service_type?: string; city?: string; language?: string }) =>
      this.client.get("/emergency/", { params }),

    search: (params?: { service_type?: string; location?: string; urgent_only?: boolean }) =>
      this.client.get("/emergency/search", { params }),

    get: (id: string) => this.client.get(`/emergency/${id}`),

    getByType: (type: string) =>
      this.client.get(`/emergency/by-type/${type}`),

    getContacts: () => this.client.get("/emergency/contacts"),
  };

  // Safety endpoints
  safety = {
    sos: (data: {
      user_id: string;
      emergency_type?: string;
      description?: string;
      severity?: number;
      location?: {
        latitude: number;
        longitude: number;
        city?: string;
      };
    }) => this.client.post("/safety/sos", data),

    getSOS: (alertId: string) => this.client.get(`/safety/sos/${alertId}`),

    startLocationSharing: (data: {
      shared_with?: string[];
      duration_hours?: number;
      current_location: {
        latitude: number;
        longitude: number;
        city?: string;
      };
      trip_description?: string;
      enable_auto_check_in?: boolean;
    }) => this.client.post("/safety/location-sharing/start", data),

    updateLocationSharing: (token: string, location: [number, number]) =>
      this.client.put(`/safety/location-sharing/${token}/update`, { location }),

    trackLocationSharing: (token: string) =>
      this.client.get(`/safety/location-sharing/track/${token}`),

    getSafetyScore: (city: string) =>
      this.client.get(`/safety/score/${city}`),

    getAlerts: (params?: { city?: string; type?: string; active_only?: boolean }) =>
      this.client.get("/safety/alerts", { params }),

    checkIn: (data: { location: [number, number]; message?: string }) =>
      this.client.post("/safety/check-in", data),

    getEmergencyNumbers: () => this.client.get("/safety/emergency-numbers"),

    getEmbassy: (params?: { country?: string }) =>
      this.client.get("/safety/embassy", { params }),

    getMedicalPhrases: (params?: { language?: string }) =>
      this.client.get("/safety/medical-phrases", { params }),

    getProfile: () => this.client.get("/safety/profile"),

    updateProfile: (data: any) => this.client.put("/safety/profile", data),

    getTips: () => this.client.get("/safety/tips"),
  };

  // Forum endpoints
  forum = {
    getPosts: (params?: { skip?: number; limit?: number; category?: string }) =>
      this.client.get("/forum/posts", { params }),

    getPost: (postId: string) => this.client.get(`/forum/posts/${postId}`),

    createPost: (data: { title: string; content: string; category?: string }) =>
      this.client.post("/forum/posts", data),

    updatePost: (postId: string, data: { title?: string; content?: string }) =>
      this.client.put(`/forum/posts/${postId}`, data),

    deletePost: (postId: string) => this.client.delete(`/forum/posts/${postId}`),

    getComments: (postId: string, params?: { skip?: number; limit?: number }) =>
      this.client.get(`/forum/posts/${postId}/comments`, { params }),

    addComment: (postId: string, data: { content: string }) =>
      this.client.post(`/forum/posts/${postId}/comments`, data),
  };

  // Challenges endpoints
  challenges = {
    list: () => this.client.get("/challenges/"),

    get: (id: string) => this.client.get(`/challenges/${id}`),

    checkIn: (id: string, data: { location?: [number, number] }) =>
      this.client.post(`/challenges/${id}/check-in`, data),

    complete: (id: string) => this.client.post(`/challenges/${id}/complete`), // Alias

    getMyProgress: () => this.client.get("/challenges/my-progress"),

    getLeaderboard: (params?: { challenge_id?: string; limit?: number }) =>
      this.client.get("/challenges/leaderboard", { params }),
  };

  // Feedback endpoints
  feedback = {
    submit: (data: {
      type: string;
      content: string;
      rating?: number;
      user_id?: string;
    }) => this.client.post("/feedback", data),

    list: (params?: { skip?: number; limit?: number; type?: string }) =>
      this.client.get("/feedback", { params }),

    get: (id: string) => this.client.get(`/feedback/${id}`),
  };

  // OAuth endpoints
  oauth = {
    login: (data: { provider: string; access_token: string }) =>
      this.client.post("/oauth/login", data),

    google: () => this.client.get("/oauth/google"),

    facebook: () => this.client.get("/oauth/facebook"),

    callback: (params: { code: string; state?: string }) =>
      this.client.get("/oauth/callback", { params }),

    getProviders: () => this.client.get("/oauth/providers"),
  };

  // Email verification endpoints
  email = {
    verify: (token: string) =>
      this.client.post("/email/verify-email", { token }),

    resendVerification: (email: string) =>
      this.client.post("/email/resend-verification", { email }),
  };

  // Admin endpoints (optional, for admin users)
  admin = {
    getUsers: (params?: { skip?: number; limit?: number }) =>
      this.client.get("/admin/users", { params }),

    updateUserRole: (userId: string, role: string) =>
      this.client.put(`/admin/users/${userId}/role`, { role }),

    getAnalytics: () => this.client.get("/admin/analytics"),

    createAttraction: (data: any) =>
      this.client.post("/admin/attractions", data),
  };

  // Health check endpoints
  health = {
    // Main health check - use backend URL directly since it's at root level
    check: () => axios.get(isServer ? `${BACKEND_URL}/health` : "/health", {
      timeout: 5000,
    }),
    live: () => axios.get(isServer ? `${BACKEND_URL}/health/live` : "/health/live", {
      timeout: 5000,
    }),
    ready: () => axios.get(isServer ? `${BACKEND_URL}/health/ready` : "/health/ready", {
      timeout: 5000,
    }),
    detailed: () => this.client.get("/health/detailed"),
    metrics: () => this.client.get("/health/metrics"),
  };
}

export const apiClient = new ApiClient();
export default apiClient;

