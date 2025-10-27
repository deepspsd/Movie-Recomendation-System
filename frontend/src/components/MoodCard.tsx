import { motion } from 'framer-motion';
import type { MoodType } from '@/types';

interface MoodCardProps {
  mood: MoodType;
  emoji: string;
  label: string;
  description: string;
  onClick: () => void;
}

const MoodCard = ({ mood, emoji, label, description, onClick }: MoodCardProps) => {
  return (
    <motion.button
      whileHover={{
        scale: 1.05,
        y: -8,
        transition: { duration: 0.3, ease: 'easeOut' },
      }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="group relative bg-card border border-border rounded-2xl p-8 text-center hover:border-primary/50 transition-all duration-300 hover:shadow-[0_0_40px_rgba(99,102,241,0.4)] overflow-hidden"
    >
      {/* Background Gradient */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
      />

      {/* Content */}
      <div className="relative z-10">
        <motion.div
          className="text-6xl mb-4"
          whileHover={{
            scale: 1.2,
            rotate: [0, -10, 10, -10, 0],
            transition: { duration: 0.5 },
          }}
        >
          {emoji}
        </motion.div>
        <h3 className="text-2xl font-bold mb-2 transition-colors duration-300 group-hover:text-primary">
          {label}
        </h3>
        <p className="text-sm text-muted-foreground transition-colors duration-300 group-hover:text-foreground/80">
          {description}
        </p>
      </div>

      {/* Glow Effect */}
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary/20 to-accent/20 blur-xl" />
      </div>
    </motion.button>
  );
};

export default MoodCard;
