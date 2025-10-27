import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search as SearchIcon } from 'lucide-react';
import Navbar from '@/components/Navbar';
import MovieCard from '@/components/MovieCard';
import { SearchSkeleton } from '@/components/LoadingSkeleton';
import { Input } from '@/components/ui/input';
import { moviesAPI } from '@/services/api';
import { debounce } from '@/utils/helpers';
import type { Movie } from '@/types';

const Search = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      searchMovies(q);
    }
  }, [searchParams]);

  const searchMovies = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setMovies([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await moviesAPI.search({ query: searchQuery });
      setMovies(response.movies);
    } catch (error) {
      console.error('Error searching movies:', error);
      setMovies([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = debounce((value: string) => {
    setSearchParams({ q: value });
  }, 500);

  const handleInputChange = (value: string) => {
    setQuery(value);
    handleSearch(value);
  };

  if (isLoading && !query) {
    return <SearchSkeleton />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 pt-24 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto mb-12"
        >
          <h1 className="text-4xl font-bold mb-6 text-center">Search Movies</h1>
          <div className="relative">
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              value={query}
              onChange={(e) => handleInputChange(e.target.value)}
              placeholder="Search for movies..."
              className="pl-12 h-14 text-lg"
              autoFocus
            />
          </div>
        </motion.div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {[...Array(20)].map((_, i) => (
              <div key={i} className="aspect-[2/3] bg-muted animate-pulse rounded-xl" />
            ))}
          </div>
        ) : movies.length > 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <p className="text-muted-foreground mb-6">
              Found {movies.length} result{movies.length !== 1 ? 's' : ''} for "{query}"
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          </motion.div>
        ) : query ? (
          <div className="text-center py-20">
            <p className="text-xl text-muted-foreground">
              No results found for "{query}"
            </p>
          </div>
        ) : (
          <div className="text-center py-20">
            <SearchIcon className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-xl text-muted-foreground">
              Start typing to search for movies
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;
