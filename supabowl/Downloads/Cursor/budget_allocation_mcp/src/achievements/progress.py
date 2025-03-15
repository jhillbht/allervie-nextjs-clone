from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import json
import os
from pathlib import Path

from .models import UserAchievement, Achievement
from .criteria import CriteriaRegistry

logger = logging.getLogger(__name__)

class ProgressTracker:
    def __init__(self):
        self.user_achievements: Dict[str, Dict[str, UserAchievement]] = {}
        self.data_dir = Path(os.getenv('DATA_DIR', '.')) / 'achievements'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_progress()
        logger.info("Initialized ProgressTracker")
    
    async def update_progress(
        self, 
        user_id: str, 
        achievement: Achievement, 
        context: Dict[str, Any]
    ) -> Optional[UserAchievement]:
        """
        Update progress for a specific achievement and user
        Returns updated UserAchievement if found, None otherwise
        """
        try:
            # Get or create user achievement record
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = {}
            
            user_achievement = self.user_achievements[user_id].get(achievement.id)
            if not user_achievement:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                self.user_achievements[user_id][achievement.id] = user_achievement
            
            # Skip if already unlocked for non-repeatable achievements
            if user_achievement.unlocked and achievement.unlocked_count >= 1:
                return user_achievement
            
            # Get criteria
            criteria = CriteriaRegistry.get(achievement.criteria_id)
            if not criteria:
                logger.error(f"Criteria not found: {achievement.criteria_id}")
                return None
            
            # Evaluate criteria
            current_value = await criteria.evaluate(user_id, context)
            
            # Update progress history
            user_achievement.progress_history.append({
                "date": datetime.now(),
                "value": current_value
            })
            
            # Update current value
            user_achievement.current_value = current_value
            
            # Check if achievement unlocked
            target_reached = current_value >= achievement.target_value
            if target_reached and not user_achievement.unlocked:
                user_achievement.unlocked = True
                user_achievement.first_achieved_at = datetime.now()
                achievement.unlocked_count += 1
                logger.info(f"Achievement unlocked: {achievement.name} for user {user_id}")
            
            # Save progress
            self._save_progress()
            
            return user_achievement
            
        except Exception as e:
            logger.error(f"Error updating achievement progress: {str(e)}")
            return None
    
    async def get_user_achievements(
        self, 
        user_id: str, 
        include_hidden: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all achievements for a user with current progress
        Returns a list of dicts with achievement and progress info
        """
        try:
            if user_id not in self.user_achievements:
                return []
            
            result = []
            for ach_id, user_ach in self.user_achievements[user_id].items():
                # Get achievement definition from AchievementEngine (to be implemented)
                # For now, this is a placeholder
                ach_def = {"id": ach_id, "name": "Achievement", "hidden": False}
                
                # Skip hidden achievements unless explicitly requested
                if ach_def.get("hidden", False) and not include_hidden:
                    continue
                
                result.append({
                    "achievement": ach_def,
                    "progress": {
                        "current_value": user_ach.current_value,
                        "unlocked": user_ach.unlocked,
                        "first_achieved_at": user_ach.first_achieved_at.isoformat() 
                            if user_ach.first_achieved_at else None
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {str(e)}")
            return []
    
    async def reset_achievement_progress(
        self, 
        user_id: str, 
        achievement_id: Optional[str] = None
    ) -> bool:
        """
        Reset achievement progress for a user
        If achievement_id is provided, only reset that achievement
        """
        try:
            if user_id not in self.user_achievements:
                return False
            
            if achievement_id:
                # Reset specific achievement
                if achievement_id in self.user_achievements[user_id]:
                    user_ach = self.user_achievements[user_id][achievement_id]
                    user_ach.current_value = 0
                    user_ach.unlocked = False
                    user_ach.first_achieved_at = None
                    user_ach.progress_history = []
            else:
                # Reset all achievements
                for ach_id in self.user_achievements[user_id]:
                    user_ach = self.user_achievements[user_id][ach_id]
                    user_ach.current_value = 0
                    user_ach.unlocked = False
                    user_ach.first_achieved_at = None
                    user_ach.progress_history = []
            
            # Save progress
            self._save_progress()
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting achievement progress: {str(e)}")
            return False
    
    def _save_progress(self) -> None:
        """Save progress data to disk"""
        try:
            # Create serializable structure
            data = {}
            for user_id, achievements in self.user_achievements.items():
                data[user_id] = {
                    ach_id: ach.dict() for ach_id, ach in achievements.items()
                }
            
            # Save to file
            file_path = self.data_dir / 'progress.json'
            with open(file_path, 'w') as f:
                json.dump(data, f, default=str)
            
            logger.debug("Saved achievement progress")
            
        except Exception as e:
            logger.error(f"Error saving achievement progress: {str(e)}")
    
    def _load_progress(self) -> None:
        """Load progress data from disk"""
        try:
            file_path = self.data_dir / 'progress.json'
            if not file_path.exists():
                logger.info("No achievement progress data found, starting fresh")
                return
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert to UserAchievement objects
            for user_id, achievements in data.items():
                self.user_achievements[user_id] = {}
                for ach_id, ach_data in achievements.items():
                    try:
                        # Fix datetime strings
                        if ach_data.get('first_achieved_at'):
                            ach_data['first_achieved_at'] = datetime.fromisoformat(
                                ach_data['first_achieved_at'].replace('Z', '+00:00')
                            )
                        
                        for entry in ach_data.get('progress_history', []):
                            if 'date' in entry:
                                entry['date'] = datetime.fromisoformat(
                                    entry['date'].replace('Z', '+00:00')
                                )
                        
                        self.user_achievements[user_id][ach_id] = UserAchievement(**ach_data)
                    except Exception as e:
                        logger.error(f"Error parsing achievement data: {str(e)}")
            
            logger.info("Loaded achievement progress data")
            
        except Exception as e:
            logger.error(f"Error loading achievement progress: {str(e)}")
