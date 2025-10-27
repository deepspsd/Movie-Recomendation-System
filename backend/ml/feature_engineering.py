"""
Advanced Feature Engineering Module
Implements Word2Vec, Sentiment Analysis, PCA, and advanced preprocessing
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from typing import List, Dict, Tuple, Optional
import logging
import pickle
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Advanced Feature Engineering for Movie Recommendation System
    - Word2Vec for semantic similarity
    - Sentiment Analysis on reviews
    - PCA for dimensionality reduction
    - Advanced imputation and scaling
    - Categorical encoding
    """
    
    def __init__(self):
        self.pca_model = None
        self.scaler = StandardScaler()
        self.min_max_scaler = MinMaxScaler()
        self.imputer = KNNImputer(n_neighbors=5)
        self.label_encoders = {}
        
        # Word2Vec model (will be initialized if gensim is available)
        self.word2vec_model = None
        self.word_vectors = {}
        
        # Sentiment analyzer (will be initialized if available)
        self.sentiment_analyzer = None
        
    def apply_pca(self, features: np.ndarray, n_components: int = 50, 
                  variance_threshold: float = 0.95) -> np.ndarray:
        """
        Apply PCA for dimensionality reduction
        
        Args:
            features: Feature matrix
            n_components: Number of components (or variance threshold)
            variance_threshold: Minimum variance to retain
            
        Returns:
            Reduced feature matrix
        """
        try:
            # Determine optimal number of components
            if n_components is None:
                # Use variance threshold
                pca_temp = PCA()
                pca_temp.fit(features)
                cumsum_variance = np.cumsum(pca_temp.explained_variance_ratio_)
                n_components = np.argmax(cumsum_variance >= variance_threshold) + 1
                logger.info(f"PCA: Using {n_components} components for {variance_threshold*100}% variance")
            
            # Apply PCA
            self.pca_model = PCA(n_components=n_components, random_state=42)
            reduced_features = self.pca_model.fit_transform(features)
            
            explained_variance = sum(self.pca_model.explained_variance_ratio_)
            logger.info(f"PCA: Reduced from {features.shape[1]} to {n_components} dimensions")
            logger.info(f"PCA: Explained variance: {explained_variance*100:.2f}%")
            
            return reduced_features
            
        except Exception as e:
            logger.error(f"Error applying PCA: {str(e)}")
            return features
    
    def train_word2vec(self, text_corpus: List[str], vector_size: int = 100, 
                       window: int = 5, min_count: int = 2):
        """
        Train Word2Vec model on text corpus
        
        Args:
            text_corpus: List of text documents
            vector_size: Dimensionality of word vectors
            window: Context window size
            min_count: Minimum word frequency
        """
        try:
            # Try to import gensim
            try:
                from gensim.models import Word2Vec
                from gensim.utils import simple_preprocess
            except ImportError:
                logger.warning("gensim not installed. Word2Vec features will be skipped.")
                return False
            
            # Preprocess text
            processed_corpus = [simple_preprocess(text) for text in text_corpus]
            
            # Train Word2Vec
            self.word2vec_model = Word2Vec(
                sentences=processed_corpus,
                vector_size=vector_size,
                window=window,
                min_count=min_count,
                workers=4,
                sg=1,  # Skip-gram model
                epochs=10,
                seed=42
            )
            
            logger.info(f"Word2Vec trained: {len(self.word2vec_model.wv)} words, {vector_size} dimensions")
            return True
            
        except Exception as e:
            logger.error(f"Error training Word2Vec: {str(e)}")
            return False
    
    def get_text_vector(self, text: str) -> np.ndarray:
        """
        Get vector representation of text using Word2Vec
        
        Args:
            text: Input text
            
        Returns:
            Vector representation (average of word vectors)
        """
        try:
            if self.word2vec_model is None:
                return np.zeros(100)
            
            from gensim.utils import simple_preprocess
            
            # Tokenize
            words = simple_preprocess(text)
            
            # Get word vectors
            word_vectors = []
            for word in words:
                if word in self.word2vec_model.wv:
                    word_vectors.append(self.word2vec_model.wv[word])
            
            # Average word vectors
            if word_vectors:
                return np.mean(word_vectors, axis=0)
            else:
                return np.zeros(self.word2vec_model.vector_size)
                
        except Exception as e:
            logger.error(f"Error getting text vector: {str(e)}")
            return np.zeros(100)
    
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts using Word2Vec
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        try:
            vec1 = self.get_text_vector(text1)
            vec2 = self.get_text_vector(text2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error computing semantic similarity: {str(e)}")
            return 0.0
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment scores
        """
        try:
            # Try to use TextBlob for sentiment analysis
            try:
                from textblob import TextBlob
            except ImportError:
                logger.warning("TextBlob not installed. Using simple sentiment analysis.")
                return self._simple_sentiment_analysis(text)
            
            # Analyze sentiment
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                'polarity': sentiment.polarity,  # -1 to 1 (negative to positive)
                'subjectivity': sentiment.subjectivity,  # 0 to 1 (objective to subjective)
                'positive': max(0, sentiment.polarity),
                'negative': abs(min(0, sentiment.polarity))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'polarity': 0.0, 'subjectivity': 0.5, 'positive': 0.0, 'negative': 0.0}
    
    def _simple_sentiment_analysis(self, text: str) -> Dict[str, float]:
        """
        Simple rule-based sentiment analysis (fallback)
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment scores
        """
        # Simple positive/negative word lists
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'best', 'perfect', 'beautiful', 'brilliant', 'awesome',
            'outstanding', 'superb', 'incredible', 'magnificent'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'poor',
            'hate', 'disappointing', 'boring', 'waste', 'dull', 'mediocre',
            'weak', 'pathetic', 'annoying', 'frustrating'
        }
        
        # Tokenize and count
        words = re.findall(r'\w+', text.lower())
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            polarity = 0.0
        else:
            polarity = (positive_count - negative_count) / total
        
        return {
            'polarity': polarity,
            'subjectivity': 0.5,
            'positive': positive_count / max(1, len(words)),
            'negative': negative_count / max(1, len(words))
        }
    
    def impute_missing_values(self, data: np.ndarray, strategy: str = 'knn') -> np.ndarray:
        """
        Advanced imputation of missing values
        
        Args:
            data: Data matrix with missing values
            strategy: Imputation strategy ('knn', 'mean', 'median', 'most_frequent')
            
        Returns:
            Imputed data matrix
        """
        try:
            if strategy == 'knn':
                imputer = KNNImputer(n_neighbors=5, weights='distance')
            else:
                imputer = SimpleImputer(strategy=strategy)
            
            imputed_data = imputer.fit_transform(data)
            
            missing_count = np.isnan(data).sum()
            logger.info(f"Imputed {missing_count} missing values using {strategy} strategy")
            
            return imputed_data
            
        except Exception as e:
            logger.error(f"Error imputing missing values: {str(e)}")
            return data
    
    def scale_features(self, features: np.ndarray, method: str = 'standard') -> np.ndarray:
        """
        Scale features using various methods
        
        Args:
            features: Feature matrix
            method: Scaling method ('standard', 'minmax', 'robust')
            
        Returns:
            Scaled feature matrix
        """
        try:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            elif method == 'robust':
                from sklearn.preprocessing import RobustScaler
                scaler = RobustScaler()
            else:
                logger.warning(f"Unknown scaling method: {method}. Using standard.")
                scaler = StandardScaler()
            
            scaled_features = scaler.fit_transform(features)
            logger.info(f"Features scaled using {method} method")
            
            return scaled_features
            
        except Exception as e:
            logger.error(f"Error scaling features: {str(e)}")
            return features
    
    def encode_categorical(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Encode categorical variables
        
        Args:
            data: DataFrame with categorical columns
            columns: List of column names to encode
            
        Returns:
            DataFrame with encoded columns
        """
        try:
            encoded_data = data.copy()
            
            for col in columns:
                if col not in data.columns:
                    continue
                
                # Create label encoder
                le = LabelEncoder()
                
                # Handle missing values
                encoded_data[col] = encoded_data[col].fillna('Unknown')
                
                # Encode
                encoded_data[col] = le.fit_transform(encoded_data[col].astype(str))
                
                # Store encoder
                self.label_encoders[col] = le
            
            logger.info(f"Encoded {len(columns)} categorical columns")
            return encoded_data
            
        except Exception as e:
            logger.error(f"Error encoding categorical variables: {str(e)}")
            return data
    
    def extract_temporal_features(self, dates: pd.Series) -> pd.DataFrame:
        """
        Extract temporal features from dates
        
        Args:
            dates: Series of date strings
            
        Returns:
            DataFrame with temporal features
        """
        try:
            # Convert to datetime
            dates_dt = pd.to_datetime(dates, errors='coerce')
            
            # Extract features
            temporal_features = pd.DataFrame({
                'year': dates_dt.dt.year,
                'month': dates_dt.dt.month,
                'day_of_week': dates_dt.dt.dayofweek,
                'quarter': dates_dt.dt.quarter,
                'is_weekend': dates_dt.dt.dayofweek.isin([5, 6]).astype(int),
                'days_since_epoch': (dates_dt - pd.Timestamp('1970-01-01')).dt.days
            })
            
            # Fill missing values
            temporal_features = temporal_features.fillna(0)
            
            logger.info("Extracted temporal features")
            return temporal_features
            
        except Exception as e:
            logger.error(f"Error extracting temporal features: {str(e)}")
            return pd.DataFrame()
    
    def create_interaction_features(self, features_df: pd.DataFrame, 
                                    feature_pairs: List[Tuple[str, str]]) -> pd.DataFrame:
        """
        Create interaction features between feature pairs
        
        Args:
            features_df: DataFrame with features
            feature_pairs: List of (feature1, feature2) tuples
            
        Returns:
            DataFrame with interaction features
        """
        try:
            interaction_df = features_df.copy()
            
            for feat1, feat2 in feature_pairs:
                if feat1 in features_df.columns and feat2 in features_df.columns:
                    # Multiplicative interaction
                    interaction_df[f'{feat1}_x_{feat2}'] = features_df[feat1] * features_df[feat2]
                    
                    # Ratio interaction (if no zeros)
                    if (features_df[feat2] != 0).all():
                        interaction_df[f'{feat1}_div_{feat2}'] = features_df[feat1] / features_df[feat2]
            
            logger.info(f"Created {len(feature_pairs)*2} interaction features")
            return interaction_df
            
        except Exception as e:
            logger.error(f"Error creating interaction features: {str(e)}")
            return features_df
    
    def extract_budget_revenue_features(self, budget: pd.Series, revenue: pd.Series) -> pd.DataFrame:
        """
        Extract advanced budget-revenue features
        
        Args:
            budget: Series of budget values
            revenue: Series of revenue values
            
        Returns:
            DataFrame with budget-revenue features
        """
        try:
            features = pd.DataFrame()
            
            # Basic ratio
            features['budget_revenue_ratio'] = revenue / budget.replace(0, np.nan)
            
            # ROI (Return on Investment)
            features['roi'] = (revenue - budget) / budget.replace(0, np.nan)
            
            # Profit
            features['profit'] = revenue - budget
            
            # Log transformations (for skewed distributions)
            features['log_budget'] = np.log1p(budget)
            features['log_revenue'] = np.log1p(revenue)
            
            # Budget category (low, medium, high)
            budget_quantiles = budget.quantile([0.33, 0.67])
            features['budget_category'] = pd.cut(
                budget, 
                bins=[-np.inf, budget_quantiles[0.33], budget_quantiles[0.67], np.inf],
                labels=[0, 1, 2]
            )
            
            # Fill missing values
            features = features.fillna(0)
            
            logger.info("Extracted budget-revenue features")
            return features
            
        except Exception as e:
            logger.error(f"Error extracting budget-revenue features: {str(e)}")
            return pd.DataFrame()
    
    def save_models(self, filepath: str):
        """Save feature engineering models"""
        try:
            models = {
                'pca_model': self.pca_model,
                'scaler': self.scaler,
                'min_max_scaler': self.min_max_scaler,
                'imputer': self.imputer,
                'label_encoders': self.label_encoders,
                'word2vec_model': self.word2vec_model
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models, f)
            
            logger.info(f"Feature engineering models saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def load_models(self, filepath: str):
        """Load feature engineering models"""
        try:
            with open(filepath, 'rb') as f:
                models = pickle.load(f)
            
            self.pca_model = models['pca_model']
            self.scaler = models['scaler']
            self.min_max_scaler = models['min_max_scaler']
            self.imputer = models['imputer']
            self.label_encoders = models['label_encoders']
            self.word2vec_model = models['word2vec_model']
            
            logger.info(f"Feature engineering models loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Create feature engineer
    fe = FeatureEngineer()
    
    # Example: PCA
    features = np.random.rand(100, 50)
    reduced = fe.apply_pca(features, n_components=10)
    print(f"PCA: {features.shape} -> {reduced.shape}")
    
    # Example: Sentiment analysis
    text = "This movie is absolutely amazing and wonderful!"
    sentiment = fe.analyze_sentiment(text)
    print(f"Sentiment: {sentiment}")
    
    # Example: Missing value imputation
    data_with_missing = np.random.rand(100, 10)
    data_with_missing[np.random.rand(100, 10) < 0.1] = np.nan
    imputed = fe.impute_missing_values(data_with_missing, strategy='knn')
    print(f"Imputed: {np.isnan(data_with_missing).sum()} -> {np.isnan(imputed).sum()} missing values")
