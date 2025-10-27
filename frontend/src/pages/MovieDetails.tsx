import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Play, Plus, Check, Star, Clock, Calendar, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Navbar from '@/components/Navbar';
import MovieCard from '@/components/MovieCard';
import { MovieDetailsSkeleton } from '@/components/LoadingSkeleton';
import { moviesAPI, recommendationsAPI, ratingsAPI, watchlistAPI } from '@/services/api';
import { getImageUrl, formatRating, formatRuntime, formatDate } from '@/utils/helpers';
import type { Movie } from '@/types';
import toast from 'react-hot-toast';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

const MovieDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);
  const [showRatingDialog, setShowRatingDialog] = useState(false);
  const [hoverRating, setHoverRating] = useState(0);

  useEffect(() => {
    if (id) {
      fetchMovieDetails();
      fetchSimilarMovies();
      checkWatchlistStatus();
      fetchUserRating();
    }
  }, [id]);

  const fetchMovieDetails = async () => {
    try {
      setIsLoading(true);
      const data = await moviesAPI.getDetails(Number(id));
      setMovie(data);
    } catch (error) {
      console.error('Error fetching movie:', error);
      toast.error('Failed to load movie details');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSimilarMovies = async () => {
    try {
      const data = await recommendationsAPI.getSimilar(Number(id));
      setSimilarMovies(data);
    } catch (error) {
      console.error('Error fetching similar movies:', error);
    }
  };

  const checkWatchlistStatus = async () => {
    try {
      const status = await watchlistAPI.check(Number(id));
      setInWatchlist(status);
    } catch (error) {
      console.error('Error checking watchlist:', error);
    }
  };

  const fetchUserRating = async () => {
    try {
      const rating = await ratingsAPI.getMovieRating(Number(id));
      if (rating) {
        setUserRating(rating.rating);
      }
    } catch (error) {
      console.error('Error fetching rating:', error);
    }
  };

  const handleWatchlistToggle = async () => {
    try {
      if (inWatchlist) {
        await watchlistAPI.remove(Number(id));
        setInWatchlist(false);
        toast.success('Removed from watchlist');
      } else {
        await watchlistAPI.add(Number(id));
        setInWatchlist(true);
        toast.success('Added to watchlist');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update watchlist');
    }
  };

  const handleRateMovie = async (rating: number) => {
    try {
      await ratingsAPI.rate({ movie_id: Number(id), rating });
      setUserRating(rating);
      setShowRatingDialog(false);
      toast.success('Rating saved!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save rating');
    }
  };

  if (isLoading) {
    return <MovieDetailsSkeleton />;
  }

  if (!movie) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Movie not found</h2>
          <Button onClick={() => navigate('/movies')}>Browse Movies</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative h-[90vh] mt-16">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${getImageUrl(movie.backdrop_path, 'original')})`,
            filter: 'brightness(0.3) blur(1px)',
          }}
        />

        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />

        <Button
          variant="ghost"
          size="icon"
          className="absolute top-24 left-4 z-20"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft className="w-6 h-6" />
        </Button>

        <div className="relative z-10 h-full flex items-center">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row gap-8 items-start">
              {/* Poster */}
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                className="flex-shrink-0"
              >
                <img
                  src={getImageUrl(movie.poster_path, 'w500')}
                  alt={movie.title}
                  className="w-80 rounded-2xl shadow-2xl"
                />
              </motion.div>

              {/* Info */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="flex-1 max-w-3xl"
              >
                <h1 className="text-5xl md:text-6xl font-bold mb-4">{movie.title}</h1>

                {movie.tagline && (
                  <p className="text-xl text-muted-foreground italic mb-6">{movie.tagline}</p>
                )}

                <div className="flex flex-wrap items-center gap-4 mb-6">
                  <div className="flex items-center gap-2">
                    <Star className="w-6 h-6 fill-accent text-accent" />
                    <span className="text-2xl font-bold">{formatRating(movie.vote_average)}</span>
                    <span className="text-muted-foreground">({movie.vote_count} votes)</span>
                  </div>

                  {userRating && (
                    <Badge variant="secondary" className="text-sm">
                      Your Rating: {userRating}/5
                    </Badge>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-4 mb-6 text-muted-foreground">
                  {movie.release_date && (
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      <span>{formatDate(movie.release_date)}</span>
                    </div>
                  )}
                  {movie.runtime && (
                    <div className="flex items-center gap-2">
                      <Clock className="w-5 h-5" />
                      <span>{formatRuntime(movie.runtime)}</span>
                    </div>
                  )}
                </div>

                {movie.genres && movie.genres.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-6">
                    {movie.genres.map((genre) => (
                      <Badge key={genre.id} variant="outline">
                        {genre.name}
                      </Badge>
                    ))}
                  </div>
                )}

                <p className="text-lg text-muted-foreground leading-relaxed mb-8">
                  {movie.overview}
                </p>

                <div className="flex flex-wrap gap-4">
                  {movie.trailer_key && (
                    <Button size="lg" className="gap-2">
                      <Play className="w-5 h-5" />
                      Play Trailer
                    </Button>
                  )}
                  <Button
                    size="lg"
                    variant="outline"
                    className="gap-2"
                    onClick={handleWatchlistToggle}
                  >
                    {inWatchlist ? (
                      <>
                        <Check className="w-5 h-5" />
                        In Watchlist
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5" />
                        Add to Watchlist
                      </>
                    )}
                  </Button>
                  <Button
                    size="lg"
                    variant="secondary"
                    onClick={() => setShowRatingDialog(true)}
                  >
                    <Star className="w-5 h-5 mr-2" />
                    {userRating ? 'Update Rating' : 'Rate Movie'}
                  </Button>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Cast Section */}
      {movie.cast && movie.cast.length > 0 && (
        <section className="py-16">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold mb-8">Cast</h2>
            <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide">
              {movie.cast.slice(0, 10).map((member) => (
                <div key={member.id} className="flex-shrink-0 text-center">
                  <div className="w-32 h-32 rounded-full overflow-hidden mb-3 bg-muted">
                    {member.profile_path ? (
                      <img
                        src={getImageUrl(member.profile_path, 'w200')}
                        alt={member.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <span className="text-4xl">👤</span>
                      </div>
                    )}
                  </div>
                  <p className="font-semibold text-sm">{member.name}</p>
                  <p className="text-xs text-muted-foreground">{member.character}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Similar Movies */}
      {similarMovies.length > 0 && (
        <section className="py-16">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold mb-8">You Might Also Like</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
              {similarMovies.slice(0, 12).map((similarMovie) => (
                <MovieCard key={similarMovie.id} movie={similarMovie} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Rating Dialog */}
      <Dialog open={showRatingDialog} onOpenChange={setShowRatingDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rate {movie.title}</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center gap-6 py-6">
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  onMouseEnter={() => setHoverRating(rating)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => handleRateMovie(rating)}
                  className="transition-transform hover:scale-110"
                >
                  <Star
                    className={`w-12 h-12 ${
                      rating <= (hoverRating || userRating || 0)
                        ? 'fill-accent text-accent'
                        : 'text-muted-foreground'
                    }`}
                  />
                </button>
              ))}
            </div>
            <p className="text-sm text-muted-foreground">
              {hoverRating > 0 ? `${hoverRating} out of 5 stars` : 'Click to rate'}
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MovieDetails;
