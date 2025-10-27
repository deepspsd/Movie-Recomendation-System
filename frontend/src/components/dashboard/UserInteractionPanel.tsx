import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Settings, Upload, Heart, Star, Film, Edit2, Save, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useAuthStore } from '@/store/authStore';

interface UserInteractionPanelProps {
  contentWeight: number;
  collaborativeWeight: number;
  onWeightChange: (content: number, collaborative: number) => void;
  favoriteGenres: string[];
  onGenresUpdate: (genres: string[]) => void;
}

const AVAILABLE_GENRES = [
  'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
  'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music',
  'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'
];

export function UserInteractionPanel({
  contentWeight,
  collaborativeWeight,
  onWeightChange,
  favoriteGenres,
  onGenresUpdate,
}: UserInteractionPanelProps) {
  const { user } = useAuthStore();
  const [isEditingPreferences, setIsEditingPreferences] = useState(false);
  const [tempGenres, setTempGenres] = useState<string[]>(favoriteGenres);
  const [weightValue, setWeightValue] = useState([contentWeight * 100]);

  const handleWeightChange = (value: number[]) => {
    setWeightValue(value);
    const content = value[0] / 100;
    const collaborative = 1 - content;
    onWeightChange(content, collaborative);
  };

  const handleGenreToggle = (genre: string) => {
    if (tempGenres.includes(genre)) {
      setTempGenres(tempGenres.filter(g => g !== genre));
    } else {
      setTempGenres([...tempGenres, genre]);
    }
  };

  const handleSavePreferences = () => {
    onGenresUpdate(tempGenres);
    setIsEditingPreferences(false);
  };

  const handleCancelEdit = () => {
    setTempGenres(favoriteGenres);
    setIsEditingPreferences(false);
  };

  return (
    <Card className="border-2 overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
              <User className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg">Profile & Preferences</CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">Customize your experience</p>
            </div>
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="icon" className="shrink-0 h-8 w-8">
                <Settings className="w-4 h-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Edit Your Preferences</DialogTitle>
                <DialogDescription>
                  Customize your movie recommendations by setting your preferences
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 py-4">
                {/* Genre Preferences */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Favorite Genres</Label>
                  <p className="text-sm text-muted-foreground">
                    Select genres you enjoy watching
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_GENRES.map((genre) => (
                      <Badge
                        key={genre}
                        variant={tempGenres.includes(genre) ? 'default' : 'outline'}
                        className="cursor-pointer hover:scale-105 transition-transform"
                        onClick={() => handleGenreToggle(genre)}
                      >
                        {genre}
                      </Badge>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Algorithm Weight */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Algorithm Balance</Label>
                  <p className="text-sm text-muted-foreground">
                    Adjust the balance between content-based and collaborative filtering
                  </p>
                  <div className="space-y-4 pt-2">
                    <Slider
                      value={weightValue}
                      onValueChange={handleWeightChange}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-purple-500" />
                        <span>Content-Based: {weightValue[0]}%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                        <span>Collaborative: {100 - weightValue[0]}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-4">
                  <Button variant="outline" onClick={handleCancelEdit}>
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                  <Button onClick={handleSavePreferences}>
                    <Save className="w-4 h-4 mr-2" />
                    Save Preferences
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>

      <CardContent className="space-y-5 pt-4">
        {/* User Info */}
        <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50 border border-border/50">
          <Avatar className="w-14 h-14 border-2 border-primary/50">
            <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username}`} />
            <AvatarFallback className="text-base font-bold bg-gradient-to-br from-purple-500 to-pink-500 text-white">
              {user?.username?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-bold truncate">{user?.username}</h3>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>

        {/* Favorite Genres */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-semibold flex items-center gap-2">
              <Heart className="w-4 h-4 text-red-500" />
              Favorite Genres
            </Label>
            {!isEditingPreferences && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsEditingPreferences(true)}
                className="h-7 w-7"
              >
                <Edit2 className="w-3 h-3" />
              </Button>
            )}
          </div>

          {isEditingPreferences ? (
            <div className="space-y-3 p-3 rounded-lg bg-muted/30 border border-border/50">
              <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
                {AVAILABLE_GENRES.map((genre) => (
                  <Badge
                    key={genre}
                    variant={tempGenres.includes(genre) ? 'default' : 'outline'}
                    className="cursor-pointer hover:scale-105 transition-transform text-xs"
                    onClick={() => handleGenreToggle(genre)}
                  >
                    {genre}
                  </Badge>
                ))}
              </div>
              <div className="flex gap-2 pt-2 border-t">
                <Button size="sm" onClick={handleSavePreferences} className="flex-1">
                  <Save className="w-3 h-3 mr-1" />
                  Save
                </Button>
                <Button size="sm" variant="outline" onClick={handleCancelEdit} className="flex-1">
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {favoriteGenres.length > 0 ? (
                favoriteGenres.slice(0, 6).map((genre) => (
                  <Badge key={genre} variant="secondary" className="text-xs">
                    {genre}
                  </Badge>
                ))
              ) : (
                <p className="text-xs text-muted-foreground italic">No genres selected</p>
              )}
              {favoriteGenres.length > 6 && (
                <Badge variant="outline" className="text-xs">
                  +{favoriteGenres.length - 6} more
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Algorithm Weight Control */}
        <div className="space-y-3">
          <Label className="text-sm font-semibold flex items-center gap-2">
            <Film className="w-4 h-4 text-purple-500" />
            Recommendation Balance
          </Label>
          <div className="space-y-3 p-4 rounded-lg bg-gradient-to-br from-purple-500/5 to-blue-500/5 border border-border/50">
            <Slider
              value={weightValue}
              onValueChange={handleWeightChange}
              max={100}
              step={5}
              className="w-full"
            />
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-center">
                <div className="flex items-center justify-center gap-1.5 mb-1">
                  <Film className="w-3.5 h-3.5 text-purple-500" />
                  <span className="text-[10px] font-medium text-purple-500 uppercase tracking-wide">Content</span>
                </div>
                <div className="text-xl font-bold">{weightValue[0]}%</div>
              </div>
              <div className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-center">
                <div className="flex items-center justify-center gap-1.5 mb-1">
                  <Star className="w-3.5 h-3.5 text-blue-500" />
                  <span className="text-[10px] font-medium text-blue-500 uppercase tracking-wide">Collaborative</span>
                </div>
                <div className="text-xl font-bold">{100 - weightValue[0]}%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" size="sm" className="gap-1.5 h-9">
            <Upload className="w-3.5 h-3.5" />
            <span className="text-xs">Import</span>
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5 h-9">
            <Heart className="w-3.5 h-3.5" />
            <span className="text-xs">Favorites</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
