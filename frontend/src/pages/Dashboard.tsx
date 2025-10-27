import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Plus, TrendingUp, Sparkles, Clock, Star, Film, Heart, Eye, Award, Zap, BarChart3, ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Navbar from "@/components/Navbar";
import MovieCard from "@/components/MovieCard";
import Carousel from "@/components/Carousel";
import MoodCard from "@/components/MoodCard";
import { DashboardSkeleton } from "@/components/LoadingSkeleton";
import { AlgorithmSelector } from "@/components/recommendations/AlgorithmSelector";
import { UserInteractionPanel } from "@/components/dashboard/UserInteractionPanel";
import { EnhancedMovieCard } from "@/components/dashboard/EnhancedMovieCard";
import { RecommendationFilters, type FilterOptions } from "@/components/dashboard/RecommendationFilters";
import { moviesAPI, recommendationsAPI, watchlistAPI, ratingsAPI } from "@/services/api";
import { getImageUrl, formatRating } from "@/utils/helpers";
import type { Movie, MoodType, AlgorithmType } from "@/types";
import toast from "react-hot-toast";

const MOOD_OPTIONS = [
  { value: 'happy' as MoodType, label: 'Happy', emoji: '😊', description: 'Feel-good movies' },
  { value: 'adventurous' as MoodType, label: 'Adventurous', emoji: '🎬', description: 'Action-packed' },
  { value: 'romantic' as MoodType, label: 'Romantic', emoji: '❤️', description: 'Love stories' },
  { value: 'scared' as MoodType, label: 'Thrilling', emoji: '😱', description: 'Suspenseful' },
];

