import logging
from typing import Dict, Callable, Any, Awaitable

from .models import Achievement

logger = logging.getLogger(__name__)

# Type definition for reward handler functions
RewardHandlerFunc = Callable[[str, Achievement, Dict[str, Any]], Awaitable[None]]

class RewardRegistry:
    """
    Registry for achievement reward handler functions.
    Each handler takes (user_id, achievement, reward_data) and processes the reward.
    """
    
    def __init__(self):
        self._handlers: Dict[str, RewardHandlerFunc] = {}
        
    def register(self, reward_type: str, handler: RewardHandlerFunc):
        """Register a reward handler function"""
        self._handlers[reward_type] = handler
        logger.debug(f"Registered reward handler for: {reward_type}")
        
    def get_handler(self, reward_type: str) -> RewardHandlerFunc:
        """Get a reward handler by type"""
        return self._handlers.get(reward_type)
        
    def list_handlers(self):
        """List all registered reward types"""
        return list(self._handlers.keys())


# Default reward handlers

async def handle_badge_reward(user_id: str, achievement: Achievement, reward_data: Dict[str, Any]):
    """Handle awarding a badge to a user"""
    badge_id = reward_data.get("value")
    
    if not badge_id:
        logger.warning(f"Badge reward missing value: {reward_data}")
        return
        
    logger.info(f"Awarding badge {badge_id} to user {user_id} for achievement {achievement.name}")
    
    # In a real implementation, would update user profile with badge
    # For now, just log the award
    
async def handle_points_reward(user_id: str, achievement: Achievement, reward_data: Dict[str, Any]):
    """Handle awarding points to a user"""
    points = reward_data.get("value", 0)
    
    if not points:
        logger.warning(f"Points reward with zero value: {reward_data}")
        return
        
    logger.info(f"Awarding {points} points to user {user_id} for achievement {achievement.name}")
    
    # In a real implementation, would update user points balance
    # For now, just log the award

async def handle_feature_unlock_reward(user_id: str, achievement: Achievement, reward_data: Dict[str, Any]):
    """Handle unlocking a feature for a user"""
    feature_id = reward_data.get("value")
    
    if not feature_id:
        logger.warning(f"Feature unlock reward missing value: {reward_data}")
        return
        
    logger.info(f"Unlocking feature {feature_id} for user {user_id} from achievement {achievement.name}")
    
    # In a real implementation, would update user permissions
    # For now, just log the unlock

async def handle_theme_reward(user_id: str, achievement: Achievement, reward_data: Dict[str, Any]):
    """Handle awarding a theme to a user"""
    theme_id = reward_data.get("value")
    
    if not theme_id:
        logger.warning(f"Theme reward missing value: {reward_data}")
        return
        
    logger.info(f"Awarding theme {theme_id} to user {user_id} for achievement {achievement.name}")
    
    # In a real implementation, would add theme to user's available themes
    # For now, just log the award
    
async def handle_discount_reward(user_id: str, achievement: Achievement, reward_data: Dict[str, Any]):
    """Handle awarding a discount to a user"""
    discount_value = reward_data.get("value")
    discount_code = reward_data.get("code")
    
    if not discount_value or not discount_code:
        logger.warning(f"Discount reward missing value or code: {reward_data}")
        return
        
    logger.info(f"Awarding {discount_value}% discount ({discount_code}) to user {user_id} for achievement {achievement.name}")
    
    # In a real implementation, would generate or assign a discount code
    # For now, just log the award


def register_default_reward_handlers(registry: RewardRegistry):
    """Register all default reward handler functions"""
    registry.register("badge", handle_badge_reward)
    registry.register("points", handle_points_reward)
    registry.register("feature_unlock", handle_feature_unlock_reward)
    registry.register("theme", handle_theme_reward)
    registry.register("discount", handle_discount_reward)
