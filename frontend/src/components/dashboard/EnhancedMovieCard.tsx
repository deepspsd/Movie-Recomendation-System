import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Star,
  Plus,
  Check,
  ThumbsUp,
  ThumbsDown,
  Eye,
  Info,
  Play,
  Bookmark,
  TrendingUp,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
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

interface EnhancedMovieCardProps {
  movie: Movie;
  recommendationScore?: number;
  contentScore?: number;
  collaborativeScore?: number;
  onWatchlistToggle?: () => void;
  onRatingChange?: () => void;
}

export function EnhancedMovieCard({
  movie,
  recommendationScore = 0,
  contentScore = 0,
  collaborativeScore = 0,
  onWatchlistToggle,
  onRatingChange,
}: EnhancedMovieCardProps) {
  const navigate = useNavigate();
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [isWatched, setIsWatched] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleWatchlistToggle = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    try {
      if (isInWatchlist) {
        await watchlistAPI.remove(movie.id);
        setIsInWatchlist(false);
        toast.success('Removed from watchlist');
      } else {
        await watchlistAPI.add(movie.id);
        setIsInWatchlist(true);
        toast.success('Added to watchlist');
      }
      onWatchlistToggle?.();
    } catch (error) {
      toast.error('Failed to update watchlist');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsWatched = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsWatched(!isWatched);
    toast.success(isWatched ? 'Marked as unwatched' : 'Marked as watched');
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await ratingsAPI.rate({ movie_id: movie.id, rating: 5 });
      setUserRating(5);
      toast.success('Liked!');
      onRatingChange?.();
    } catch (error) {
      toast.error('Failed to rate movie');
    }
  };

  const handleDislike = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await ratingsAPI.rate({ movie_id: movie.id, rating: 1 });
      setUserRating(1);
      toast.success('Disliked');
      onRatingChange?.();
    } catch (error) {
      toast.error('Failed to rate movie');
    }
  };

  const handleCardClick = () => {
    navigate(`/movies/${movie.id}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.03 }}
      transition={{ duration: 0.2 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <Card
        className="overflow-hidden cursor-pointer border-2 hover:border-primary/50 transition-all group relative"
        onClick={handleCardClick}
      >
        {/* Poster Image */}
        <div className="relative aspect-[2/3] overflow-hidden bg-muted">
          <img
            src={getImageUrl(movie.poster_path, 'w500')}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
            loading="lazy"
          />

          {/* Overlay on Hover */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent flex flex-col justify-end p-4"
          >
            <div className="space-y-2">
              {/* Quick Actions */}
              <div className="flex gap-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        size="sm"
                        variant="secondary"
                        className="flex-1"
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
                      {isInWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        size="sm"
                        variant="secondary"
                        className="flex-1"
                        onClick={handleMarkAsWatched}
                      >
                        <Eye className={`w-4 h-4 ${isWatched ? 'fill-current' : ''}`} />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      {isWatched ? 'Mark as Unwatched' : 'Mark as Watched'}
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>

              {/* Like/Dislike */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant={userRating === 5 ? 'default' : 'secondary'}
                  className="flex-1 gap-1"
                  onClick={handleLike}
                >
                  <ThumbsUp className="w-4 h-4" />
                  Like
                </Button>
                <Button
                  size="sm"
                  variant={userRating === 1 ? 'destructive' : 'secondary'}
                  className="flex-1 gap-1"
                  onClick={handleDislike}
                >
                  <ThumbsDown className="w-4 h-4" />
                  Dislike
                </Button>
              </div>
            </div>
          </motion.div>

          {/* Watched Badge */}
          {isWatched && (
            <Badge className="absolute top-2 left-2 bg-green-500 gap-1">
              <Check className="w-3 h-3" />
              Watched
            </Badge>
          )}

          {/* Watchlist Badge */}
          {isInWatchlist && (
            <Badge className="absolute top-2 right-2 bg-blue-500">
              <Bookmark className="w-3 h-3" />
            </Badge>
          )}
        </div>

        <CardContent className="p-4 space-y-3">
          {/* Title */}
          <h3 className="font-semibold line-clamp-2 min-h-[3rem]">{movie.title}</h3>

          {/* Rating & Year */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1 text-yellow-500">
              <Star className="w-4 h-4 fill-current" />
              <span className="font-semibold">{formatRating(movie.vote_average)}</span>
            </div>
            {movie.release_date && (
              <span className="text-muted-foreground">
                {new Date(movie.release_date).getFullYear()}
              </span>
            )}
          </div>

          {/* Genres */}
          {movie.genres && movie.genres.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {movie.genres.slice(0, 2).map((genre) => (
                <Badge key={genre.id} variant="outline" className="text-xs">
                  {genre.name}
                </Badge>
              ))}
            </div>
          )}

          {/* Recommendation Score */}
          {recommendationScore > 0 && (
            <div className="space-y-2 pt-2 border-t">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground font-medium">Match Score</span>
                <span className="font-bold text-primary">
                  {Math.round(recommendationScore * 100)}%
                </span>
              </div>
              <Progress value={recommendationScore * 100} className="h-2" />

              {/* Algorithm Breakdown */}
              {(contentScore > 0 || collaborativeScore > 0) && (
                <div className="flex gap-2 text-xs">
                  {contentScore > 0 && (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="flex items-center gap-1 text-purple-500">
                            <div className="w-2 h-2 rounded-full bg-purple-500" />
                            <span>{Math.round(contentScore * 100)}%</span>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>Content-Based Score</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                  {collaborativeScore > 0 && (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="flex items-center gap-1 text-blue-500">
                            <div className="w-2 h-2 rounded-full bg-blue-500" />
                            <span>{Math.round(collaborativeScore * 100)}%</span>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>Collaborative Score</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
