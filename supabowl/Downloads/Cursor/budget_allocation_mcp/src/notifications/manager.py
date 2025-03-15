import os
import logging
from typing import Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    BUDGET_ALERT = "budget_alert"
    TRANSACTION = "transaction"
    SYSTEM = "system"
    ACHIEVEMENT = "achievement"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class NotificationManager:
    def __init__(self):
        self.enabled = os.getenv('NOTIFICATION_ENABLED', 'true').lower() == 'true'
        self.sound_enabled = os.getenv('NOTIFICATION_SOUND', 'true').lower() == 'true'
        self.frequency = os.getenv('NOTIFICATION_FREQUENCY', 'real-time')
        self.notification_history = []
        logger.info("Initialized NotificationManager")

    async def send_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[dict] = None
    ) -> bool:
        """Send a notification through macOS notification system"""
        try:
            if not self.enabled:
                logger.info("Notifications are disabled, skipping notification")
                return False

            # Check frequency settings
            if self.frequency != 'real-time' and notification_type != NotificationType.SYSTEM:
                # Store for batch processing
                self.notification_history.append({
                    'title': title,
                    'message': message,
                    'type': notification_type,
                    'priority': priority,
                    'metadata': metadata or {},
                    'timestamp': datetime.now()
                })
                return True

            # Send immediate notification
            await self._send_macos_notification(title, message, priority)
            return True

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False

    async def send_budget_alert(
        self,
        category: str,
        percentage: float,
        amount_remaining: float
    ) -> bool:
        """Send a budget-specific alert notification"""
        title = f"Budget Alert: {category}"
        message = (
            f"You've used {percentage:.1f}% of your {category} budget. "
            f"${amount_remaining:.2f} remaining."
        )
        
        return await self.send_notification(
            title=title,
            message=message,
            notification_type=NotificationType.BUDGET_ALERT,
            priority=NotificationPriority.HIGH
        )

    async def send_achievement_notification(
        self,
        achievement_name: str,
        description: str
    ) -> bool:
        """Send an achievement unlock notification"""
        title = f"Achievement Unlocked: {achievement_name}"
        
        return await self.send_notification(
            title=title,
            message=description,
            notification_type=NotificationType.ACHIEVEMENT,
            priority=NotificationPriority.NORMAL
        )

    async def _send_macos_notification(
        self,
        title: str,
        message: str,
        priority: NotificationPriority
    ) -> None:
        """Internal method to send macOS notification"""
        try:
            # Import here to avoid initialization issues
            from systemInfo import sendNotification
            
            await sendNotification(
                title=title,
                message=message,
                sound=self.sound_enabled and priority != NotificationPriority.LOW
            )
            
            logger.info(f"Sent macOS notification: {title}")
        except Exception as e:
            logger.error(f"Error sending macOS notification: {str(e)}")
            raise

    async def process_pending_notifications(self) -> None:
        """Process stored notifications based on frequency settings"""
        if not self.notification_history:
            return

        try:
            if self.frequency == 'daily':
                # Group notifications by type
                notifications_by_type = {}
                for notif in self.notification_history:
                    notif_type = notif['type']
                    if notif_type not in notifications_by_type:
                        notifications_by_type[notif_type] = []
                    notifications_by_type[notif_type].append(notif)

                # Send summary notifications
                for notif_type, notifications in notifications_by_type.items():
                    if notifications:
                        title = f"Daily {notif_type.value.title()} Summary"
                        message = f"You have {len(notifications)} new {notif_type.value} notifications."
                        
                        await self._send_macos_notification(
                            title=title,
                            message=message,
                            priority=NotificationPriority.NORMAL
                        )

            # Clear processed notifications
            self.notification_history.clear()
            logger.info("Successfully processed pending notifications")

        except Exception as e:
            logger.error(f"Error processing pending notifications: {str(e)}")
            raise