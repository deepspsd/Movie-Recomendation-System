import type { Movie } from '@/types';

const TMDB_IMAGE_BASE_URL = import.meta.env.VITE_TMDB_IMAGE_BASE_URL || 'https://image.tmdb.org/t/p';
const FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&h=750&fit=crop';

/**
 * Get full image URL - handles both OMDb full URLs and TMDB paths
 */
export const getImageUrl = (path: string | null, size: 'w200' | 'w300' | 'w500' | 'w780' | 'original' = 'w500'): string => {
  if (!path || path === 'N/A') {
    return FALLBACK_IMAGE;
  }
  
  // Check if it's already a full URL (OMDb returns full URLs)
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // TMDB path format (starts with /)
  if (path.startsWith('/')) {
    return `${TMDB_IMAGE_BASE_URL}/${size}${path}`;
  }
  
  // Fallback for any other format
  return FALLBACK_IMAGE;
};

/**
 * Format movie release year
 */
export const getYear = (dateString: string): string => {
  if (!dateString) return 'N/A';
  return new Date(dateString).getFullYear().toString();
};

/**
 * Format rating to 1 decimal place
 */
export const formatRating = (rating: number | null | undefined): string => {
  if (rating === null || rating === undefined || isNaN(rating)) {
    return 'N/A';
  }
  return rating.toFixed(1);
};

/**
 * Format runtime to hours and minutes
 */
export const formatRuntime = (minutes: number): string => {
  if (!minutes) return 'N/A';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

/**
 * Get genre names from genre IDs
 */
export const getGenreNames = (genreIds: number[], allGenres: { id: number; name: string }[]): string[] => {
  return genreIds
    .map((id) => allGenres.find((g) => g.id === id)?.name)
    .filter((name): name is string => !!name);
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
};

/**
 * Format date to readable string
 */
export const formatDate = (dateString: string): string => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Debounce function for search
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};

/**
 * Get YouTube embed URL from key
 */
export const getYouTubeEmbedUrl = (key: string): string => {
  return `https://www.youtube.com/embed/${key}`;
};

/**
 * Calculate compatibility percentage
 */
export const calculateCompatibility = (score: number): number => {
  return Math.round(score * 100);
};

/**
 * Get mood emoji
 */
export const getMoodEmoji = (mood: string): string => {
  const moodEmojis: { [key: string]: string } = {
    happy: '😊',
    sad: '😢',
    adventurous: '🎬',
    romantic: '❤️',
    scared: '😱',
    thoughtful: '🤔',
  };
  return moodEmojis[mood.toLowerCase()] || '🎭';
};

/**
 * Get mood description
 */
export const getMoodDescription = (mood: string): string => {
  const descriptions: { [key: string]: string } = {
    happy: 'Feel-good movies that will lift your spirits',
    sad: 'Emotional dramas that touch the heart',
    adventurous: 'Action-packed thrillers and adventures',
    romantic: 'Love stories and romantic comedies',
    scared: 'Horror and suspense that will keep you on edge',
    thoughtful: 'Thought-provoking films that make you think',
  };
  return descriptions[mood.toLowerCase()] || 'Movies that match your mood';
};
