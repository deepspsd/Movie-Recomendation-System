/**
 * Utility functions for fetching and managing movie trailers
 * Works with YouTube Data API to find trailers
 */

const YOUTUBE_API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY || '';
const YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search';

export interface TrailerVideo {
  id: string;
  key: string;
  title: string;
}

/**
 * Fetch trailer videos for a movie from YouTube
 */
export const fetchMovieTrailer = async (movieTitle: string, year?: string): Promise<string | null> => {
  try {
    // Construct search query
    const searchQuery = `${movieTitle} ${year || ''} official trailer`.trim();
    
    const response = await fetch(
      `${YOUTUBE_SEARCH_URL}?part=snippet&q=${encodeURIComponent(searchQuery)}&type=video&maxResults=1&key=${YOUTUBE_API_KEY}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch trailer from YouTube');
    }

    const data = await response.json();
    
    if (data.items && data.items.length > 0) {
      const videoId = data.items[0].id.videoId;
      // Return YouTube embed URL with autoplay and muted
      return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1&loop=1&playlist=${videoId}`;
    }

    return null;
  } catch (error) {
    console.error('Error fetching trailer:', error);
    // Return a fallback sample video if YouTube API fails
    return null;
  }
};

/**
 * Get YouTube thumbnail URL from video key
 */
export const getYouTubeThumbnail = (videoKey: string, quality: 'default' | 'hq' | 'maxres' = 'hq'): string => {
  const qualityMap = {
    default: 'default',
    hq: 'hqdefault',
    maxres: 'maxresdefault'
  };
  
  return `https://img.youtube.com/vi/${videoKey}/${qualityMap[quality]}.jpg`;
};

/**
 * Cache for storing fetched trailers to avoid repeated API calls
 */
const trailerCache = new Map<string, string | null>();

/**
 * Get trailer with caching
 */
export const getCachedTrailer = async (movieTitle: string, year?: string): Promise<string | null> => {
  const cacheKey = `${movieTitle}_${year || ''}`;
  
  if (trailerCache.has(cacheKey)) {
    return trailerCache.get(cacheKey) || null;
  }

  const trailer = await fetchMovieTrailer(movieTitle, year);
  trailerCache.set(cacheKey, trailer);
  
  return trailer;
};

/**
 * Preload trailers for multiple movies
 */
export const preloadTrailers = async (movies: Array<{ title: string; year?: string }>): Promise<void> => {
  const promises = movies.map(movie => getCachedTrailer(movie.title, movie.year));
  await Promise.allSettled(promises);
};

/**
 * Clear trailer cache
 */
export const clearTrailerCache = (): void => {
  trailerCache.clear();
};
