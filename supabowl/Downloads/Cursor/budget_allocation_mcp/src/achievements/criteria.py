from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod

from .models import ProgressType, AchievementCategory

logger = logging.getLogger(__name__)

class AchievementCriteria(ABC):
    def __init__(self, 
                 criteria_id: str, 
                 name: str, 
                 description: str,
                 progress_type: ProgressType,
                 category: AchievementCategory):
        self.id = criteria_id
        self.name = name
        self.description = description
        self.progress_type = progress_type
        self.category = category
    
    @abstractmethod
    async def evaluate(self, user_id: str, context: Dict[str, Any]) -> float:
        """
        Evaluate if the criteria is met based on the provided context
        Returns the current progress value (e.g., count, percentage, etc.)
        """
        pass

    @abstractmethod
    async def reset_progress(self, user_id: str) -> bool:
        """Reset progress for a specific user for this criteria"""
        pass


class BudgetCriteria(AchievementCriteria):
    """Base class for budget-related achievement criteria"""
    def __init__(self, criteria_id: str, name: str, description: str, 
                 progress_type: ProgressType):
        super().__init__(
            criteria_id=criteria_id,
            name=name, 
            description=description,
            progress_type=progress_type,
            category=AchievementCategory.BUDGET
        )


class BudgetCompletionCriteria(BudgetCriteria):
    """Achievement criteria for staying under budget"""
    def __init__(self, budget_categories: Optional[List[str]] = None):
        super().__init__(
            criteria_id="budget_completion",
            name="Budget Completion",
            description="Stay under budget for specified categories",
            progress_type=ProgressType.PERCENTAGE
        )
        self.budget_categories = budget_categories
    
    async def evaluate(self, user_id: str, context: Dict[str, Any]) -> float:
        try:
            # Extract budgets and transactions from context
            budgets = context.get('budgets', {})
            
            if not budgets:
                return 0.0
            
            # Filter categories if specified
            if self.budget_categories:
                budgets = {k: v for k, v in budgets.items() if k in self.budget_categories}
            
            # Count budgets that are under limit
            under_budget_count = sum(1 for budget in budgets.values() 
                                    if budget.current_spending <= budget.amount)
            
            # Calculate percentage
            if len(budgets) > 0:
                return under_budget_count / len(budgets) * 100
            return 0.0
            
        except Exception as e:
            logger.error(f"Error evaluating budget completion criteria: {str(e)}")
            return 0.0
    
    async def reset_progress(self, user_id: str) -> bool:
        # For percentage-based criteria, no persistent storage needed
        return True


class BudgetStreakCriteria(BudgetCriteria):
    """Achievement criteria for maintaining a streak of staying under budget"""
    def __init__(self, required_streak: int = 3, 
                budget_categories: Optional[List[str]] = None):
        super().__init__(
            criteria_id=f"budget_streak_{required_streak}",
            name=f"Budget Streak ({required_streak})",
            description=f"Stay under budget for {required_streak} consecutive periods",
            progress_type=ProgressType.STREAK
        )
        self.required_streak = required_streak
        self.budget_categories = budget_categories
        self.user_streaks: Dict[str, int] = {}
    
    async def evaluate(self, user_id: str, context: Dict[str, Any]) -> float:
        try:
            # Extract budgets and period info from context
            budgets = context.get('budgets', {})
            current_period = context.get('current_period')
            last_checked_period = context.get('last_checked_period')
            
            if not budgets or not current_period:
                return float(self.user_streaks.get(user_id, 0))
            
            # Ensure we're only evaluating once per period
            if last_checked_period == current_period:
                return float(self.user_streaks.get(user_id, 0))
            
            # Filter categories if specified
            if self.budget_categories:
                budgets = {k: v for k, v in budgets.items() if k in self.budget_categories}
            
            # Check if all budgets are under limit
            all_under_budget = all(budget.current_spending <= budget.amount 
                                  for budget in budgets.values())
            
            # Update streak
            if all_under_budget:
                self.user_streaks[user_id] = self.user_streaks.get(user_id, 0) + 1
            else:
                # Reset streak if any budget is over
                self.user_streaks[user_id] = 0
            
            return float(self.user_streaks.get(user_id, 0))
            
        except Exception as e:
            logger.error(f"Error evaluating budget streak criteria: {str(e)}")
            return float(self.user_streaks.get(user_id, 0))
    
    async def reset_progress(self, user_id: str) -> bool:
        try:
            if user_id in self.user_streaks:
                self.user_streaks[user_id] = 0
            return True
        except Exception as e:
            logger.error(f"Error resetting budget streak: {str(e)}")
            return False


