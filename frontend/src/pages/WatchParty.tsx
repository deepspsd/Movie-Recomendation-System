import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Plus, X, Search, Sparkles, TrendingUp, UserPlus, Zap, Award, Star } from 'lucide-react';
import Navbar from '@/components/Navbar';
import MovieCard from '@/components/MovieCard';
import { MovieCardSkeleton } from '@/components/LoadingSkeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { recommendationsAPI } from '@/services/api';
import type { Movie } from '@/types';
import toast from 'react-hot-toast';

const WatchParty = () => {
  const [userIds, setUserIds] = useState<string[]>([]);
  const [newUserId, setNewUserId] = useState('');
  const [movies, setMovies] = useState<Movie[]>([]);
  const [compatibilityScores, setCompatibilityScores] = useState<{ [key: number]: number }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedUsers] = useState(['user123', 'moviefan456', 'cinephile789']); // Mock suggested users

  const handleAddUser = () => {
    if (newUserId.trim() && !userIds.includes(newUserId.trim())) {
      setUserIds([...userIds, newUserId.trim()]);
      setNewUserId('');
    }
  };

  const handleRemoveUser = (userId: string) => {
    setUserIds(userIds.filter((id) => id !== userId));
  };

  const handleFindMovies = async () => {
    if (userIds.length === 0) {
      toast.error('Please add at least one user');
      return;
    }

    setIsLoading(true);
    try {
      const response = await recommendationsAPI.getWatchParty(userIds);
      setMovies(response.movies);
      setCompatibilityScores(response.compatibility_scores);
      toast.success(`Found ${response.movies.length} perfect movies for your group!`);
    } catch (error: any) {
      console.error('Error fetching watch party recommendations:', error);
      toast.error(error.response?.data?.detail || 'Failed to load recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddSuggestedUser = (userId: string) => {
    if (!userIds.includes(userId)) {
      setUserIds([...userIds, userId]);
      toast.success(`Added ${userId} to the group`);
    }
  };

  const getCompatibilityColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 pt-24 pb-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-block mb-6"
          >
            <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white border-0 text-lg px-6 py-2">
              <Zap className="w-5 h-5 mr-2" />
              AI Group Matching
            </Badge>
          </motion.div>
          <div className="flex items-center justify-center gap-4 mb-4">
            <Users className="w-12 h-12 text-primary" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-primary via-blue-500 to-purple-500 bg-clip-text text-transparent">
              Watch Party Matcher
            </h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Add your friends and let our ML algorithm find movies that everyone will love
          </p>
        </motion.div>

        {/* Add Users Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="max-w-3xl mx-auto mb-12"
        >
          <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <UserPlus className="w-6 h-6 text-primary" />
                Add Group Members
              </h2>
              {userIds.length > 0 && (
                <Badge variant="secondary" className="text-lg px-4 py-1">
                  {userIds.length} {userIds.length === 1 ? 'member' : 'members'}
                </Badge>
              )}
            </div>

            <div className="flex gap-2 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Enter user ID or email..."
                  value={newUserId}
                  onChange={(e) => setNewUserId(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddUser()}
                  className="pl-10"
                />
              </div>
              <Button onClick={handleAddUser} className="gap-2">
                <Plus className="w-4 h-4" />
                Add
              </Button>
            </div>

            {/* Suggested Users */}
            {userIds.length === 0 && suggestedUsers.length > 0 && (
              <div className="mb-6 p-4 bg-accent/10 rounded-lg border border-accent/20">
                <p className="text-sm font-medium mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-accent" />
                  Suggested Friends
                </p>
                <div className="flex flex-wrap gap-2">
                  {suggestedUsers.map((userId) => (
                    <button
                      key={userId}
                      onClick={() => handleAddSuggestedUser(userId)}
                      className="px-3 py-2 bg-background border border-border rounded-lg hover:border-primary transition-all text-sm font-medium"
                    >
                      <Plus className="w-3 h-3 inline mr-1" />
                      {userId}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* User List */}
            {userIds.length > 0 && (
              <div className="space-y-2 mb-6">
                <p className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Group Members
                </p>
                <div className="flex flex-wrap gap-2">
                  {userIds.map((userId, index) => (
                    <motion.div
                      key={userId}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Badge variant="secondary" className="text-sm px-4 py-2 gap-2">
                        <span className="font-medium">{userId}</span>
                        <button
                          onClick={() => handleRemoveUser(userId)}
                          className="hover:text-destructive transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </Badge>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            <Button
              size="lg"
              onClick={handleFindMovies}
              disabled={isLoading || userIds.length === 0}
              className="w-full gap-2 bg-gradient-to-r from-primary to-purple-500 hover:from-primary/90 hover:to-purple-500/90"
            >
              {isLoading ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <Sparkles className="w-5 h-5" />
                  </motion.div>
                  Analyzing Group Preferences...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Find Perfect Movies
                </>
              )}
            </Button>
          </div>
        </motion.div>

        {/* Group Stats */}
        {movies.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-3xl mx-auto mb-12"
          >
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-card border border-border rounded-xl p-6 text-center">
                <TrendingUp className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                <p className="text-2xl font-bold">{movies.length}</p>
                <p className="text-sm text-muted-foreground">Matches Found</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 text-center">
                <Award className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
                <p className="text-2xl font-bold">
                  {Math.round(Object.values(compatibilityScores).reduce((a, b) => a + b, 0) / Object.values(compatibilityScores).length * 100)}%
                </p>
                <p className="text-sm text-muted-foreground">Avg Match</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 text-center">
                <Users className="w-8 h-8 mx-auto mb-2 text-purple-500" />
                <p className="text-2xl font-bold">{userIds.length}</p>
                <p className="text-sm text-muted-foreground">Group Size</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Results */}
        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {[...Array(10)].map((_, i) => (
              <MovieCardSkeleton key={i} />
            ))}
          </div>
        ) : movies.length > 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="mb-8 text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                <h2 className="text-3xl font-bold">Recommended for Your Group</h2>
                <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white border-0">
                  <Sparkles className="w-3 h-3 mr-1" />
                  ML Powered
                </Badge>
              </div>
              <p className="text-muted-foreground text-lg">
                Movies ranked by group compatibility using collaborative filtering
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {movies.map((movie, index) => (
                <motion.div
                  key={movie.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="relative"
                >
                  <MovieCard movie={movie} />
                  {compatibilityScores[movie.id] && (
                    <Badge
                      className={`absolute -top-2 -right-2 z-10 ${getCompatibilityColor(compatibilityScores[movie.id])} text-white border-0 shadow-lg`}
                    >
                      <Star className="w-3 h-3 mr-1 fill-white" />
                      {Math.round(compatibilityScores[movie.id] * 100)}%
                    </Badge>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        ) : null}
      </div>
    </div>
  );
};

export default WatchParty;
