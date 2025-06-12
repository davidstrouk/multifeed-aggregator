import pytest
import respx
from httpx import AsyncClient
import asyncio

from app.api import app
from app.database import db_manager

# Mock data to simulate the external API's responses.
MOCK_BASE_URL = "https://credcompare-hr-test-d81ffdfbad0d.herokuapp.com"
MOCK_STREAM1_DATA = [
    {"created_at": "2025-01-01T12:00:00Z", "stream": "stream1", "topic": "news", "image": "img1", "data": "data1"},
    {"created_at": "2025-01-01T11:00:00Z", "stream": "stream1", "topic": "golf", "image": "img2", "data": "data2"},
]
MOCK_STREAM2_DATA = [
    {"created_at": "2025-01-01T13:00:00Z", "stream": "stream2", "topic": "food", "image": "img3", "data": "data3"},
]

@pytest.fixture(scope="module")
def anyio_backend():
    """Required by pytest-asyncio to specify the async backend."""
    return "asyncio"

@pytest.fixture(scope="function")
async def test_client():
    """A fixture to set up the test client and mock external APIs."""
    with respx.mock(base_url=MOCK_BASE_URL) as mock:
        # Define the mock responses for our configured streams.
        mock.get("/stream1/").respond(200, json=MOCK_STREAM1_DATA)
        mock.get("/stream2/").respond(200, json=MOCK_STREAM2_DATA)
        # Simulate a stream that is down or has an error.
        mock.get("/stream3/").respond(500)
        # Simulate a stream that is up but has no data.
        mock.get("/stream4/").respond(200, json=[])

        # Create an async client to interact with our app.
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Manually run the startup events, which connects to the DB
            # and triggers the initial data fetch against our mocks.
            await app.router.startup()
            yield client
            # Cleanup: Drop the mock database and run shutdown events.
            await db_manager.db.command("dropDatabase")
            await app.router.shutdown()

@pytest.mark.anyio
async def test_get_all_items(test_client: AsyncClient):
    """
    Tests that the app correctly fetches, stores, and serves aggregated items.
    """
    # The startup event triggers a background fetch. We wait a moment for it to complete.
    await asyncio.sleep(0.1)

    # Make a request to our API.
    response = await test_client.get("/items/all")
    assert response.status_code == 200
    items = response.json()
    
    # We should have 3 items in total from the two successful mocked streams.
    # The streams that returned a 500 error or an empty list should be ignored.
    assert len(items) == 3
    
    # Verify that the items are sorted by date (newest first), as per the requirement.
    assert items[0]["data"] == "data3"  # From stream2, newest @ 13:00
    assert items[1]["data"] == "data1"  # From stream1, middle @ 12:00
    assert items[2]["data"] == "data2"  # From stream1, oldest @ 11:00


@pytest.mark.anyio
async def test_subscription_flow(test_client: AsyncClient):
    """
    Tests the full end-to-end user subscription and retrieval process.
    """
    # Wait for the initial data fetch to populate the database.
    await asyncio.sleep(0.1)

    # 1. Subscribe a user to the 'news' topic.
    sub_response = await test_client.post(
        "/subscriptions",
        json={"user_id": "testuser", "topic": "news"}
    )
    assert sub_response.status_code == 201
    assert sub_response.json()["message"] == "User testuser subscribed to topic news"

    # 2. Fetch subscribed items for that user and verify only the 'news' item is returned.
    items_response = await test_client.get("/items/subscribed/testuser")
    assert items_response.status_code == 200
    items = items_response.json()

    assert len(items) == 1
    assert items[0]["topic"] == "news"
    assert items[0]["data"] == "data1"

    # 3. Subscribe the same user to another topic, 'food'.
    await test_client.post(
        "/subscriptions",
        json={"user_id": "testuser", "topic": "food"}
    )

    # 4. Fetch subscribed items again. Now it should return both 'news' and 'food' items.
    items_response_2 = await test_client.get("/items/subscribed/testuser")
    assert items_response_2.status_code == 200
    items_2 = items_response_2.json()
    
    # Items should still be sorted by date, so 'food' comes first.
    assert len(items_2) == 2
    assert items_2[0]["topic"] == "food"
    assert items_2[1]["topic"] == "news"
    
    # A more robust check is to look at the set of topics.
    topics_in_response = {item['topic'] for item in items_2}
    assert topics_in_response == {"news", "food"}