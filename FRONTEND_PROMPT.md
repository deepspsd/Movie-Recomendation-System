# 🎬 Frontend Development Prompt for Movie Recommendation System

## Project Overview
Build a modern, visually stunning movie recommendation web application with smooth animations, intuitive UX, and professional design. The frontend should connect to a FastAPI backend and provide an immersive movie browsing experience.

---

## 🎯 Requirements

### Core Features to Implement:
1. **User Authentication**
   - Login/Register pages with smooth transitions
   - JWT token management
   - Protected routes

2. **Home/Dashboard Page**
   - Personalized movie recommendations
   - Trending movies section
   - Continue watching section
   - Genre-based carousels

3. **Movie Details Page**
   - Full movie information (poster, plot, cast, ratings)
   - Rate movie functionality
   - Similar movies section
   - Trailer player (YouTube embed)
   - "Add to Watchlist" button

4. **Search & Filter**
   - Real-time search with autocomplete
   - Filter by genre, year, rating
   - Advanced search options

5. **Mood-Based Recommendations** (Unique Feature)
   - Mood selector interface (happy, sad, adventurous, etc.)
   - Animated mood cards
   - Dynamic recommendations based on mood

6. **Watch Party Matcher** (Alternative Unique Feature)
   - Add multiple users to a group
   - Show group-compatible movie recommendations
   - Visual compatibility scores

7. **User Profile**
   - Viewing history
   - Rated movies
   - Favorite genres
   - Watchlist

---

## 🎨 Design Requirements

