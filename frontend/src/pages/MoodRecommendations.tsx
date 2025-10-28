import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Sparkles, Filter, SlidersHorizontal, Zap } from 'lucide-react';
import Navbar from '@/components/Navbar';
import MoodCard from '@/components/MoodCard';
import MovieCard from '@/components/MovieCard';
import { MovieCardSkeleton } from '@/components/LoadingSkeleton';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { recommendationsAPI } from '@/services/api';
import type { Movie, MoodType, MoodOption } from '@/types';
import toast from 'react-hot-toast';

const MOOD_OPTIONS: MoodOption[] = [
  {
    value: 'happy',
    label: 'Happy',
    emoji: '😊',
    description: 'Feel-good movies that will lift your spirits',
    genres: ['comedy', 'family', 'animation'],
  },
  {
    value: 'sad',
    label: 'Emotional',
    emoji: '😢',
    description: 'Touching dramas that will move you',
    genres: ['drama', 'romance'],
  },
  {
    value: 'adventurous',
    label: 'Sci-Fi',
    emoji: '🎬',
    description: 'Action-packed sci-fi thrillers and adventures',
    genres: ['action', 'adventure', 'thriller'],
  },
  {
    value: 'romantic',
    label: 'Feel-Good',
    emoji: '❤️',
    description: 'Love stories and romantic comedies',
    genres: ['romance', 'comedy'],
  },
  {
    value: 'scared',
    label: 'Thrilling',
    emoji: '😱',
    description: 'Horror and suspense that will keep you on edge',
    genres: ['horror', 'thriller', 'mystery'],
  },
  {
    value: 'thoughtful',
    label: 'Thoughtful',
    emoji: '🤔',
    description: 'Thought-provoking films that make you think',
    genres: ['drama', 'documentary', 'sci-fi'],
  },
];

const MoodRecommendations = () => {
  const [selectedMood, setSelectedMood] = useState<MoodType | null>(null);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState<'rating' | 'popularity' | 'recent'>('rating');
  const [filteredMovies, setFilteredMovies] = useState<Movie[]>([]);

  const handleMoodSelect = async (mood: MoodType) => {
    setSelectedMood(mood);
    setIsLoading(true);

    try {
      const response = await recommendationsAPI.getByMood(mood);
      setMovies(response.movies);
      toast.success(`Found ${response.movies.length} movies matching your mood!`);
    } catch (error) {
      console.error('Error fetching mood recommendations:', error);
      toast.error('Failed to load recommendations');
      setMovies([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Sort and filter movies
  useEffect(() => {
    if (movies.length === 0) {
      setFilteredMovies([]);
      return;
    }

    let sorted = [...movies];
    
    switch (sortBy) {
      case 'rating':
        sorted.sort((a, b) => (b.vote_average || 0) - (a.vote_average || 0));
        break;
      case 'popularity':
        sorted.sort((a, b) => (b.popularity || 0) - (a.popularity || 0));
        break;
      case 'recent':
        sorted.sort((a, b) => {
          const dateA = new Date(a.release_date || 0).getTime();
          const dateB = new Date(b.release_date || 0).getTime();
          return dateB - dateA;
        });
        break;
    }
    
    setFilteredMovies(sorted);
  }, [movies, sortBy]);

  const handleBack = () => {
    setSelectedMood(null);
    setMovies([]);
  };

  const selectedMoodOption = MOOD_OPTIONS.find((m) => m.value === selectedMood);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 pt-24 pb-16">
        <AnimatePresence mode="wait">
          {!selectedMood ? (
            <motion.div
              key="mood-selector"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {/* Header */}
              <div className="text-center mb-16">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="inline-block mb-6"
                >
                  <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 text-lg px-6 py-2">
                    <Zap className="w-5 h-5 mr-2" />
                    AI-Powered Mood Matching
                  </Badge>
                </motion.div>
                <motion.h1
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent"
                >
                  How Are You Feeling?
                </motion.h1>
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-xl text-muted-foreground max-w-2xl mx-auto"
                >
                  Select your mood and we'll use machine learning to recommend the perfect movies
                </motion.p>
              </div>

              {/* Mood Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                {MOOD_OPTIONS.map((mood, index) => (
                  <motion.div
                    key={mood.value}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <MoodCard
                      mood={mood.value}
                      emoji={mood.emoji}
                      label={mood.label}
                      description={mood.description}
                      onClick={() => handleMoodSelect(mood.value)}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="mood-results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {/* Back Button & Header */}
              <div className="mb-12">
                <Button
                  variant="ghost"
                  onClick={handleBack}
                  className="mb-6 gap-2 hover:gap-3 transition-all"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Change Mood
                </Button>

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-6">
                  <div className="flex items-center gap-4">
                    <motion.span 
                      className="text-6xl"
                      animate={{ rotate: [0, 10, -10, 0] }}
                      transition={{ duration: 0.5 }}
                    >
                      {selectedMoodOption?.emoji}
                    </motion.span>
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h1 className="text-4xl md:text-5xl font-bold">
                          {selectedMoodOption?.label} Movies
                        </h1>
                        <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0">
                          <Sparkles className="w-3 h-3 mr-1" />
                          ML Curated
                        </Badge>
                      </div>
                      <p className="text-xl text-muted-foreground mt-2">
                        {selectedMoodOption?.description}
                      </p>
                    </div>
                  </div>

                  {/* Sort Filter */}
                  <div className="flex items-center gap-3">
                    <SlidersHorizontal className="w-5 h-5 text-muted-foreground" />
                    <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Sort by" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="rating">Highest Rated</SelectItem>
                        <SelectItem value="popularity">Most Popular</SelectItem>
                        <SelectItem value="recent">Most Recent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Results Count */}
                {filteredMovies.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-muted-foreground"
                  >
                    Found <span className="font-semibold text-foreground">{filteredMovies.length}</span> movies matching your mood
                  </motion.div>
                )}
              </div>

              {/* Movies Grid */}
              {isLoading ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                  {[...Array(20)].map((_, i) => (
                    <MovieCardSkeleton key={i} />
                  ))}
                </div>
              ) : filteredMovies.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                  {filteredMovies.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: Math.min(index * 0.03, 0.5) }}
                      whileHover={{ y: -5 }}
                    >
                      <MovieCard movie={movie} />
                    </motion.div>
                  ))}
                </div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-20 bg-card/30 rounded-2xl border border-border"
                >
                  <Sparkles className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-xl text-muted-foreground mb-4">
                    No movies found for this mood. Try another one!
                  </p>
                  <Button onClick={handleBack} variant="outline">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Choose Different Mood
                  </Button>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MoodRecommendations;
