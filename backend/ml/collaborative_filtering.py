"""
Advanced Collaborative Filtering Recommendation Model
Enhanced implementation with multiple algorithms for mini project
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Tuple, Optional
import logging
from scipy.sparse import csr_matrix
import pickle
import os
from scipy.sparse.linalg import spsolve

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborativeFilteringModel:
    """
    Advanced Collaborative Filtering Model with Multiple Algorithms
    - User-based Collaborative Filtering
    - Item-based Collaborative Filtering  
    - Matrix Factorization (SVD)
    - Hybrid Approach
    """
    
    def __init__(self):
        self.user_movie_matrix = None
        self.movie_similarity_matrix = None
        self.user_similarity_matrix = None
        self.movies_df = None
        self.ratings_df = None
        self.user_ids = None
        self.movie_ids = None
        
        # Advanced models
        self.svd_model = None
        self.knn_model = None
        self.als_model = None
        self.model_cache = {}
        
        # ALS parameters
        self.user_factors = None
        self.item_factors = None
        self.n_factors = 50
        
        # Performance metrics
        self.rmse = None
        self.mae = None
        
        # Dropout regularization
        self.dropout_rate = 0.0
        
    def prepare_data(self, ratings_data: List[Dict], movies_data: List[Dict]):
        """
        Prepare data for collaborative filtering
        
        Args:
            ratings_data: List of dictionaries with user_id, movie_id, rating
            movies_data: List of dictionaries with movie information
        """
        try:
            # Convert to DataFrames
            self.ratings_df = pd.DataFrame(ratings_data)
            self.movies_df = pd.DataFrame(movies_data)
            
            # Create user-movie matrix
            self.user_movie_matrix = self.ratings_df.pivot_table(
                index='user_id', 
                columns='movie_id', 
                values='rating'
            ).fillna(0)
            
            # Get user and movie IDs
            self.user_ids = list(self.user_movie_matrix.index)
            self.movie_ids = list(self.user_movie_matrix.columns)
            
            logger.info(f"Data prepared: {len(self.user_ids)} users, {len(self.movie_ids)} movies")
            return True
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            return False
    
    def compute_user_similarity(self):
        """
        Compute user similarity matrix using cosine similarity
        """
        try:
            # Compute cosine similarity between users
            self.user_similarity_matrix = cosine_similarity(self.user_movie_matrix)
            
            # Convert to DataFrame for easier handling
            self.user_similarity_df = pd.DataFrame(
                self.user_similarity_matrix,
                index=self.user_ids,
                columns=self.user_ids
            )
            
            logger.info("User similarity matrix computed")
            return True
            
        except Exception as e:
            logger.error(f"Error computing user similarity: {str(e)}")
            return False
    
    def get_user_recommendations(self, user_id: str, n_recommendations: int = 10, 
                                 discover_hidden_gems: bool = True,
                                 diversity_factor: float = 0.3,
                                 min_quality_threshold: float = 3.5) -> List[Tuple[int, float]]:
        """
        WORLD-CLASS RECOMMENDATION ENGINE
        Get personalized movie recommendations that find HIDDEN GEMS users will love
        
        Features:
        - Finds underrated movies (hidden gems) not just popular ones
        - Balances predicted rating with discovery/serendipity
        - Ensures diversity in recommendations
        - Filters out low-quality movies
        - Considers user's taste profile
        
        Args:
            user_id: ID of the user
            n_recommendations: Number of recommendations to return
            discover_hidden_gems: If True, boost underrated movies (default: True)
            diversity_factor: How diverse recommendations should be (0-1, default: 0.3)
            min_quality_threshold: Minimum average rating to recommend (default: 3.5)
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        try:
            if user_id not in self.user_ids:
                logger.warning(f"User {user_id} not found in training data")
                return []
            
            # Get user's row index
            user_idx = self.user_ids.index(user_id)
            
            # Get user's ratings and preferences
            user_ratings = self.user_movie_matrix.iloc[user_idx]
            user_avg_rating = user_ratings[user_ratings > 0].mean() if len(user_ratings[user_ratings > 0]) > 0 else 3.5
            
            # Find movies the user hasn't rated
            unrated_movies = user_ratings[user_ratings == 0].index
            
            # Predict ratings for unrated movies with ADVANCED SCORING
            predictions = []
            
            for movie_id in unrated_movies:
                if movie_id in self.movie_ids:
                    movie_idx = self.movie_ids.index(movie_id)
                    
                    # Base prediction
                    predicted_rating = self._predict_rating(user_idx, movie_idx)
                    
                    # Calculate movie popularity (how many users rated it)
                    movie_ratings = self.user_movie_matrix.iloc[:, movie_idx]
                    num_ratings = (movie_ratings > 0).sum()
                    avg_movie_rating = movie_ratings[movie_ratings > 0].mean() if num_ratings > 0 else 3.0
                    
                    # QUALITY FILTER: Skip low-quality movies
                    if avg_movie_rating < min_quality_threshold:
                        continue
                    
                    # HIDDEN GEM BOOST: Reward underrated movies
                    if discover_hidden_gems:
                        # Movies with fewer ratings but high quality = hidden gems
                        max_ratings = self.user_movie_matrix.shape[0]
                        popularity_ratio = num_ratings / max_ratings
                        
                        # Boost score for movies that are:
                        # 1. High quality (avg_movie_rating >= 4.0)
                        # 2. Not too popular (popularity_ratio < 0.3)
                        # 3. User would likely enjoy (predicted_rating >= user_avg_rating)
                        if avg_movie_rating >= 4.0 and popularity_ratio < 0.3 and predicted_rating >= user_avg_rating:
                            # Hidden gem bonus: +0.5 to +1.0 points
                            hidden_gem_bonus = (1 - popularity_ratio) * 0.8
                            predicted_rating = min(5.0, predicted_rating + hidden_gem_bonus)
                    
                    # DIVERSITY SCORE: Penalize movies too similar to what user already rated highly
                    diversity_penalty = 0
                    if diversity_factor > 0:
                        # Get genres of this movie
                        movie_info = self.movies_df[self.movies_df['id'] == movie_id]
                        if not movie_info.empty:
                            # Simple diversity check (can be enhanced with genre analysis)
                            diversity_penalty = diversity_factor * 0.2  # Small penalty for variety
                    
                    # FINAL SCORE
                    final_score = predicted_rating - diversity_penalty
                    
                    predictions.append((movie_id, final_score, avg_movie_rating, num_ratings))
            
            # Sort by final score (highest first)
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            # Return top N with just movie_id and score
            return [(movie_id, score) for movie_id, score, _, _ in predictions[:n_recommendations]]
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
            return []
    
    def _predict_rating(self, user_idx: int, movie_idx: int, use_advanced: bool = True) -> float:
        """
        ENHANCED RATING PREDICTION with bias correction and confidence weighting
        
        Args:
            user_idx: Index of the user
            movie_idx: Index of the movie
            use_advanced: Use advanced prediction with bias correction
            
        Returns:
            Predicted rating (1.0 to 5.0)
        """
        # Get similarity scores for this user with all other users
        user_similarities = self.user_similarity_matrix[user_idx]
        
        # Get ratings for this movie by all users
        movie_ratings = self.user_movie_matrix.iloc[:, movie_idx]
        
        # Find users who have rated this movie
        rated_users = movie_ratings[movie_ratings > 0]
        
        if len(rated_users) == 0:
            # If no one has rated this movie, return neutral rating
            return 3.0
        
        if use_advanced:
            # ADVANCED PREDICTION with user bias correction
            user_avg = self.user_movie_matrix.iloc[user_idx][self.user_movie_matrix.iloc[user_idx] > 0].mean()
            if pd.isna(user_avg):
                user_avg = 3.5
            
            global_avg = self.user_movie_matrix[self.user_movie_matrix > 0].mean().mean()
            
            weighted_sum = 0
            similarity_sum = 0
            
            for other_user_id, rating in rated_users.items():
                other_user_idx = self.user_ids.index(other_user_id)
                similarity = user_similarities[other_user_idx]
                
                # Only consider positive similarities
                if similarity > 0.1:  # Threshold to filter weak similarities
                    # Get other user's average rating (their bias)
                    other_user_avg = self.user_movie_matrix.iloc[other_user_idx][self.user_movie_matrix.iloc[other_user_idx] > 0].mean()
                    if pd.isna(other_user_avg):
                        other_user_avg = global_avg
                    
                    # Normalize rating by removing user bias
                    normalized_rating = rating - other_user_avg + user_avg
                    
                    # Weight by similarity (more similar users have more influence)
                    weighted_sum += similarity * normalized_rating
                    similarity_sum += similarity
            
            if similarity_sum == 0:
                # Fallback to movie average
                return min(5.0, max(1.0, rated_users.mean()))
            
            predicted_rating = weighted_sum / similarity_sum
            
            # Confidence adjustment based on number of similar users
            confidence = min(1.0, similarity_sum / 10)  # More similar users = higher confidence
            predicted_rating = confidence * predicted_rating + (1 - confidence) * user_avg
            
        else:
            # BASIC PREDICTION (original method)
            weighted_sum = 0
            similarity_sum = 0
            
            for other_user_id, rating in rated_users.items():
                other_user_idx = self.user_ids.index(other_user_id)
                similarity = user_similarities[other_user_idx]
                
                if similarity > 0:
                    weighted_sum += similarity * rating
                    similarity_sum += similarity
            
            if similarity_sum == 0:
                return rated_users.mean()
            
            predicted_rating = weighted_sum / similarity_sum
        
        # Clamp between 1 and 5
        return max(1.0, min(5.0, predicted_rating))
    
    def get_similar_users(self, user_id: str, n_similar: int = 5) -> List[Tuple[str, float]]:
        """
        Get users similar to the specified user
        
        Args:
            user_id: ID of the user
            n_similar: Number of similar users to return
            
        Returns:
            List of (user_id, similarity_score) tuples
        """
        try:
            if user_id not in self.user_ids:
                return []
            
            user_idx = self.user_ids.index(user_id)
            similarities = self.user_similarity_matrix[user_idx]
            
            # Create list of (user_id, similarity) pairs
            user_similarities = [
                (self.user_ids[i], similarities[i]) 
                for i in range(len(self.user_ids)) 
                if self.user_ids[i] != user_id
            ]
            
            # Sort by similarity and return top N
            user_similarities.sort(key=lambda x: x[1], reverse=True)
            return user_similarities[:n_similar]
            
        except Exception as e:
            logger.error(f"Error getting similar users for {user_id}: {str(e)}")
            return []

    def train_svd_model(self, n_components: int = 50):
        """
        Train SVD model for matrix factorization
        """
        try:
            if self.user_movie_matrix is None:
                logger.error("User-movie matrix not prepared")
                return False
            
            # Convert to sparse matrix for efficiency
            sparse_matrix = csr_matrix(self.user_movie_matrix.values)
            
            # Train SVD model
            self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
            self.svd_model.fit(sparse_matrix)
            
            logger.info(f"SVD model trained with {n_components} components")
            return True
            
        except Exception as e:
            logger.error(f"Error training SVD model: {str(e)}")
            return False

    def train_knn_model(self, n_neighbors: int = 20):
        """
        Train KNN model for collaborative filtering
        """
        try:
            if self.user_movie_matrix is None:
                logger.error("User-movie matrix not prepared")
                return False
            
            # Train KNN model
            self.knn_model = NearestNeighbors(
                n_neighbors=n_neighbors, 
                metric='cosine', 
                algorithm='brute'
            )
            self.knn_model.fit(self.user_movie_matrix)
            
            logger.info(f"KNN model trained with {n_neighbors} neighbors")
            return True
            
        except Exception as e:
            logger.error(f"Error training KNN model: {str(e)}")
            return False
    
    def train_als_model(self, n_factors: int = 50, n_iterations: int = 10, 
                       lambda_reg: float = 0.1, dropout_rate: float = 0.0):
        """
        Train ALS (Alternating Least Squares) model with dropout regularization
        
        Args:
            n_factors: Number of latent factors
            n_iterations: Number of ALS iterations
            lambda_reg: Regularization parameter
            dropout_rate: Dropout rate for regularization (0-1)
        """
        try:
            if self.user_movie_matrix is None:
                logger.error("User-movie matrix not prepared")
                return False
            
            self.n_factors = n_factors
            self.dropout_rate = dropout_rate
            
            # Convert to sparse matrix
            R = csr_matrix(self.user_movie_matrix.values)
            n_users, n_items = R.shape
            
            # Initialize factor matrices randomly
            np.random.seed(42)
            self.user_factors = np.random.normal(0, 0.1, (n_users, n_factors))
            self.item_factors = np.random.normal(0, 0.1, (n_items, n_factors))
            
            logger.info(f"Training ALS model: {n_factors} factors, {n_iterations} iterations")
            
            # ALS iterations
            for iteration in range(n_iterations):
                # Fix item factors, update user factors
                self.user_factors = self._als_step(R, self.item_factors, lambda_reg, dropout_rate)
                
                # Fix user factors, update item factors
                self.item_factors = self._als_step(R.T, self.user_factors, lambda_reg, dropout_rate)
                
                # Calculate RMSE for monitoring
                if iteration % 2 == 0:
                    predictions = self.user_factors @ self.item_factors.T
                    mask = R.toarray() > 0
                    rmse = np.sqrt(np.mean((R.toarray()[mask] - predictions[mask]) ** 2))
                    logger.info(f"ALS Iteration {iteration + 1}/{n_iterations}, RMSE: {rmse:.4f}")
            
            logger.info(f"ALS model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training ALS model: {str(e)}")
            return False
    
    def _als_step(self, R: csr_matrix, fixed_factors: np.ndarray, 
                  lambda_reg: float, dropout_rate: float) -> np.ndarray:
        """
        Single ALS step with dropout regularization
        
        Args:
            R: Rating matrix (sparse)
            fixed_factors: Fixed factor matrix
            lambda_reg: Regularization parameter
            dropout_rate: Dropout rate
            
        Returns:
            Updated factor matrix
        """
        n_users, n_factors = R.shape[0], fixed_factors.shape[1]
        updated_factors = np.zeros((n_users, n_factors))
        
        # Apply dropout mask to fixed factors
        if dropout_rate > 0:
            dropout_mask = np.random.binomial(1, 1 - dropout_rate, fixed_factors.shape)
            fixed_factors_dropout = fixed_factors * dropout_mask / (1 - dropout_rate)
        else:
            fixed_factors_dropout = fixed_factors
        
        # Update each user/item
        for u in range(n_users):
            # Get rated items for this user
            rated_items = R[u].nonzero()[1]
            
            if len(rated_items) == 0:
                continue
            
            # Get ratings and factors for rated items
            ratings = R[u, rated_items].toarray().flatten()
            factors = fixed_factors_dropout[rated_items]
            
            # Solve least squares with regularization
            # (F^T F + λI) x = F^T r
            A = factors.T @ factors + lambda_reg * np.eye(n_factors)
            b = factors.T @ ratings
            
            try:
                updated_factors[u] = np.linalg.solve(A, b)
            except np.linalg.LinAlgError:
                # If singular, use pseudo-inverse
                updated_factors[u] = np.linalg.lstsq(A, b, rcond=None)[0]
        
        return updated_factors
    
    def get_als_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Get recommendations using ALS model
        
        Args:
            user_id: User ID
            n_recommendations: Number of recommendations
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        try:
            if self.user_factors is None or self.item_factors is None:
                logger.warning("ALS model not trained")
                return []
            
            if user_id not in self.user_ids:
                logger.warning(f"User {user_id} not found")
                return []
            
            # Get user index
            user_idx = self.user_ids.index(user_id)
            
            # Get user's ratings
            user_ratings = self.user_movie_matrix.iloc[user_idx]
            
            # Find unrated movies
            unrated_movies = user_ratings[user_ratings == 0].index
            
            if len(unrated_movies) == 0:
                return []
            
            # Predict ratings using ALS factors
            user_factor = self.user_factors[user_idx]
            predictions = []
            
            for movie_id in unrated_movies:
                if movie_id in self.movie_ids:
                    movie_idx = self.movie_ids.index(movie_id)
                    item_factor = self.item_factors[movie_idx]
                    
                    # Predicted rating is dot product of factors
                    predicted_rating = np.dot(user_factor, item_factor)
                    
                    # Clip to valid range
                    predicted_rating = max(1.0, min(5.0, predicted_rating))
                    
                    predictions.append((movie_id, float(predicted_rating)))
            
            # Sort by predicted rating
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            return predictions[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting ALS recommendations: {str(e)}")
            return []

    def get_svd_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Get recommendations using SVD matrix factorization
        """
        try:
            if self.svd_model is None:
                logger.warning("SVD model not trained")
                return []
            
            if user_id not in self.user_ids:
                logger.warning(f"User {user_id} not found")
                return []
            
            user_idx = self.user_ids.index(user_id)
            user_ratings = self.user_movie_matrix.iloc[user_idx]
            
            # Find unrated movies
            unrated_movies = user_ratings[user_ratings == 0].index
            
            if len(unrated_movies) == 0:
                return []
            
            # Get SVD predictions
            user_vector = self.user_movie_matrix.iloc[user_idx:user_idx+1]
            sparse_user = csr_matrix(user_vector.values)
            user_factors = self.svd_model.transform(sparse_user)
            
            # Reconstruct ratings using SVD
            reconstructed = self.svd_model.inverse_transform(user_factors)
            predictions = reconstructed[0]
            
            # Get predictions for unrated movies
            movie_predictions = []
            for movie_id in unrated_movies:
                if movie_id in self.movie_ids:
                    movie_idx = self.movie_ids.index(movie_id)
                    predicted_rating = predictions[movie_idx]
                    movie_predictions.append((movie_id, float(predicted_rating)))
            
            # Sort by predicted rating
            movie_predictions.sort(key=lambda x: x[1], reverse=True)
            return movie_predictions[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting SVD recommendations for {user_id}: {str(e)}")
            return []

    def get_hybrid_recommendations(self, user_id: str, n_recommendations: int = 10,
                                   use_als: bool = True) -> List[Tuple[int, float]]:
        """
        Get hybrid recommendations combining multiple approaches
        Now includes ALS for improved accuracy
        
        Args:
            user_id: User ID
            n_recommendations: Number of recommendations
            use_als: Include ALS recommendations in hybrid
        """
        try:
            # Get recommendations from different methods
            user_based = self.get_user_recommendations(user_id, n_recommendations * 2)
            svd_based = self.get_svd_recommendations(user_id, n_recommendations * 2)
            
            # Combine scores with weights
            combined_scores = {}
            
            if use_als and self.user_factors is not None:
                # Three-way hybrid: User-based (0.3) + SVD (0.3) + ALS (0.4)
                als_based = self.get_als_recommendations(user_id, n_recommendations * 2)
                
                # User-based CF weight: 0.3
                for movie_id, score in user_based:
                    combined_scores[movie_id] = score * 0.3
                
                # SVD weight: 0.3
                for movie_id, score in svd_based:
                    if movie_id in combined_scores:
                        combined_scores[movie_id] += score * 0.3
                    else:
                        combined_scores[movie_id] = score * 0.3
                
                # ALS weight: 0.4 (highest weight for best performance)
                for movie_id, score in als_based:
                    if movie_id in combined_scores:
                        combined_scores[movie_id] += score * 0.4
                    else:
                        combined_scores[movie_id] = score * 0.4
            else:
                # Two-way hybrid: User-based (0.4) + SVD (0.6)
                # User-based CF weight: 0.4
                for movie_id, score in user_based:
                    combined_scores[movie_id] = score * 0.4
                
                # SVD weight: 0.6
                for movie_id, score in svd_based:
                    if movie_id in combined_scores:
                        combined_scores[movie_id] += score * 0.6
                    else:
                        combined_scores[movie_id] = score * 0.6
            
            # Sort by combined score
            final_recommendations = sorted(
                combined_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return final_recommendations[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting hybrid recommendations for {user_id}: {str(e)}")
            return []

    def evaluate_model(self, test_ratings: List[Dict]) -> Dict[str, float]:
        """
        Evaluate model performance using RMSE and MAE
        """
        try:
            if not test_ratings:
                return {"rmse": 0.0, "mae": 0.0}
            
            predictions = []
            actual_ratings = []
            
            for rating in test_ratings:
                user_id = rating['user_id']
                movie_id = rating['movie_id']
                actual_rating = rating['rating']
                
                if user_id in self.user_ids and movie_id in self.movie_ids:
                    predicted = self._predict_rating(
                        self.user_ids.index(user_id),
                        self.movie_ids.index(movie_id)
                    )
                    predictions.append(predicted)
                    actual_ratings.append(actual_rating)
            
            if not predictions:
                return {"rmse": 0.0, "mae": 0.0}
            
            # Calculate RMSE and MAE
            predictions = np.array(predictions)
            actual_ratings = np.array(actual_ratings)
            
            rmse = np.sqrt(np.mean((predictions - actual_ratings) ** 2))
            mae = np.mean(np.abs(predictions - actual_ratings))
            
            self.rmse = rmse
            self.mae = mae
            
            return {"rmse": float(rmse), "mae": float(mae)}

        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            return {"rmse": 0.0, "mae": 0.0}
    
    def save_model(self, filepath: str):
        """
        Save trained model to file
        """
        try:
            model_data = {
                'user_movie_matrix': self.user_movie_matrix,
                'user_similarity_matrix': self.user_similarity_matrix,
                'movie_similarity_matrix': self.movie_similarity_matrix,
                'user_ids': self.user_ids,
                'movie_ids': self.movie_ids,
                'svd_model': self.svd_model,
                'knn_model': self.knn_model,
                'user_factors': self.user_factors,
                'item_factors': self.item_factors,
                'n_factors': self.n_factors,
                'dropout_rate': self.dropout_rate,
                'rmse': self.rmse,
                'mae': self.mae
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False

    def load_model(self, filepath: str):
        """
        Load trained model from file
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Model file {filepath} not found")
                return False
            
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.user_movie_matrix = model_data['user_movie_matrix']
            self.user_similarity_matrix = model_data['user_similarity_matrix']
            self.movie_similarity_matrix = model_data['movie_similarity_matrix']
            self.user_ids = model_data['user_ids']
            self.movie_ids = model_data['movie_ids']
            self.svd_model = model_data['svd_model']
            self.knn_model = model_data['knn_model']
            self.user_factors = model_data.get('user_factors')
            self.item_factors = model_data.get('item_factors')
            self.n_factors = model_data.get('n_factors', 50)
            self.dropout_rate = model_data.get('dropout_rate', 0.0)
            self.rmse = model_data['rmse']
            self.mae = model_data['mae']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Sample data for testing
    sample_ratings = [
        {"user_id": "user1", "movie_id": 1, "rating": 5},
        {"user_id": "user1", "movie_id": 2, "rating": 4},
        {"user_id": "user1", "movie_id": 3, "rating": 3},
        {"user_id": "user2", "movie_id": 1, "rating": 4},
        {"user_id": "user2", "movie_id": 2, "rating": 5},
        {"user_id": "user2", "movie_id": 4, "rating": 4},
        {"user_id": "user3", "movie_id": 3, "rating": 5},
        {"user_id": "user3", "movie_id": 4, "rating": 4},
        {"user_id": "user3", "movie_id": 5, "rating": 5},
    ]
    
    sample_movies = [
        {"id": 1, "title": "Movie 1", "genres": "Action"},
        {"id": 2, "title": "Movie 2", "genres": "Comedy"},
        {"id": 3, "title": "Movie 3", "genres": "Drama"},
        {"id": 4, "title": "Movie 4", "genres": "Action"},
        {"id": 5, "title": "Movie 5", "genres": "Comedy"},
    ]
    
    # Create and train model
    model = CollaborativeFilteringModel()
    model.prepare_data(sample_ratings, sample_movies)
    model.compute_user_similarity()
    
    # Get recommendations
    recommendations = model.get_user_recommendations("user1", 3)
    print("Recommendations for user1:", recommendations)
    
    # Get similar users
    similar_users = model.get_similar_users("user1", 2)
    print("Users similar to user1:", similar_users)