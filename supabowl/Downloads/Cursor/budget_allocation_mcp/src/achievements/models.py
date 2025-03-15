from enum import Enum
from typing import List, Dict, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid

class AchievementCategory(str, Enum):
    BUDGET = "budget"              # Budget management achievements
    SAVING = "saving"              # Saving money achievements
    CONSISTENCY = "consistency"    # Regular financial behaviors
    MILESTONE = "milestone"        # Significant financial milestones
    CHALLENGE = "challenge"        # Special challenge achievements
    SYSTEM = "system"              # System-related achievements

class AchievementTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class ProgressType(str, Enum):
    COUNTER = "counter"            # Simple count (e.g., number of transactions)
    PERCENTAGE = "percentage"      # Percentage progress (e.g., 75% of budget goal)
    BOOLEAN = "boolean"            # Yes/no completion (e.g., linked a bank account)
    STREAK = "streak"              # Consecutive completions (e.g., stayed under budget for 3 months)

class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: AchievementCategory
    tier: AchievementTier
    icon: str  # Path or identifier for achievement icon
    criteria_id: str  # Reference to the criteria for this achievement
    progress_type: ProgressType
    target_value: float  # Target value to reach for completion
    rewards: List[Dict[str, Union[str, int, float]]] = []  # Flexible rewards structure
    
    # Achievement metadata
    hidden: bool = False  # Whether this is a hidden/surprise achievement
    unlocked_count: int = 0  # How many times this has been unlocked globally
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Budget Master",
                "description": "Stay under budget in all categories for 3 consecutive months",
                "category": "budget",
                "tier": "gold",
                "icon": "budget_master.png",
                "criteria_id": "budget_streak_3months",
                "progress_type": "streak",
                "target_value": 3,
                "rewards": [
                    {"type": "badge", "value": "budget_master"},
                    {"type": "points", "value": 500}
                ],
                "hidden": False
            }
        }

class UserAchievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    achievement_id: str
    current_value: float = 0  # Current progress value
    unlocked: bool = False
    first_achieved_at: Optional[datetime] = None
    progress_history: List[Dict[str, Union[datetime, float]]] = []  # Track progress over time
    
    @validator('first_achieved_at', pre=True, always=True)
    def set_achieved_time(cls, v, values):
        # If unlocked is True and no achievement time is set, set it to now
        if values.get('unlocked') and v is None:
            return datetime.now()
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "achievement_id": "ach456",
                "current_value": 2,
                "unlocked": False,
                "progress_history": [
                    {"date": "2025-01-15T20:20:39.123", "value": 1},
                    {"date": "2025-02-15T10:15:22.456", "value": 2}
                ]
            }
        }
