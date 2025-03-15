import logging
from typing import Tuple, Dict, Any
from datetime import datetime

from .models import Achievement, UserAchievement, ProgressType

logger = logging.getLogger(__name__)

class ProgressTracker:
    """
    Handles tracking of user progress toward achievements
    based on the achievement's progress type.
    """
    
    async def update_progress(
        self, 
        user_achievement: UserAchievement, 
        achievement: Achievement,
        new_value: float
    ) -> Tuple[float, bool]:
        """
        Update the progress for a user achievement.
        
        Args:
            user_achievement: The user's achievement progress
            achievement: The achievement definition
            new_value: The new progress value
            
        Returns:
            Tuple of (updated_value, is_unlocked)
        """
        progress_type = achievement.progress_type
        current_value = user_achievement.current_value
        target_value = achievement.target_value
        
        # Track history
        timestamp = datetime.now()
        user_achievement.progress_history.append({
            "date": timestamp,
            "value": new_value
        })
        
        # Handle different progress types
        if progress_type == ProgressType.BOOLEAN:
            # For boolean progress, any non-zero value completes it
            updated_value = 1.0 if new_value > 0 else 0.0
            
        elif progress_type == ProgressType.COUNTER:
            # For counters, use the new value directly (assuming it's cumulative)
            updated_value = new_value
            
        elif progress_type == ProgressType.PERCENTAGE:
            # For percentages, use the highest achieved value
            updated_value = max(current_value, new_value)
            
        elif progress_type == ProgressType.STREAK:
            if new_value == 0:
                # Reset streak
                updated_value = 0
            else:
                # Increment streak
                updated_value = new_value
        else:
            # Unknown progress type, use new value directly
            logger.warning(f"Unknown progress type: {progress_type}")
            updated_value = new_value
        
        # Update the user achievement
        user_achievement.current_value = updated_value
        
        # Check if achievement is now unlocked
        is_unlocked = updated_value >= target_value
        
        return updated_value, is_unlocked
        
    async def reset_progress(self, user_achievement: UserAchievement) -> None:
        """Reset progress for a user achievement"""
        user_achievement.current_value = 0
        user_achievement.unlocked = False
        
        # Add a reset event to history
        timestamp = datetime.now()
        user_achievement.progress_history.append({
            "date": timestamp,
            "value": 0,
            "event": "reset"
        })
