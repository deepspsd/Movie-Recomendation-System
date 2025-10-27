import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { User, Calendar, Star } from 'lucide-react';
import Navbar from '@/components/Navbar';
import MovieCard from '@/components/MovieCard';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuthStore } from '@/store/authStore';
import { ratingsAPI } from '@/services/api';
import type { Rating } from '@/types';
import { formatDate } from '@/utils/helpers';

const Profile = () => {
  const { user } = useAuthStore();
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchUserRatings();
  }, []);

  const fetchUserRatings = async () => {
    try {
      const data = await ratingsAPI.getUserRatings();
      setRatings(data);
    } catch (error) {
      console.error('Error fetching ratings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 pt-24 pb-16">
        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-2xl p-8 mb-8"
        >
          <div className="flex items-start gap-6">
            <Avatar className="w-24 h-24">
              <AvatarFallback className="bg-primary text-primary-foreground text-3xl">
                {user.username.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <h1 className="text-4xl font-bold mb-2">{user.username}</h1>
              <p className="text-muted-foreground mb-4">{user.email}</p>

              <div className="flex flex-wrap gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-muted-foreground" />
                  <span>Joined {formatDate(user.created_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-accent fill-accent" />
                  <span>{ratings.length} movies rated</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <Tabs defaultValue="ratings" className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="ratings">Rated Movies</TabsTrigger>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="ratings">
            {isLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {[...Array(10)].map((_, i) => (
                  <div key={i} className="aspect-[2/3] bg-muted animate-pulse rounded-xl" />
                ))}
              </div>
            ) : ratings.length > 0 ? (
              <div className="space-y-4">
                {ratings.map((rating) => (
                  <div
                    key={rating.id}
                    className="bg-card border border-border rounded-xl p-4 flex items-center gap-4"
                  >
                    <div className="flex items-center gap-2">
                      <Star className="w-5 h-5 fill-accent text-accent" />
                      <span className="text-xl font-bold">{rating.rating}</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">Movie ID: {rating.movie_id}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(rating.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <Star className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-xl text-muted-foreground">
                  You haven't rated any movies yet
                </p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="stats">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-card border border-border rounded-xl p-6 text-center">
                <p className="text-4xl font-bold text-primary mb-2">{ratings.length}</p>
                <p className="text-muted-foreground">Movies Rated</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 text-center">
                <p className="text-4xl font-bold text-primary mb-2">
                  {ratings.length > 0
                    ? (ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length).toFixed(1)
                    : '0'}
                </p>
                <p className="text-muted-foreground">Average Rating</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 text-center">
                <p className="text-4xl font-bold text-primary mb-2">
                  {user.favorite_genres?.length || 0}
                </p>
                <p className="text-muted-foreground">Favorite Genres</p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Profile;