class SavingsCriteria(AchievementCriteria):
    """Base class for savings-related achievement criteria"""
    def __init__(self, criteria_id: str, name: str, description: str, 
                 progress_type: ProgressType):
        super().__init__(
            criteria_id=criteria_id,
            name=name, 
            description=description,
            progress_type=progress_type,
            category=AchievementCategory.SAVING
        )


class SavingsGoalCriteria(SavingsCriteria):
    """Achievement criteria for reaching savings goals"""
    def __init__(self, target_amount: float):
        super().__init__(
            criteria_id=f"savings_goal_{int(target_amount)}",
            name=f"Savings Goal (${target_amount})",
            description=f"Save a total of ${target_amount}",
            progress_type=ProgressType.PERCENTAGE
        )
        self.target_amount = target_amount
    
    async def evaluate(self, user_id: str, context: Dict[str, Any]) -> float:
        try:
            # Extract savings data from context
            total_savings = context.get('total_savings', 0.0)
            
            # Calculate percentage of goal achieved
            percentage = min(100.0, (total_savings / self.target_amount) * 100)
            return percentage
            
        except Exception as e:
            logger.error(f"Error evaluating savings goal criteria: {str(e)}")
            return 0.0
    
    async def reset_progress(self, user_id: str) -> bool:
        # For savings goals, progress is directly tied to account balances
        # No need to reset anything in the criteria itself
        return True


class MilestoneCriteria(AchievementCriteria):
    """Base class for milestone-related achievement criteria"""
    def __init__(self, criteria_id: str, name: str, description: str, 
                 progress_type: ProgressType):
        super().__init__(
            criteria_id=criteria_id,
            name=name, 
            description=description,
            progress_type=progress_type,
            category=AchievementCategory.MILESTONE
        )


class TransactionCountCriteria(MilestoneCriteria):
    """Achievement criteria for reaching a certain number of tracked transactions"""
    def __init__(self, target_count: int):
        super().__init__(
            criteria_id=f"transaction_count_{target_count}",
            name=f"Transaction Milestone ({target_count})",
            description=f"Track {target_count} transactions in the system",
            progress_type=ProgressType.COUNTER
        )
        self.target_count = target_count
    
    async def evaluate(self, user_id: str, context: Dict[str, Any]) -> float:
        try:
            # Extract transaction data from context
            transactions = context.get('transactions', [])
            
            # Return current count
            return float(len(transactions))
            
        except Exception as e:
            logger.error(f"Error evaluating transaction count criteria: {str(e)}")
            return 0.0
    
    async def reset_progress(self, user_id: str) -> bool:
        # Cannot reset transaction count as it's based on historical data
        return False


# Criteria Registry for easy lookups
class CriteriaRegistry:
    _criteria: Dict[str, AchievementCriteria] = {}
    
    @classmethod
    def register(cls, criteria: AchievementCriteria) -> None:
        """Register a criteria instance"""
        cls._criteria[criteria.id] = criteria
        logger.info(f"Registered achievement criteria: {criteria.id}")
    
    @classmethod
    def get(cls, criteria_id: str) -> Optional[AchievementCriteria]:
        """Get a criteria by ID"""
        return cls._criteria.get(criteria_id)
    
    @classmethod
    def get_all(cls) -> List[AchievementCriteria]:
        """Get all registered criteria"""
        return list(cls._criteria.values())
    
    @classmethod
    def get_by_category(cls, category: AchievementCategory) -> List[AchievementCriteria]:
        """Get all criteria for a specific category"""
        return [
            criteria for criteria in cls._criteria.values()
            if criteria.category == category
        ]


# Register default criteria
def register_default_criteria():
    """Register default achievement criteria"""
    # Budget criteria
    CriteriaRegistry.register(BudgetCompletionCriteria())
    CriteriaRegistry.register(BudgetStreakCriteria(required_streak=3))
    CriteriaRegistry.register(BudgetStreakCriteria(required_streak=6))
    CriteriaRegistry.register(BudgetStreakCriteria(required_streak=12))
    
    # Savings criteria
    CriteriaRegistry.register(SavingsGoalCriteria(target_amount=1000))
    CriteriaRegistry.register(SavingsGoalCriteria(target_amount=5000))
    CriteriaRegistry.register(SavingsGoalCriteria(target_amount=10000))
    
    # Milestone criteria
    CriteriaRegistry.register(TransactionCountCriteria(target_count=10))
    CriteriaRegistry.register(TransactionCountCriteria(target_count=100))
    CriteriaRegistry.register(TransactionCountCriteria(target_count=1000))
    
    logger.info("Registered default achievement criteria")
