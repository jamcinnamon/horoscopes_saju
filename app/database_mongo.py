"""
MongoDB configuration and connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# MongoDB client
mongodb_client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global mongodb_client
    try:
        mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"❌ Could not connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


async def init_db():
    """Initialize Beanie with document models"""
    from app.models.mongo import (
        HoroscopeDocument,
        SajuInterpretationDocument,
        UserRequestDocument,
        UserFeedbackDocument,
        ModelVersionDocument
    )
    
    await init_beanie(
        database=mongodb_client[settings.mongodb_db_name],
        document_models=[
            HoroscopeDocument,
            SajuInterpretationDocument,
            UserRequestDocument,
            UserFeedbackDocument,
            ModelVersionDocument
        ]
    )
    logger.info("✅ Beanie initialized with document models")


def get_database():
    """Get MongoDB database instance"""
    return mongodb_client[settings.mongodb_db_name]
