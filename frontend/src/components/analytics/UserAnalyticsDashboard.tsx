import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Star, Film, Target, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { UserAnalytics } from '@/types';

interface UserAnalyticsDashboardProps {
  analytics: UserAnalytics;
}

const COLORS = ['#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export function UserAnalyticsDashboard({ analytics }: UserAnalyticsDashboardProps) {
  const {
    total_movies_watched,
    total_ratings,
    average_rating,
    favorite_genres,
    rating_distribution,
    recommendation_performance,
    viewing_trends,
  } = analytics;

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border-2 border-purple-500/20 bg-gradient-to-br from-purple-500/10 to-transparent">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Movies Watched</p>
                  <h3 className="text-3xl font-bold mt-1">{total_movies_watched}</h3>
                </div>
                <div className="p-3 rounded-full bg-purple-500/20">
                  <Film className="w-6 h-6 text-purple-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-2 border-blue-500/20 bg-gradient-to-br from-blue-500/10 to-transparent">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Ratings</p>
                  <h3 className="text-3xl font-bold mt-1">{total_ratings}</h3>
                </div>
                <div className="p-3 rounded-full bg-blue-500/20">
                  <Star className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="border-2 border-green-500/20 bg-gradient-to-br from-green-500/10 to-transparent">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Rating</p>
                  <h3 className="text-3xl font-bold mt-1">{average_rating.toFixed(1)}</h3>
                </div>
                <div className="p-3 rounded-full bg-green-500/20">
                  <TrendingUp className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-2 border-orange-500/20 bg-gradient-to-br from-orange-500/10 to-transparent">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Accuracy</p>
                  <h3 className="text-3xl font-bold mt-1">
                    {Math.round(recommendation_performance.precision_at_10 * 100)}%
                  </h3>
                </div>
                <div className="p-3 rounded-full bg-orange-500/20">
                  <Target className="w-6 h-6 text-orange-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Genre Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Favorite Genres
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={favorite_genres}
                  dataKey="count"
                  nameKey="genre"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.genre} (${entry.percentage}%)`}
                >
                  {favorite_genres.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Rating Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5" />
              Rating Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={rating_distribution}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="rating" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    border: '1px solid hsl(var(--border))',
                  }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recommendation Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            AI Recommendation Performance
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Precision@10</span>
                <Badge variant="secondary">
                  {Math.round(recommendation_performance.precision_at_10 * 100)}%
                </Badge>
              </div>
              <Progress value={recommendation_performance.precision_at_10 * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">
                How many recommended movies you actually liked
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Recall@10</span>
                <Badge variant="secondary">
                  {Math.round(recommendation_performance.recall_at_10 * 100)}%
                </Badge>
              </div>
              <Progress value={recommendation_performance.recall_at_10 * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">
                How many of your favorites we found
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">F1 Score</span>
                <Badge variant="secondary">
                  {Math.round(recommendation_performance.f1_score * 100)}%
                </Badge>
              </div>
              <Progress value={recommendation_performance.f1_score * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">Overall recommendation quality</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">NDCG</span>
                <Badge variant="secondary">
                  {Math.round(recommendation_performance.ndcg * 100)}%
                </Badge>
              </div>
              <Progress value={recommendation_performance.ndcg * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">Ranking quality score</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Diversity</span>
                <Badge variant="secondary">
                  {Math.round(recommendation_performance.diversity * 100)}%
                </Badge>
              </div>
              <Progress value={recommendation_performance.diversity * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">Variety in recommendations</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Novelty</span>
                <Badge variant="secondary">
                  {Math.round(recommendation_performance.novelty * 100)}%
                </Badge>
              </div>
              <Progress value={recommendation_performance.novelty * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">Discovery of hidden gems</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Viewing Trends */}
      {viewing_trends && viewing_trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Viewing Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={viewing_trends}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    border: '1px solid hsl(var(--border))',
                  }}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="count"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  name="Movies Watched"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="average_rating"
                  stroke="#ec4899"
                  strokeWidth={2}
                  name="Avg Rating"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
