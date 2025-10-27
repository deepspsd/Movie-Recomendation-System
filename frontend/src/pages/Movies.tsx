import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Filter, Search, TrendingUp, Star, Clock, Film, X } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { EnhancedMovieCard } from '@/components/dashboard/EnhancedMovieCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { moviesAPI, omdbAPI } from '@/services/api';
import type { Movie } from '@/types';
import toast from 'react-hot-toast';

const GENRES = [
  { id: 28, name: 'Action' },
  { id: 12, name: 'Adventure' },
  { id: 16, name: 'Animation' },
  { id: 35, name: 'Comedy' },
  { id: 80, name: 'Crime' },
  { id: 99, name: 'Documentary' },
  { id: 18, name: 'Drama' },
  { id: 10751, name: 'Family' },
  { id: 14, name: 'Fantasy' },
  { id: 36, name: 'History' },
  { id: 27, name: 'Horror' },
  { id: 10402, name: 'Music' },
  { id: 9648, name: 'Mystery' },
  { id: 10749, name: 'Romance' },
  { id: 878, name: 'Science Fiction' },
  { id: 10770, name: 'TV Movie' },
  { id: 53, name: 'Thriller' },
  { id: 10752, name: 'War' },
  { id: 37, name: 'Western' },
];

const Movies = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedGenre, setSelectedGenre] = useState<string>('');
  const [sortBy, setSortBy] = useState<'popularity' | 'rating' | 'release_date'>('popularity');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('popular');
  const [yearFilter, setYearFilter] = useState('');
  const [initialLoad, setInitialLoad] = useState(true);

  useEffect(() => {
    fetchMovies();
  }, [page, selectedGenre, sortBy, activeTab]);

  const fetchMovies = async () => {
    try {
      setIsLoading(true);
      let data;

      // Fetch based on active tab (all tabs show 30 movies)
      if (activeTab === 'popular') {
        data = await omdbAPI.getPopularMovies(30);
        setMovies(data.movies || []);
        setTotalPages(1);
      } else if (activeTab === 'top-rated') {
        data = await omdbAPI.getBestMovies(30);
        setMovies(data.movies || []);
        setTotalPages(1);
      } else if (activeTab === 'latest') {
        const currentYear = new Date().getFullYear();
        data = await omdbAPI.getMoviesByYear(currentYear, 30);
        setMovies(data.movies || []);
        setTotalPages(1);
      }

      if (initialLoad) {
        setInitialLoad(false);
      }

      if (data.movies?.length > 0) {
        toast.success(`Loaded ${data.movies.length} movies`, { duration: 2000 });
      }
    } catch (error) {
      console.error('Error fetching movies:', error);
      toast.error('Failed to load movies. Please try again.');
      setMovies([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (page < totalPages) {
      setPage(page + 1);
    }
  };

  return (
    <div className="min-h-screen bg-background pt-20">
      <Navbar />

      <div className="container mx-auto px-4 max-w-7xl py-8">
        {/* Header with Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-6">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500">
                  <Film className="w-8 h-8 text-white" />
                </div>
                Browse Movies
              </h1>
              <p className="text-sm text-muted-foreground">
                Discover thousands of movies from around the world
              </p>
            </div>
            <Badge variant="secondary" className="text-sm">
              {movies.length} movies loaded
            </Badge>
          </div>

          {/* Search Bar */}
          <div className="relative max-w-2xl">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search movies by title, actor, director..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-10 h-12 text-base"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </motion.div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="popular" className="gap-2">
              <TrendingUp className="w-4 h-4" />
              Popular
            </TabsTrigger>
            <TabsTrigger value="top-rated" className="gap-2">
              <Star className="w-4 h-4" />
              Top Rated
            </TabsTrigger>
            <TabsTrigger value="latest" className="gap-2">
              <Clock className="w-4 h-4" />
              Latest
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-4 mb-12 items-center"
        >
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-muted-foreground" />
            <span className="font-semibold">Filters:</span>
          </div>

          <Select value={selectedGenre || "all"} onValueChange={(value) => setSelectedGenre(value === "all" ? "" : value)}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="All Genres" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Genres</SelectItem>
              {GENRES.map((genre) => (
                <SelectItem key={genre.id} value={genre.id.toString()}>
                  {genre.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="popularity">Most Popular</SelectItem>
              <SelectItem value="rating">Highest Rated</SelectItem>
              <SelectItem value="release_date">Latest Release</SelectItem>
            </SelectContent>
          </Select>

          {selectedGenre && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSelectedGenre('');
                setPage(1);
              }}
            >
              Clear Filters
            </Button>
          )}
        </motion.div>

        {/* Movies Grid */}
        {isLoading && movies.length === 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {[...Array(20)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="aspect-[2/3] bg-muted/30 rounded-lg mb-3" />
                <div className="h-4 bg-muted/30 rounded w-3/4 mb-2" />
                <div className="h-3 bg-muted/30 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Results Count */}
            {movies.length > 0 && (
              <div className="flex items-center justify-between mb-4 p-3 bg-card/50 rounded-lg border border-border/50">
                <div className="flex items-center gap-2 text-sm">
                  <Film className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">
                    Showing <span className="font-semibold text-foreground">{movies.length}</span> movies
                  </span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {activeTab === 'popular' ? 'Most Popular' : activeTab === 'top-rated' ? 'Highest Rated' : 'Latest Releases'}
                </Badge>
              </div>
            )}

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
            >
              {movies
                .filter(movie => 
                  searchQuery === '' || 
                  movie.title.toLowerCase().includes(searchQuery.toLowerCase())
                )
                .map((movie, index) => (
                  <motion.div
                    key={movie.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: Math.min(index * 0.03, 0.5) }}
                  >
                    <EnhancedMovieCard
                      movie={movie}
                      recommendationScore={0.8}
                      contentScore={0.5}
                      collaborativeScore={0.5}
                    />
                  </motion.div>
                ))}
            </motion.div>

            {/* Load More */}
            {page < totalPages && (
              <div className="flex justify-center mt-12">
                <Button
                  size="lg"
                  onClick={handleLoadMore}
                  disabled={isLoading}
                  className="min-w-[200px]"
                >
                  {isLoading ? 'Loading...' : 'Load More Movies'}
                </Button>
              </div>
            )}

            {movies.length === 0 && !isLoading && (
              <div className="text-center py-20">
                <Film className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-xl font-semibold mb-2">No movies found</p>
                <p className="text-muted-foreground">
                  Try adjusting your filters or search query
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Movies;
