from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Topics(str, Enum):
    """An enumeration for the allowed topic types."""
    golf = "golf"
    news = "news"
    food = "food"
    movies = "movies"
    hobby = "hobby"
    games = "games"

class SourceItem(BaseModel):
    """Represents a single item from an external data source."""
    created_at: datetime
    stream: str
    topic: Topics
    image: str
    data: str