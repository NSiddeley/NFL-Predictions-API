from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Establish connection to MongoDB
client = MongoClient(MONGO_URI)
# Access the database
db = client[DB_NAME]

# Pointer to nfl_predictions collection
nfl_predictions = db["nfl_predictions"]
# Poointer to nba_predictions collection
nba_predictions = db["nba_predictions"]
# Pointer to ml_models collection
ml_models = db["ml_models"]
# Pointer to test collection
test_collection = db["test"]