import os
from dotenv import load_dotenv

load_dotenv()

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")

# Configuration for data sources
# This structure allows us to support multiple different source providers.
DATA_PROVIDERS = {
    "heroku_provider": {
        "base_url": "https://credcompare-hr-test-d81ffdfbad0d.herokuapp.com",
        "streams": ["stream1", "stream2", "stream3", "stream4"],
    }
    # To add another provider:
    # "another_provider": {
    #     "base_url": "http://some-other-service.com",
    #     "streams": ["alpha", "beta"],
    # }
}

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "data_aggregator_db"

POLLING_INTERVAL_SECONDS = 300  # 5 minutes for fallback polling
HTTP_TIMEOUT_SECONDS = 10 # Timeout for external API calls