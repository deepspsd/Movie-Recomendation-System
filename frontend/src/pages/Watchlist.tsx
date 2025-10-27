import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Heart, Trash2 } from 'lucide-react';
import Navbar from '@/components/Navbar';
import MovieCard from '@/components/MovieCard';
import { Button } from '@/components/ui/button';
import { watchlistAPI } from '@/services/api';
import type { WatchlistItem } from '@/types';
import toast from 'react-hot-toast';

const Watchlist = () => {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const data = await watchlistAPI.getAll();
      setWatchlist(data);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
      toast.error('Failed to load watchlist');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemove = async (movieId: number) => {
    try {
      await watchlistAPI.remove(movieId);
      setWatchlist(watchlist.filter((item) => item.movie_id !== movieId));
      toast.success('Removed from watchlist');
    } catch (error) {
      toast.error('Failed to remove from watchlist');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 pt-24 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center gap-4 mb-4">
            <Heart className="w-10 h-10 text-primary fill-primary" />
            <h1 className="text-5xl font-bold">My Watchlist</h1>
          </div>
          <p className="text-xl text-muted-foreground">
            {watchlist.length} movie{watchlist.length !== 1 ? 's' : ''} saved
          </p>
        </motion.div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="aspect-[2/3] bg-muted animate-pulse rounded-xl" />
            ))}
          </div>
        ) : watchlist.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {watchlist.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="relative group"
              >
                <MovieCard movie={item.movie} />
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemove(item.movie_id);
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <Heart className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-xl text-muted-foreground mb-4">
              Your watchlist is empty
            </p>
            <Button onClick={() => window.location.href = '/movies'}>
              Browse Movies
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Watchlist;
