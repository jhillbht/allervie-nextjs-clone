from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
import logging
from abc import ABC, abstractmethod

from .models import Achievement, UserAchievement

logger = logging.getLogger(__name__)

class RewardHandler(ABC):
    """Base class for achievement reward handlers"""
    @abstractmethod
    async def process_reward(
        self, 
        user_id: str, 
        achievement: Achievement, 
        user_achievement: UserAchievement,
        reward_data: Dict[str, Any]
    ) -> bool:
        """Process a reward for a user who unlocked an achievement"""
        pass


class PointsRewardHandler(RewardHandler):
    """Handler for point-based rewards"""
    def __init__(self):
        self.user_points: Dict[str, int] = {}
    
    async def process_reward(
        self, 
        user_id: str, 
        achievement: Achievement, 
        user_achievement: UserAchievement,
        reward_data: Dict[str, Any]
    ) -> bool:
        try:
            # Extract points from reward data
            points = int(reward_data.get('value', 0))
            if points <= 0:
                logger.warning(f"Invalid points value in reward: {points}")
                return False
            
            # Add points to user's total
            if user_id not in self.user_points:
                self.user_points[user_id] = 0
            
            self.user_points[user_id] += points
            logger.info(f"Awarded {points} points to user {user_id} for achievement {achievement.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing points reward: {str(e)}")
            return False
    
    async def get_user_points(self, user_id: str) -> int:
        """Get total points for a user"""
        return self.user_points.get(user_id, 0)


class BadgeRewardHandler(RewardHandler):
    """Handler for badge rewards"""
    def __init__(self):
        self.user_badges: Dict[str, List[str]] = {}
    
    async def process_reward(
        self, 
        user_id: str, 
        achievement: Achievement, 
        user_achievement: UserAchievement,
        reward_data: Dict[str, Any]
    ) -> bool:
        try:
            # Extract badge ID from reward data
            badge_id = reward_data.get('value')
            if not badge_id:
                logger.warning(f"Invalid badge ID in reward: {badge_id}")
                return False
            
            # Add badge to user's collection
            if user_id not in self.user_badges:
                self.user_badges[user_id] = []
            
            if badge_id not in self.user_badges[user_id]:
                self.user_badges[user_id].append(badge_id)
            
            logger.info(f"Awarded badge {badge_id} to user {user_id} for achievement {achievement.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing badge reward: {str(e)}")
            return False
    
    async def get_user_badges(self, user_id: str) -> List[str]:
        """Get all badges for a user"""
        return self.user_badges.get(user_id, [])


class FeatureUnlockRewardHandler(RewardHandler):
    """Handler for feature unlock rewards"""
    def __init__(self):
        self.user_features: Dict[str, List[str]] = {}
    
    async def process_reward(
        self, 
        user_id: str, 
        achievement: Achievement, 
        user_achievement: UserAchievement,
        reward_data: Dict[str, Any]
    ) -> bool:
        try:
            # Extract feature ID from reward data
            feature_id = reward_data.get('value')
            if not feature_id:
                logger.warning(f"Invalid feature ID in reward: {feature_id}")
                return False
            
            # Add feature to user's unlocked features
            if user_id not in self.user_features:
                self.user_features[user_id] = []
            
            if feature_id not in self.user_features[user_id]:
                self.user_features[user_id].append(feature_id)
            
            logger.info(f"Unlocked feature {feature_id} for user {user_id} via achievement {achievement.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing feature unlock reward: {str(e)}")
            return False
    
    async def has_feature_access(self, user_id: str, feature_id: str) -> bool:
        """Check if a user has access to a specific feature"""
        return user_id in self.user_features and feature_id in self.user_features[user_id]


class RewardRegistry:
    """Registry for reward handlers"""
    _handlers: Dict[str, RewardHandler] = {}
    
    @classmethod
    def register(cls, reward_type: str, handler: RewardHandler) -> None:
        """Register a reward handler for a specific type"""
        cls._handlers[reward_type] = handler
        logger.info(f"Registered reward handler for type: {reward_type}")
    
    @classmethod
    def get(cls, reward_type: str) -> Optional[RewardHandler]:
        """Get a reward handler by type"""
        return cls._handlers.get(reward_type)
    
    @classmethod
    async def process_rewards(
        cls, 
        user_id: str, 
        achievement: Achievement, 
        user_achievement: UserAchievement
    ) -> Dict[str, bool]:
        """
        Process all rewards for an achievement
        Returns a dict of reward type -> success status
        """
        results = {}
        
        for reward in achievement.rewards:
            reward_type = reward.get('type')
            if not reward_type:
                logger.warning(f"Reward missing type: {reward}")
                continue
            
            handler = cls.get(reward_type)
            if not handler:
                logger.warning(f"No handler registered for reward type: {reward_type}")
                results[reward_type] = False
                continue
            
            success = await handler.process_reward(
                user_id=user_id,
                achievement=achievement,
                user_achievement=user_achievement,
                reward_data=reward
            )
            
            results[reward_type] = success
        
        return results


# Register default reward handlers
def register_default_reward_handlers():
    """Register default reward handlers"""
    RewardRegistry.register('points', PointsRewardHandler())
    RewardRegistry.register('badge', BadgeRewardHandler())
    RewardRegistry.register('feature', FeatureUnlockRewardHandler())
    
    logger.info("Registered default reward handlers")
