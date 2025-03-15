import os
from dotenv import load_dotenv
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from financial.engine import FinancialEngine
from notifications.manager import NotificationManager
from integrations.quickbooks import QuickBooksIntegration
from achievements.engine import AchievementEngine  # Added for Achievement System

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'budget_allocation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Budget Allocation MCP",
    description="MCP server for budget allocation and financial tracking",
    version="1.0.0"
)

# Initialize components
financial_engine = None
notification_manager = None
quickbooks_integration = None
achievement_engine = None  # Added for Achievement System

@app.on_event("startup")
async def startup_event():
    global financial_engine, notification_manager, quickbooks_integration, achievement_engine
    
    try:
        # Initialize components
        notification_manager = NotificationManager()
        financial_engine = FinancialEngine()
        quickbooks_integration = QuickBooksIntegration()
        
        # Initialize achievement engine with notification manager
        achievement_engine = AchievementEngine(notification_manager=notification_manager)
        await achievement_engine.start()  # Start achievement engine
        
        logger.info("Successfully initialized all components")
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise HTTPException(status_code=500, detail="Server initialization failed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    if achievement_engine:
        await achievement_engine.stop()
    logger.info("Shutdown complete")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "components": {
        "financial_engine": financial_engine is not None,
        "notification_manager": notification_manager is not None,
        "quickbooks_integration": quickbooks_integration is not None,
        "achievement_engine": achievement_engine is not None
    }}

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "Budget Allocation MCP",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/achievements")
async def list_achievements():
    """List all available achievements"""
    if not achievement_engine:
        raise HTTPException(status_code=503, detail="Achievement system not available")
    
    achievements = await achievement_engine.get_achievements()
    return {
        "count": len(achievements),
        "achievements": [
            {
                "id": ach.id,
                "name": ach.name,
                "description": ach.description,
                "category": ach.category,
                "tier": ach.tier,
                "icon": ach.icon
            }
            for ach in achievements
        ]
    }

@app.get("/achievements/{user_id}")
async def get_user_achievements(user_id: str, include_hidden: bool = False):
    """Get achievements for a specific user"""
    if not achievement_engine:
        raise HTTPException(status_code=503, detail="Achievement system not available")
    
    summary = await achievement_engine.get_user_achievement_summary(
        user_id=user_id,
        include_hidden=include_hidden
    )
    
    return summary

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('SERVER_PORT', 5000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
