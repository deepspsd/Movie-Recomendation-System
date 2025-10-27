import { motion, useScroll, useTransform } from "framer-motion";
import { Link } from "react-router-dom";
import { Film, Sparkles, Users, ArrowRight, Star, TrendingUp, Heart, Zap, Shield, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Navbar from "@/components/Navbar";
import heroImage from "@/assets/hero-image.jpg";

const Landing = () => {
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);

  const stats = [
    { value: "10M+", label: "Movies Analyzed" },
    { value: "500K+", label: "Active Users" },
    { value: "98%", label: "Match Accuracy" },
    { value: "4.9/5", label: "User Rating" },
  ];

  const features = [
    {
      icon: Sparkles,
      title: "AI-Powered Recommendations",
      description: "Advanced machine learning algorithms analyze your preferences to suggest movies you'll love",
      color: "from-purple-500 to-pink-500",
    },
    {
      icon: Film,
      title: "Mood-Based Discovery",
      description: "Select your current mood and get instant recommendations that match your emotional state",
      color: "from-blue-500 to-cyan-500",
    },
    {
      icon: Users,
      title: "Watch Party Matcher",
      description: "Find the perfect movie for your group with our intelligent compatibility algorithm",
      color: "from-orange-500 to-red-500",
    },
    {
      icon: Zap,
      title: "Real-Time Updates",
      description: "Get instant access to trending movies and latest releases as they become available",
      color: "from-yellow-500 to-orange-500",
    },
    {
      icon: Shield,
      title: "Privacy First",
      description: "Your data is encrypted and secure. We never share your viewing preferences",
      color: "from-green-500 to-emerald-500",
    },
    {
      icon: Heart,
      title: "Personalized Watchlist",
      description: "Save movies you want to watch and get notified when they're available",
      color: "from-pink-500 to-rose-500",
    },
  ];

  const howItWorks = [
    {
      step: "01",
      title: "Create Your Profile",
      description: "Sign up in seconds and tell us about your movie preferences",
    },
    {
      step: "02",
      title: "Rate Some Movies",
      description: "Rate a few movies you've watched to help our AI understand your taste",
    },
    {
      step: "03",
      title: "Get Recommendations",
      description: "Receive personalized movie suggestions tailored just for you",
    },
    {
      step: "04",
      title: "Discover & Enjoy",
      description: "Explore new movies, create watchlists, and enjoy your perfect matches",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-24">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${heroImage})`,
            filter: "brightness(0.25) blur(1px)",
          }}
        />
        
        <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/40 to-background" />
        <div className="absolute inset-0 bg-gradient-to-r from-background/60 via-transparent to-background/60" />

        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Badge className="mb-8 text-sm px-6 py-2.5 bg-primary/20 hover:bg-primary/30 border-primary/40 backdrop-blur-sm shadow-lg">
              <Star className="w-4 h-4 mr-2 fill-primary text-primary" />
              Trusted by 500K+ Movie Lovers
            </Badge>
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black mb-8 leading-tight">
              <span className="bg-gradient-to-r from-white via-white to-gray-300 bg-clip-text text-transparent drop-shadow-2xl">
                Your Personal
              </span>
              <br />
              <span className="relative inline-block">
                <span className="bg-gradient-to-r from-primary via-purple-400 to-accent bg-clip-text text-transparent">
                  Movie Curator
                </span>
                <motion.div
                  className="absolute -bottom-3 left-0 right-0 h-1.5 bg-gradient-to-r from-primary via-purple-500 to-accent rounded-full"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                />
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed font-medium">
              Stop endless scrolling. Get <span className="text-primary font-bold">AI-powered recommendations</span> that actually match your taste. Discover movies based on your mood, preferences, and even find perfect picks for group watch parties.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <Link to="/register">
                <Button size="lg" className="text-lg gap-2 px-10 h-14 shadow-2xl shadow-primary/30 hover:shadow-primary/50 transition-all font-semibold">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="text-lg px-10 h-14 border-2 hover:bg-white/10 font-semibold backdrop-blur-sm">
                  Sign In
                </Button>
              </Link>
            </div>
            <p className="text-sm text-gray-400 flex items-center justify-center gap-2 flex-wrap">
              <span>✓ No credit card required</span>
              <span>•</span>
              <span>✓ Free forever</span>
              <span>•</span>
              <span>✓ 2 minutes setup</span>
            </p>
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

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
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
                  <div className="bg-card border border-border rounded-2xl p-6 h-full transition-all duration-300 group-hover:border-primary/50 group-hover:shadow-[0_0_30px_rgba(99,102,241,0.3)] relative overflow-hidden">
                    <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${feature.color} opacity-10 rounded-full blur-2xl group-hover:opacity-20 transition-opacity duration-300`} />
                    <motion.div 
                      whileHover={{ 
                        scale: 1.15,
                        rotate: [0, -10, 10, 0],
                        transition: { duration: 0.5 }
                      }}
                      className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4 relative z-10`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </motion.div>
                    <h3 className="text-xl font-bold mb-2 transition-colors duration-300 group-hover:text-primary relative z-10">{feature.title}</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed transition-colors duration-300 group-hover:text-foreground/80 relative z-10">
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

      {/* How It Works Section */}
      <section className="py-24 bg-card/30">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="mb-4 text-sm px-4 py-2 bg-primary/10 hover:bg-primary/20 border-primary/20">
              <Clock className="w-4 h-4 mr-2" />
              Get Started in Minutes
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Four simple steps to discover your perfect movie matches
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {/* Connection Line */}
            <div className="hidden lg:block absolute top-24 left-0 right-0 h-0.5 bg-gradient-to-r from-primary/20 via-primary to-primary/20" />
            
            {howItWorks.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                viewport={{ once: true }}
                className="relative"
              >
                <div className="bg-card border border-border rounded-2xl p-6 h-full hover:border-primary/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(99,102,241,0.2)]">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center mb-4 text-2xl font-bold text-white mx-auto relative z-10">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-bold mb-2 text-center">{item.title}</h3>
                  <p className="text-muted-foreground text-sm text-center leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10" />
        <motion.div
          className="absolute inset-0"
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: 'reverse',
          }}
          style={{
            backgroundImage: 'radial-gradient(circle at center, rgba(99,102,241,0.1) 0%, transparent 50%)',
            backgroundSize: '100% 100%',
          }}
        />
        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto text-center"
          >
            <Badge className="mb-6 text-sm px-4 py-2 bg-primary/10 hover:bg-primary/20 border-primary/20">
              <TrendingUp className="w-4 h-4 mr-2" />
              Join 500K+ Active Users
            </Badge>
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              Start Your Movie Journey Today
            </h2>
            <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
              Create your free account and get instant access to personalized movie recommendations powered by AI
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button size="lg" className="text-lg gap-2 px-12 h-14 shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="text-lg px-12 h-14">
                  Sign In
                </Button>
              </Link>
            </div>
            <p className="text-sm text-muted-foreground mt-6">
              No credit card required • Free forever • Cancel anytime
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
