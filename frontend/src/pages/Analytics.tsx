import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Zap, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Navbar from '@/components/Navbar';
import { UserAnalyticsDashboard } from '@/components/analytics/UserAnalyticsDashboard';
import { AdaptiveWeightsVisualizer } from '@/components/preferences/AdaptiveWeightsVisualizer';
import { userAPI } from '@/services/api';
import type { UserAnalytics, UserPreferences } from '@/types';
import toast from 'react-hot-toast';

const Analytics = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [adaptiveWeights, setAdaptiveWeights] = useState({ content: 0.5, collaborative: 0.5 });

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setIsLoading(true);

      // Fetch analytics and preferences
      const [analyticsData, preferencesData, weightsData] = await Promise.all([
        userAPI.getAnalytics().catch(() => getMockAnalytics()),
        userAPI.getPreferences().catch(() => getMockPreferences()),
        userAPI.getAdaptiveWeights().catch(() => ({ content: 0.5, collaborative: 0.5 })),
      ]);

      setAnalytics(analyticsData);
      setPreferences(preferencesData);
      setAdaptiveWeights(weightsData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics data');
      // Set mock data as fallback
      setAnalytics(getMockAnalytics());
      setPreferences(getMockPreferences());
    } finally {
      setIsLoading(false);
    }
  };

  // Mock data generator for development/fallback
  const getMockAnalytics = (): UserAnalytics => ({
    total_movies_watched: 127,
    total_ratings: 89,
    average_rating: 4.2,
    favorite_genres: [
      { genre: 'Action', count: 35, percentage: 28 },
      { genre: 'Sci-Fi', count: 28, percentage: 22 },
      { genre: 'Drama', count: 22, percentage: 17 },
      { genre: 'Comedy', count: 18, percentage: 14 },
      { genre: 'Thriller', count: 15, percentage: 12 },
      { genre: 'Horror', count: 9, percentage: 7 },
    ],
    rating_distribution: [
      { rating: 1, count: 2 },
      { rating: 2, count: 5 },
      { rating: 3, count: 15 },
      { rating: 4, count: 38 },
      { rating: 5, count: 29 },
    ],
    recommendation_performance: {
      precision_at_10: 0.78,
      recall_at_10: 0.65,
      f1_score: 0.71,
      ndcg: 0.82,
      diversity: 0.68,
      novelty: 0.55,
    },
    viewing_trends: [
      { date: '2025-01', count: 12, average_rating: 4.1 },
      { date: '2025-02', count: 18, average_rating: 4.3 },
      { date: '2025-03', count: 22, average_rating: 4.2 },
      { date: '2025-04', count: 25, average_rating: 4.4 },
      { date: '2025-05', count: 28, average_rating: 4.3 },
      { date: '2025-06', count: 22, average_rating: 4.1 },
    ],
  });

  const getMockPreferences = (): UserPreferences => ({
    user_id: 'current_user',
    adaptive_weights: {
      content: 0.45,
      collaborative: 0.55,
    },
    favorite_genres: ['Action', 'Sci-Fi', 'Drama'],
    favorite_directors: ['Christopher Nolan', 'Denis Villeneuve', 'Quentin Tarantino'],
    favorite_actors: ['Tom Hardy', 'Ryan Gosling', 'Margot Robbie'],
    average_rating: 4.2,
    total_ratings: 89,
    recommendation_accuracy: 0.78,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-24">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"
              />
              <p className="text-muted-foreground">Loading your analytics...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 py-24">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Button
            variant="ghost"
            className="mb-4"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <div className="flex items-center gap-4 mb-2">
            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold">Your Analytics</h1>
              <p className="text-muted-foreground text-lg">
                Insights into your movie preferences and AI recommendations
              </p>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="overview" className="gap-2">
              <BarChart3 className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="ai" className="gap-2">
              <Zap className="w-4 h-4" />
              AI Personalization
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {analytics && <UserAnalyticsDashboard analytics={analytics} />}
          </TabsContent>

          <TabsContent value="ai" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              {/* Adaptive Weights */}
              <AdaptiveWeightsVisualizer
                contentWeight={adaptiveWeights.content}
                collaborativeWeight={adaptiveWeights.collaborative}
                isLearning={true}
              />

              {/* Preferences Card */}
              {preferences && (
                <div className="space-y-6">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="p-6 rounded-xl border-2 bg-card"
                  >
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-500" />
                      Your Preferences
                    </h3>

                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-muted-foreground">
                          Favorite Genres
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {preferences.favorite_genres.map((genre) => (
                            <span
                              key={genre}
                              className="px-3 py-1 rounded-full bg-purple-500/10 text-purple-500 text-sm font-medium border border-purple-500/20"
                            >
                              {genre}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-muted-foreground">
                          Favorite Directors
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {preferences.favorite_directors.map((director) => (
                            <span
                              key={director}
                              className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-sm font-medium border border-blue-500/20"
                            >
                              {director}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-muted-foreground">
                          Favorite Actors
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {preferences.favorite_actors.map((actor) => (
                            <span
                              key={actor}
                              className="px-3 py-1 rounded-full bg-green-500/10 text-green-500 text-sm font-medium border border-green-500/20"
                            >
                              {actor}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="p-6 rounded-xl border-2 bg-gradient-to-br from-orange-500/10 to-red-500/10 border-orange-500/20"
                  >
                    <h3 className="text-xl font-bold mb-4">Recommendation Accuracy</h3>
                    <div className="text-5xl font-bold text-orange-500 mb-2">
                      {Math.round(preferences.recommendation_accuracy * 100)}%
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Based on {preferences.total_ratings} ratings you've provided
                    </p>
                  </motion.div>
                </div>
              )}
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Analytics;
