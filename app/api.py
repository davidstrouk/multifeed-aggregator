import asyncio
from typing import List
import aiohttp
from fastapi import FastAPI

from . import models, background, config

app = FastAPI(
    title="Data Aggregator Service",
    description="A simple service to aggregate data from multiple sources.",
    version="0.0.1",
)


@app.get("/items/all", response_model=List[models.SourceItem], tags=["Items"])
async def get_all_aggregated_items_live():
    """
    Fetches, aggregates, and sorts items live from all sources.
    """
    tasks = []
    all_items = []

    # Use a single session for all requests for performance
    async with aiohttp.ClientSession() as session:
        # Create a fetch task for every stream in our configuration
        for provider_config in config.DATA_PROVIDERS.values():
            base_url = provider_config["base_url"]
            for stream in provider_config["streams"]:
                task = background.fetch_stream_data(session, base_url, stream)
                tasks.append(task)
        
        # Run all fetch tasks concurrently
        results = await asyncio.gather(*tasks)

    # Aggregate results from all successful tasks
    for result_list in results:
        if result_list:  # Check if the fetch was successful (not None)
            all_items.extend(result_list)
    
    # Sort the final list by date of appearance (newest first)
    all_items.sort(key=lambda item: item.created_at, reverse=True)
    
    return all_items