import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Plus, TrendingUp, Sparkles, Clock, Check, Star, Film, Heart, Eye, Award, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Navbar from "@/components/Navbar";
import MovieCard from "@/components/MovieCard";
import Carousel from "@/components/Carousel";
import MoodCard from "@/components/MoodCard";
import { DashboardSkeleton } from "@/components/LoadingSkeleton";
import { moviesAPI, recommendationsAPI, watchlistAPI, ratingsAPI } from "@/services/api";
import { getImageUrl, formatRating } from "@/utils/helpers";
import type { Movie, MoodType } from "@/types";
import toast from "react-hot-toast";

const MOOD_OPTIONS = [
  { value: 'happy' as MoodType, label: 'Happy', emoji: '😊', description: 'Feel-good movies' },
  { value: 'adventurous' as MoodType, label: 'Adventurous', emoji: '🎬', description: 'Action-packed' },
  { value: 'romantic' as MoodType, label: 'Romantic', emoji: '❤️', description: 'Love stories' },
  { value: 'scared' as MoodType, label: 'Thrilling', emoji: '😱', description: 'Suspenseful' },
];

const Dashboard = () => {
  const navigate = useNavigate();
  const [featuredMovie, setFeaturedMovie] = useState<Movie | null>(null);
  const [featuredIndex, setFeaturedIndex] = useState(0);
  const [recommendedMovies, setRecommendedMovies] = useState<Movie[]>([]);
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([]);
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [topRatedMovies, setTopRatedMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [userStats, setUserStats] = useState({
    watchedCount: 0,
    watchlistCount: 0,
    ratingsCount: 0,
    favoriteGenres: [] as string[]
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch all data in parallel
      const [recommendedData, trendingData, popularData, watchlistData, ratingsData] = await Promise.all([
        recommendationsAPI.getPersonalized().catch(() => ({ movies: [] })),
        moviesAPI.getTrending().catch(() => []),
        moviesAPI.getPopular().catch(() => []),
        watchlistAPI.getAll().catch(() => []),
        ratingsAPI.getUserRatings().catch(() => []),
      ]);

      setRecommendedMovies(recommendedData.movies || []);
      setTrendingMovies(trendingData || []);
      setPopularMovies(popularData || []);
      
      // Set user stats
      setUserStats({
        watchedCount: ratingsData?.length || 0,
        watchlistCount: watchlistData?.length || 0,
        ratingsCount: ratingsData?.length || 0,
        favoriteGenres: ['Action', 'Sci-Fi', 'Drama'] // Mock data
      });
      
      // Set top rated movies (from popular with high ratings)
      const topRated = (popularData || []).filter((m: Movie) => m.vote_average >= 8.0).slice(0, 10);
      setTopRatedMovies(topRated);
      
      // Set featured movie from popular movies
      if (popularData && popularData.length > 0) {
        setFeaturedMovie(popularData[0]);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMoodClick = (mood: MoodType) => {
    navigate(`/mood?selected=${mood}`);
  };

  // Auto-rotate featured movie
  useEffect(() => {
    if (popularMovies.length > 1) {
      const interval = setInterval(() => {
        setFeaturedIndex((prev) => (prev + 1) % Math.min(popularMovies.length, 5));
      }, 8000);
      return () => clearInterval(interval);
    }
  }, [popularMovies]);

  useEffect(() => {
    if (popularMovies.length > 0) {
      setFeaturedMovie(popularMovies[featuredIndex]);
    }
  }, [featuredIndex, popularMovies]);

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      {featuredMovie && (
        <section className="relative h-[85vh] mt-20">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: `url(${getImageUrl(featuredMovie.backdrop_path, 'original')})`,
              filter: "brightness(0.35)",
            }}
          />
          
          <div className="absolute inset-0 bg-gradient-to-b from-background/70 via-background/50 to-background" />
          <div className="absolute inset-0 bg-gradient-to-r from-background/95 via-background/30 to-transparent" />

          <div className="relative z-10 h-full flex items-center">
            <div className="container mx-auto px-4">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="max-w-2xl"
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={featuredMovie.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <Badge className="bg-primary/20 text-primary border-primary/30">
                        <TrendingUp className="w-3 h-3 mr-1" />
                        Featured
                      </Badge>
                      <div className="flex items-center gap-1 text-accent">
                        <Sparkles className="w-4 h-4 fill-accent" />
                        <span className="font-semibold">{formatRating(featuredMovie.vote_average)}</span>
                      </div>
                      <span className="text-muted-foreground">
                        {new Date(featuredMovie.release_date).getFullYear()}
                      </span>
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                      {featuredMovie.title}
                    </h1>
                    <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed max-w-2xl">
                      {featuredMovie.overview?.slice(0, 200)}{featuredMovie.overview?.length > 200 ? '...' : ''}
                    </p>
                    <div className="flex flex-wrap gap-4">
                      <Button 
                        size="lg" 
                        className="gap-2 h-12 px-8 shadow-lg shadow-primary/20"
                        onClick={() => navigate(`/movies/${featuredMovie.id}`)}
                      >
                        <Play className="w-5 h-5" />
                        Watch Now
                      </Button>
                      <Button 
                        size="lg" 
                        variant="outline" 
                        className="gap-2 h-12 px-8"
                        onClick={() => navigate(`/movies/${featuredMovie.id}`)}
                      >
                        <Plus className="w-5 h-5" />
                        My List
                      </Button>
                      <Button 
                        size="lg" 
                        variant="ghost" 
                        className="gap-2 h-12 px-8"
                        onClick={() => navigate(`/movies/${featuredMovie.id}`)}
                      >
                        More Info
                      </Button>
                    </div>
                  </motion.div>
                </AnimatePresence>
                
                {/* Featured Movie Indicators */}
                {popularMovies.length > 1 && (
                  <div className="flex gap-2 mt-8">
                    {popularMovies.slice(0, 5).map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setFeaturedIndex(index)}
                        className={`h-1 rounded-full transition-all duration-300 ${
                          index === featuredIndex 
                            ? 'w-8 bg-primary' 
                            : 'w-6 bg-muted-foreground/30 hover:bg-muted-foreground/50'
                        }`}
                      />
                    ))}
                  </div>
                )}
              </motion.div>
            </div>
          </div>
        </section>
      )}

      {/* Stats Section */}
      <section className="py-12 bg-gradient-to-b from-background to-card/30">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: Eye, label: 'Watched', value: userStats.watchedCount, color: 'text-blue-500' },
              { icon: Heart, label: 'Watchlist', value: userStats.watchlistCount, color: 'text-red-500' },
              { icon: Star, label: 'Ratings', value: userStats.ratingsCount, color: 'text-yellow-500' },
              { icon: Award, label: 'Favorites', value: userStats.favoriteGenres.length, color: 'text-purple-500' },
            ].map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all cursor-pointer group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <Icon className={`w-8 h-8 ${stat.color} group-hover:scale-110 transition-transform`} />
                    <span className="text-3xl font-bold">{stat.value}</span>
                  </div>
                  <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="py-8 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
            {[
              { icon: Sparkles, label: 'For You', path: '/dashboard', gradient: 'from-purple-500 to-pink-500' },
              { icon: TrendingUp, label: 'Trending', path: '/movies', gradient: 'from-orange-500 to-red-500' },
              { icon: Heart, label: 'Mood Match', path: '/mood', gradient: 'from-pink-500 to-rose-500' },
              { icon: Clock, label: 'Continue Watching', path: '/watchlist', gradient: 'from-blue-500 to-cyan-500' },
              { icon: Plus, label: 'My List', path: '/watchlist', gradient: 'from-green-500 to-emerald-500' },
            ].map((action, index) => {
              const Icon = action.icon;
              return (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => navigate(action.path)}
                  className="relative flex items-center gap-2 px-6 py-3 bg-card border border-border rounded-full hover:border-primary/50 transition-all whitespace-nowrap group overflow-hidden"
                >
                  <div className={`absolute inset-0 bg-gradient-to-r ${action.gradient} opacity-0 group-hover:opacity-10 transition-opacity`} />
                  <Icon className="w-4 h-4 relative z-10" />
                  <span className="text-sm font-medium relative z-10">{action.label}</span>
                </motion.button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Recommended Section - ML Powered */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-3xl font-bold flex items-center gap-2">
                    <Sparkles className="w-7 h-7 text-primary" />
                    Recommended For You
                  </h2>
                  <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0">
                    <Zap className="w-3 h-3 mr-1" />
                    AI Powered
                  </Badge>
                </div>
                <p className="text-muted-foreground mt-1">Personalized using advanced ML algorithms</p>
              </div>
              <Button variant="ghost" onClick={() => navigate('/movies')}>
                View All
              </Button>
            </div>
            {recommendedMovies.length > 0 ? (
              <Carousel>
                <div className="flex gap-6">
                  {recommendedMovies.slice(0, 10).map((movie) => (
                    <div key={movie.id} className="w-48 flex-shrink-0">
                      <MovieCard movie={movie} />
                    </div>
                  ))}
                </div>
              </Carousel>
            ) : (
              <div className="text-center py-12 bg-card/30 rounded-xl border border-border">
                <Sparkles className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Rate some movies to get personalized recommendations!</p>
                <Button className="mt-4" onClick={() => navigate('/movies')}>
                  Explore Movies
                </Button>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Trending Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold flex items-center gap-2">
                  <TrendingUp className="w-7 h-7 text-orange-500" />
                  Trending Now
                </h2>
                <p className="text-muted-foreground mt-1">What everyone's watching right now</p>
              </div>
              <Button variant="ghost" onClick={() => navigate('/movies')}>
                View All
              </Button>
            </div>
            <Carousel>
              <div className="flex gap-6">
                {trendingMovies.slice(0, 10).map((movie) => (
                  <div key={movie.id} className="w-48 flex-shrink-0">
                    <MovieCard movie={movie} />
                  </div>
                ))}
              </div>
            </Carousel>
          </motion.div>
        </div>
      </section>

      {/* Top Rated Section */}
      {topRatedMovies.length > 0 && (
        <section className="py-16 bg-card/30">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-bold flex items-center gap-2">
                    <Award className="w-7 h-7 text-yellow-500" />
                    Top Rated Movies
                  </h2>
                  <p className="text-muted-foreground mt-1">Critically acclaimed masterpieces</p>
                </div>
                <Button variant="ghost" onClick={() => navigate('/movies')}>
                  View All
                </Button>
              </div>
              <Carousel>
                <div className="flex gap-6">
                  {topRatedMovies.map((movie) => (
                    <div key={movie.id} className="w-48 flex-shrink-0">
                      <MovieCard movie={movie} />
                    </div>
                  ))}
                </div>
              </Carousel>
            </motion.div>
          </div>
        </section>
      )}

      {/* Mood Selector Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Browse by Mood</h2>
              <p className="text-muted-foreground text-lg">
                Find movies that match how you're feeling today
              </p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {MOOD_OPTIONS.map((mood, index) => (
                <motion.div
                  key={mood.value}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <MoodCard
                    mood={mood.value}
                    emoji={mood.emoji}
                    label={mood.label}
                    description={mood.description}
                    onClick={() => handleMoodClick(mood.value)}
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
