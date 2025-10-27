import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CarouselProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
}

const Carousel = ({ children, title, className = '' }: CarouselProps) => {
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = scrollRef.current.clientWidth * 0.8;
      const newScrollLeft =
        direction === 'left'
          ? scrollRef.current.scrollLeft - scrollAmount
          : scrollRef.current.scrollLeft + scrollAmount;

      scrollRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth',
      });
    }
  };

  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  return (
    <div className={`relative group ${className}`}>
      {title && <h2 className="text-3xl font-bold mb-6">{title}</h2>}
      
      <div className="relative">
        {/* Left Arrow */}
        {showLeftArrow && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute left-0 top-0 bottom-0 z-10 flex items-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          >
            <Button
              variant="secondary"
              size="icon"
              className="h-12 w-12 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background/90 shadow-lg ml-2"
              onClick={() => scroll('left')}
            >
              <ChevronLeft className="w-6 h-6" />
            </Button>
          </motion.div>
        )}

        {/* Scrollable Container */}
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="flex gap-4 overflow-x-auto scrollbar-hide scroll-smooth"
          style={{
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
          }}
        >
          {children}
        </div>

        {/* Right Arrow */}
        {showRightArrow && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute right-0 top-0 bottom-0 z-10 flex items-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          >
            <Button
              variant="secondary"
              size="icon"
              className="h-12 w-12 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background/90 shadow-lg mr-2"
              onClick={() => scroll('right')}
            >
              <ChevronRight className="w-6 h-6" />
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Carousel;
