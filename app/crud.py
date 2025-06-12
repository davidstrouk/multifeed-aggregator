from pymongo import UpdateOne
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from .models import SourceItem, SubscriptionRequest

async def save_items_to_db(db: AsyncIOMotorDatabase, items: List[SourceItem]):
    """
    Saves a list of items to the database efficiently, avoiding duplicates.
    
    Uses UpdateOne with upsert=True in a bulk_write operation. This is far
    more performant than inserting documents one by one.
    """
    if not items:
        return 0

    # Create a list of database operations to perform in a single batch.
    operations = [
        UpdateOne(
            # The filter to find the document.
            {"stream": item.stream, "created_at": item.created_at},
            # The update to apply. $set updates fields without replacing the whole doc.
            {"$set": item.dict()},
            # If no document matches the filter, insert this one.
            upsert=True
        )
        for item in items
    ]
    
    # Execute all operations in a single command to the database.
    # ordered=False tells MongoDB to continue even if one operation fails.
    result = await db.items.bulk_write(operations, ordered=False)
    
    # Return the number of documents that were newly inserted or modified.
    return result.upserted_count + result.modified_count

async def get_all_items(db: AsyncIOMotorDatabase, limit: int = 100) -> List[SourceItem]:
    """Fetches all items from the DB, sorted by date (newest first)."""
    cursor = db.items.find().sort("created_at", -1).limit(limit)
    # Convert the documents from the DB back into Pydantic models
    return [SourceItem(**doc) async for doc in cursor]

async def subscribe_user_to_topic(db: AsyncIOMotorDatabase, subscription: SubscriptionRequest):
    """Creates or updates a user subscription to a topic in the database."""
    # Use update_one with upsert=True. If the subscription exists, it does nothing.
    # If it doesn't exist, it creates it.
    await db.subscriptions.update_one(
        {"user_id": subscription.user_id, "topic": subscription.topic},
        {"$set": subscription.dict()},
        upsert=True
    )

async def get_user_subscriptions(db: AsyncIOMotorDatabase, user_id: str) -> List[str]:
    """Fetches a list of all topic strings a user is subscribed to."""
    cursor = db.subscriptions.find({"user_id": user_id}, {"topic": 1, "_id": 0})
    return [sub["topic"] async for sub in cursor]

async def get_items_by_topics(db: AsyncIOMotorDatabase, topics: List[str], limit: int = 100) -> List[SourceItem]:
    """Fetches items that match any of the topics in the provided list, sorted by date."""
    if not topics:
        return []
    # Use the $in operator to find documents where the 'topic' field matches any
    # value in the topics list.
    cursor = db.items.find({"topic": {"$in": topics}}).sort("created_at", -1).limit(limit)
    return [SourceItem(**doc) async for doc in cursor]