import { useState } from 'react';
import { motion } from 'framer-motion';
import { Filter, SlidersHorizontal, Calendar, Star, Grid, List } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Separator } from '@/components/ui/separator';

export interface FilterOptions {
  genres: string[];
  yearRange: [number, number];
  minRating: number;
  sortBy: 'score' | 'rating' | 'year' | 'popularity';
  viewMode: 'grid' | 'list';
}

interface RecommendationFiltersProps {
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
  availableGenres: string[];
}

export function RecommendationFilters({
  filters,
  onFiltersChange,
  availableGenres,
}: RecommendationFiltersProps) {
  const [isOpen, setIsOpen] = useState(false);
  const currentYear = new Date().getFullYear();

  const handleGenreToggle = (genre: string) => {
    const newGenres = filters.genres.includes(genre)
      ? filters.genres.filter((g) => g !== genre)
      : [...filters.genres, genre];
    onFiltersChange({ ...filters, genres: newGenres });
  };

  const handleYearRangeChange = (value: number[]) => {
    onFiltersChange({ ...filters, yearRange: [value[0], value[1]] });
  };

  const handleMinRatingChange = (value: number[]) => {
    onFiltersChange({ ...filters, minRating: value[0] });
  };

  const handleSortChange = (value: string) => {
    onFiltersChange({ ...filters, sortBy: value as FilterOptions['sortBy'] });
  };

  const handleViewModeChange = (mode: 'grid' | 'list') => {
    onFiltersChange({ ...filters, viewMode: mode });
  };

  const handleClearFilters = () => {
    onFiltersChange({
      genres: [],
      yearRange: [1900, currentYear],
      minRating: 0,
      sortBy: 'score',
      viewMode: 'grid',
    });
  };

  const activeFiltersCount =
    filters.genres.length +
    (filters.minRating > 0 ? 1 : 0) +
    (filters.yearRange[0] !== 1900 || filters.yearRange[1] !== currentYear ? 1 : 0);

  return (
    <div className="flex items-center gap-3 flex-wrap">
      {/* Filter Popover */}
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="gap-2 relative">
            <Filter className="w-4 h-4" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge variant="destructive" className="ml-1 px-1.5 py-0 text-xs">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-96" align="start">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold">Filter Recommendations</h4>
              <Button variant="ghost" size="sm" onClick={handleClearFilters}>
                Clear All
              </Button>
            </div>

            <Separator />

            {/* Genre Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-semibold">Genres</Label>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {availableGenres.map((genre) => (
                  <Badge
                    key={genre}
                    variant={filters.genres.includes(genre) ? 'default' : 'outline'}
                    className="cursor-pointer hover:scale-105 transition-transform"
                    onClick={() => handleGenreToggle(genre)}
                  >
                    {genre}
                  </Badge>
                ))}
              </div>
            </div>

            <Separator />

            {/* Year Range */}
            <div className="space-y-3">
              <Label className="text-sm font-semibold">Release Year</Label>
              <div className="px-2">
                <Slider
                  value={filters.yearRange}
                  onValueChange={handleYearRangeChange}
                  min={1900}
                  max={currentYear}
                  step={1}
                  className="w-full"
                />
                <div className="flex items-center justify-between text-xs text-muted-foreground mt-2">
                  <span>{filters.yearRange[0]}</span>
                  <span>{filters.yearRange[1]}</span>
                </div>
              </div>
            </div>

            <Separator />

            {/* Minimum Rating */}
            <div className="space-y-3">
              <Label className="text-sm font-semibold">Minimum Rating</Label>
              <div className="px-2">
                <Slider
                  value={[filters.minRating]}
                  onValueChange={handleMinRatingChange}
                  min={0}
                  max={10}
                  step={0.5}
                  className="w-full"
                />
                <div className="flex items-center justify-between text-xs text-muted-foreground mt-2">
                  <span>Any</span>
                  <div className="flex items-center gap-1">
                    <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                    <span className="font-semibold">{filters.minRating.toFixed(1)}+</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      {/* Sort By */}
      <Select value={filters.sortBy} onValueChange={handleSortChange}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="score">Match Score</SelectItem>
          <SelectItem value="rating">Rating</SelectItem>
          <SelectItem value="year">Release Year</SelectItem>
          <SelectItem value="popularity">Popularity</SelectItem>
        </SelectContent>
      </Select>

      {/* View Mode Toggle */}
      <div className="flex items-center gap-1 border rounded-lg p-1">
        <Button
          variant={filters.viewMode === 'grid' ? 'secondary' : 'ghost'}
          size="sm"
          className="h-8 w-8 p-0"
          onClick={() => handleViewModeChange('grid')}
        >
          <Grid className="w-4 h-4" />
        </Button>
        <Button
          variant={filters.viewMode === 'list' ? 'secondary' : 'ghost'}
          size="sm"
          className="h-8 w-8 p-0"
          onClick={() => handleViewModeChange('list')}
        >
          <List className="w-4 h-4" />
        </Button>
      </div>

      {/* Active Filters Display */}
      {activeFiltersCount > 0 && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-2 flex-wrap"
        >
          {filters.genres.map((genre) => (
            <Badge key={genre} variant="secondary" className="gap-1">
              {genre}
              <button
                onClick={() => handleGenreToggle(genre)}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          ))}
          {filters.minRating > 0 && (
            <Badge variant="secondary" className="gap-1">
              Rating: {filters.minRating}+
              <button
                onClick={() => handleMinRatingChange([0])}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          )}
          {(filters.yearRange[0] !== 1900 || filters.yearRange[1] !== currentYear) && (
            <Badge variant="secondary" className="gap-1">
              {filters.yearRange[0]} - {filters.yearRange[1]}
              <button
                onClick={() => handleYearRangeChange([1900, currentYear])}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          )}
        </motion.div>
      )}
    </div>
  );
}
