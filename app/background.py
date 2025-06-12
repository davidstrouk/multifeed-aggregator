import aiohttp
from typing import List, Optional

from .models import SourceItem

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
                # Validate the data against our Pydantic model
                return [SourceItem(**item) for item in data]
            else:
                # Basic error logging for now
                print(f"Error fetching {url}: Status {response.status}")
                return None
    except Exception as e:
        print(f"An unexpected error occurred for {url}: {e}")
        return None