"""
Model manager for handling model restrictions and availability.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
import structlog

from config import MODEL_RESTRICTIONS_FILE

logger = structlog.get_logger()

# Available models with their display names and categories
ALL_MODELS = {
    "claude-sonnet-4-5-20250929": {
        "name": "claude-sonnet-4-5-20250929",
        "category": "Anthropic Claude",
        "display_name": "Claude Sonnet 4.5",
        "requires_key": "ANTHROPIC_API_KEY"
    },
    "claude-opus-4-1-20250805": {
        "name": "claude-opus-4-1-20250805",
        "category": "Anthropic Claude", 
        "display_name": "Claude Opus 4.1",
        "requires_key": "ANTHROPIC_API_KEY"
    },
    "gemini-2.5-pro": {
        "name": "gemini-2.5-pro",
        "category": "Google Gemini",
        "display_name": "Gemini 2.5 Pro",
        "requires_key": "GOOGLE_API_KEY"
    },
    "gemini-2.5-flash": {
        "name": "gemini-2.5-flash",
        "category": "Google Gemini",
        "display_name": "Gemini 2.5 Flash",
        "requires_key": "GOOGLE_API_KEY"
    }
}


class ModelManager:
    """Manages model availability and restrictions."""
    
    @staticmethod
    def load_restrictions() -> Dict:
        """Load model restrictions from file."""
        if MODEL_RESTRICTIONS_FILE.exists():
            try:
                with open(MODEL_RESTRICTIONS_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error("Failed to load model restrictions", error=str(e))
                return {"enabled": False, "allowed_models": []}
        return {"enabled": False, "allowed_models": []}
    
    @staticmethod
    def save_restrictions(restrictions: Dict) -> bool:
        """Save model restrictions to file."""
        try:
            with open(MODEL_RESTRICTIONS_FILE, 'w') as f:
                json.dump(restrictions, f, indent=2)
            logger.info("Model restrictions saved", restrictions=restrictions)
            return True
        except IOError as e:
            logger.error("Failed to save model restrictions", error=str(e))
            return False
    
    @staticmethod
    def get_available_models(user_role: str = "editor", api_keys: Optional[Dict] = None) -> List[Dict]:
        """
        Get available models based on user role and API keys.
        
        Args:
            user_role: The user's role (admin or editor)
            api_keys: Dictionary of available API keys
            
        Returns:
            List of available model configurations
        """
        # Load restrictions
        restrictions = ModelManager.load_restrictions()
        
        # Start with all models
        available_models = []
        
        # Filter by API keys if provided
        for model_id, model_info in ALL_MODELS.items():
            if api_keys:
                required_key = model_info.get("requires_key")
                if required_key and not api_keys.get(required_key):
                    continue  # Skip models without required API key
            
            available_models.append(model_info)
        
        # If user is admin, return all available models
        if user_role == "admin":
            return available_models
        
        # For non-admin users, check if restrictions are enabled
        if restrictions.get("enabled", False) and restrictions.get("allowed_models"):
            # Filter to only allowed models
            allowed_model_ids = restrictions.get("allowed_models", [])
            filtered_models = [
                model for model in available_models 
                if model["name"] in allowed_model_ids
            ]
            
            # If no models match the restrictions, fallback to all available
            # (to prevent locking users out completely)
            if filtered_models:
                return filtered_models
            else:
                logger.warning("No models match restrictions, returning all available")
                return available_models
        
        # No restrictions, return all available models
        return available_models
    
    @staticmethod
    def is_model_allowed(model_id: str, user_role: str = "editor") -> bool:
        """
        Check if a specific model is allowed for a user.
        
        Args:
            model_id: The model identifier
            user_role: The user's role
            
        Returns:
            True if the model is allowed, False otherwise
        """
        if user_role == "admin":
            return True  # Admins can use any model
        
        restrictions = ModelManager.load_restrictions()
        
        # If restrictions are not enabled, all models are allowed
        if not restrictions.get("enabled", False):
            return True
        
        # Check if the model is in the allowed list
        allowed_models = restrictions.get("allowed_models", [])
        
        # If no models are specified, allow all
        if not allowed_models:
            return True
            
        return model_id in allowed_models
    
    @staticmethod
    def update_restrictions(enabled: bool, allowed_models: List[str]) -> bool:
        """
        Update model restrictions.
        
        Args:
            enabled: Whether restrictions are enabled
            allowed_models: List of allowed model IDs
            
        Returns:
            True if successful, False otherwise
        """
        # Validate model IDs
        valid_models = []
        for model_id in allowed_models:
            if model_id in ALL_MODELS:
                valid_models.append(model_id)
            else:
                logger.warning(f"Invalid model ID: {model_id}")
        
        restrictions = {
            "enabled": enabled,
            "allowed_models": valid_models
        }
        
        return ModelManager.save_restrictions(restrictions)
