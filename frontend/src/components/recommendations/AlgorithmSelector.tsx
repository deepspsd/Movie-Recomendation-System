import { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Sparkles, Network, BarChart3, Layers } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { AlgorithmType, AlgorithmOption } from '@/types';

const algorithmOptions: AlgorithmOption[] = [
  {
    value: 'hybrid',
    label: 'Hybrid AI',
    description: 'Best of all worlds - combines content, collaborative, and ALS for maximum accuracy',
    icon: 'Sparkles',
    color: 'from-purple-500 to-pink-500',
  },
  {
    value: 'als',
    label: 'ALS Matrix',
    description: 'Advanced matrix factorization with dropout regularization for precise predictions',
    icon: 'Layers',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    value: 'svd',
    label: 'SVD Decomposition',
    description: 'Singular value decomposition for pattern discovery in user preferences',
    icon: 'BarChart3',
    color: 'from-green-500 to-emerald-500',
  },
  {
    value: 'collaborative',
    label: 'Collaborative',
    description: 'Find movies loved by users with similar tastes to yours',
    icon: 'Network',
    color: 'from-orange-500 to-red-500',
  },
  {
    value: 'content',
    label: 'Content-Based',
    description: 'Discover movies similar to ones you already love based on metadata',
    icon: 'Brain',
    color: 'from-indigo-500 to-purple-500',
  },
];

const iconMap = {
  Sparkles,
  Layers,
  BarChart3,
  Network,
  Brain,
};

interface AlgorithmSelectorProps {
  selected: AlgorithmType;
  onChange: (algorithm: AlgorithmType) => void;
  className?: string;
}

export function AlgorithmSelector({ selected, onChange, className }: AlgorithmSelectorProps) {
  const [hoveredAlgorithm, setHoveredAlgorithm] = useState<AlgorithmType | null>(null);

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Recommendation Algorithm</h3>
          <p className="text-sm text-muted-foreground">
            Choose how we find your perfect movies
          </p>
        </div>
        <Badge variant="secondary" className="text-xs">
          AI-Powered
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        {algorithmOptions.map((option) => {
          const Icon = iconMap[option.icon as keyof typeof iconMap];
          const isSelected = selected === option.value;
          const isHovered = hoveredAlgorithm === option.value;

          return (
            <motion.div
              key={option.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onHoverStart={() => setHoveredAlgorithm(option.value)}
              onHoverEnd={() => setHoveredAlgorithm(null)}
            >
              <Card
                className={cn(
                  'cursor-pointer transition-all duration-300 border-2',
                  isSelected
                    ? 'border-primary shadow-lg shadow-primary/20'
                    : 'border-transparent hover:border-primary/50',
                  'relative overflow-hidden'
                )}
                onClick={() => onChange(option.value)}
              >
                {/* Gradient background on hover/select */}
                <div
                  className={cn(
                    'absolute inset-0 bg-gradient-to-br opacity-0 transition-opacity duration-300',
                    option.color,
                    (isSelected || isHovered) && 'opacity-10'
                  )}
                />

                <CardContent className="p-4 relative z-10">
                  <div className="flex flex-col items-center text-center space-y-2">
                    {/* Icon */}
                    <div
                      className={cn(
                        'p-3 rounded-full bg-gradient-to-br transition-all duration-300',
                        option.color,
                        isSelected ? 'shadow-lg' : 'opacity-70'
                      )}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>

                    {/* Label */}
                    <div>
                      <h4 className="font-semibold text-sm">{option.label}</h4>
                      {isSelected && (
                        <Badge variant="default" className="mt-1 text-xs">
                          Active
                        </Badge>
                      )}
                    </div>

                    {/* Description - show on hover or select */}
                    <motion.p
                      initial={{ opacity: 0, height: 0 }}
                      animate={{
                        opacity: isSelected || isHovered ? 1 : 0,
                        height: isSelected || isHovered ? 'auto' : 0,
                      }}
                      className="text-xs text-muted-foreground overflow-hidden"
                    >
                      {option.description}
                    </motion.p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Selected algorithm info */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        key={selected}
        className="p-4 rounded-lg bg-muted/50 border"
      >
        <div className="flex items-start gap-3">
          <div
            className={cn(
              'p-2 rounded-lg bg-gradient-to-br',
              algorithmOptions.find((o) => o.value === selected)?.color
            )}
          >
            {(() => {
              const Icon =
                iconMap[
                  algorithmOptions.find((o) => o.value === selected)?.icon as keyof typeof iconMap
                ];
              return <Icon className="w-4 h-4 text-white" />;
            })()}
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-sm mb-1">
              {algorithmOptions.find((o) => o.value === selected)?.label}
            </h4>
            <p className="text-xs text-muted-foreground">
              {algorithmOptions.find((o) => o.value === selected)?.description}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
