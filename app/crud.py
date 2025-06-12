from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from .models import SourceItem

async def save_items_to_db(db: AsyncIOMotorDatabase, items: List[SourceItem]):
    """
    Saves a list of items to the database.
    
    This initial version uses replace_one with upsert=True. It ensures that if we
    fetch the same item again, it will be updated rather than creating a duplicate.
    This is less efficient than a bulk operation but is a solid first step.
    """
    if not items:
        return

    for item in items:
        # Using the stream and created_at as a unique identifier for each item.
        await db.items.replace_one(
            {"stream": item.stream, "created_at": item.created_at},
            item.dict(),
            upsert=True
        )

async def get_all_items(db: AsyncIOMotorDatabase, limit: int = 100) -> List[SourceItem]:
    """Fetches all items from the DB, sorted by date (newest first)."""
    cursor = db.items.find().sort("created_at", -1).limit(limit)
    # Convert the documents from the DB back into Pydantic models
    return [SourceItem(**doc) async for doc in cursor]