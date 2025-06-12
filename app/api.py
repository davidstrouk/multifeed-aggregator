import asyncio
from typing import List

from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from . import crud, models
from .background import aggregate_from_all_sources
from .database import connect_to_db, close_db_connection, get_db

app = FastAPI(
    title="Data Aggregator API",
    description="Fetches and aggregates data from multiple sources.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """On startup, connect to DB and perform initial data fetch."""
    await connect_to_db()
    # Run the initial data fetch in the background as a separate task
    # so it doesn't block the server from starting.
    asyncio.create_task(aggregate_from_all_sources(db=get_db()))

@app.on_event("shutdown")
async def shutdown_event():
    """On shutdown, close the DB connection."""
    await close_db_connection()


@app.get("/items/all", response_model=List[models.SourceItem], tags=["Items"])
async def get_all_aggregated_items(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Fetch a list of all items aggregated from different sources,
    ordered by the date of appearance (newest first).

    This data is now read from the database.
    """
    return await crud.get_all_items(db)


@app.get("/items/subscribed/{user_id}", response_model=List[models.SourceItem], tags=["Items"])
async def get_subscribed_items(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Fetch a list of items from topics the user has previously subscribed to,
    ordered by date.
    """
    # Step 1: Get the list of topics the user is subscribed to.
    topics = await crud.get_user_subscriptions(db, user_id)
    if not topics:
        return [] # Return an empty list if the user has no subscriptions.
    # Step 2: Fetch all items that match those topics.
    return await crud.get_items_by_topics(db, topics)


@app.post("/subscriptions", status_code=201, tags=["Subscriptions"])
async def subscribe_to_topic(
    subscription: models.SubscriptionRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Subscribe a user to a specific topic.
    """
    await crud.subscribe_user_to_topic(db, subscription)
    return {"message": f"User {subscription.user_id} subscribed to topic {subscription.topic}"}
