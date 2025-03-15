import logging
from typing import Dict, Callable, Any, Optional, Awaitable

from .models import Achievement

logger = logging.getLogger(__name__)

# Type definition for criteria functions
CriteriaFunc = Callable[[str, Dict[str, Any], Achievement], Awaitable[Optional[float]]]

class CriteriaRegistry:
    """
    Registry for achievement criteria evaluation functions.
    Each criteria function takes (user_id, event_data, achievement) and returns
    a progress value or None if no progress update is needed.
    """
    
    def __init__(self):
        self._criteria: Dict[str, CriteriaFunc] = {}
        
    def register(self, criteria_id: str, func: CriteriaFunc):
        """Register a criteria evaluation function"""
        self._criteria[criteria_id] = func
        logger.debug(f"Registered criteria: {criteria_id}")
        
    def get_criteria(self, criteria_id: str) -> Optional[CriteriaFunc]:
        """Get a criteria function by ID"""
        return self._criteria.get(criteria_id)
        
    def list_criteria(self):
        """List all registered criteria IDs"""
        return list(self._criteria.keys())


# Default criteria implementation functions

async def first_budget_created(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for first budget creation"""
    event_type = data.get("event_type")
    
    if event_type == "budget_created":
        # This is a boolean achievement, so return 1.0 for completion
        return 1.0
    
    return None

async def monthly_saving_percentage(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for saving percentage of income"""
    if data.get("event_type") != "month_summary":
        return None
        
    income = data.get("total_income", 0)
    savings = data.get("total_savings", 0)
    
    if income <= 0:
        return None
        
    # Calculate saving percentage
    saving_percentage = (savings / income) * 100
    
    # Return the actual percentage as progress
    return saving_percentage

async def budget_streak(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for consecutive months under budget"""
    if data.get("event_type") != "month_summary":
        return None
        
    # Check if under budget
    under_budget = data.get("under_budget", False)
    current_streak = data.get("budget_streak", 0)
    
    if under_budget:
        # Increment streak
        return current_streak + 1
    else:
        # Reset streak
        return 0

async def account_setup_complete(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for completing account setup steps"""
    if data.get("event_type") != "setup_action":
        return None
        
    action_type = data.get("action_type")
    valid_actions = {
        "connect_bank", "setup_profile", "create_budget",
        "set_goals", "enable_notifications"
    }
    
    if action_type in valid_actions:
        # Get current progress from data or default to 0
        current_progress = data.get("completed_actions", 0)
        return current_progress + 1
        
    return None

async def reached_savings_goal(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for reaching a savings goal"""
    if data.get("event_type") != "goal_reached":
        return None
        
    goal_type = data.get("goal_type")
    
    if goal_type == "savings":
        # Boolean achievement - return 1.0 for completion
        return 1.0
        
    return None

async def transaction_count(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for tracking number of transactions"""
    if data.get("event_type") != "transaction_stats":
        return None
        
    # Return the total transaction count
    return data.get("transaction_count", 0)

async def expense_reduction(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for reducing expenses in a category"""
    if data.get("event_type") != "expense_comparison":
        return None
        
    # Get percentage reduction
    reduction = data.get("reduction_percentage", 0)
    return reduction if reduction > 0 else 0

async def consecutive_logins(user_id: str, data: Dict[str, Any], achievement: Achievement) -> Optional[float]:
    """Criteria for tracking consecutive daily logins"""
    if data.get("event_type") != "user_login":
        return None
        
    # Get the current streak
    streak = data.get("login_streak", 0)
    return streak


def register_default_criteria(registry: CriteriaRegistry):
    """Register all default criteria functions"""
    registry.register("first_budget_created", first_budget_created)
    registry.register("monthly_saving_percentage", monthly_saving_percentage)
    registry.register("budget_streak", budget_streak)
    registry.register("account_setup_complete", account_setup_complete)
    registry.register("reached_savings_goal", reached_savings_goal)
    registry.register("transaction_count", transaction_count)
    registry.register("expense_reduction", expense_reduction)
    registry.register("consecutive_logins", consecutive_logins)
