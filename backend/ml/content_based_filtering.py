"""
Advanced Content-Based Filtering Recommendation Model
Implements TF-IDF, Word2Vec, and metadata-based recommendations
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from typing import List, Dict, Tuple, Optional
import logging
import pickle
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentBasedFilteringModel:
    """
    Advanced Content-Based Filtering using:
    - TF-IDF Vectorization for text features
    - Cosine Similarity for content matching
    - Metadata features (genres, cast, director, keywords)
    - Advanced feature engineering
    """
    
    def __init__(self):
        self.movies_df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.cosine_sim_matrix = None
        self.movie_indices = None
        self.feature_matrix = None
        self.scaler = StandardScaler()
        
        # Advanced features
        self.genre_matrix = None
        self.metadata_matrix = None
        self.combined_features = None
        
    def prepare_data(self, movies_data: List[Dict]):
        """
        Prepare movie data for content-based filtering
        
        Args:
            movies_data: List of dictionaries with movie information
        """
        try:
            self.movies_df = pd.DataFrame(movies_data)
            
            # Create movie index mapping
            self.movie_indices = pd.Series(
                self.movies_df.index, 
                index=self.movies_df['id']
            ).to_dict()
            
            logger.info(f"Data prepared: {len(self.movies_df)} movies")
            return True
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            return False
    
    def build_tfidf_features(self, text_column: str = 'overview'):
        """
        Build TF-IDF features from movie text descriptions
        
        Args:
            text_column: Column name containing text to vectorize
        """
        try:
            # Handle missing values
            self.movies_df[text_column] = self.movies_df[text_column].fillna('')
            
            # Create TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=2,  # Minimum document frequency
                max_df=0.8,  # Maximum document frequency
                sublinear_tf=True  # Use sublinear tf scaling
            )
            
            # Fit and transform
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                self.movies_df[text_column]
            )
            
            logger.info(f"TF-IDF matrix shape: {self.tfidf_matrix.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error building TF-IDF features: {str(e)}")
            return False
    
    def build_genre_features(self):
        """
        Build genre-based features using one-hot encoding
        """
        try:
            # Extract all unique genres
            all_genres = set()
            for genres_str in self.movies_df['genres']:
                if pd.notna(genres_str) and genres_str:
                    try:
                        genres_list = json.loads(genres_str)
                        for genre in genres_list:
                            if isinstance(genre, dict) and 'name' in genre:
                                all_genres.add(genre['name'])
                            elif isinstance(genre, str):
                                all_genres.add(genre)
                    except:
                        # Handle pipe-separated genres
                        genres = str(genres_str).split('|')
                        all_genres.update(genres)
            
            all_genres = sorted(list(all_genres))
            
            # Create genre matrix
            genre_matrix = []
            for genres_str in self.movies_df['genres']:
                genre_vector = [0] * len(all_genres)
                if pd.notna(genres_str) and genres_str:
                    try:
                        genres_list = json.loads(genres_str)
                        for genre in genres_list:
                            genre_name = genre['name'] if isinstance(genre, dict) else genre
                            if genre_name in all_genres:
                                idx = all_genres.index(genre_name)
                                genre_vector[idx] = 1
                    except:
                        genres = str(genres_str).split('|')
                        for genre in genres:
                            if genre in all_genres:
                                idx = all_genres.index(genre)
                                genre_vector[idx] = 1
                
                genre_matrix.append(genre_vector)
            
            self.genre_matrix = np.array(genre_matrix)
            logger.info(f"Genre matrix shape: {self.genre_matrix.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error building genre features: {str(e)}")
            return False
    
    def build_metadata_features(self):
        """
        Build metadata features from movie attributes
        Includes: popularity, vote_average, vote_count, runtime, release_year
        """
        try:
            metadata_features = []
            
            for idx, row in self.movies_df.iterrows():
                features = []
                
                # Popularity (normalized)
                popularity = float(row.get('popularity', 0))
                features.append(popularity)
                
                # Vote average
                vote_avg = float(row.get('vote_average', 0))
                features.append(vote_avg)
                
                # Vote count (log-scaled)
                vote_count = float(row.get('vote_count', 0))
                features.append(np.log1p(vote_count))
                
                # Runtime (normalized)
                runtime = float(row.get('runtime', 0))
                features.append(runtime)
                
                # Release year (extracted from release_date)
                release_date = row.get('release_date', '')
                year = 0
                if release_date and isinstance(release_date, str):
                    try:
                        year = int(release_date.split('-')[0])
                    except:
                        year = 0
                features.append(year)
                
                # Budget-to-revenue ratio (if available)
                budget = float(row.get('budget', 0))
                revenue = float(row.get('revenue', 0))
                budget_revenue_ratio = revenue / budget if budget > 0 else 0
                features.append(budget_revenue_ratio)
                
                # Director reputation score (if available)
                director_score = float(row.get('director_score', 0))
                features.append(director_score)
                
                # Actor popularity score (if available)
                actor_score = float(row.get('actor_score', 0))
                features.append(actor_score)
                
                metadata_features.append(features)
            
            # Convert to numpy array and scale
            self.metadata_matrix = np.array(metadata_features)
            
            # Handle NaN and inf values
            self.metadata_matrix = np.nan_to_num(self.metadata_matrix, 
                                                  nan=0.0, 
                                                  posinf=0.0, 
                                                  neginf=0.0)
            
            # Normalize features
            self.metadata_matrix = self.scaler.fit_transform(self.metadata_matrix)
            
            logger.info(f"Metadata matrix shape: {self.metadata_matrix.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error building metadata features: {str(e)}")
            return False
    
    def compute_similarity_matrix(self, use_combined: bool = True):
        """
        Compute cosine similarity matrix
        
        Args:
            use_combined: If True, combine TF-IDF, genre, and metadata features
        """
        try:
            if use_combined:
                # Combine all features
                features_list = []
                
                # TF-IDF features (weight: 0.5)
                if self.tfidf_matrix is not None:
                    tfidf_dense = self.tfidf_matrix.toarray()
                    features_list.append(tfidf_dense * 0.5)
                
                # Genre features (weight: 0.3)
                if self.genre_matrix is not None:
                    features_list.append(self.genre_matrix * 0.3)
                
                # Metadata features (weight: 0.2)
                if self.metadata_matrix is not None:
                    features_list.append(self.metadata_matrix * 0.2)
                
                # Combine all features
                if features_list:
                    self.combined_features = np.hstack(features_list)
                    self.cosine_sim_matrix = cosine_similarity(self.combined_features)
                else:
                    logger.error("No features available to compute similarity")
                    return False
            else:
                # Use only TF-IDF
                if self.tfidf_matrix is not None:
                    self.cosine_sim_matrix = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
                else:
                    logger.error("TF-IDF matrix not built")
                    return False
            
            logger.info(f"Similarity matrix computed: {self.cosine_sim_matrix.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error computing similarity matrix: {str(e)}")
            return False
    
    def get_similar_movies(self, movie_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Get movies similar to the specified movie
        
        Args:
            movie_id: ID of the movie
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        try:
            if movie_id not in self.movie_indices:
                logger.warning(f"Movie {movie_id} not found")
                return []
            
            # Get movie index
            idx = self.movie_indices[movie_id]
            
            # Get similarity scores
            sim_scores = list(enumerate(self.cosine_sim_matrix[idx]))
            
            # Sort by similarity (excluding the movie itself)
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n_recommendations+1]
            
            # Get movie IDs and scores
            movie_ids = [self.movies_df.iloc[i[0]]['id'] for i in sim_scores]
            scores = [i[1] for i in sim_scores]
            
            return list(zip(movie_ids, scores))
            
        except Exception as e:
            logger.error(f"Error getting similar movies for {movie_id}: {str(e)}")
            return []
    
    def get_recommendations_for_user(self, user_liked_movies: List[int], 
                                     n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Get content-based recommendations based on user's liked movies
        
        Args:
            user_liked_movies: List of movie IDs the user liked
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of (movie_id, score) tuples
        """
        try:
            if not user_liked_movies:
                return []
            
            # Get similarity scores for all liked movies
            all_scores = {}
            
            for movie_id in user_liked_movies:
                similar_movies = self.get_similar_movies(movie_id, n_recommendations * 2)
                
                for rec_movie_id, score in similar_movies:
                    if rec_movie_id not in user_liked_movies:
                        if rec_movie_id in all_scores:
                            all_scores[rec_movie_id] += score
                        else:
                            all_scores[rec_movie_id] = score
            
            # Average the scores
            for movie_id in all_scores:
                all_scores[movie_id] /= len(user_liked_movies)
            
            # Sort and return top N
            recommendations = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
            return recommendations[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {str(e)}")
            return []
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        try:
            model_data = {
                'movies_df': self.movies_df,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'tfidf_matrix': self.tfidf_matrix,
                'cosine_sim_matrix': self.cosine_sim_matrix,
                'movie_indices': self.movie_indices,
                'genre_matrix': self.genre_matrix,
                'metadata_matrix': self.metadata_matrix,
                'combined_features': self.combined_features,
                'scaler': self.scaler
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Model file {filepath} not found")
                return False
            
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.movies_df = model_data['movies_df']
            self.tfidf_vectorizer = model_data['tfidf_vectorizer']
            self.tfidf_matrix = model_data['tfidf_matrix']
            self.cosine_sim_matrix = model_data['cosine_sim_matrix']
            self.movie_indices = model_data['movie_indices']
            self.genre_matrix = model_data['genre_matrix']
            self.metadata_matrix = model_data['metadata_matrix']
            self.combined_features = model_data['combined_features']
            self.scaler = model_data['scaler']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_movies = [
        {
            "id": 1,
            "title": "The Shawshank Redemption",
            "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "genres": '[{"name": "Drama"}, {"name": "Crime"}]',
            "popularity": 85.5,
            "vote_average": 8.7,
            "vote_count": 20000,
            "runtime": 142,
            "release_date": "1994-09-23"
        },
        {
            "id": 2,
            "title": "The Godfather",
            "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "genres": '[{"name": "Drama"}, {"name": "Crime"}]',
            "popularity": 92.3,
            "vote_average": 8.7,
            "vote_count": 15000,
            "runtime": 175,
            "release_date": "1972-03-24"
        }
    ]
    
    # Create and train model
    model = ContentBasedFilteringModel()
    model.prepare_data(sample_movies)
    model.build_tfidf_features('overview')
    model.build_genre_features()
    model.build_metadata_features()
    model.compute_similarity_matrix(use_combined=True)
    
    # Get recommendations
    similar = model.get_similar_movies(1, 5)
    print("Similar movies to movie 1:", similar)
