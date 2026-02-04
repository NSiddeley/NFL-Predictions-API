from fastapi import FastAPI
from routes.nfl_predictions_routes import nfl_predictions_router
from routes.ml_models_routes import models_router
from database import client
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Test MongoDB connection on startup"""
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

    yield

    # Close MongoDB connection on shutdown
    client.close()
    print("MongoDB connection closed")

app = FastAPI(
    title="NFL Predictions API",
    description="API for managing NFL game predictions",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(nfl_predictions_router, prefix="/nflpredictions", tags=["NFL predictions"])
app.include_router(models_router, prefix="/models", tags=["ML model packages"])

@app.get("/")
async def root():
    return {"message": "Welcome to NFL Predictions API"}