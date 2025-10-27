"""
Advanced Hybrid Recommendation System
Combines Content-Based and Collaborative Filtering with Adaptive Fusion
Implements Reinforcement Learning for dynamic weight adjustment
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
import pickle
import os
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdaptiveHybridRecommender:
    """
    Hybrid Recommender with Adaptive Weighting
    - Combines content-based and collaborative filtering
    - Uses reinforcement learning for weight adaptation
    - Implements contextual bandits for personalization
    """
    
    def __init__(self):
        self.content_based_model = None
        self.collaborative_model = None
        
        # Adaptive weights (initialized to equal)
        self.global_weights = {
            'content': 0.5,
            'collaborative': 0.5
        }
        
        # User-specific weights (personalized)
        self.user_weights = defaultdict(lambda: {'content': 0.5, 'collaborative': 0.5})
        
        # Reinforcement learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.1  # Epsilon for epsilon-greedy
        self.discount_factor = 0.9
        
        # Performance tracking
        self.user_feedback_history = defaultdict(list)
        self.weight_history = []
        
        # Contextual features for weight adaptation
        self.user_contexts = {}
        
    def set_models(self, content_model, collaborative_model):
        """
        Set the content-based and collaborative filtering models
        
        Args:
            content_model: Content-based filtering model
            collaborative_model: Collaborative filtering model
        """
        self.content_based_model = content_model
        self.collaborative_model = collaborative_model
        logger.info("Models set for hybrid recommender")
    
    def get_hybrid_recommendations(self, user_id: str, n_recommendations: int = 10,
                                   use_adaptive: bool = True,
                                   context: Optional[Dict] = None) -> List[Tuple[int, float]]:
        """
        Get hybrid recommendations with adaptive weighting
        
        Args:
            user_id: User ID
            n_recommendations: Number of recommendations
            use_adaptive: Use adaptive weights or global weights
            context: Optional context information (time, device, mood, etc.)
            
        Returns:
            List of (movie_id, score) tuples
        """
        try:
            # Get recommendations from both models
            content_recs = self._get_content_recommendations(user_id, n_recommendations * 2)
            collab_recs = self._get_collaborative_recommendations(user_id, n_recommendations * 2)
            
            # Get weights
            if use_adaptive and user_id in self.user_weights:
                weights = self.user_weights[user_id]
            else:
                weights = self.global_weights
            
            # Apply context-aware adjustment if context provided
            if context:
                weights = self._adjust_weights_by_context(weights, context)
            
            # Combine recommendations
            combined_scores = {}
            
            # Content-based scores
            for movie_id, score in content_recs:
                combined_scores[movie_id] = score * weights['content']
            
            # Collaborative scores
            for movie_id, score in collab_recs:
                if movie_id in combined_scores:
                    combined_scores[movie_id] += score * weights['collaborative']
                else:
                    combined_scores[movie_id] = score * weights['collaborative']
            
            # Sort by combined score
            recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
            return recommendations[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting hybrid recommendations: {str(e)}")
            return []
    
    def _get_content_recommendations(self, user_id: str, n: int) -> List[Tuple[int, float]]:
        """Get recommendations from content-based model"""
        try:
            if self.content_based_model is None:
                return []
            
            # Get user's liked movies (would come from database in production)
            # For now, return empty list as placeholder
            # In production: query user's highly rated movies
            user_liked_movies = []
            
            if hasattr(self.content_based_model, 'get_recommendations_for_user'):
                return self.content_based_model.get_recommendations_for_user(user_liked_movies, n)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting content recommendations: {str(e)}")
            return []
    
    def _get_collaborative_recommendations(self, user_id: str, n: int) -> List[Tuple[int, float]]:
        """Get recommendations from collaborative filtering model"""
        try:
            if self.collaborative_model is None:
                return []
            
            if hasattr(self.collaborative_model, 'get_hybrid_recommendations'):
                return self.collaborative_model.get_hybrid_recommendations(user_id, n)
            elif hasattr(self.collaborative_model, 'get_user_recommendations'):
                return self.collaborative_model.get_user_recommendations(user_id, n)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {str(e)}")
            return []
    
    def _adjust_weights_by_context(self, weights: Dict[str, float], 
                                   context: Dict) -> Dict[str, float]:
        """
        Adjust weights based on contextual information
        
        Args:
            weights: Current weights
            context: Context dictionary (time_of_day, device, mood, etc.)
            
        Returns:
            Adjusted weights
        """
        try:
            adjusted = weights.copy()
            
            # Time-based adjustment
            if 'time_of_day' in context:
                time = context['time_of_day']
                if time in ['evening', 'night']:
                    # Users might prefer more personalized (collaborative) at night
                    adjusted['collaborative'] *= 1.2
                    adjusted['content'] *= 0.8
            
            # Mood-based adjustment
            if 'mood' in context:
                mood = context['mood']
                if mood in ['adventurous', 'discover']:
                    # Boost content-based for discovery
                    adjusted['content'] *= 1.3
                    adjusted['collaborative'] *= 0.7
                elif mood in ['comfort', 'familiar']:
                    # Boost collaborative for familiar recommendations
                    adjusted['collaborative'] *= 1.3
                    adjusted['content'] *= 0.7
            
            # Device-based adjustment
            if 'device' in context:
                device = context['device']
                if device == 'mobile':
                    # Mobile users might prefer quick, popular picks (collaborative)
                    adjusted['collaborative'] *= 1.1
                    adjusted['content'] *= 0.9
            
            # Normalize weights to sum to 1
            total = sum(adjusted.values())
            adjusted = {k: v/total for k, v in adjusted.items()}
            
            return adjusted
            
        except Exception as e:
            logger.error(f"Error adjusting weights by context: {str(e)}")
            return weights
    
    def update_weights_with_feedback(self, user_id: str, recommended_items: List[int],
                                     feedback: Dict[int, float], method: str = 'rl'):
        """
        Update weights based on user feedback using reinforcement learning
        
        Args:
            user_id: User ID
            recommended_items: List of recommended item IDs
            feedback: Dictionary of {item_id: rating/feedback_score}
            method: Update method ('rl' for reinforcement learning, 'gradient' for gradient descent)
        """
        try:
            if not feedback:
                return
            
            # Calculate reward (average feedback)
            rewards = list(feedback.values())
            avg_reward = np.mean(rewards)
            
            # Normalize reward to [-1, 1]
            normalized_reward = (avg_reward - 3.0) / 2.0  # Assuming 1-5 rating scale
            
            # Store feedback
            self.user_feedback_history[user_id].append({
                'items': recommended_items,
                'feedback': feedback,
                'reward': normalized_reward
            })
            
            if method == 'rl':
                self._update_weights_rl(user_id, normalized_reward)
            elif method == 'gradient':
                self._update_weights_gradient(user_id, normalized_reward)
            
            logger.info(f"Updated weights for user {user_id}: {self.user_weights[user_id]}")
            
        except Exception as e:
            logger.error(f"Error updating weights with feedback: {str(e)}")
    
    def _update_weights_rl(self, user_id: str, reward: float):
        """
        Update weights using reinforcement learning (Q-learning inspired)
        
        Args:
            user_id: User ID
            reward: Normalized reward (-1 to 1)
        """
        try:
            current_weights = self.user_weights[user_id]
            
            # Exploration vs Exploitation (epsilon-greedy)
            if np.random.random() < self.exploration_rate:
                # Explore: Random adjustment
                adjustment = np.random.uniform(-0.1, 0.1)
            else:
                # Exploit: Adjust based on reward
                # If reward is positive, strengthen current weights
                # If reward is negative, shift weights
                adjustment = self.learning_rate * reward
            
            # Update content weight
            new_content_weight = current_weights['content'] + adjustment
            
            # Ensure weights are in valid range [0.1, 0.9]
            new_content_weight = max(0.1, min(0.9, new_content_weight))
            
            # Update weights (they must sum to 1)
            self.user_weights[user_id] = {
                'content': new_content_weight,
                'collaborative': 1.0 - new_content_weight
            }
            
            # Decay exploration rate over time
            self.exploration_rate *= 0.995
            
        except Exception as e:
            logger.error(f"Error in RL weight update: {str(e)}")
    
    def _update_weights_gradient(self, user_id: str, reward: float):
        """
        Update weights using gradient descent
        
        Args:
            user_id: User ID
            reward: Normalized reward
        """
        try:
            current_weights = self.user_weights[user_id]
            
            # Gradient is proportional to reward
            gradient = self.learning_rate * reward
            
            # Update content weight
            new_content_weight = current_weights['content'] + gradient
            
            # Clip to valid range
            new_content_weight = max(0.1, min(0.9, new_content_weight))
            
            # Update weights
            self.user_weights[user_id] = {
                'content': new_content_weight,
                'collaborative': 1.0 - new_content_weight
            }
            
        except Exception as e:
            logger.error(f"Error in gradient weight update: {str(e)}")
    
    def get_explanation(self, user_id: str, movie_id: int) -> str:
        """
        Generate explanation for why a movie was recommended
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            
        Returns:
            Explanation string
        """
        try:
            weights = self.user_weights.get(user_id, self.global_weights)
            
            explanation_parts = []
            
            # Determine dominant factor
            if weights['content'] > weights['collaborative']:
                explanation_parts.append(
                    f"This movie matches your taste based on content similarity "
                    f"({weights['content']*100:.0f}% content-based)"
                )
            elif weights['collaborative'] > weights['content']:
                explanation_parts.append(
                    f"Users with similar preferences enjoyed this movie "
                    f"({weights['collaborative']*100:.0f}% collaborative)"
                )
            else:
                explanation_parts.append(
                    "This movie is recommended based on a balanced mix of "
                    "content similarity and user preferences"
                )
            
            return " ".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "Recommended based on your viewing history"
    
    def get_weight_statistics(self) -> Dict:
        """
        Get statistics about weight distribution
        
        Returns:
            Dictionary with weight statistics
        """
        try:
            if not self.user_weights:
                return {
                    'global_weights': self.global_weights,
                    'num_users': 0
                }
            
            content_weights = [w['content'] for w in self.user_weights.values()]
            collab_weights = [w['collaborative'] for w in self.user_weights.values()]
            
            stats = {
                'global_weights': self.global_weights,
                'num_users': len(self.user_weights),
                'content_weight_stats': {
                    'mean': np.mean(content_weights),
                    'std': np.std(content_weights),
                    'min': np.min(content_weights),
                    'max': np.max(content_weights)
                },
                'collaborative_weight_stats': {
                    'mean': np.mean(collab_weights),
                    'std': np.std(collab_weights),
                    'min': np.min(collab_weights),
                    'max': np.max(collab_weights)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting weight statistics: {str(e)}")
            return {}
    
    def save_model(self, filepath: str):
        """Save hybrid model state"""
        try:
            model_data = {
                'global_weights': self.global_weights,
                'user_weights': dict(self.user_weights),
                'learning_rate': self.learning_rate,
                'exploration_rate': self.exploration_rate,
                'discount_factor': self.discount_factor,
                'user_feedback_history': dict(self.user_feedback_history),
                'weight_history': self.weight_history
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Hybrid model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving hybrid model: {str(e)}")
            return False
    
    def load_model(self, filepath: str):
        """Load hybrid model state"""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Model file {filepath} not found")
                return False
            
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.global_weights = model_data['global_weights']
            self.user_weights = defaultdict(lambda: {'content': 0.5, 'collaborative': 0.5}, 
                                           model_data['user_weights'])
            self.learning_rate = model_data['learning_rate']
            self.exploration_rate = model_data['exploration_rate']
            self.discount_factor = model_data['discount_factor']
            self.user_feedback_history = defaultdict(list, model_data['user_feedback_history'])
            self.weight_history = model_data['weight_history']
            
            logger.info(f"Hybrid model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading hybrid model: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Create hybrid recommender
    hybrid = AdaptiveHybridRecommender()
    
    # Simulate recommendations and feedback
    user_id = "user123"
    
    # Get recommendations (would use actual models in production)
    # recommendations = hybrid.get_hybrid_recommendations(user_id, 10)
    
    # Simulate feedback
    feedback = {1: 5.0, 2: 4.0, 3: 3.0}
    recommended_items = [1, 2, 3, 4, 5]
    
    # Update weights based on feedback
    hybrid.update_weights_with_feedback(user_id, recommended_items, feedback, method='rl')
    
    # Get weight statistics
    stats = hybrid.get_weight_statistics()
    print("Weight Statistics:", stats)
    
    # Get explanation
    explanation = hybrid.get_explanation(user_id, 1)
    print("Explanation:", explanation)
