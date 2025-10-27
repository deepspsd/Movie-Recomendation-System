import { motion } from 'framer-motion';
import { Brain, Users, Zap, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface AdaptiveWeightsVisualizerProps {
  contentWeight: number;
  collaborativeWeight: number;
  isLearning?: boolean;
}

export function AdaptiveWeightsVisualizer({
  contentWeight,
  collaborativeWeight,
  isLearning = false,
}: AdaptiveWeightsVisualizerProps) {
  const contentPercentage = Math.round(contentWeight * 100);
  const collaborativePercentage = Math.round(collaborativeWeight * 100);

  return (
    <Card className="border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Your AI Personalization
          </CardTitle>
          {isLearning && (
            <Badge variant="secondary" className="gap-1">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <Brain className="w-3 h-3" />
              </motion.div>
              Learning...
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="p-4 rounded-lg bg-muted/50 border">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
            <p className="text-sm text-muted-foreground">
              Our AI adapts to your preferences in real-time using reinforcement learning. These
              weights show how we personalize recommendations just for you.
            </p>
          </div>
        </div>

        {/* Content-Based Weight */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Content-Based Filtering</h4>
                <p className="text-xs text-muted-foreground">
                  Finds movies similar to what you love
                </p>
              </div>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Badge variant="outline" className="text-sm font-bold">
                    {contentPercentage}%
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Content-based filtering weight</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          <div className="relative">
            <Progress value={contentPercentage} className="h-3" />
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 2 }}
              style={{ width: `${contentPercentage}%` }}
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="flex-1 flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-purple-500" />
              <span>Analyzes genres, directors, cast, plot</span>
            </div>
          </div>
        </div>

        {/* Collaborative Weight */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500">
                <Users className="w-4 h-4 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Collaborative Filtering</h4>
                <p className="text-xs text-muted-foreground">
                  Learns from users with similar tastes
                </p>
              </div>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Badge variant="outline" className="text-sm font-bold">
                    {collaborativePercentage}%
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Collaborative filtering weight</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          <div className="relative">
            <Progress value={collaborativePercentage} className="h-3" />
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-full"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}
              style={{ width: `${collaborativePercentage}%` }}
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="flex-1 flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span>Uses SVD, ALS matrix factorization</span>
            </div>
          </div>
        </div>

        {/* Balance Indicator */}
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Recommendation Balance</span>
            <Badge variant="secondary">
              {contentPercentage > collaborativePercentage
                ? 'Content-Focused'
                : collaborativePercentage > contentPercentage
                ? 'Collaborative-Focused'
                : 'Balanced'}
            </Badge>
          </div>
          <div className="mt-3 p-3 rounded-lg bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 border">
            <p className="text-xs text-muted-foreground">
              {contentPercentage > 60
                ? '🎯 Your recommendations focus more on content similarity - perfect for discovering movies like your favorites!'
                : collaborativePercentage > 60
                ? '👥 Your recommendations leverage community wisdom - great for finding hidden gems!'
                : '⚖️ Your recommendations use a balanced approach - best of both worlds!'}
            </p>
          </div>
        </div>

        {/* Learning Info */}
        <div className="p-4 rounded-lg bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/20">
          <div className="flex items-start gap-3">
            <Zap className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="font-semibold text-sm">Adaptive Learning Active</h4>
              <p className="text-xs text-muted-foreground">
                Every rating you give helps our AI fine-tune these weights to match your unique
                taste. The system uses reinforcement learning to continuously improve your
                recommendations.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
