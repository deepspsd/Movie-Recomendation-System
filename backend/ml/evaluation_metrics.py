"""
Comprehensive Evaluation Metrics for Recommendation Systems
Implements Precision, Recall, F1, NDCG, MAP, and K-Fold Cross-Validation
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import List, Dict, Tuple, Optional, Callable
import logging
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationEvaluator:
    """
    Comprehensive evaluation metrics for recommendation systems
    """
    
    def __init__(self):
        self.metrics_history = []
        
    def precision_at_k(self, recommended: List[int], relevant: List[int], k: int = 10) -> float:
        """
        Precision@K: Proportion of recommended items that are relevant
        
        Args:
            recommended: List of recommended item IDs (ordered by score)
            relevant: List of relevant/liked item IDs
            k: Number of top recommendations to consider
            
        Returns:
            Precision score (0-1)
        """
        try:
            if not recommended or not relevant:
                return 0.0
            
            # Take top K recommendations
            top_k = recommended[:k]
            
            # Count relevant items in top K
            relevant_set = set(relevant)
            hits = sum(1 for item in top_k if item in relevant_set)
            
            precision = hits / min(k, len(top_k))
            return precision
            
        except Exception as e:
            logger.error(f"Error calculating precision@k: {str(e)}")
            return 0.0
    
    def recall_at_k(self, recommended: List[int], relevant: List[int], k: int = 10) -> float:
        """
        Recall@K: Proportion of relevant items that are recommended
        
        Args:
            recommended: List of recommended item IDs (ordered by score)
            relevant: List of relevant/liked item IDs
            k: Number of top recommendations to consider
            
        Returns:
            Recall score (0-1)
        """
        try:
            if not recommended or not relevant:
                return 0.0
            
            # Take top K recommendations
            top_k = recommended[:k]
            
            # Count relevant items in top K
            relevant_set = set(relevant)
            hits = sum(1 for item in top_k if item in relevant_set)
            
            recall = hits / len(relevant_set)
            return recall
            
        except Exception as e:
            logger.error(f"Error calculating recall@k: {str(e)}")
            return 0.0
    
    def f1_score_at_k(self, recommended: List[int], relevant: List[int], k: int = 10) -> float:
        """
        F1 Score@K: Harmonic mean of precision and recall
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            F1 score (0-1)
        """
        try:
            precision = self.precision_at_k(recommended, relevant, k)
            recall = self.recall_at_k(recommended, relevant, k)
            
            if precision + recall == 0:
                return 0.0
            
            f1 = 2 * (precision * recall) / (precision + recall)
            return f1
            
        except Exception as e:
            logger.error(f"Error calculating F1@k: {str(e)}")
            return 0.0
    
    def ndcg_at_k(self, recommended: List[int], relevant: Dict[int, float], k: int = 10) -> float:
        """
        NDCG@K: Normalized Discounted Cumulative Gain
        Measures ranking quality with position discount
        
        Args:
            recommended: List of recommended item IDs (ordered by score)
            relevant: Dictionary of {item_id: relevance_score}
            k: Number of top recommendations to consider
            
        Returns:
            NDCG score (0-1)
        """
        try:
            if not recommended or not relevant:
                return 0.0
            
            # Take top K recommendations
            top_k = recommended[:k]
            
            # Calculate DCG (Discounted Cumulative Gain)
            dcg = 0.0
            for i, item_id in enumerate(top_k):
                relevance = relevant.get(item_id, 0.0)
                # Discount by position (log2(i+2) because i starts at 0)
                dcg += relevance / np.log2(i + 2)
            
            # Calculate IDCG (Ideal DCG)
            # Sort relevant items by relevance score
            ideal_relevances = sorted(relevant.values(), reverse=True)[:k]
            idcg = 0.0
            for i, relevance in enumerate(ideal_relevances):
                idcg += relevance / np.log2(i + 2)
            
            # Normalize
            if idcg == 0:
                return 0.0
            
            ndcg = dcg / idcg
            return ndcg
            
        except Exception as e:
            logger.error(f"Error calculating NDCG@k: {str(e)}")
            return 0.0
    
    def map_at_k(self, recommended: List[int], relevant: List[int], k: int = 10) -> float:
        """
        MAP@K: Mean Average Precision
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            MAP score (0-1)
        """
        try:
            if not recommended or not relevant:
                return 0.0
            
            top_k = recommended[:k]
            relevant_set = set(relevant)
            
            # Calculate average precision
            hits = 0
            sum_precisions = 0.0
            
            for i, item_id in enumerate(top_k):
                if item_id in relevant_set:
                    hits += 1
                    precision_at_i = hits / (i + 1)
                    sum_precisions += precision_at_i
            
            if hits == 0:
                return 0.0
            
            avg_precision = sum_precisions / min(len(relevant_set), k)
            return avg_precision
            
        except Exception as e:
            logger.error(f"Error calculating MAP@k: {str(e)}")
            return 0.0
    
    def hit_rate_at_k(self, recommended: List[int], relevant: List[int], k: int = 10) -> float:
        """
        Hit Rate@K: Whether at least one relevant item is in top K
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            Hit rate (0 or 1)
        """
        try:
            if not recommended or not relevant:
                return 0.0
            
            top_k = set(recommended[:k])
            relevant_set = set(relevant)
            
            # Check if there's any overlap
            hit = 1.0 if len(top_k & relevant_set) > 0 else 0.0
            return hit
            
        except Exception as e:
            logger.error(f"Error calculating hit rate@k: {str(e)}")
            return 0.0
    
    def mrr(self, recommended: List[int], relevant: List[int]) -> float:
        """
        MRR: Mean Reciprocal Rank
        Reciprocal of the rank of the first relevant item
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            
        Returns:
            MRR score
        """
        try:
            if not recommended or not relevant:
                return 0.0
            
            relevant_set = set(relevant)
            
            for i, item_id in enumerate(recommended):
                if item_id in relevant_set:
                    return 1.0 / (i + 1)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating MRR: {str(e)}")
            return 0.0
    
    def coverage(self, all_recommendations: List[List[int]], total_items: int) -> float:
        """
        Catalog Coverage: Percentage of items that are recommended
        
        Args:
            all_recommendations: List of recommendation lists for all users
            total_items: Total number of items in catalog
            
        Returns:
            Coverage score (0-1)
        """
        try:
            if not all_recommendations or total_items == 0:
                return 0.0
            
            # Get unique recommended items
            recommended_items = set()
            for recs in all_recommendations:
                recommended_items.update(recs)
            
            coverage = len(recommended_items) / total_items
            return coverage
            
        except Exception as e:
            logger.error(f"Error calculating coverage: {str(e)}")
            return 0.0
    
    def diversity(self, recommendations: List[int], similarity_matrix: np.ndarray, 
                  item_to_idx: Dict[int, int]) -> float:
        """
        Diversity: Average dissimilarity between recommended items
        
        Args:
            recommendations: List of recommended item IDs
            similarity_matrix: Item-item similarity matrix
            item_to_idx: Mapping from item ID to matrix index
            
        Returns:
            Diversity score (0-1)
        """
        try:
            if len(recommendations) < 2:
                return 0.0
            
            # Get indices
            indices = [item_to_idx[item_id] for item_id in recommendations if item_id in item_to_idx]
            
            if len(indices) < 2:
                return 0.0
            
            # Calculate average dissimilarity
            total_dissimilarity = 0.0
            count = 0
            
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    similarity = similarity_matrix[indices[i], indices[j]]
                    dissimilarity = 1 - similarity
                    total_dissimilarity += dissimilarity
                    count += 1
            
            diversity = total_dissimilarity / count if count > 0 else 0.0
            return diversity
            
        except Exception as e:
            logger.error(f"Error calculating diversity: {str(e)}")
            return 0.0
    
    def novelty(self, recommendations: List[int], item_popularity: Dict[int, float]) -> float:
        """
        Novelty: Average unexpectedness of recommendations
        
        Args:
            recommendations: List of recommended item IDs
            item_popularity: Dictionary of {item_id: popularity_score}
            
        Returns:
            Novelty score
        """
        try:
            if not recommendations:
                return 0.0
            
            # Calculate average negative log popularity
            novelty_scores = []
            for item_id in recommendations:
                popularity = item_popularity.get(item_id, 0.01)
                # Avoid log(0)
                popularity = max(0.0001, min(1.0, popularity))
                novelty_scores.append(-np.log2(popularity))
            
            avg_novelty = np.mean(novelty_scores)
            return avg_novelty
            
        except Exception as e:
            logger.error(f"Error calculating novelty: {str(e)}")
            return 0.0
    
    def evaluate_recommendations(self, recommended: List[int], relevant: List[int], 
                                 relevant_scores: Optional[Dict[int, float]] = None,
                                 k_values: List[int] = [5, 10, 20]) -> Dict[str, float]:
        """
        Comprehensive evaluation of recommendations
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            relevant_scores: Optional dictionary of relevance scores
            k_values: List of K values to evaluate
            
        Returns:
            Dictionary of metric scores
        """
        try:
            metrics = {}
            
            for k in k_values:
                metrics[f'precision@{k}'] = self.precision_at_k(recommended, relevant, k)
                metrics[f'recall@{k}'] = self.recall_at_k(recommended, relevant, k)
                metrics[f'f1@{k}'] = self.f1_score_at_k(recommended, relevant, k)
                metrics[f'hit_rate@{k}'] = self.hit_rate_at_k(recommended, relevant, k)
                metrics[f'map@{k}'] = self.map_at_k(recommended, relevant, k)
                
                if relevant_scores:
                    metrics[f'ndcg@{k}'] = self.ndcg_at_k(recommended, relevant_scores, k)
            
            metrics['mrr'] = self.mrr(recommended, relevant)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating recommendations: {str(e)}")
            return {}
    
    def k_fold_cross_validation(self, data: pd.DataFrame, model_train_func: Callable,
                                model_predict_func: Callable, n_splits: int = 5,
                                random_state: int = 42) -> Dict[str, List[float]]:
        """
        K-Fold Cross-Validation for recommendation models
        
        Args:
            data: DataFrame with user_id, item_id, rating columns
            model_train_func: Function to train model on training data
            model_predict_func: Function to predict ratings
            n_splits: Number of folds
            random_state: Random seed
            
        Returns:
            Dictionary of metric scores for each fold
        """
        try:
            kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
            
            fold_metrics = {
                'rmse': [],
                'mae': [],
                'precision@10': [],
                'recall@10': [],
                'ndcg@10': []
            }
            
            logger.info(f"Starting {n_splits}-fold cross-validation...")
            
            for fold, (train_idx, test_idx) in enumerate(kf.split(data)):
                logger.info(f"Fold {fold + 1}/{n_splits}")
                
                # Split data
                train_data = data.iloc[train_idx]
                test_data = data.iloc[test_idx]
                
                # Train model
                model = model_train_func(train_data)
                
                # Evaluate
                predictions = []
                actuals = []
                
                for _, row in test_data.iterrows():
                    pred = model_predict_func(model, row['user_id'], row['item_id'])
                    predictions.append(pred)
                    actuals.append(row['rating'])
                
                # Calculate metrics
                predictions = np.array(predictions)
                actuals = np.array(actuals)
                
                rmse = np.sqrt(mean_squared_error(actuals, predictions))
                mae = mean_absolute_error(actuals, predictions)
                
                fold_metrics['rmse'].append(rmse)
                fold_metrics['mae'].append(mae)
                
                logger.info(f"Fold {fold + 1} - RMSE: {rmse:.4f}, MAE: {mae:.4f}")
            
            # Calculate average metrics
            avg_metrics = {
                metric: np.mean(scores) for metric, scores in fold_metrics.items()
            }
            
            logger.info(f"\nCross-Validation Results:")
            logger.info(f"Average RMSE: {avg_metrics['rmse']:.4f} ± {np.std(fold_metrics['rmse']):.4f}")
            logger.info(f"Average MAE: {avg_metrics['mae']:.4f} ± {np.std(fold_metrics['mae']):.4f}")
            
            return fold_metrics
            
        except Exception as e:
            logger.error(f"Error in k-fold cross-validation: {str(e)}")
            return {}
    
    def statistical_significance_test(self, metrics1: List[float], metrics2: List[float],
                                      test: str = 'ttest') -> Dict[str, float]:
        """
        Test statistical significance between two sets of metrics
        
        Args:
            metrics1: First set of metric scores
            metrics2: Second set of metric scores
            test: Statistical test ('ttest', 'wilcoxon')
            
        Returns:
            Dictionary with test statistic and p-value
        """
        try:
            if test == 'ttest':
                statistic, p_value = stats.ttest_rel(metrics1, metrics2)
            elif test == 'wilcoxon':
                statistic, p_value = stats.wilcoxon(metrics1, metrics2)
            else:
                logger.error(f"Unknown test: {test}")
                return {}
            
            result = {
                'statistic': statistic,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
            
            logger.info(f"{test} test: statistic={statistic:.4f}, p-value={p_value:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in statistical significance test: {str(e)}")
            return {}


# Example usage
if __name__ == "__main__":
    evaluator = RecommendationEvaluator()
    
    # Example recommendations and ground truth
    recommended = [1, 3, 5, 7, 9, 2, 4, 6, 8, 10]
    relevant = [1, 2, 5, 8, 12, 15]
    relevant_scores = {1: 5.0, 2: 4.5, 5: 4.0, 8: 3.5, 12: 3.0, 15: 4.5}
    
    # Evaluate
    metrics = evaluator.evaluate_recommendations(recommended, relevant, relevant_scores)
    
    print("Evaluation Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
