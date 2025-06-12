import aiohttp
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import SourceItem
from .config import DATA_PROVIDERS
from .crud import save_items_to_db

async def fetch_stream_data(session: aiohttp.ClientSession, base_url: str, stream: str) -> Optional[List[SourceItem]]:
    """
    Fetches the last 20 items from a single stream.
    
    Returns a list of SourceItem objects on success, or None on failure.
    """
    url = f"{base_url}/{stream}/"
    try:
        async with session.get(url, params={"limit": 20}) as response:
            if response.status == 200:
                data = await response.json()
                return [SourceItem(**item) for item in data]
            else:
                print(f"Error fetching {url}: Status {response.status}")
                return None
    except Exception as e:
        print(f"An unexpected error occurred for {url}: {e}")
        return None

async def aggregate_from_all_sources(db: AsyncIOMotorDatabase):
    """
    Fetches data from all configured sources concurrently and saves it to the DB.
    """
    print("Starting initial data aggregation from all sources...")
    tasks = []
    async with aiohttp.ClientSession() as session:
        for provider_config in DATA_PROVIDERS.values():
            base_url = provider_config["base_url"]
            for stream in provider_config["streams"]:
                tasks.append(fetch_stream_data(session, base_url, stream))

        results = await asyncio.gather(*tasks)

    all_items = []
    for res in results:
        if isinstance(res, list):
            all_items.extend(res)

    if all_items:
        await save_items_to_db(db, all_items)
        print(f"Aggregation complete. Saved {len(all_items)} items to the database.")