import { Film, User, LogOut, Heart, UserCircle, Menu, X, Bell, Moon, Sun, TrendingUp, Sparkles, Users, BarChart3 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import SearchBar from "./SearchBar";
import { useAuthStore } from "@/store/authStore";
import { useState, useEffect } from "react";

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [notifications] = useState(3); // Mock notification count

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark');
  };

  const navLinks = [
    { to: '/dashboard', label: 'Home', icon: Sparkles },
    { to: '/movies', label: 'Movies', icon: Film },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/mood', label: 'Mood Match', icon: Heart },
    { to: '/watch-party', label: 'Watch Party', icon: Users },
  ];

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-xl border-b border-border/50 shadow-lg"
    >
      <div className="container mx-auto px-4 h-20 flex items-center justify-between">
        <Link to={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/60 rounded-lg flex items-center justify-center">
            <Film className="w-6 h-6 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            CineMatch
          </span>
        </Link>

        {isAuthenticated && (
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className="flex items-center gap-2 text-foreground/80 hover:text-foreground transition-colors group"
                >
                  <Icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>
        )}

        <div className="flex items-center gap-2 md:gap-4">
          {isAuthenticated && (
            <>
              <div className="hidden md:block">
                <SearchBar />
              </div>
              
              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="w-5 h-5" />
                {notifications > 0 && (
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs">
                    {notifications}
                  </Badge>
                )}
              </Button>

              {/* Theme Toggle */}
              <Button variant="ghost" size="icon" onClick={toggleTheme}>
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </Button>
            </>
          )}
          
          {isAuthenticated ? (
            <>
              {/* Mobile Menu */}
              <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
                <SheetTrigger asChild className="md:hidden">
                  <Button variant="ghost" size="icon">
                    <Menu className="w-6 h-6" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-80">
                  <div className="flex flex-col gap-6 mt-8">
                    <div className="flex items-center gap-3 pb-4 border-b">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-primary text-primary-foreground text-lg">
                          {user?.username?.charAt(0).toUpperCase() || 'U'}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">{user?.username}</p>
                        <p className="text-sm text-muted-foreground">{user?.email}</p>
                      </div>
                    </div>

                    <div className="md:hidden mb-4">
                      <SearchBar />
                    </div>

                    <nav className="flex flex-col gap-2">
                      {navLinks.map((link) => {
                        const Icon = link.icon;
                        return (
                          <Link
                            key={link.to}
                            to={link.to}
                            onClick={() => setMobileMenuOpen(false)}
                            className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors"
                          >
                            <Icon className="w-5 h-5" />
                            <span className="font-medium">{link.label}</span>
                          </Link>
                        );
                      })}
                    </nav>

                    <div className="border-t pt-4 mt-auto">
                      <Link
                        to="/profile"
                        onClick={() => setMobileMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors mb-2"
                      >
                        <UserCircle className="w-5 h-5" />
                        <span className="font-medium">Profile</span>
                      </Link>
                      <Link
                        to="/watchlist"
                        onClick={() => setMobileMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-accent transition-colors mb-2"
                      >
                        <Heart className="w-5 h-5" />
                        <span className="font-medium">Watchlist</span>
                      </Link>
                      <Button
                        variant="ghost"
                        onClick={handleLogout}
                        className="w-full justify-start gap-3 text-destructive hover:text-destructive hover:bg-destructive/10"
                      >
                        <LogOut className="w-5 h-5" />
                        <span className="font-medium">Logout</span>
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>

              {/* Desktop User Menu */}
              <div className="hidden md:block">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {user?.username?.charAt(0).toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span className="font-semibold">{user?.username}</span>
                    <span className="text-xs text-muted-foreground">{user?.email}</span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/profile')}>
                  <UserCircle className="w-4 h-4 mr-2" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/watchlist')}>
                  <Heart className="w-4 h-4 mr-2" />
                  Watchlist
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
              </div>
            </>
          ) : (
            <Link to="/login">
              <Button variant="default" size="sm" className="gap-2">
                <User className="w-4 h-4" />
                Sign In
              </Button>
            </Link>
          )}
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
