# 🎬 Movie Recommendation System

A comprehensive, production-ready movie recommendation system built with FastAPI and React, featuring advanced ML algorithms and modern web technologies.

## ✨ Features

### 🧠 **Advanced ML Algorithms**
- **Collaborative Filtering**: User-based and item-based recommendations
- **Content-Based Filtering**: Recommendations based on movie features
- **Matrix Factorization**: SVD-based recommendations using scikit-learn
- **Hybrid Approach**: Combines multiple algorithms for optimal accuracy

### 🎯 **Unique Features**
- **Mood-Based Recommendations**: Get movies based on your current mood
- **Watch Party Matcher**: Find movies that work for groups with compatibility scores
- **Explanation Engine**: Understand why movies were recommended
- **Real-Time Search**: Live search with TMDB API integration

### 🔐 **Security & Performance**
- JWT-based authentication with refresh tokens
- Rate limiting and caching
- Comprehensive logging and monitoring
- Health checks and system metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │   MySQL DB      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TMDB API      │    │   Redis Cache   │    │   File Storage  │
│   (Movie Data)  │    │   (Optional)    │    │   (Logs/Models) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- TMDB API Key (free)

### 1. Clone Repository
```bash
git clone <repository-url>
cd movie-recommendation-system
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your database credentials and TMDB API key

# Initialize database
python seed_database.py

# Start backend
python main.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000/api)

# Start frontend
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh access token

### Movies
- `GET /api/movies/` - Get all movies (paginated)
- `GET /api/movies/{id}` - Get movie details
- `GET /api/movies/search` - Search movies
- `GET /api/movies/trending` - Get trending movies
- `GET /api/movies/popular` - Get popular movies

### Recommendations
- `GET /api/recommendations/` - Personalized recommendations
- `GET /api/recommendations/mood` - Mood-based recommendations
- `GET /api/recommendations/similar/{id}` - Similar movies
- `POST /api/recommendations/group` - Watch party recommendations

### User Features
- `POST /api/ratings` - Rate a movie
- `GET /api/ratings/user` - Get user ratings
- `GET /api/watchlist` - Get user watchlist
- `POST /api/watchlist` - Add to watchlist
- `DELETE /api/watchlist/{id}` - Remove from watchlist

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Performance

- **Response Time**: < 500ms for most endpoints
- **Recommendation Accuracy**: RMSE < 1.0
- **Concurrent Users**: 1000+ (with proper scaling)
- **Database**: Optimized queries with proper indexing

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=movie_recommendation_db

# JWT
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# TMDB API
TMDB_API_KEY=your_tmdb_api_key

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
VITE_TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Frontend Guide**: [frontend/SETUP.md](frontend/SETUP.md)
- **Project Guide**: [PROJECT_GUIDE.md](PROJECT_GUIDE.md)

## 🛠️ Development

### Code Quality
- **Backend**: Black, Flake8, MyPy
- **Frontend**: ESLint, Prettier
- **Testing**: Pytest, Jest
- **Type Safety**: Full TypeScript coverage

### Database Schema
```sql
Users: id, username, email, password_hash, created_at, favorite_genres
Movies: id, title, overview, poster_path, backdrop_path, release_date, vote_average, vote_count, popularity, genres, runtime, tagline
Ratings: id, user_id, movie_id, rating, timestamp
Watchlist: id, user_id, movie_id, added_at
Reviews: id, user_id, movie_id, review_text, timestamp
```

## 🚀 Deployment

### Production Checklist
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Set up SSL certificates
- [ ] Configure backup strategy

### Recommended Stack
- **Backend**: FastAPI + Uvicorn + Gunicorn
- **Database**: MySQL 8.0+ with proper indexing
- **Cache**: Redis (optional but recommended)
- **Frontend**: React + Vite + Nginx
- **Monitoring**: Prometheus + Grafana (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **TMDB API** for movie data
- **FastAPI** for the excellent web framework
- **React** and **shadcn/ui** for the frontend
- **scikit-learn** for ML algorithms

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Python, React, and modern web technologies**
