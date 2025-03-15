from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    id: str
    amount: Decimal
    category: str
    description: str
    date: datetime
    source: str  # e.g., 'quickbooks', 'bank', 'manual'
    status: str  # e.g., 'pending', 'completed', 'failed'
    metadata: Dict

@dataclass
class Budget:
    id: str
    category: str
    amount: Decimal
    period: str  # e.g., 'monthly', 'quarterly', 'annual'
    start_date: datetime
    end_date: datetime
    current_spending: Decimal
    alerts_enabled: bool
    alert_threshold: float  # percentage as decimal (e.g., 0.8 for 80%)

class FinancialEngine:
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.budgets: Dict[str, Budget] = {}
        logger.info("Initialized FinancialEngine")
    
    async def add_transaction(self, transaction: Transaction) -> bool:
        """Add a new transaction and update related budgets"""
        try:
            # Add transaction
            self.transactions.append(transaction)
            
            # Update budget if exists for category
            if transaction.category in self.budgets:
                budget = self.budgets[transaction.category]
                budget.current_spending += transaction.amount
                
                # Check if alert threshold exceeded
                if budget.alerts_enabled:
                    spending_ratio = float(budget.current_spending / budget.amount)
                    if spending_ratio >= budget.alert_threshold:
                        await self._trigger_budget_alert(budget, spending_ratio)
            
            logger.info(f"Successfully added transaction {transaction.id}")
            return True
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            return False
    
    async def create_budget(self, budget: Budget) -> bool:
        """Create a new budget category"""
        try:
            self.budgets[budget.category] = budget
            logger.info(f"Successfully created budget for category {budget.category}")
            return True
        except Exception as e:
            logger.error(f"Error creating budget: {str(e)}")
            return False
    
    async def get_budget_status(self, category: str) -> Optional[Dict]:
        """Get current status of a budget category"""
        try:
            if category not in self.budgets:
                return None
            
            budget = self.budgets[category]
            return {
                "category": budget.category,
                "total_amount": float(budget.amount),
                "current_spending": float(budget.current_spending),
                "remaining": float(budget.amount - budget.current_spending),
                "percentage_used": float(budget.current_spending / budget.amount * 100),
                "period": budget.period,
                "start_date": budget.start_date.isoformat(),
                "end_date": budget.end_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting budget status: {str(e)}")
            return None
    
    async def _trigger_budget_alert(self, budget: Budget, spending_ratio: float) -> None:
        """Trigger an alert when budget threshold is exceeded"""
        try:
            # Create alert message
            message = (
                f"Budget Alert: {budget.category} spending has reached "
                f"{spending_ratio*100:.1f}% of the allocated budget"
            )
            
            # TODO: Integrate with notification system
            logger.warning(message)
        except Exception as e:
            logger.error(f"Error triggering budget alert: {str(e)}")
    
    async def get_transaction_history(
        self,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get transaction history with optional filters"""
        try:
            filtered_transactions = self.transactions
            
            if category:
                filtered_transactions = [
                    t for t in filtered_transactions
                    if t.category == category
                ]
            
            if start_date:
                filtered_transactions = [
                    t for t in filtered_transactions
                    if t.date >= start_date
                ]
            
            if end_date:
                filtered_transactions = [
                    t for t in filtered_transactions
                    if t.date <= end_date
                ]
            
            return [
                {
                    "id": t.id,
                    "amount": float(t.amount),
                    "category": t.category,
                    "description": t.description,
                    "date": t.date.isoformat(),
                    "source": t.source,
                    "status": t.status,
                    "metadata": t.metadata
                }
                for t in filtered_transactions
            ]
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return []