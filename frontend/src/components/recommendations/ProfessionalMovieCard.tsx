import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Star,
  Plus,
  Check,
  Play,
  Info,
  Clock,
  Calendar,
  TrendingUp,
  Award,
  Users,
  Sparkles,
  Heart,
  Eye,
  EyeOff,
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { getImageUrl, formatRating } from '@/utils/helpers';
import { watchlistAPI, ratingsAPI } from '@/services/api';
import type { Movie } from '@/types';
import toast from 'react-hot-toast';

interface ProfessionalMovieCardProps {
  movie: Movie;
  recommendationScore?: number;
  rank?: number;
  showRank?: boolean;
  onWatchlistToggle?: () => void;
  onRatingChange?: () => void;
}

export function ProfessionalMovieCard({
  movie,
  recommendationScore = 0,
  rank = 0,
  showRank = false,
  onWatchlistToggle,
  onRatingChange,
}: ProfessionalMovieCardProps) {
  const navigate = useNavigate();
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  // Check if movie is in watchlist on mount
  useEffect(() => {
    checkWatchlistStatus();
  }, [movie.id]);

  const checkWatchlistStatus = async () => {
    try {
      const watchlist = await watchlistAPI.getAll();
      const inList = watchlist.some((item: any) => item.movie_id === movie.id);
      setIsInWatchlist(inList);
    } catch (error) {
      // Silently fail
    }
  };

  const handleWatchlistToggle = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    try {
      if (isInWatchlist) {
        await watchlistAPI.remove(movie.id);
        setIsInWatchlist(false);
        toast.success(`Removed "${movie.title}" from watchlist`, {
          icon: '🗑️',
          duration: 2000,
        });
      } else {
        await watchlistAPI.add(movie.id);
        setIsInWatchlist(true);
        toast.success(`Added "${movie.title}" to watchlist`, {
          icon: '✅',
          duration: 2000,
        });
      }
      onWatchlistToggle?.();
    } catch (error) {
      toast.error('Failed to update watchlist');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRate = async (e: React.MouseEvent, rating: number) => {
    e.stopPropagation();
    try {
      await ratingsAPI.rate({ movie_id: movie.id, rating });
      setUserRating(rating);
      toast.success(`Rated "${movie.title}" ${rating}/5 stars`, {
        icon: '⭐',
        duration: 2000,
      });
      onRatingChange?.();
    } catch (error) {
      toast.error('Failed to rate movie');
    }
  };

  const handleCardClick = () => {
    navigate(`/movies/${movie.id}`);
  };

  // Calculate match percentage
  const matchPercentage = recommendationScore > 0 
    ? Math.round(recommendationScore * 100) 
    : Math.round((movie.vote_average / 10) * 100);

  // Get genre names
  const genreNames = movie.genres?.map((g) => g.name).slice(0, 3) || [];

  // Format runtime
  const formatRuntime = (minutes: number) => {
    if (!minutes) return null;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="group"
    >
      <Card
        className="overflow-hidden cursor-pointer border-2 border-border/50 hover:border-primary/60 transition-all duration-300 bg-card/95 backdrop-blur-sm shadow-lg hover:shadow-2xl hover:shadow-primary/20 relative"
        onClick={handleCardClick}
      >
        {/* Rank Badge */}
        {showRank && rank > 0 && (
          <div className="absolute top-3 left-3 z-20">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg border-2 border-white/20"
            >
              <span className="text-white font-bold text-sm">#{rank}</span>
            </motion.div>
          </div>
        )}

        {/* Poster Section */}
        <div className="relative aspect-[2/3] overflow-hidden bg-gradient-to-br from-muted/50 to-muted">
          {/* Loading Skeleton */}
          {!imageLoaded && (
            <div className="absolute inset-0 bg-gradient-to-br from-muted via-muted/80 to-muted animate-pulse" />
          )}

          {/* Poster Image */}
          <motion.img
            src={getImageUrl(movie.poster_path, 'w500')}
            alt={movie.title}
            className={`w-full h-full object-cover transition-all duration-500 ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            } ${isHovered ? 'scale-110' : 'scale-100'}`}
            loading="lazy"
            onLoad={() => setImageLoaded(true)}
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&h=750&fit=crop';
              setImageLoaded(true);
            }}
          />

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-300" />

          {/* Match Score Badge */}
          {matchPercentage > 0 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="absolute top-3 right-3 z-10"
            >
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="px-3 py-1.5 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 shadow-lg border border-white/20 backdrop-blur-sm">
                      <div className="flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-white" />
                        <span className="text-white font-bold text-sm">
                          {matchPercentage}%
                        </span>
                      </div>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="font-semibold">Match Score</p>
                    <p className="text-xs text-muted-foreground">
                      Based on your preferences
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </motion.div>
          )}

          {/* Hover Overlay with Actions */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="absolute inset-0 bg-gradient-to-t from-black via-black/90 to-black/50 flex flex-col justify-end p-4 z-10"
              >
                {/* Quick Info */}
                <div className="space-y-3 mb-4">
                  {/* Title */}
                  <h3 className="text-white font-bold text-lg leading-tight line-clamp-2 drop-shadow-lg">
                    {movie.title}
                  </h3>

                  {/* Meta Info */}
                  <div className="flex flex-wrap items-center gap-2 text-xs text-white/90">
                    <div className="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-2 py-1 rounded-md">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      <span className="font-semibold">{formatRating(movie.vote_average)}</span>
                    </div>
                    {movie.release_date && (
                      <div className="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-2 py-1 rounded-md">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(movie.release_date).getFullYear()}</span>
                      </div>
                    )}
                    {movie.runtime && (
                      <div className="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-2 py-1 rounded-md">
                        <Clock className="w-3 h-3" />
                        <span>{formatRuntime(movie.runtime)}</span>
                      </div>
                    )}
                  </div>

                  {/* Genres */}
                  {genreNames.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {genreNames.map((genre, idx) => (
                        <Badge
                          key={idx}
                          variant="secondary"
                          className="text-xs bg-white/20 backdrop-blur-sm text-white border-white/20"
                        >
                          {genre}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    className="flex-1 gap-2 bg-white text-black hover:bg-white/90 font-semibold shadow-lg"
                    onClick={handleCardClick}
                  >
                    <Play className="w-4 h-4" />
                    Details
                  </Button>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          size="sm"
                          variant="secondary"
                          className={`gap-2 shadow-lg ${
                            isInWatchlist
                              ? 'bg-green-500 hover:bg-green-600 text-white'
                              : 'bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm'
                          }`}
                          onClick={handleWatchlistToggle}
                          disabled={isLoading}
                        >
                          {isInWatchlist ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <Plus className="w-4 h-4" />
                          )}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        {isInWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Info Section */}
        <div className="p-4 space-y-3">
          {/* Title (visible when not hovering) */}
          <h3 className="font-bold text-base leading-tight line-clamp-2 min-h-[2.5rem] group-hover:text-primary transition-colors">
            {movie.title}
          </h3>

          {/* Rating & Year */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1.5">
              <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
              <span className="font-bold text-foreground">
                {formatRating(movie.vote_average)}
              </span>
              {movie.vote_count && (
                <span className="text-muted-foreground text-xs">
                  ({movie.vote_count.toLocaleString()})
                </span>
              )}
            </div>
            {movie.release_date && (
              <span className="text-muted-foreground font-medium">
                {new Date(movie.release_date).getFullYear()}
              </span>
            )}
          </div>

          {/* Match Progress Bar */}
          {matchPercentage > 0 && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground font-medium">Your Match</span>
                <span className="font-bold text-primary">{matchPercentage}%</span>
              </div>
              <Progress
                value={matchPercentage}
                className="h-2 bg-muted"
                indicatorClassName="bg-gradient-to-r from-green-500 to-emerald-600"
              />
            </div>
          )}

          {/* Quick Actions (visible when not hovering) */}
          <div className="flex gap-2 pt-2 border-t border-border/50">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={handleWatchlistToggle}
                    disabled={isLoading}
                  >
                    {isInWatchlist ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <Plus className="w-4 h-4" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  {isInWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={(e) => handleRate(e, 5)}
                  >
                    <Heart
                      className={`w-4 h-4 ${
                        userRating === 5 ? 'fill-red-500 text-red-500' : ''
                      }`}
                    />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Like this movie</TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleCardClick}
                  >
                    <Info className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>View Details</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>

        {/* Glow Effect */}
        <div className="absolute inset-0 rounded-lg ring-2 ring-transparent group-hover:ring-primary/50 pointer-events-none transition-all duration-300" />
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/0 via-primary/20 to-primary/0 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 pointer-events-none -z-10" />
      </Card>
    </motion.div>
  );
}
