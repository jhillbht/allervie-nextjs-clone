from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import json
import os
from pathlib import Path
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .models import Achievement, UserAchievement, AchievementCategory, AchievementTier
from .criteria import CriteriaRegistry, register_default_criteria
from .progress import ProgressTracker
from .rewards import RewardRegistry, register_default_reward_handlers

logger = logging.getLogger(__name__)

class AchievementEngine:
    def __init__(self, notification_manager=None):
        self.achievements: Dict[str, Achievement] = {}
        self.progress_tracker = ProgressTracker()
        self.notification_manager = notification_manager
        self.data_dir = Path(os.getenv('DATA_DIR', '.')) / 'achievements'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize scheduler for periodic checks
        self.scheduler = AsyncIOScheduler()
        
        # Load achievements
        self._load_achievements()
        
        # Register criteria and reward handlers
        register_default_criteria()
        register_default_reward_handlers()
        
        logger.info("Initialized AchievementEngine")
    
    async def start(self):
        """Start the achievement engine"""
        # Schedule periodic update (daily at midnight)
        self.scheduler.add_job(
            self._periodic_update,
            'cron',
            hour=0,
            minute=0,
            id='achievement_periodic_update'
        )
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Started AchievementEngine scheduler")
    
    async def stop(self):
        """Stop the achievement engine"""
        self.scheduler.shutdown()
        logger.info("Stopped AchievementEngine scheduler")
    
    async def register_achievement(self, achievement: Achievement) -> bool:
        """Register a new achievement"""
        try:
            # Validate criteria exists
            if not CriteriaRegistry.get(achievement.criteria_id):
                logger.error(f"Cannot register achievement: criteria not found: {achievement.criteria_id}")
                return False
            
            # Store achievement
            self.achievements[achievement.id] = achievement
            
            # Save to disk
            self._save_achievements()
            
            logger.info(f"Registered achievement: {achievement.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering achievement: {str(e)}")
            return False
    
    async def process_event(
        self, 
        user_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Process an event that might trigger achievement progress
        Returns a list of achievements that were unlocked by this event
        """
        try:
            # Prepare context from event data
            context = event_data.copy()
            context['event_type'] = event_type
            
            # Track unlocked achievements
            unlocked_achievements = []
            
            # Evaluate all achievements
            for achievement in self.achievements.values():
                # Skip hidden achievements for certain event types
                if achievement.hidden and event_type not in ['system_check', 'periodic_update']:
                    continue
                
                # Update progress
                user_achievement = await self.progress_tracker.update_progress(
                    user_id=user_id,
                    achievement=achievement,
                    context=context
                )
                
                if user_achievement and user_achievement.unlocked:
                    # Check if this was just unlocked (no first_achieved_at previously)
                    just_unlocked = (
                        user_achievement.first_achieved_at and 
                        (datetime.now() - user_achievement.first_achieved_at).total_seconds() < 60
                    )
                    
                    if just_unlocked:
                        # Process rewards
                        await RewardRegistry.process_rewards(
                            user_id=user_id,
                            achievement=achievement,
                            user_achievement=user_achievement
                        )
                        
                        # Send notification if available
                        if self.notification_manager:
                            await self.notification_manager.send_achievement_notification(
                                achievement_name=achievement.name,
                                description=achievement.description
                            )
                        
                        # Add to unlocked list
                        unlocked_achievements.append({
                            "id": achievement.id,
                            "name": achievement.name,
                            "description": achievement.description,
                            "tier": achievement.tier,
                            "category": achievement.category,
                            "icon": achievement.icon
                        })
            
            # Save achievements
            self._save_achievements()
            
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            return []
    
    async def get_achievements(
        self, 
        category: Optional[AchievementCategory] = None,
        tier: Optional[AchievementTier] = None,
        include_hidden: bool = False
    ) -> List[Achievement]:
        """Get all registered achievements, optionally filtered"""
        try:
            achievements = list(self.achievements.values())
            
            # Filter by category
            if category:
                achievements = [a for a in achievements if a.category == category]
            
            # Filter by tier
            if tier:
                achievements = [a for a in achievements if a.tier == tier]
            
            # Filter hidden
            if not include_hidden:
                achievements = [a for a in achievements if not a.hidden]
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error getting achievements: {str(e)}")
            return []
    
    async def get_user_achievement_summary(
        self, 
        user_id: str,
        include_hidden: bool = False
    ) -> Dict[str, Any]:
        """Get a summary of a user's achievements"""
        try:
            # Get user achievements
            user_achievements = await self.progress_tracker.get_user_achievements(
                user_id=user_id,
                include_hidden=include_hidden
            )
            
            # Count by category and tier
            total_achievements = len(self.achievements)
            unlocked_count = sum(1 for ua in user_achievements if ua.get('progress', {}).get('unlocked', False))
            
            # Get points (if using PointsRewardHandler)
            points_handler = RewardRegistry.get('points')
            total_points = 0
            if points_handler:
                total_points = await points_handler.get_user_points(user_id)
            
            # Get badges (if using BadgeRewardHandler)
            badge_handler = RewardRegistry.get('badge')
            badges = []
            if badge_handler:
                badges = await badge_handler.get_user_badges(user_id)
            
            # Build summary
            return {
                "user_id": user_id,
                "total_achievements": total_achievements,
                "unlocked_achievements": unlocked_count,
                "completion_percentage": (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0,
                "total_points": total_points,
                "badges": badges,
                "recent_unlocks": [
                    {
                        "id": ua.get('achievement', {}).get('id'),
                        "name": ua.get('achievement', {}).get('name'),
                        "unlocked_at": ua.get('progress', {}).get('first_achieved_at')
                    }
                    for ua in user_achievements
                    if ua.get('progress', {}).get('unlocked', False) and ua.get('progress', {}).get('first_achieved_at')
                ][:5]  # Last 5 unlocked
            }
            
        except Exception as e:
            logger.error(f"Error getting user achievement summary: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
    
    async def _periodic_update(self):
        """Perform periodic update of achievements (daily)"""
        try:
            logger.info("Running periodic achievement update")
            
            # Get all users with achievement data
            users = self.progress_tracker.user_achievements.keys()
            
            # Process system check event for each user
            for user_id in users:
                # Create context with daily flags
                context = {
                    "periodic_update": True,
                    "current_period": datetime.now().strftime("%Y-%m"),
                    "last_checked_period": (datetime.now().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
                }
                
                await self.process_event(
                    user_id=user_id,
                    event_type="periodic_update",
                    event_data=context
                )
            
            logger.info("Completed periodic achievement update")
            
        except Exception as e:
            logger.error(f"Error in periodic achievement update: {str(e)}")
    
    def _save_achievements(self):
        """Save achievements to disk"""
        try:
            # Create serializable structure
            data = {
                ach_id: ach.dict() for ach_id, ach in self.achievements.items()
            }
            
            # Save to file
            file_path = self.data_dir / 'achievements.json'
            with open(file_path, 'w') as f:
                json.dump(data, f, default=str)
            
            logger.debug("Saved achievements")
            
        except Exception as e:
            logger.error(f"Error saving achievements: {str(e)}")
    
    def _load_achievements(self):
        """Load achievements from disk"""
        try:
            file_path = self.data_dir / 'achievements.json'
            if not file_path.exists():
                self._create_default_achievements()
                return
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert to Achievement objects
            for ach_id, ach_data in data.items():
                try:
                    self.achievements[ach_id] = Achievement(**ach_data)
                except Exception as e:
                    logger.error(f"Error parsing achievement data: {str(e)}")
            
            logger.info(f"Loaded {len(self.achievements)} achievements")
            
        except Exception as e:
            logger.error(f"Error loading achievements: {str(e)}")
            self._create_default_achievements()
    
    def _create_default_achievements(self):
        """Create default achievements"""
        try:
            # Budget achievements
            self.achievements["budget_master_bronze"] = Achievement(
                id="budget_master_bronze",
                name="Budget Novice",
                description="Stay under budget in all categories for 1 month",
                category=AchievementCategory.BUDGET,
                tier=AchievementTier.BRONZE,
                icon="budget_bronze.png",
                criteria_id="budget_streak_1",
                progress_type="streak",
                target_value=1,
                rewards=[
                    {"type": "badge", "value": "budget_novice"},
                    {"type": "points", "value": 100}
                ]
            )
            
            self.achievements["budget_master_silver"] = Achievement(
                id="budget_master_silver",
                name="Budget Apprentice",
                description="Stay under budget in all categories for 3 consecutive months",
                category=AchievementCategory.BUDGET,
                tier=AchievementTier.SILVER,
                icon="budget_silver.png",
                criteria_id="budget_streak_3",
                progress_type="streak",
                target_value=3,
                rewards=[
                    {"type": "badge", "value": "budget_apprentice"},
                    {"type": "points", "value": 250}
                ]
            )
            
            self.achievements["budget_master_gold"] = Achievement(
                id="budget_master_gold",
                name="Budget Master",
                description="Stay under budget in all categories for 6 consecutive months",
                category=AchievementCategory.BUDGET,
                tier=AchievementTier.GOLD,
                icon="budget_gold.png",
                criteria_id="budget_streak_6",
                progress_type="streak",
                target_value=6,
                rewards=[
                    {"type": "badge", "value": "budget_master"},
                    {"type": "points", "value": 500},
                    {"type": "feature", "value": "advanced_reporting"}
                ]
            )
            
            # Savings achievements
            self.achievements["savings_bronze"] = Achievement(
                id="savings_bronze",
                name="Savings Starter",
                description="Save your first $1,000",
                category=AchievementCategory.SAVING,
                tier=AchievementTier.BRONZE,
                icon="savings_bronze.png",
                criteria_id="savings_goal_1000",
                progress_type="percentage",
                target_value=100,
                rewards=[
                    {"type": "badge", "value": "saver_starter"},
                    {"type": "points", "value": 150}
                ]
            )
            
            self.achievements["savings_silver"] = Achievement(
                id="savings_silver",
                name="Savings Builder",
                description="Save $5,000",
                category=AchievementCategory.SAVING,
                tier=AchievementTier.SILVER,
                icon="savings_silver.png",
                criteria_id="savings_goal_5000",
                progress_type="percentage",
                target_value=100,
                rewards=[
                    {"type": "badge", "value": "saver_builder"},
                    {"type": "points", "value": 300}
                ]
            )
            
            self.achievements["savings_gold"] = Achievement(
                id="savings_gold",
                name="Savings Expert",
                description="Save $10,000",
                category=AchievementCategory.SAVING,
                tier=AchievementTier.GOLD,
                icon="savings_gold.png",
                criteria_id="savings_goal_10000",
                progress_type="percentage",
                target_value=100,
                rewards=[
                    {"type": "badge", "value": "saver_expert"},
                    {"type": "points", "value": 600},
                    {"type": "feature", "value": "investment_tracking"}
                ]
            )
            
            # Milestone achievements
            self.achievements["transaction_bronze"] = Achievement(
                id="transaction_bronze",
                name="Transaction Tracker",
                description="Track 10 transactions",
                category=AchievementCategory.MILESTONE,
                tier=AchievementTier.BRONZE,
                icon="transaction_bronze.png",
                criteria_id="transaction_count_10",
                progress_type="counter",
                target_value=10,
                rewards=[
                    {"type": "badge", "value": "transaction_tracker"},
                    {"type": "points", "value": 50}
                ]
            )
            
            self.achievements["transaction_silver"] = Achievement(
                id="transaction_silver",
                name="Transaction Manager",
                description="Track 100 transactions",
                category=AchievementCategory.MILESTONE,
                tier=AchievementTier.SILVER,
                icon="transaction_silver.png",
                criteria_id="transaction_count_100",
                progress_type="counter",
                target_value=100,
                rewards=[
                    {"type": "badge", "value": "transaction_manager"},
                    {"type": "points", "value": 200}
                ]
            )
            
            self.achievements["transaction_gold"] = Achievement(
                id="transaction_gold",
                name="Transaction Master",
                description="Track 1,000 transactions",
                category=AchievementCategory.MILESTONE,
                tier=AchievementTier.GOLD,
                icon="transaction_gold.png",
                criteria_id="transaction_count_1000",
                progress_type="counter",
                target_value=1000,
                rewards=[
                    {"type": "badge", "value": "transaction_master"},
                    {"type": "points", "value": 500},
                    {"type": "feature", "value": "spending_insights"}
                ]
            )
            
            # Save default achievements
            self._save_achievements()
            
            logger.info(f"Created {len(self.achievements)} default achievements")
            
        except Exception as e:
            logger.error(f"Error creating default achievements: {str(e)}")
