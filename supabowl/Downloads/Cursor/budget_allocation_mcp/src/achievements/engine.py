import logging
import asyncio
from typing import List, Dict, Optional, Any, Set
from datetime import datetime

from .models import Achievement, UserAchievement, AchievementCategory, ProgressType
from .criteria import CriteriaRegistry, register_default_criteria
from .rewards import RewardRegistry, register_default_reward_handlers
from .progress import ProgressTracker

logger = logging.getLogger(__name__)

class AchievementEngine:
    """
    Core achievement system engine responsible for:
    - Managing achievement definitions
    - Tracking user progress
    - Evaluating achievement criteria
    - Unlocking achievements
    - Distributing rewards
    """
    
    def __init__(self, notification_manager=None, db_connection=None):
        """
        Initialize the achievement engine.
        
        Args:
            notification_manager: Manager for sending notifications
            db_connection: Database connection for persistence
        """
        self.notification_manager = notification_manager
        self.db_connection = db_connection
        
        # Internal state
        self._achievements: Dict[str, Achievement] = {}
        self._user_achievements: Dict[str, Dict[str, UserAchievement]] = {}
        self._criteria_registry = CriteriaRegistry()
        self._reward_registry = RewardRegistry()
        self._progress_tracker = ProgressTracker()
        self._running = False
        self._task = None
        self._event_queue = asyncio.Queue()
        
    async def start(self):
        """Start the achievement engine and background processing"""
        if self._running:
            return
            
        # Register default criteria and rewards
        register_default_criteria(self._criteria_registry)
        register_default_reward_handlers(self._reward_registry)
        
        # Load achievements from storage
        await self._load_achievements()
        
        # Start background processing
        self._running = True
        self._task = asyncio.create_task(self._process_events())
        
        logger.info("Achievement engine started successfully")
        
    async def stop(self):
        """Stop the achievement engine and cleanup resources"""
        if not self._running:
            return
            
        self._running = False
        if self._task:
            # Signal task to stop and wait for completion
            await self._event_queue.put(None)  # Sentinel value
            await self._task
            self._task = None
            
        logger.info("Achievement engine stopped")
    
    async def _process_events(self):
        """Background task to process achievement events"""
        while self._running:
            try:
                # Get next event with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Check for sentinel value indicating shutdown
                if event is None:
                    break
                    
                # Process the event
                await self._handle_event(event)
                self._event_queue.task_done()
                
            except asyncio.TimeoutError:
                # Just a timeout, continue the loop
                continue
            except Exception as e:
                logger.error(f"Error processing achievement event: {str(e)}")
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Process a single achievement event"""
        event_type = event.get("type")
        user_id = event.get("user_id")
        
        if not user_id:
            logger.warning(f"Received event without user_id: {event}")
            return
            
        if event_type == "transaction":
            await self._process_transaction_event(user_id, event)
        elif event_type == "budget_update":
            await self._process_budget_event(user_id, event)
        elif event_type == "system":
            await self._process_system_event(user_id, event)
        else:
            logger.warning(f"Unknown achievement event type: {event_type}")
    
    async def _process_transaction_event(self, user_id: str, event: Dict[str, Any]):
        """Process transaction-related events"""
        transaction = event.get("data", {})
        
        # Check all transaction-related achievements
        applicable_achievements = [
            ach for ach in self._achievements.values() 
            if ach.category in (AchievementCategory.BUDGET, AchievementCategory.SAVING)
        ]
        
        for achievement in applicable_achievements:
            # Get criteria function
            criteria_func = self._criteria_registry.get_criteria(achievement.criteria_id)
            if not criteria_func:
                continue
                
            # Evaluate criteria
            result = await criteria_func(user_id, transaction, achievement)
            if result is not None:
                await self._update_progress(user_id, achievement.id, result)
    
    async def _process_budget_event(self, user_id: str, event: Dict[str, Any]):
        """Process budget-related events"""
        budget_data = event.get("data", {})
        
        # Check all budget-related achievements
        applicable_achievements = [
            ach for ach in self._achievements.values() 
            if ach.category in (AchievementCategory.BUDGET, AchievementCategory.CONSISTENCY)
        ]
        
        for achievement in applicable_achievements:
            criteria_func = self._criteria_registry.get_criteria(achievement.criteria_id)
            if not criteria_func:
                continue
                
            result = await criteria_func(user_id, budget_data, achievement)
            if result is not None:
                await self._update_progress(user_id, achievement.id, result)
    
    async def _process_system_event(self, user_id: str, event: Dict[str, Any]):
        """Process system-related events"""
        system_data = event.get("data", {})
        
        # Check all system-related achievements
        applicable_achievements = [
            ach for ach in self._achievements.values()
            if ach.category in (AchievementCategory.SYSTEM, AchievementCategory.MILESTONE)
        ]
        
        for achievement in applicable_achievements:
            criteria_func = self._criteria_registry.get_criteria(achievement.criteria_id)
            if not criteria_func:
                continue
                
            result = await criteria_func(user_id, system_data, achievement)
            if result is not None:
                await self._update_progress(user_id, achievement.id, result)
    
    async def _update_progress(self, user_id: str, achievement_id: str, progress_value: float):
        """Update user progress toward an achievement"""
        # Get achievement and user achievement
        achievement = self._achievements.get(achievement_id)
        if not achievement:
            logger.warning(f"Attempting to update progress for unknown achievement: {achievement_id}")
            return
            
        # Ensure user exists in tracking
        if user_id not in self._user_achievements:
            self._user_achievements[user_id] = {}
            
        # Get or create user achievement
        if achievement_id not in self._user_achievements[user_id]:
            self._user_achievements[user_id][achievement_id] = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id
            )
            
        user_achievement = self._user_achievements[user_id][achievement_id]
        
        # Skip if already unlocked for non-repeatable achievements
        if user_achievement.unlocked and not self._is_repeatable(achievement):
            return
            
        # Update progress using progress tracker
        new_value, unlocked = await self._progress_tracker.update_progress(
            user_achievement=user_achievement,
            achievement=achievement,
            new_value=progress_value
        )
        
        # Handle achievement unlocking
        if unlocked:
            await self._unlock_achievement(user_id, achievement_id)
            
        # Save updated user achievement
        await self._save_user_achievement(user_achievement)
    
    async def _unlock_achievement(self, user_id: str, achievement_id: str):
        """Handle the unlocking of an achievement"""
        achievement = self._achievements.get(achievement_id)
        user_achievement = self._user_achievements.get(user_id, {}).get(achievement_id)
        
        if not achievement or not user_achievement:
            return
            
        # Update achievement state
        user_achievement.unlocked = True
        if user_achievement.first_achieved_at is None:
            user_achievement.first_achieved_at = datetime.now()
            
        # Update global unlock count
        achievement.unlocked_count += 1
        await self._save_achievement(achievement)
        
        # Process rewards
        if achievement.rewards:
            for reward in achievement.rewards:
                reward_type = reward.get("type")
                reward_handler = self._reward_registry.get_handler(reward_type)
                
                if reward_handler:
                    try:
                        await reward_handler(user_id, achievement, reward)
                    except Exception as e:
                        logger.error(f"Error processing reward {reward_type}: {str(e)}")
        
        # Send notification if notification manager is available
        if self.notification_manager:
            await self.notification_manager.send_achievement_notification(
                user_id=user_id,
                achievement_name=achievement.name,
                achievement_description=achievement.description,
                achievement_tier=achievement.tier
            )
    
    def _is_repeatable(self, achievement: Achievement) -> bool:
        """Check if an achievement can be unlocked multiple times"""
        # For now, consider streak achievements as repeatable
        return achievement.progress_type == ProgressType.STREAK
    
    async def track_event(self, event: Dict[str, Any]):
        """
        Track a new event for achievement processing.
        
        Args:
            event: Event data dictionary with type, user_id, and data fields
        """
        if not self._running:
            logger.warning("Achievement engine not running, event ignored")
            return
            
        await self._event_queue.put(event)
    
    async def get_achievements(self) -> List[Achievement]:
        """Get all available achievements"""
        return list(self._achievements.values())
    
    async def get_user_achievement_summary(self, user_id: str, include_hidden: bool = False) -> Dict[str, Any]:
        """
        Get achievement summary for a specific user.
        
        Args:
            user_id: The user ID to get achievements for
            include_hidden: Whether to include hidden achievements
            
        Returns:
            Dictionary with achievement summary
        """
        user_achs = self._user_achievements.get(user_id, {})
        
        # Filter achievements
        visible_achievements = {}
        for ach_id, achievement in self._achievements.items():
            # Skip hidden achievements unless requested
            if achievement.hidden and not include_hidden:
                continue
                
            # Include if unlocked or not hidden
            if not achievement.hidden or ach_id in user_achs:
                visible_achievements[ach_id] = achievement
        
        # Build achievement data
        achievement_data = []
        unlocked_count = 0
        
        for ach_id, achievement in visible_achievements.items():
            user_ach = user_achs.get(ach_id)
            
            if user_ach and user_ach.unlocked:
                unlocked_count += 1
                
            # Calculate progress percentage
            progress_pct = 0
            if user_ach:
                if achievement.target_value > 0:
                    progress_pct = min(100, (user_ach.current_value / achievement.target_value) * 100)
                elif user_ach.unlocked:
                    progress_pct = 100
            
            achievement_data.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category,
                "tier": achievement.tier,
                "icon": achievement.icon,
                "unlocked": user_ach.unlocked if user_ach else False,
                "progress_value": user_ach.current_value if user_ach else 0,
                "progress_percentage": progress_pct,
                "target_value": achievement.target_value,
                "unlocked_date": user_ach.first_achieved_at if user_ach and user_ach.unlocked else None
            })
        
        # Calculate completion percentage
        total_count = len(visible_achievements)
        completion_percentage = (unlocked_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "user_id": user_id,
            "total_achievements": total_count,
            "unlocked_achievements": unlocked_count,
            "completion_percentage": completion_percentage,
            "achievements": achievement_data
        }
    
    async def _load_achievements(self):
        """Load achievements from storage"""
        # In a real implementation, this would load from database
        # For now, load from predefined list
        
        # Example achievements
        sample_achievements = [
            Achievement(
                name="Budget Beginner",
                description="Create your first budget",
                category=AchievementCategory.BUDGET,
                tier=AchievementCategory.BRONZE,
                icon="budget_beginner.png",
                criteria_id="first_budget_created",
                progress_type=ProgressType.BOOLEAN,
                target_value=1,
                rewards=[{"type": "badge", "value": "budget_beginner"}]
            ),
            Achievement(
                name="Saving Star",
                description="Save more than 20% of your income in a month",
                category=AchievementCategory.SAVING,
                tier=AchievementCategory.SILVER,
                icon="saving_star.png",
                criteria_id="monthly_saving_percentage",
                progress_type=ProgressType.PERCENTAGE,
                target_value=20,
                rewards=[
                    {"type": "badge", "value": "saving_star"},
                    {"type": "points", "value": 100}
                ]
            ),
            Achievement(
                name="Consistency King",
                description="Stay under budget for 3 months in a row",
                category=AchievementCategory.CONSISTENCY,
                tier=AchievementCategory.GOLD,
                icon="consistency_king.png",
                criteria_id="budget_streak",
                progress_type=ProgressType.STREAK,
                target_value=3,
                rewards=[
                    {"type": "badge", "value": "consistency_king"},
                    {"type": "points", "value": 250}
                ]
            ),
            Achievement(
                name="Setup Superstar",
                description="Set up all account connections and preferences",
                category=AchievementCategory.SYSTEM,
                tier=AchievementCategory.BRONZE,
                icon="setup_superstar.png",
                criteria_id="account_setup_complete",
                progress_type=ProgressType.COUNTER,
                target_value=5,  # 5 setup tasks to complete
                rewards=[{"type": "badge", "value": "setup_superstar"}]
            ),
            Achievement(
                name="First Milestone",
                description="Reach your first savings goal",
                category=AchievementCategory.MILESTONE,
                tier=AchievementCategory.SILVER,
                icon="first_milestone.png",
                criteria_id="reached_savings_goal",
                progress_type=ProgressType.BOOLEAN,
                target_value=1,
                rewards=[
                    {"type": "badge", "value": "milestone_master"},
                    {"type": "points", "value": 150}
                ]
            ),
        ]
        
        # Add to internal dictionary
        for achievement in sample_achievements:
            self._achievements[achievement.id] = achievement
    
    async def _save_achievement(self, achievement: Achievement):
        """Save achievement to storage"""
        # In a real implementation, this would save to database
        self._achievements[achievement.id] = achievement
    
    async def _save_user_achievement(self, user_achievement: UserAchievement):
        """Save user achievement to storage"""
        # In a real implementation, this would save to database
        user_id = user_achievement.user_id
        ach_id = user_achievement.achievement_id
        
        if user_id not in self._user_achievements:
            self._user_achievements[user_id] = {}
            
        self._user_achievements[user_id][ach_id] = user_achievement
