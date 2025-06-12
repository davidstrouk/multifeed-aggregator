from motor.motor_asyncio import AsyncIOMotorClient
import mongomock_motor as mongomock
import os

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "data_aggregator_db"

class DBManager:
    """A simple manager for the database client and instance."""
    client: AsyncIOMotorClient = None
    db = None

db_manager = DBManager()

async def connect_to_db():
    """Initializes the database connection."""
    if MONGO_URI:
        print("Connecting to MongoDB...")
        db_manager.client = AsyncIOMotorClient(MONGO_URI)
    else:
        print("Using in-memory mongomock database.")
        db_manager.client = mongomock.AsyncMongoMockClient()
    db_manager.db = db_manager.client[DB_NAME]

async def close_db_connection():
    """Closes the database connection."""
    if db_manager.client:
        print("Closing database connection.")
        db_manager.client.close()

def get_db():
    """Dependency injector to get the database instance for API endpoints."""
    return db_manager.db