import { motion } from 'framer-motion';
import { Info, Star, Users, Film, TrendingUp, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface ExplanationFactor {
  type: 'genre' | 'director' | 'cast' | 'similar_users' | 'content_similarity' | 'popularity';
  value: string;
  weight: number;
}

interface RecommendationExplanationProps {
  movieTitle: string;
  primaryReason: string;
  factors: ExplanationFactor[];
  confidence: number;
  algorithmBreakdown?: {
    content_score?: number;
    collaborative_score?: number;
    als_score?: number;
    svd_score?: number;
  };
}

const factorIcons = {
  genre: Film,
  director: Star,
  cast: Users,
  similar_users: Users,
  content_similarity: Sparkles,
  popularity: TrendingUp,
};

const factorLabels = {
  genre: 'Genre Match',
  director: 'Director',
  cast: 'Cast',
  similar_users: 'Similar Users',
  content_similarity: 'Content Similarity',
  popularity: 'Popularity',
};

const factorColors = {
  genre: 'from-purple-500 to-pink-500',
  director: 'from-yellow-500 to-orange-500',
  cast: 'from-blue-500 to-cyan-500',
  similar_users: 'from-green-500 to-emerald-500',
  content_similarity: 'from-indigo-500 to-purple-500',
  popularity: 'from-red-500 to-pink-500',
};

export function RecommendationExplanation({
  movieTitle,
  primaryReason,
  factors,
  confidence,
  algorithmBreakdown,
}: RecommendationExplanationProps) {
  return (
    <Card className="border-2">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Info className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">Why we recommended this</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">{movieTitle}</p>
            </div>
          </div>
          <Badge variant="secondary" className="text-xs">
            {Math.round(confidence * 100)}% Match
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Primary Reason */}
        <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
          <p className="text-sm font-medium text-primary">{primaryReason}</p>
        </div>

        {/* Confidence Score */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Confidence Score</span>
            <span className="text-muted-foreground">{Math.round(confidence * 100)}%</span>
          </div>
          <Progress value={confidence * 100} className="h-2" />
        </div>

        {/* Factors */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold">Key Factors</h4>
          <div className="space-y-2">
            {factors.map((factor, index) => {
              const Icon = factorIcons[factor.type];
              const label = factorLabels[factor.type];
              const color = factorColors[factor.type];

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                >
                  <div className={cn('p-2 rounded-lg bg-gradient-to-br', color)}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium truncate">{label}</span>
                      <Badge variant="outline" className="text-xs shrink-0">
                        {Math.round(factor.weight * 100)}%
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{factor.value}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Algorithm Breakdown */}
        {algorithmBreakdown && (
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Algorithm Breakdown</h4>
            <div className="grid grid-cols-2 gap-3">
              {algorithmBreakdown.content_score !== undefined && (
                <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
                  <div className="text-xs text-muted-foreground mb-1">Content-Based</div>
                  <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                    {Math.round(algorithmBreakdown.content_score * 100)}%
                  </div>
                </div>
              )}
              {algorithmBreakdown.collaborative_score !== undefined && (
                <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <div className="text-xs text-muted-foreground mb-1">Collaborative</div>
                  <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {Math.round(algorithmBreakdown.collaborative_score * 100)}%
                  </div>
                </div>
              )}
              {algorithmBreakdown.als_score !== undefined && (
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <div className="text-xs text-muted-foreground mb-1">ALS Matrix</div>
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                    {Math.round(algorithmBreakdown.als_score * 100)}%
                  </div>
                </div>
              )}
              {algorithmBreakdown.svd_score !== undefined && (
                <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                  <div className="text-xs text-muted-foreground mb-1">SVD</div>
                  <div className="text-lg font-bold text-orange-600 dark:text-orange-400">
                    {Math.round(algorithmBreakdown.svd_score * 100)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
