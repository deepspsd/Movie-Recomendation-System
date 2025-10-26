import { motion } from "framer-motion";
import { Star, Play } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MovieCardProps {
  title: string;
  rating: number;
  year: string;
  imageUrl: string;
  genre?: string;
}

const MovieCard = ({ title, rating, year, imageUrl, genre }: MovieCardProps) => {
  return (
    <motion.div
      whileHover={{ 
        scale: 1.05,
        y: -10,
      }}
      transition={{ 
        duration: 0.3,
        ease: "easeOut"
      }}
      className="group relative aspect-[2/3] rounded-xl overflow-hidden cursor-pointer"
    >
      <img
        src={imageUrl}
        alt={title}
        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
      />
      
      <motion.div
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent p-4 flex flex-col justify-end"
      >
        <h3 className="text-foreground font-bold text-lg mb-2">{title}</h3>
        <div className="flex items-center gap-3 text-sm text-muted-foreground mb-3">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 fill-accent text-accent" />
            <span className="text-foreground">{rating}</span>
          </div>
          <span>{year}</span>
          {genre && <span className="text-primary">{genre}</span>}
        </div>
        <Button size="sm" className="w-full gap-2">
          <Play className="w-4 h-4" />
          View Details
        </Button>
      </motion.div>

      <div className="absolute inset-0 ring-2 ring-transparent group-hover:ring-primary/50 rounded-xl pointer-events-none transition-all duration-300" />
      <div className="absolute inset-0 shadow-lg group-hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] rounded-xl pointer-events-none transition-all duration-300" />
    </motion.div>
  );
};

export default MovieCard;
