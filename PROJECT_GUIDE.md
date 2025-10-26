# 🎬 Movie Recommendation System - Mini Project Guide

## 🎯 Goal
Build a movie recommendation system with 2-3 algorithms and one unique feature.

---

## 🚀 Core Features

### 1. **Recommendation Algorithms** (Pick 2-3)
- **Collaborative Filtering**: Recommend based on similar users
- **Content-Based**: Recommend based on movie features (genre, cast)
- **Hybrid**: Combine both approaches

### 2. **Pick ONE Unique Feature**
- **Mood-Based**: "I'm feeling adventurous" → Action movies
- **Watch Party Matcher**: Find movies for groups
- **Explanation Engine**: Show why movie was recommended

---

## 📁 Simple Project Structure

```
movie-recommendation-system/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   └── routes/
│   │       ├── auth.py          # Login/Register
│   │       ├── movies.py        # Movie endpoints
│   │       └── recommendations.py
│   ├── models/
│   │   ├── user.py
│   │   ├── movie.py
│   │   └── rating.py
│   ├── ml/
│   │   ├── collaborative.py     # CF algorithm
│   │   ├── content_based.py     # Content filtering
│   │   └── hybrid.py            # Combine both
│   └── database/
│       └── db.py                # Database setup
├── data/
│   ├── movielens/               # Downloaded dataset
│   └── processed/               # Cleaned data
├── notebooks/
│   └── model_training.ipynb     # Jupyter notebook
├── .env.example
├── requirements.txt
└── PROJECT_GUIDE.md
```

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **ML**: scikit-learn, pandas, numpy
- **Cache**: Redis (optional)

---

## 📄 Project Guide

## 📊 Dataset

**Use MovieLens 25M** (FREE)
- 25 million ratings
- 62,000 movies
- Download: https://grouplens.org/datasets/movielens/

**Enhance with TMDB API** (FREE)
- Movie posters, plots, cast
- Sign up: https://www.themoviedb.org/settings/api

---

## 🎓 Implementation Steps (4-6 Weeks)

### **Week 1: Setup**
1. Install dependencies: `pip install -r requirements.txt`
2. Download MovieLens dataset
3. Setup database (MySQL)
4. Create basic FastAPI app

### **Week 2: Basic API**
1. User authentication (JWT)
2. CRUD endpoints for movies
3. Rating endpoints
4. Database models

### **Week 3: Collaborative Filtering**
1. Load MovieLens data
2. Implement user-based CF
3. Or implement item-based CF
4. Create recommendation endpoint

### **Week 4: Content-Based Filtering**
1. Extract movie features (genres, cast)
2. Use TF-IDF for plot similarity
3. Implement content-based algorithm
4. Test recommendations

### **Week 5: Hybrid + Unique Feature**
1. Combine CF + Content-Based
2. Implement your unique feature (mood/watch party/explanation)
3. Add caching for speed

### **Week 6: Testing & Polish**
1. Write tests
2. Add API documentation
3. Optimize performance
4. Deploy (optional)

---

## 🎯 Key Algorithms

### 1. **Collaborative Filtering**
```python
# User-based: Find similar users, recommend their favorites
# Item-based: Find similar movies, recommend those
# Matrix Factorization: Use SVD from scikit-learn
```

### 2. **Content-Based**
```python
# Use movie features:
- Genres (action, comedy, drama)
- Cast and director
- Plot (TF-IDF similarity)
```

### 3. **Hybrid**
```python
# Combine scores:
final_score = 0.6 * collaborative_score + 0.4 * content_score
```

---

## 📝 API Endpoints (Minimum)

```
POST   /auth/register          - Register user
POST   /auth/login             - Login user
GET    /movies                 - Get all movies
GET    /movies/{id}            - Get movie details
POST   /ratings                - Rate a movie
GET    /recommendations        - Get personalized recommendations
GET    /recommendations/mood   - Mood-based (if you pick this feature)
POST   /recommendations/group  - Watch party (if you pick this feature)
```

---

## 💾 Database Schema (Simple)

```sql
Users:
- id, username, email, password_hash

Movies:
- id, title, genres, year, tmdb_id

Ratings:
- id, user_id, movie_id, rating (1-5), timestamp
```

---

## 📈 Success Metrics

- **Recommendation Quality**: RMSE < 1.0 (good for mini project)
- **API Speed**: Response time < 500ms
- **Coverage**: Recommend at least 50% of movies
- **Code Quality**: Clean, organized, documented

---

## 💡 Quick Tips

1. **Start Simple**: Get collaborative filtering working first
2. **Use SQLite**: Easier than PostgreSQL for mini project
3. **Cache Results**: Store recommendations in memory/Redis
4. **Test Often**: Make sure recommendations make sense
5. **Document**: Add comments and API docs

---

## 🚀 What Makes It 10/10

✅ **2-3 algorithms** (Collaborative + Content-Based)
✅ **One unique feature** (Mood/Watch Party/Explanation)
✅ **Working API** with documentation
✅ **Clean code** structure
✅ **Basic tests**
✅ **Good README** explaining your approach

---

## 📚 Quick Resources

- **MovieLens**: https://grouplens.org/datasets/movielens/
- **TMDB API**: https://www.themoviedb.org/documentation/api
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Surprise Library**: https://surpriselib.com/ (for CF)

---

**That's it! Keep it simple, focus on core features, and make one thing unique. Good luck! 🎯**
