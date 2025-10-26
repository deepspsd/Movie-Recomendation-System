import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Film, Sparkles, Users, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";
import heroImage from "@/assets/hero-image.jpg";

const Landing = () => {
  const features = [
    {
      icon: Sparkles,
      title: "Personalized Recommendations",
      description: "AI-powered suggestions tailored to your unique taste in movies",
    },
    {
      icon: Film,
      title: "Mood-Based Discovery",
      description: "Find the perfect movie that matches how you're feeling right now",
    },
    {
      icon: Users,
      title: "Watch Party Matching",
      description: "Discover movies that everyone in your group will love",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${heroImage})`,
            filter: "brightness(0.3) blur(2px)",
          }}
        />
        
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />

        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary via-primary/80 to-accent bg-clip-text text-transparent leading-tight">
              Discover Your Next
              <br />
              Favorite Movie
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Personalized recommendations powered by AI. Find movies that match your mood, taste, and the perfect picks for watch parties.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button size="lg" className="text-lg gap-2 px-8">
                  Get Started
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="text-lg px-8">
                  Sign In
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>

        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/4 right-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
          className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl"
        />
      </section>

      {/* Features Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Why Choose CineMatch?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Experience movie discovery like never before with our innovative features
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                  viewport={{ once: true }}
                  whileHover={{ 
                    y: -15,
                    transition: { duration: 0.3, ease: "easeOut" }
                  }}
                  className="relative group"
                >
                  <div className="bg-card border border-border rounded-2xl p-8 h-full transition-all duration-300 group-hover:border-primary/50 group-hover:shadow-[0_0_30px_rgba(99,102,241,0.3)]">
                    <motion.div 
                      whileHover={{ 
                        scale: 1.15,
                        rotate: [0, -10, 10, 0],
                        transition: { duration: 0.5 }
                      }}
                      className="w-14 h-14 bg-gradient-to-br from-primary to-primary/60 rounded-xl flex items-center justify-center mb-6"
                    >
                      <Icon className="w-7 h-7 text-primary-foreground" />
                    </motion.div>
                    <h3 className="text-2xl font-bold mb-3 transition-colors duration-300 group-hover:text-primary">{feature.title}</h3>
                    <p className="text-muted-foreground leading-relaxed transition-colors duration-300 group-hover:text-foreground/80">
                      {feature.description}
                    </p>
                  </div>
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/10" />
        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto text-center"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to Start Your Movie Journey?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of movie lovers who've found their perfect matches
            </p>
            <Link to="/register">
              <Button size="lg" className="text-lg gap-2 px-12">
                Create Free Account
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