### Visual Style:
- **Theme**: Dark mode with Netflix/Disney+ inspired design
- **Color Scheme**: 
  - Primary: Deep purple/blue gradient (#6366f1 to #8b5cf6)
  - Secondary: Warm orange/red for accents (#f59e0b, #ef4444)
  - Background: Dark (#0f172a, #1e293b)
  - Text: White/gray (#f8fafc, #94a3b8)
- **Typography**: 
  - Headings: Inter or Poppins (bold, modern)
  - Body: Inter or System UI
- **Aesthetic**: Modern, cinematic, immersive

### UI Components Needed:
- **Movie Cards**: Hover effects with scale, glow, overlay with rating
- **Carousels**: Smooth horizontal scrolling with navigation arrows
- **Hero Section**: Large featured movie with gradient overlay
- **Loading States**: Skeleton screens and smooth loaders
- **Modals**: For movie details, ratings, filters
- **Toast Notifications**: Success/error messages
- **Animated Backgrounds**: Subtle particle effects or gradients

---

## 🛠️ Tech Stack

### Framework & Libraries:
```json
{
  "framework": "React 18+ with Vite",
  "styling": "TailwindCSS",
  "ui_components": "shadcn/ui",
  "animations": "Framer Motion",
  "icons": "Lucide React",
  "routing": "React Router v6",
  "state_management": "Zustand or React Context",
  "api_calls": "Axios or React Query",
  "forms": "React Hook Form + Zod validation",
  "carousel": "Swiper.js or Embla Carousel"
}
```

### Additional Libraries:
- **react-hot-toast**: Toast notifications
- **react-player**: Video player for trailers
- **react-intersection-observer**: Lazy loading
- **date-fns**: Date formatting
- **clsx**: Conditional classnames

---

## 📱 Pages & Routes

```
/                          → Landing page (if not logged in) or Dashboard
/login                     → Login page
/register                  → Register page
/dashboard                 → Main dashboard with recommendations
/movies                    → Browse all movies
/movies/:id                → Movie details page
/search                    → Search results page
/mood                      → Mood-based recommendations
/watch-party               → Watch party matcher
/profile                   → User profile
/watchlist                 → User's watchlist
```

---

## 🎬 Detailed Component Specifications

### 1. **Landing Page** (Not Logged In)
```
Components:
- Hero section with animated movie posters in background
- Tagline: "Discover Your Next Favorite Movie"
- CTA buttons: "Get Started" (Register) and "Sign In"
- Feature highlights (3 cards):
  * Personalized Recommendations
  * Mood-Based Discovery
  * Watch Party Matching
- Smooth scroll animations (fade in, slide up)
- Particle background effect (subtle)
```

### 2. **Login/Register Pages**
```
Design:
- Split screen layout
  * Left: Form (centered, card with glass morphism)
  * Right: Animated movie collage or gradient
- Form fields with floating labels
- Password strength indicator (register)
- Social login buttons (optional)
- Smooth transitions between login/register
- Loading state on submit button
- Error messages with animations
```

### 3. **Dashboard/Home Page**
```
Layout (Top to Bottom):
1. Header/Navbar:
   - Logo (left)
   - Search bar (center, expandable)
   - User avatar + notifications (right)
   - Sticky on scroll

2. Hero Section:
   - Large featured movie backdrop
   - Gradient overlay (bottom to top)
   - Movie title, plot snippet, rating
   - "Play Trailer" and "Add to Watchlist" buttons
   - Auto-rotate every 5 seconds

3. "Recommended For You" Section:
   - Horizontal scrolling carousel
   - 5-6 movie cards visible
   - Smooth scroll with arrows
   - Hover effect: scale + show rating overlay

4. "Trending Now" Section:
   - Similar carousel layout
   - Badge showing "Trending" on cards

5. "Browse by Mood" Section:
   - Grid of mood cards (4-6 moods)
   - Animated icons (happy, sad, adventurous, etc.)
   - Click to get mood-based recommendations

6. Genre Sections:
   - Multiple carousels for each genre
   - "Action Movies", "Comedy", "Drama", etc.
   - Lazy load as user scrolls

Animations:
- Fade in sections on scroll
- Stagger animation for movie cards
- Smooth carousel transitions
```

### 4. **Movie Card Component**
```
Design:
- Aspect ratio: 2:3 (poster style)
- Rounded corners (8px)
- Shadow on hover
- Overlay on hover showing:
  * Movie title
  * Rating (stars or number)
  * Genre tags
  * "View Details" button
- Smooth scale transform on hover (1.05x)
- Glow effect around card
- Loading skeleton while image loads
```

### 5. **Movie Details Page**
```
Layout:
1. Hero Section:
   - Full-width backdrop image (blurred)
   - Gradient overlay
   - Movie poster (left, elevated with shadow)
   - Movie info (right):
     * Title (large, bold)
     * Tagline (italic)
     * Rating (stars + number)
     * Year, Runtime, Genres (badges)
     * Plot summary
     * Cast (horizontal scroll with avatars)
     * Director, Writer
   - Action buttons:
     * "Play Trailer" (opens modal with video)
     * "Rate This Movie" (opens rating modal)
     * "Add to Watchlist"

2. Trailer Section:
   - Embedded YouTube player
   - Fullscreen option

3. "You Might Also Like" Section:
   - Carousel of similar movies
   - Same card design as homepage

4. Reviews Section (Optional):
   - User reviews with ratings
   - Add review functionality

Animations:
- Fade in on page load
- Parallax effect on backdrop
- Smooth modal transitions
```

### 6. **Search Page**
```
Layout:
- Search bar at top (large, prominent)
- Filters sidebar (left):
  * Genre checkboxes
  * Year range slider
  * Rating filter
  * Sort by (popularity, rating, year)
- Results grid (right):
  * Responsive grid (2-6 columns based on screen size)
  * Movie cards with same hover effects
  * Infinite scroll or pagination
- Empty state if no results (illustration + message)

Features:
- Real-time search (debounced)
- Autocomplete dropdown
- Filter chips showing active filters
- Clear all filters button
```

### 7. **Mood-Based Recommendations Page**
```
Layout:
1. Mood Selector:
   - Large cards for each mood
   - Animated icons/illustrations
   - Moods: Happy, Sad, Adventurous, Romantic, Scared, Thoughtful
   - Click animation (pulse effect)

2. Results Section:
   - Shows after mood selection
   - Smooth transition from selector to results
   - Grid of recommended movies
   - Explanation: "Because you're feeling [mood]..."

Animations:
- Mood cards float/bounce on hover
- Smooth page transition
- Stagger animation for results
```

### 8. **Watch Party Matcher Page**
```
Layout:
1. Add Users Section:
   - Search and add users to group
   - User chips with remove button
   - "Find Movies" button

2. Results Section:
   - Movies ranked by group compatibility
   - Compatibility score (visual bar or percentage)
   - Show which users will like it
   - User avatars with checkmarks

Design:
- Collaborative feel (multiple user colors)
- Visual indicators for group preferences
```

### 9. **User Profile Page**
```
Layout:
- Profile header:
  * Avatar (large, editable)
  * Username, email
  * Member since date
  * Stats (movies watched, ratings given)

- Tabs:
  * Watchlist (grid of movie cards)
  * Rated Movies (grid with user's rating shown)
  * Viewing History (timeline view)
  * Favorite Genres (pie chart or bars)

- Edit profile button
```

### 10. **Navbar Component**
```
Design:
- Sticky at top
- Transparent initially, solid on scroll
- Logo (left, clickable to home)
- Nav links: Home, Movies, Mood, Watch Party
- Search bar (center, expandable on click)
- User menu (right):
  * Avatar
  * Dropdown: Profile, Settings, Logout
- Mobile: Hamburger menu
```

---

## 🎨 Animation Specifications

### Page Transitions:
```javascript
// Use Framer Motion
- Fade in: opacity 0 → 1 (300ms)
- Slide up: translateY(20px) → 0 (400ms)
- Scale in: scale(0.95) → 1 (300ms)
```

### Hover Effects:
```javascript
// Movie cards
- Scale: 1 → 1.05 (200ms ease-out)
- Shadow: small → large (200ms)
- Overlay: opacity 0 → 1 (200ms)

// Buttons
- Scale: 1 → 1.02 (150ms)
- Brightness: 100% → 110% (150ms)
```

### Loading States:
```javascript
// Skeleton screens
- Pulse animation (gray → light gray)
- Shimmer effect (gradient sweep)

// Spinners
- Circular spinner with brand colors
- Smooth rotation
```

### Scroll Animations:
```javascript
// Use Intersection Observer
- Fade in when 20% visible
- Stagger children by 100ms
- Parallax on hero sections (slower scroll)
```

---

## 📐 Responsive Design

### Breakpoints:
```css
- Mobile: < 640px (1 column)
- Tablet: 640px - 1024px (2-3 columns)
- Desktop: > 1024px (4-6 columns)
```

### Mobile Optimizations:
- Bottom navigation bar
- Swipeable carousels
- Simplified filters (modal instead of sidebar)
- Larger touch targets (48px minimum)
- Optimized images (smaller sizes)

---

## 🎯 Key User Flows

### 1. **First Time User:**
```
Landing Page → Register → Onboarding (select favorite genres) 
→ Dashboard with initial recommendations
```

### 2. **Returning User:**
```
Login → Dashboard → Browse recommendations → Click movie 
→ View details → Rate movie → Get updated recommendations
```

### 3. **Mood-Based Discovery:**
```
Dashboard → "Browse by Mood" → Select mood → View recommendations 
→ Click movie → Watch trailer → Add to watchlist
```

### 4. **Watch Party:**
```
Dashboard → Watch Party → Add friends → Get recommendations 
→ View compatibility → Select movie
```

---

## 🚀 Performance Requirements

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Lighthouse Score**: > 90
- **Image Optimization**: WebP format, lazy loading
- **Code Splitting**: Route-based chunks
- **Caching**: API responses cached

---

## 🎨 Example Component Code Structure

```javascript
// Example: MovieCard.jsx
import { motion } from 'framer-motion';
import { Star, Play } from 'lucide-react';

const MovieCard = ({ movie }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="relative group cursor-pointer rounded-lg overflow-hidden shadow-lg"
    >
      <img 
        src={movie.poster} 
        alt={movie.title}
        className="w-full h-full object-cover"
      />
      <motion.div
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        className="absolute inset-0 bg-gradient-to-t from-black/90 to-transparent p-4 flex flex-col justify-end"
      >
        <h3 className="text-white font-bold text-lg">{movie.title}</h3>
        <div className="flex items-center gap-2 mt-2">
          <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
          <span className="text-white">{movie.rating}</span>
        </div>
        <button className="mt-3 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-full flex items-center gap-2">
          <Play className="w-4 h-4" />
          View Details
        </button>
      </motion.div>
    </motion.div>
  );
};
```

---

## 📦 Project Structure

```
frontend/
├── public/
│   └── assets/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── MovieCard.jsx
│   │   ├── Navbar.jsx
│   │   ├── Carousel.jsx
│   │   ├── MoodCard.jsx
│   │   └── ...
│   ├── pages/
│   │   ├── Landing.jsx
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── MovieDetails.jsx
│   │   ├── Search.jsx
│   │   ├── MoodRecommendations.jsx
│   │   ├── WatchParty.jsx
│   │   └── Profile.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useMovies.js
│   │   └── useRecommendations.js
│   ├── services/
│   │   └── api.js           # Axios instance
│   ├── store/
│   │   └── authStore.js     # Zustand store
│   ├── utils/
│   │   └── helpers.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── tailwind.config.js
├── vite.config.js
└── README.md
```

---

## 🔌 API Integration

### Base URL:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### Key Endpoints:
```javascript
// Auth
POST   /auth/register
POST   /auth/login

// Movies
GET    /movies
GET    /movies/{id}
GET    /search?q={query}

// Recommendations
GET    /recommendations
GET    /recommendations/mood?mood={mood}
POST   /recommendations/group

// Ratings
POST   /ratings
GET    /ratings/user
```

### Example API Call:
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getRecommendations = async () => {
  const response = await api.get('/recommendations');
  return response.data;
};
```

---

## ✨ Extra Polish

### Micro-interactions:
- Button ripple effect on click
- Smooth color transitions
- Bounce animation on success
- Shake animation on error

### Easter Eggs:
- Konami code for special theme
- Hidden movie recommendations
- Fun loading messages

### Accessibility:
- Keyboard navigation
- ARIA labels
- Focus indicators
- Screen reader support
- Alt text for images

---

## 🎬 Final Checklist

✅ All pages implemented with responsive design
✅ Smooth animations and transitions
✅ Loading states and error handling
✅ API integration complete
✅ Authentication flow working
✅ Movie cards with hover effects
✅ Carousels with smooth scrolling
✅ Search with autocomplete
✅ Mood-based recommendations UI
✅ Watch party matcher UI
✅ User profile with stats
✅ Toast notifications
✅ Dark mode theme
✅ Mobile responsive
✅ Performance optimized
✅ Accessibility features

---

## 🚀 Getting Started Command

```bash
# Create React app with Vite
npm create vite@latest frontend -- --template react

# Install dependencies
cd frontend
npm install react-router-dom axios zustand framer-motion lucide-react react-hot-toast react-hook-form zod swiper

# Install TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui
npx shadcn-ui@latest init

# Start dev server
npm run dev
```

---

**Build a stunning, modern movie recommendation app with smooth animations, intuitive UX, and professional design. Make it feel like Netflix meets your unique features! 🎬✨**
