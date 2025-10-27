"""
Model Persistence Module
Handles saving and loading of trained ML models to/from disk
"""
import pickle
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Model storage directory
MODEL_DIR = Path(__file__).parent.parent / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)

class ModelPersistence:
    """Handles saving and loading of recommendation models"""
    
    @staticmethod
    def save_model(model: Any, model_name: str, metadata: Optional[Dict] = None) -> bool:
        """
        Save a trained model to disk
        
        Args:
            model: The model object to save
            model_name: Name identifier for the model
            metadata: Optional metadata about the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            model_path = MODEL_DIR / f"{model_name}.pkl"
            metadata_path = MODEL_DIR / f"{model_name}_metadata.json"
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Save metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'saved_at': datetime.now().isoformat(),
                'model_name': model_name,
                'file_path': str(model_path)
            })
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model '{model_name}' saved successfully to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model '{model_name}': {str(e)}")
            return False
    
    @staticmethod
    def load_model(model_name: str) -> Optional[Any]:
        """
        Load a trained model from disk
        
        Args:
            model_name: Name identifier for the model
            
        Returns:
            The loaded model object or None if not found
        """
        try:
            model_path = MODEL_DIR / f"{model_name}.pkl"
            
            if not model_path.exists():
                logger.warning(f"Model '{model_name}' not found at {model_path}")
                return None
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            logger.info(f"Model '{model_name}' loaded successfully from {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model '{model_name}': {str(e)}")
            return None
    
    @staticmethod
    def get_model_metadata(model_name: str) -> Optional[Dict]:
        """
        Get metadata for a saved model
        
        Args:
            model_name: Name identifier for the model
            
        Returns:
            Dictionary containing model metadata or None
        """
        try:
            metadata_path = MODEL_DIR / f"{model_name}_metadata.json"
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error loading metadata for '{model_name}': {str(e)}")
            return None
    
    @staticmethod
    def model_exists(model_name: str) -> bool:
        """Check if a model exists on disk"""
        model_path = MODEL_DIR / f"{model_name}.pkl"
        return model_path.exists()
    
    @staticmethod
    def delete_model(model_name: str) -> bool:
        """Delete a saved model and its metadata"""
        try:
            model_path = MODEL_DIR / f"{model_name}.pkl"
            metadata_path = MODEL_DIR / f"{model_name}_metadata.json"
            
            if model_path.exists():
                os.remove(model_path)
            
            if metadata_path.exists():
                os.remove(metadata_path)
            
            logger.info(f"Model '{model_name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting model '{model_name}': {str(e)}")
            return False
    
    @staticmethod
    def list_saved_models() -> list:
        """List all saved models"""
        try:
            models = []
            for file in MODEL_DIR.glob("*.pkl"):
                model_name = file.stem
                metadata = ModelPersistence.get_model_metadata(model_name)
                models.append({
                    'name': model_name,
                    'path': str(file),
                    'metadata': metadata
                })
            return models
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    @staticmethod
    def should_retrain(model_name: str, max_age_hours: int = 24) -> bool:
        """
        Check if a model should be retrained based on age
        
        Args:
            model_name: Name identifier for the model
            max_age_hours: Maximum age in hours before retraining
            
        Returns:
            bool: True if model should be retrained
        """
        try:
            metadata = ModelPersistence.get_model_metadata(model_name)
            
            if metadata is None:
                return True
            
            saved_at = datetime.fromisoformat(metadata.get('saved_at', ''))
            age_hours = (datetime.now() - saved_at).total_seconds() / 3600
            
            return age_hours > max_age_hours
            
        except Exception as e:
            logger.error(f"Error checking model age: {str(e)}")
            return True
