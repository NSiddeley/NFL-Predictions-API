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

# Pointer to predictions collection
predictions = db["predictions"]
# Pointer to ml_models collection
ml_models = db["ml_models"]
# Pointer to test collection
test_collection = db["test"]