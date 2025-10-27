import { motion, AnimatePresence } from "framer-motion";
import { Star, Play, Plus, ThumbsUp, Info, Volume2, VolumeX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { getImageUrl, formatRating } from "@/utils/helpers";
import { getCachedTrailer } from "@/utils/trailerUtils";
import type { Movie } from "@/types";
import { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";

interface MovieCardProps {
  movie: Movie;
  showTrailer?: boolean;
}

const MovieCard = ({ movie, showTrailer = true }: MovieCardProps) => {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [showVideo, setShowVideo] = useState(false);
  const [trailerUrl, setTrailerUrl] = useState<string | null>(null);
  const [isLoadingTrailer, setIsLoadingTrailer] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleClick = () => {
    navigate(`/movies/${movie.id}`);
  };

  const handleAddToWatchlist = (e: React.MouseEvent) => {
    e.stopPropagation();
    toast.success(`Added "${movie.title}" to watchlist`);
  };

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    toast.success(`Liked "${movie.title}"`);
  };

  const toggleMute = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMuted(!isMuted);
  };

  // Fetch trailer when component mounts
  useEffect(() => {
    if (showTrailer && !trailerUrl && !isLoadingTrailer) {
      setIsLoadingTrailer(true);
      const year = movie.release_date ? new Date(movie.release_date).getFullYear().toString() : undefined;
      getCachedTrailer(movie.title, year)
        .then((url) => {
          setTrailerUrl(url);
        })
        .catch((error) => {
          console.error('Failed to load trailer:', error);
        })
        .finally(() => {
          setIsLoadingTrailer(false);
        });
    }
  }, [movie.title, movie.release_date, showTrailer, trailerUrl, isLoadingTrailer]);

  // Handle hover state for video playback
  useEffect(() => {
    if (isHovered && showTrailer && trailerUrl) {
      // Delay video playback for better UX
      hoverTimeoutRef.current = setTimeout(() => {
        setShowVideo(true);
      }, 600);
    } else {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
      setShowVideo(false);
    }

    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, [isHovered, showTrailer, trailerUrl]);

  // Modify trailer URL to control mute state
  const getTrailerUrlWithMute = () => {
    if (!trailerUrl) return null;
    return trailerUrl.replace('mute=1', `mute=${isMuted ? '1' : '0'}`);
  };

  return (
    <motion.div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ 
        scale: 1.05,
        y: -10,
        zIndex: 50,
      }}
      transition={{ 
        duration: 0.3,
        ease: "easeOut"
      }}
      className="group relative aspect-[2/3] rounded-lg overflow-hidden cursor-pointer flex-shrink-0 w-full bg-card"
    >
      {/* Poster Image */}
      <div className="relative w-full h-full">
        <img
          src={getImageUrl(movie.poster_path, 'w500')}
          alt={movie.title}
          className="w-full h-full object-cover transition-all duration-500 group-hover:scale-105"
          loading="lazy"
          onError={(e) => {
            (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&h=750&fit=crop';
          }}
        />
        
        {/* Rating Badge - Always Visible */}
        <div className="absolute top-2 left-2 z-10">
          <Badge className="bg-black/80 backdrop-blur-sm text-white border-0 gap-1">
            <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
            <span className="font-bold">{formatRating(movie.vote_average)}</span>
          </Badge>
        </div>

        {/* Year Badge */}
        {movie.release_date && (
          <div className="absolute top-2 right-2 z-10">
            <Badge className="bg-black/80 backdrop-blur-sm text-white border-0">
              {new Date(movie.release_date).getFullYear()}
            </Badge>
          </div>
        )}
      </div>

      {/* Video Trailer Overlay - Shows on Hover */}
      <AnimatePresence>
        {isHovered && showVideo && showTrailer && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0 z-20"
          >
            <iframe
              ref={iframeRef}
              src={getTrailerUrlWithMute() || ''}
              className="w-full h-full object-cover"
              allow="autoplay; encrypted-media"
              allowFullScreen
              frameBorder="0"
            />
            
            {/* Mute/Unmute Button */}
            <button
              onClick={toggleMute}
              className="absolute top-2 right-2 z-30 p-2 bg-black/60 hover:bg-black/80 rounded-full transition-colors"
            >
              {isMuted ? (
                <VolumeX className="w-4 h-4 text-white" />
              ) : (
                <Volume2 className="w-4 h-4 text-white" />
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Hover Overlay with Info */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="absolute inset-0 bg-gradient-to-t from-black via-black/80 to-transparent p-4 flex flex-col justify-end z-30"
          >
            {/* Title */}
            <h3 className="text-white font-bold text-base mb-2 line-clamp-2 drop-shadow-lg">
              {movie.title}
            </h3>
            
            {/* Meta Info */}
            <div className="flex items-center gap-2 text-xs text-white/90 mb-3">
              <div className="flex items-center gap-1">
                <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                <span className="font-semibold">{formatRating(movie.vote_average)}</span>
              </div>
              {movie.release_date && (
                <>
                  <span>•</span>
                  <span>{new Date(movie.release_date).getFullYear()}</span>
                </>
              )}
              {movie.vote_count && (
                <>
                  <span>•</span>
                  <span>{movie.vote_count.toLocaleString()} votes</span>
                </>
              )}
            </div>

            {/* Overview */}
            {movie.overview && (
              <p className="text-white/80 text-xs mb-3 line-clamp-2">
                {movie.overview}
              </p>
            )}
            
            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <Button 
                size="sm" 
                onClick={handleClick}
                className="flex-1 gap-1 h-8 text-xs bg-white text-black hover:bg-white/90"
              >
                <Play className="w-3 h-3" />
                Details
              </Button>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={handleAddToWatchlist}
                className="h-8 w-8 p-0 bg-black/60 hover:bg-black/80 text-white border border-white/20"
              >
                <Plus className="w-4 h-4" />
              </Button>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={handleLike}
                className="h-8 w-8 p-0 bg-black/60 hover:bg-black/80 text-white border border-white/20"
              >
                <ThumbsUp className="w-4 h-4" />
              </Button>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={handleClick}
                className="h-8 w-8 p-0 bg-black/60 hover:bg-black/80 text-white border border-white/20"
              >
                <Info className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Glow Effect on Hover */}
      <div className="absolute inset-0 ring-2 ring-transparent group-hover:ring-primary/50 rounded-lg pointer-events-none transition-all duration-300" />
      <div className="absolute -inset-1 bg-gradient-to-r from-primary/0 via-primary/20 to-primary/0 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 pointer-events-none" />
    </motion.div>
  );
};

export default MovieCard;
