# Frontend Setup & Development Guide

## 🎉 Project Status: COMPLETE

All pages, components, and features have been implemented according to the FRONTEND_PROMPT.md specifications.

---

## 📦 Installation

```bash
cd frontend
npm install
```

---

## 🚀 Running the Application

### Development Mode
```bash
npm run dev
```
The app will be available at `http://localhost:5173`

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 🔧 Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api
VITE_TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── Carousel.tsx
│   │   ├── MovieCard.tsx
│   │   ├── MoodCard.tsx
│   │   ├── Navbar.tsx
│   │   ├── SearchBar.tsx
│   │   ├── LoadingSkeleton.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/              # Page components
│   │   ├── Landing.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Movies.tsx
│   │   ├── MovieDetails.tsx
│   │   ├── Search.tsx
│   │   ├── MoodRecommendations.tsx
│   │   ├── WatchParty.tsx
│   │   ├── Profile.tsx
│   │   ├── Watchlist.tsx
│   │   └── NotFound.tsx
│   ├── services/           # API services
│   │   └── api.ts
│   ├── store/              # State management
│   │   └── authStore.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── utils/              # Helper functions
│   │   └── helpers.ts
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── .env                    # Environment variables
├── .env.example            # Environment template
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

---

## 🎨 Features Implemented

### ✅ Pages
- [x] Landing Page - Hero section with features
- [x] Login Page - JWT authentication
- [x] Register Page - User registration with validation
- [x] Dashboard - Personalized recommendations, trending, mood selector
- [x] Movies Browse - Grid view with filters and sorting
- [x] Movie Details - Full movie info, cast, similar movies, rating
- [x] Search - Real-time search with autocomplete
- [x] Mood Recommendations - Mood-based movie discovery
- [x] Watch Party - Group movie recommendations
- [x] Profile - User stats and rated movies
- [x] Watchlist - Saved movies

### ✅ Components
- [x] Navbar - Auth state, search, user menu
- [x] MovieCard - Hover effects, rating display
- [x] Carousel - Horizontal scrolling with arrows
- [x] MoodCard - Animated mood selection
- [x] SearchBar - Expandable search with debounce
- [x] LoadingSkeleton - Loading states for all pages
- [x] ProtectedRoute - Route protection

### ✅ Features
- [x] JWT Authentication with token refresh
- [x] Protected routes
- [x] Real-time API integration
- [x] Toast notifications
- [x] Loading states
- [x] Error handling
- [x] Responsive design
- [x] Dark theme
- [x] Smooth animations (Framer Motion)
- [x] Form validation

---

## 🔌 API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api`

### API Endpoints Used:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `GET /movies` - Get all movies
- `GET /movies/{id}` - Get movie details
- `GET /movies/trending` - Get trending movies
- `GET /movies/popular` - Get popular movies
- `GET /movies/search` - Search movies
- `GET /recommendations` - Get personalized recommendations
- `GET /recommendations/mood` - Get mood-based recommendations
- `GET /recommendations/similar/{id}` - Get similar movies
- `POST /recommendations/group` - Get watch party recommendations
- `POST /ratings` - Rate a movie
- `GET /ratings/user` - Get user ratings
- `GET /watchlist` - Get user watchlist
- `POST /watchlist` - Add to watchlist
- `DELETE /watchlist/{id}` - Remove from watchlist

---

## 🎨 Design System

### Colors
- **Primary**: Purple/Blue (#6366f1)
- **Accent**: Orange (#f59e0b)
- **Background**: Dark (#0f172a)
- **Card**: Dark (#1e293b)

### Typography
- **Font**: Inter (system default)
- **Headings**: Bold, large sizes
- **Body**: Regular weight

### Animations
- **Page transitions**: Fade in, slide up
- **Hover effects**: Scale, glow
- **Loading**: Skeleton screens
- **Scroll**: Intersection observer

---

## 🧪 Testing

```bash
# Run tests (when implemented)
npm run test

# Run linting
npm run lint
```

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

The build output will be in the `dist/` directory.

### Deploy to Vercel/Netlify
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

---

## 📝 Notes

### Backend Connection
Make sure the FastAPI backend is running at `http://localhost:8000` before starting the frontend.

### TMDB Images
Movie images are fetched from TMDB's CDN. The backend should provide the poster/backdrop paths.

### Authentication
- JWT tokens are stored in localStorage
- Automatic token refresh on 401 errors
- Protected routes redirect to login

---

## 🎯 Next Steps

1. **Start Backend**: Make sure FastAPI backend is running
2. **Run Frontend**: `npm run dev`
3. **Test Features**: Register, login, browse movies
4. **Customize**: Adjust colors, fonts, layouts as needed

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173
```

### API Connection Issues
- Check backend is running on port 8000
- Verify VITE_API_URL in .env
- Check CORS settings in backend

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Framer Motion Documentation](https://www.framer.com/motion)
- [Zustand Documentation](https://zustand-demo.pmnd.rs)

---

**Built with ❤️ using React, TypeScript, TailwindCSS, and shadcn/ui**
