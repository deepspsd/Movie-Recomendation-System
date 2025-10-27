// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  favorite_genres?: string[];
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// Movie Types
export interface Movie {
  id: number;
  title: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  release_date: string;
  vote_average: number;
  vote_count: number;
  popularity: number;
  genre_ids: number[];
  genres?: Genre[];
  runtime?: number;
  tagline?: string;
  cast?: CastMember[];
  director?: string;
  trailer_key?: string;
  // Advanced metadata for ML
  keywords?: string[];
  budget?: number;
  revenue?: number;
  director_score?: number;
  actor_score?: number;
  budget_revenue_ratio?: number;
}

export interface Genre {
  id: number;
  name: string;
}

export interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path: string | null;
}

// Rating Types
export interface Rating {
  id: string;
  user_id: string;
  movie_id: number;
  rating: number;
  timestamp: string;
}

export interface RatingRequest {
  movie_id: number;
  rating: number;
}

// Recommendation Types
export type AlgorithmType = 'hybrid' | 'als' | 'svd' | 'collaborative' | 'content';

export interface RecommendationResponse {
  movies: Movie[];
  algorithm: string;
  explanation?: string;
  recommendations?: RecommendationItem[];
}

export interface RecommendationItem {
  movie: Movie;
  score: number;
  explanation: string;
  algorithm_breakdown?: {
    content_score?: number;
    collaborative_score?: number;
    als_score?: number;
    svd_score?: number;
  };
}

export interface AlgorithmOption {
  value: AlgorithmType;
  label: string;
  description: string;
  icon: string;
  color: string;
}

export interface RecommendationExplanation {
  movie_id: number;
  primary_reason: string;
  factors: ExplanationFactor[];
  confidence: number;
}

export interface ExplanationFactor {
  type: 'genre' | 'director' | 'cast' | 'similar_users' | 'content_similarity' | 'popularity';
  value: string;
  weight: number;
}

export interface MoodRecommendationRequest {
  mood: string;
}

export interface WatchPartyRequest {
  user_ids: string[];
}

export interface WatchPartyResponse {
  movies: Movie[];
  compatibility_scores: { [key: number]: number };
}

// Search Types
export interface SearchParams {
  query?: string;
  genre?: string;
  year?: string;
  min_rating?: number;
  sort_by?: 'popularity' | 'rating' | 'release_date';
  page?: number;
}

export interface SearchResponse {
  movies: Movie[];
  total_results: number;
  total_pages: number;
  page: number;
}

// Watchlist Types
export interface WatchlistItem {
  id: string;
  user_id: string;
  movie_id: number;
  movie: Movie;
  added_at: string;
}

// API Error Type
export interface ApiError {
  detail: string;
  status_code: number;
}

// Mood Types
export type MoodType = 'happy' | 'sad' | 'adventurous' | 'romantic' | 'scared' | 'thoughtful';

export interface MoodOption {
  value: MoodType;
  label: string;
  emoji: string;
  description: string;
  genres: string[];
}

// User Preferences & Analytics Types
export interface UserPreferences {
  user_id: string;
  adaptive_weights: {
    content: number;
    collaborative: number;
  };
  favorite_genres: string[];
  favorite_directors: string[];
  favorite_actors: string[];
  average_rating: number;
  total_ratings: number;
  recommendation_accuracy: number;
}

export interface UserAnalytics {
  total_movies_watched: number;
  total_ratings: number;
  average_rating: number;
  favorite_genres: GenreDistribution[];
  rating_distribution: RatingDistribution[];
  recommendation_performance: RecommendationMetrics;
  viewing_trends: ViewingTrend[];
}

export interface GenreDistribution {
  genre: string;
  count: number;
  percentage: number;
}

export interface RatingDistribution {
  rating: number;
  count: number;
}

export interface RecommendationMetrics {
  precision_at_10: number;
  recall_at_10: number;
  f1_score: number;
  ndcg: number;
  diversity: number;
  novelty: number;
}

export interface ViewingTrend {
  date: string;
  count: number;
  average_rating: number;
}

// Feedback Types for Adaptive Learning
export interface RecommendationFeedback {
  movie_id: number;
  rating: number;
  watched: boolean;
  liked: boolean;
}

export interface AdaptiveWeightUpdate {
  user_id: string;
  recommended_items: number[];
  feedback: { [key: number]: number };
  method: 'rl' | 'gradient';
}
