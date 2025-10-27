import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  AuthResponse,
  LoginCredentials,
  RegisterData,
  Movie,
  Rating,
  RatingRequest,
  RecommendationResponse,
  MoodRecommendationRequest,
  WatchPartyRequest,
  WatchPartyResponse,
  SearchParams,
  SearchResponse,
  WatchlistItem,
  ApiError,
  AlgorithmType,
  UserPreferences,
  UserAnalytics,
  AdaptiveWeightUpdate,
  RecommendationExplanation,
} from '@/types';

// Extend Axios config to include custom properties
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    _retry?: boolean;
    metadata?: { startTime: number };
  }
}

// API Base URL - change this to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Helper function for exponential backoff
const getRetryDelay = (retryCount: number) => {
  return RETRY_DELAY * Math.pow(2, retryCount);
};

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // Increased timeout for ML operations
  withCredentials: true, // Enable credentials for CORS
  // Performance optimizations
  maxRedirects: 3,
  maxContentLength: 50 * 1024 * 1024, // 50MB max content length
});

// Request interceptor for performance monitoring (must be first)
api.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: Date.now() };
    return config;
  }
);

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for enhanced error handling with retry logic
api.interceptors.response.use(
  (response) => {
    // Add response time logging for performance monitoring
    if (response.config.metadata) {
      const responseTime = Date.now() - response.config.metadata.startTime;
      console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${responseTime}ms`);
    }
    return response;
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig;
    
    // Retry logic for network errors and 5xx errors
    if (
      originalRequest &&
      !originalRequest._retry &&
      (error.code === 'ECONNABORTED' || 
       error.code === 'ERR_NETWORK' ||
       (error.response && error.response.status >= 500))
    ) {
      const retryCount = (originalRequest as any).retryCount || 0;
      
      if (retryCount < MAX_RETRIES) {
        (originalRequest as any).retryCount = retryCount + 1;
        const delay = getRetryDelay(retryCount);
        
        console.log(`Retrying request (${retryCount + 1}/${MAX_RETRIES}) after ${delay}ms...`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return api(originalRequest);
      }
    }
    
    // Handle 401 Unauthorized - token refresh
    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true;
      
      // Token expired, try to refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request
          if (originalRequest) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
          // Refresh failed, logout user
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    // Enhanced error logging
    const errorDetails = {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data
    };
    
    console.error('API Error:', errorDetails);
    
    // Ensure error has proper structure for frontend
    if (error.response && !error.response.data?.detail) {
      const originalData = error.response.data || {};
      error.response.data = {
        detail: (originalData as any)?.message || error.message || 'An error occurred',
        ...(originalData as any)
      } as ApiError;
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Movies API
export const moviesAPI = {
  search: async (params: any) => {
    const response = await api.get('/movies/search', { params });
    return response.data;
  },

  getDetails: async (id: number) => {
    const response = await api.get(`/movies/${id}`);
    return response.data;
  },

  getTrending: async () => {
    const response = await api.get('/movies/trending');
    return response.data;
  },

  getPopular: async () => {
    const response = await api.get('/movies/popular');
    return response.data;
  },

  getTopRated: async () => {
    const response = await api.get('/movies/top-rated');
    return response.data;
  },

  getByGenre: async (genreId: number) => {
    const response = await api.get(`/movies/genre/${genreId}`);
    return response.data;
  },
};

// OMDB API endpoints
export const omdbAPI = {
  getBestMovies: async (limit: number = 50) => {
    const response = await api.get(`/omdb/best-movies?limit=${limit}`);
    return response.data;
  },

  getPopularMovies: async (limit: number = 20) => {
    const response = await api.get(`/omdb/popular?limit=${limit}`);
    return response.data;
  },

  searchMovies: async (query: string, page: number = 1) => {
    const response = await api.get(`/omdb/search?query=${encodeURIComponent(query)}&page=${page}`);
    return response.data;
  },

  getMovieDetails: async (imdbId: string) => {
    const response = await api.get(`/omdb/movie/${imdbId}`);
    return response.data;
  },

  getMoviesByYear: async (year: number, limit: number = 20) => {
    const response = await api.get(`/omdb/by-year/${year}?limit=${limit}`);
    return response.data;
  },
};

// Recommendations API
export const recommendationsAPI = {
  getPersonalized: async (algorithm?: AlgorithmType): Promise<RecommendationResponse> => {
    const response = await api.get<RecommendationResponse>('/recommendations', {
      params: algorithm ? { algorithm } : {},
    });
    return response.data;
  },

  getByMood: async (mood: string): Promise<RecommendationResponse> => {
    const response = await api.get<RecommendationResponse>('/recommendations/mood', {
      params: { mood },
    });
    return response.data;
  },

  getSimilar: async (movieId: number): Promise<Movie[]> => {
    const response = await api.get<Movie[]>(`/recommendations/similar/${movieId}`);
    return response.data;
  },

  getWatchParty: async (userIds: string[]): Promise<WatchPartyResponse> => {
    const response = await api.post<WatchPartyResponse>('/recommendations/group', {
      user_ids: userIds,
    });
    return response.data;
  },

  getExplanation: async (movieId: number): Promise<RecommendationExplanation> => {
    const response = await api.get<RecommendationExplanation>(`/recommendations/explain/${movieId}`);
    return response.data;
  },

  submitFeedback: async (data: AdaptiveWeightUpdate): Promise<void> => {
    await api.post('/recommendations/feedback', data);
  },
};

// Ratings API
export const ratingsAPI = {
  rate: async (data: RatingRequest): Promise<Rating> => {
    const response = await api.post<Rating>('/ratings', data);
    return response.data;
  },

  getUserRatings: async (): Promise<Rating[]> => {
    const response = await api.get<Rating[]>('/ratings/user');
    return response.data;
  },

  getMovieRating: async (movieId: number): Promise<Rating | null> => {
    try {
      const response = await api.get<Rating>(`/ratings/movie/${movieId}`);
      return response.data;
    } catch (error) {
      return null;
    }
  },
};

// Watchlist API
export const watchlistAPI = {
  getAll: async (): Promise<WatchlistItem[]> => {
    const response = await api.get<WatchlistItem[]>('/watchlist');
    return response.data;
  },

  add: async (movieId: number): Promise<WatchlistItem> => {
    const response = await api.post<WatchlistItem>('/watchlist', {
      movie_id: movieId,
    });
    return response.data;
  },

  remove: async (movieId: number): Promise<void> => {
    await api.delete(`/watchlist/${movieId}`);
  },

  check: async (movieId: number): Promise<boolean> => {
    try {
      const response = await api.get<{ in_watchlist: boolean }>(`/watchlist/check/${movieId}`);
      return response.data.in_watchlist;
    } catch (error) {
      return false;
    }
  },
};

// User Preferences & Analytics API
export const userAPI = {
  getPreferences: async (): Promise<UserPreferences> => {
    const response = await api.get<UserPreferences>('/user/preferences');
    return response.data;
  },

  updatePreferences: async (preferences: Partial<UserPreferences>): Promise<UserPreferences> => {
    const response = await api.put<UserPreferences>('/user/preferences', preferences);
    return response.data;
  },

  getAnalytics: async (): Promise<UserAnalytics> => {
    const response = await api.get<UserAnalytics>('/user/analytics');
    return response.data;
  },

  getAdaptiveWeights: async (): Promise<{ content: number; collaborative: number }> => {
    const response = await api.get<{ content: number; collaborative: number }>('/user/weights');
    return response.data;
  },
};

// Export the axios instance for custom requests
export default api;
