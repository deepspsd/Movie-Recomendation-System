import { motion } from "framer-motion";
import { Play, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";
import MovieCard from "@/components/MovieCard";
import heroImage from "@/assets/hero-image.jpg";

const Dashboard = () => {
  // Mock data - will be replaced with real API data
  const featuredMovie = {
    title: "Inception",
    plot: "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
    rating: 8.8,
    year: "2010",
  };

  const recommendedMovies = [
    { title: "The Dark Knight", rating: 9.0, year: "2008", imageUrl: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=400", genre: "Action" },
    { title: "Interstellar", rating: 8.6, year: "2014", imageUrl: "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400", genre: "Sci-Fi" },
    { title: "Pulp Fiction", rating: 8.9, year: "1994", imageUrl: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400", genre: "Crime" },
    { title: "The Matrix", rating: 8.7, year: "1999", imageUrl: "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400", genre: "Sci-Fi" },
    { title: "Forrest Gump", rating: 8.8, year: "1994", imageUrl: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400", genre: "Drama" },
  ];

  const trendingMovies = [
    { title: "Oppenheimer", rating: 8.5, year: "2023", imageUrl: "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400", genre: "Biography" },
    { title: "Dune", rating: 8.0, year: "2021", imageUrl: "https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=400", genre: "Sci-Fi" },
    { title: "Everything Everywhere", rating: 7.8, year: "2022", imageUrl: "https://images.unsplash.com/photo-1574267432644-f74f8ec0c15e?w=400", genre: "Comedy" },
    { title: "Top Gun: Maverick", rating: 8.3, year: "2022", imageUrl: "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=400", genre: "Action" },
    { title: "Avatar 2", rating: 7.9, year: "2022", imageUrl: "https://images.unsplash.com/photo-1594908900066-3f47337549d8?w=400", genre: "Fantasy" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative h-[80vh] mt-16">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${heroImage})`,
            filter: "brightness(0.4)",
          }}
        />
        
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />

        <div className="relative z-10 h-full flex items-center">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="max-w-2xl"
            >
              <h1 className="text-5xl md:text-6xl font-bold mb-4">
                {featuredMovie.title}
              </h1>
              <div className="flex items-center gap-4 mb-6 text-lg">
                <span className="flex items-center gap-1 text-accent">
                  ★ {featuredMovie.rating}
                </span>
                <span className="text-muted-foreground">{featuredMovie.year}</span>
              </div>
              <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
                {featuredMovie.plot}
              </p>
              <div className="flex gap-4">
                <Button size="lg" className="gap-2">
                  <Play className="w-5 h-5" />
                  Play Trailer
                </Button>
                <Button size="lg" variant="outline" className="gap-2">
                  <Plus className="w-5 h-5" />
                  Add to Watchlist
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Recommended Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold mb-8">Recommended For You</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {recommendedMovies.map((movie, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <MovieCard {...movie} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Trending Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold mb-8">Trending Now</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {trendingMovies.map((movie, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <MovieCard {...movie} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Mood Selector Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold mb-4">Browse by Mood</h2>
            <p className="text-muted-foreground mb-8">
              Find movies that match how you're feeling
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {["Happy", "Adventurous", "Romantic", "Thrilling"].map((mood, index) => (
                <motion.button
                  key={mood}
                  whileHover={{ 
                    scale: 1.08,
                    y: -8,
                    transition: { duration: 0.3, ease: "easeOut" }
                  }}
                  whileTap={{ scale: 0.95 }}
                  className="group bg-card border border-border rounded-xl p-6 text-center hover:border-primary/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(99,102,241,0.3)] relative overflow-hidden"
                >
                  <motion.div 
                    className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  />
                  <motion.div 
                    className="text-4xl mb-3 relative z-10"
                    whileHover={{ 
                      scale: 1.2,
                      rotate: [0, -10, 10, 0],
                      transition: { duration: 0.5 }
                    }}
                  >
                    {index === 0 && "😊"}
                    {index === 1 && "🎬"}
                    {index === 2 && "❤️"}
                    {index === 3 && "😱"}
                  </motion.div>
                  <h3 className="font-semibold relative z-10 transition-colors duration-300 group-hover:text-primary">{mood}</h3>
                </motion.button>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
