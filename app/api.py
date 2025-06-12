from fastapi import FastAPI

# Instantiate the FastAPI application
app = FastAPI(
    title="Data Aggregator Service",
    description="A simple service to aggregate data from multiple sources.",
    version="0.0.1",
)

@app.get("/")
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"status": "ok", "message": "Welcome to the Data Aggregator API!"}