const EnhancedDashboard = () => {
  const navigate = useNavigate();
  const [featuredMovie, setFeaturedMovie] = useState<Movie | null>(null);
  const [featuredIndex, setFeaturedIndex] = useState(0);
  const [recommendedMovies, setRecommendedMovies] = useState<Movie[]>([]);
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([]);
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [topRatedMovies, setTopRatedMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<AlgorithmType>('hybrid');
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [sectionsLoaded, setSectionsLoaded] = useState({
    popular: false,
    trending: false,
    recommended: false,
    stats: false
  });
  const [userStats, setUserStats] = useState({
    watchedCount: 0,
    watchlistCount: 0,
    ratingsCount: 0,
    favoriteGenres: ['Action', 'Sci-Fi', 'Drama'] as string[]
  });
  const [contentWeight, setContentWeight] = useState(0.5);
  const [collaborativeWeight, setCollaborativeWeight] = useState(0.5);
  const [filters, setFilters] = useState<FilterOptions>({
    genres: [],
    yearRange: [1900, new Date().getFullYear()],
    minRating: 0,
    sortBy: 'score',
    viewMode: 'grid',
  });
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      fetchRecommendations(selectedAlgorithm);
    }
  }, [selectedAlgorithm]);

  const fetchDashboardData = async () => {
    try {
      // Load popular movies first (fastest, for hero section)
      moviesAPI.getPopular().then((popularData) => {
        setPopularMovies(popularData || []);
        setSectionsLoaded(prev => ({ ...prev, popular: true }));
        
        const topRated = (popularData || []).filter((m: Movie) => m.vote_average >= 8.0).slice(0, 10);
        setTopRatedMovies(topRated);
        
        if (popularData && popularData.length > 0) {
          setFeaturedMovie(popularData[0]);
        }
      }).catch((err) => {
        console.warn('Failed to load popular:', err);
        setSectionsLoaded(prev => ({ ...prev, popular: true }));
      });

      // Load trending movies
      moviesAPI.getTrending().then((trendingData) => {
        setTrendingMovies(trendingData || []);
        setSectionsLoaded(prev => ({ ...prev, trending: true }));
      }).catch((err) => {
        console.warn('Failed to load trending:', err);
        setSectionsLoaded(prev => ({ ...prev, trending: true }));
      });

      // Load user stats
      Promise.all([
        watchlistAPI.getAll().catch(() => []),
        ratingsAPI.getUserRatings().catch(() => [])
      ]).then(([watchlistData, ratingsData]) => {
        setUserStats({
          watchedCount: ratingsData?.length || 0,
          watchlistCount: watchlistData?.length || 0,
          ratingsCount: ratingsData?.length || 0,
          favoriteGenres: userStats.favoriteGenres
        });
        setSectionsLoaded(prev => ({ ...prev, stats: true }));
      }).catch((err) => {
        console.warn('Failed to load stats:', err);
        setSectionsLoaded(prev => ({ ...prev, stats: true }));
      });

      // Load recommendations last (slowest due to ML)
      recommendationsAPI.getPersonalized('hybrid').then((recommendedData) => {
        setRecommendedMovies(recommendedData.movies || []);
        setSectionsLoaded(prev => ({ ...prev, recommended: true }));
        
        if (recommendedData.movies?.length > 0) {
          toast.success('Personalized recommendations ready!', { duration: 2000 });
        }
      }).catch((err) => {
        console.warn('Failed to load recommendations:', err);
        setSectionsLoaded(prev => ({ ...prev, recommended: true }));
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Some content failed to load. Please refresh the page.');
    }
  };

  const fetchRecommendations = async (algorithm: AlgorithmType) => {
    try {
      setIsLoadingRecommendations(true);
      const data = await recommendationsAPI.getPersonalized(algorithm);
      setRecommendedMovies(data.movies || []);
      toast.success(`Recommendations updated using ${algorithm.toUpperCase()} algorithm`);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      toast.error('Failed to update recommendations');
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const handleMoodClick = (mood: MoodType) => {
    navigate(`/mood?selected=${mood}`);
  };

  const handleWeightChange = (content: number, collaborative: number) => {
    setContentWeight(content);
    setCollaborativeWeight(collaborative);
    toast.success('Algorithm weights updated');
  };

  const handleGenresUpdate = (genres: string[]) => {
    setUserStats({ ...userStats, favoriteGenres: genres });
    toast.success('Preferences updated');
  };

  // Filter and sort recommendations
  const filteredRecommendations = useMemo(() => {
    let filtered = [...recommendedMovies];

    // Filter by genres
    if (filters.genres.length > 0) {
      filtered = filtered.filter((movie) =>
        movie.genres?.some((g) => filters.genres.includes(g.name))
      );
    }

    // Filter by year
    filtered = filtered.filter((movie) => {
      if (!movie.release_date) return true; // Include movies without release date
      const year = new Date(movie.release_date).getFullYear();
      return year >= filters.yearRange[0] && year <= filters.yearRange[1];
    });

    // Filter by rating
    if (filters.minRating > 0) {
      filtered = filtered.filter((movie) => movie.vote_average >= filters.minRating);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'rating':
          return b.vote_average - a.vote_average;
        case 'year':
          return new Date(b.release_date).getTime() - new Date(a.release_date).getTime();
        case 'popularity':
          return b.popularity - a.popularity;
        case 'score':
        default:
          return 0;
      }
    });

    return filtered;
  }, [recommendedMovies, filters]);

  const availableGenres = useMemo(() => {
    const genres = new Set<string>();
    recommendedMovies.forEach((movie) => {
      movie.genres?.forEach((g) => genres.add(g.name));
    });
    return Array.from(genres).sort();
  }, [recommendedMovies]);

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

  // Scroll to top button visibility
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 500);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-background pt-20">
      <Navbar />
      
      {/* Stats Section - Moved to Top */}
      <section className="py-6 bg-background/95 backdrop-blur-sm border-b border-border/50 sticky top-20 z-40">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="grid grid-cols-5 gap-3">
            {[
              { icon: Eye, label: 'Watched', value: userStats.watchedCount, color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
              { icon: Heart, label: 'Watchlist', value: userStats.watchlistCount, color: 'text-red-500', bgColor: 'bg-red-500/10' },
              { icon: Star, label: 'Ratings', value: userStats.ratingsCount, color: 'text-yellow-500', bgColor: 'bg-yellow-500/10' },
              { icon: Award, label: 'Favorites', value: userStats.favoriteGenres.length, color: 'text-purple-500', bgColor: 'bg-purple-500/10' },
              { icon: BarChart3, label: 'Analytics', value: '→', color: 'text-green-500', bgColor: 'bg-green-500/10', onClick: () => navigate('/analytics') },
            ].map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-card/80 backdrop-blur-sm border border-border/50 rounded-lg p-3 hover:border-primary/30 hover:shadow-lg transition-all cursor-pointer group"
                  onClick={stat.onClick}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className={`p-1.5 rounded-md ${stat.bgColor} group-hover:scale-110 transition-transform`}>
                      <Icon className={`w-4 h-4 ${stat.color}`} />
                    </div>
                    <span className="text-xl font-bold">{stat.value}</span>
                  </div>
                  <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{stat.label}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>
      
      {/* Hero Section */}
      {!sectionsLoaded.popular ? (
        <section className="relative h-[50vh] bg-muted/20 animate-pulse">
          <div className="absolute inset-0 bg-gradient-to-b from-background/70 via-background/50 to-background" />
        </section>
      ) : featuredMovie ? (
        <section className="relative h-[50vh]">
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
            <div className="container mx-auto px-4 max-w-7xl">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="max-w-3xl"
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={featuredMovie.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.4 }}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <Badge className="bg-primary/20 text-primary border-primary/30 text-xs">
                        <TrendingUp className="w-3 h-3 mr-1" />
                        Featured
                      </Badge>
                      <div className="flex items-center gap-1 text-accent">
                        <Sparkles className="w-3 h-3 fill-accent" />
                        <span className="text-sm font-semibold">{formatRating(featuredMovie.vote_average)}</span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {new Date(featuredMovie.release_date).getFullYear()}
                      </span>
                    </div>
                    <h1 className="text-3xl md:text-5xl font-bold mb-4 leading-tight">
                      {featuredMovie.title}
                    </h1>
                    <p className="text-sm md:text-base text-muted-foreground mb-6 leading-relaxed max-w-2xl line-clamp-2">
                      {featuredMovie.overview}
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <Button 
                        size="default"
                        className="gap-2 shadow-lg shadow-primary/20"
                        onClick={() => navigate(`/movies/${featuredMovie.id}`)}
                      >
                        <Play className="w-4 h-4" />
                        Watch Now
                      </Button>
                      <Button 
                        size="default"
                        variant="outline" 
                        className="gap-2"
                        onClick={() => navigate(`/movies/${featuredMovie.id}`)}
                      >
                        <Plus className="w-4 h-4" />
                        My List
                      </Button>
                    </div>
                  </motion.div>
                </AnimatePresence>
                
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
      ) : null}

      {/* User Interaction Panel & Algorithm Selector */}
      <section className="py-12 bg-background">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* User Panel - Left Sidebar */}
            <div className="lg:col-span-4 xl:col-span-3">
              <UserInteractionPanel
                contentWeight={contentWeight}
                collaborativeWeight={collaborativeWeight}
                onWeightChange={handleWeightChange}
                favoriteGenres={userStats.favoriteGenres}
                onGenresUpdate={handleGenresUpdate}
              />
            </div>
            
            {/* Algorithm Selector - Main Content */}
            <div className="lg:col-span-8 xl:col-span-9">
              <AlgorithmSelector
                selected={selectedAlgorithm}
                onChange={setSelectedAlgorithm}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Recommended Section - ML Powered with Filters */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            {/* Section Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/20">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">Recommended For You</h2>
                    <p className="text-sm text-muted-foreground">
                      {filteredRecommendations.length > 0 
                        ? `${filteredRecommendations.length} movies match your preferences`
                        : 'Personalized using advanced ML algorithms'
                      }
                    </p>
                  </div>
                </div>
              </div>
              <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 px-4 py-2 text-sm font-semibold shadow-lg shadow-purple-500/20">
                <Zap className="w-4 h-4 mr-2" />
                {selectedAlgorithm.toUpperCase()} AI
              </Badge>
            </div>

            {/* Filters */}
            <div className="mb-8 p-4 bg-card/50 backdrop-blur-sm rounded-lg border border-border/50">
              <RecommendationFilters
                filters={filters}
                onFiltersChange={setFilters}
                availableGenres={availableGenres}
              />
            </div>
            
            {isLoadingRecommendations ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {[...Array(10)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="aspect-[2/3] bg-muted rounded-lg mb-3" />
                    <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                    <div className="h-3 bg-muted rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : filteredRecommendations.length > 0 ? (
              <>
                {/* Results Summary */}
                <div className="flex items-center justify-between mb-4 p-3 bg-card/50 rounded-lg border border-border/50">
                  <div className="flex items-center gap-2 text-sm">
                    <Film className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Showing <span className="font-semibold text-foreground">{filteredRecommendations.length}</span> {filteredRecommendations.length === 1 ? 'movie' : 'movies'}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Sorted by {filters.sortBy === 'score' ? 'Match Score' : filters.sortBy === 'rating' ? 'Rating' : filters.sortBy === 'year' ? 'Release Year' : 'Popularity'}
                  </div>
                </div>

                <div className={filters.viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4' : 'space-y-4'}>
                  {filteredRecommendations.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: Math.min(index * 0.03, 0.5), duration: 0.3 }}
                    >
                      <EnhancedMovieCard
                        movie={movie}
                        recommendationScore={0.85}
                        contentScore={contentWeight}
                        collaborativeScore={collaborativeWeight}
                        onWatchlistToggle={fetchDashboardData}
                        onRatingChange={fetchDashboardData}
                      />
                    </motion.div>
                  ))}
                </div>
              </>
            
            ) : recommendedMovies.length > 0 ? (
              <div className="text-center py-12 bg-card/30 rounded-xl border border-border">
                <Sparkles className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">No movies match your filters. Try adjusting them!</p>
                <Button className="mt-4" onClick={() => setFilters({
                  genres: [],
                  yearRange: [1900, new Date().getFullYear()],
                  minRating: 0,
                  sortBy: 'score',
                  viewMode: 'grid',
                })}>
                  Clear Filters
                </Button>
              </div>
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
      <section className="py-12 bg-background">
        <div className="container mx-auto px-4 max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-red-500">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Trending Now</h2>
                  <p className="text-sm text-muted-foreground">What everyone's watching right now</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/movies')}>
                View All
              </Button>
            </div>
            {!sectionsLoaded.trending ? (
              <div className="flex gap-4">
                {[...Array(10)].map((_, i) => (
                  <div key={i} className="w-44 flex-shrink-0">
                    <div className="aspect-[2/3] bg-muted/20 rounded-lg animate-pulse" />
                  </div>
                ))}
              </div>
            ) : (
              <Carousel>
                <div className="flex gap-4">
                  {trendingMovies.slice(0, 10).map((movie) => (
                    <div key={movie.id} className="w-44 flex-shrink-0">
                      <MovieCard movie={movie} />
                    </div>
                  ))}
                </div>
              </Carousel>
            )}
          </motion.div>
        </div>
      </section>

      {/* Top Rated Section */}
      {topRatedMovies.length > 0 && (
        <section className="py-12 bg-muted/30">
          <div className="container mx-auto px-4 max-w-7xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">Top Rated Movies</h2>
                    <p className="text-sm text-muted-foreground">Critically acclaimed masterpieces</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => navigate('/movies')}>
                  View All
                </Button>
              </div>
              <Carousel>
                <div className="flex gap-4">
                  {topRatedMovies.map((movie) => (
                    <div key={movie.id} className="w-44 flex-shrink-0">
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
      <section className="py-12 bg-background">
        <div className="container mx-auto px-4 max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Browse by Mood</h2>
              <p className="text-sm text-muted-foreground">
                Find movies that match how you're feeling today
              </p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {MOOD_OPTIONS.map((mood, index) => (
                <motion.div
                  key={mood.value}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
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

      {/* Scroll to Top Button */}
      <AnimatePresence>
        {showScrollTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={scrollToTop}
            className="fixed bottom-8 right-8 z-50 p-3 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all hover:scale-110"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <ArrowUp className="w-5 h-5" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EnhancedDashboard;
