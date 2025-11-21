from database import predictions
from models.predictions import Prediction, CreatePredictionRequest
from bson import ObjectId
from typing import Optional

def individual_serial(prediction) -> dict:
    """Convert a MongoDB document to a dictionary and return it as a Prediction Pydantic model"""
    return {
        "pred_id": str(prediction["_id"]),
        "season": prediction["season"],
        "week": prediction["week"],
        "home_team": prediction["home_team"],
        "away_team": prediction["away_team"],
        "home_win": prediction["home_win"],
        "confidence": prediction["confidence"],
        "model_used": prediction["model_used"],
        "is_correct": prediction.get("is_correct")  # Use .get() to handle None/missing values
    }

def list_serial(prediction_list) -> list[dict]:
    """Convert a list of MongoDB documents to Prediction Pydantic models"""
    return [individual_serial(pred) for pred in prediction_list]

def get_all_predictions() -> list[dict]:
    """Retrieve all predictions from the database"""
    all_predictions = predictions.find({})
    count = predictions.count_documents({})

    if all_predictions is None or count == 0:
        raise ValueError("No predictions found")
    
    return list_serial(all_predictions)

def get_prediction_by_id(prediction_id: str) -> dict:
    """Retrieve a single prediction by ID"""
    prediction = predictions.find_one({"_id": ObjectId(prediction_id)})

    if prediction is None:
        raise ValueError(f"Prediction with id: {prediction_id} not found") 
    
    return individual_serial(prediction)

def get_predictions_by_params(season: Optional[int] = None, week: Optional[int] = None, team: Optional[str] = None) -> list[dict]:
    query = {}

    if season:
        query["season"] = season
    if week:
        query["week"] = week
    if team:
        query["$or"] = [{"home_team": team}, {"away_team": team}]

    filterered_predictions = predictions.find(query)
    count = predictions.count_documents(query)

    if filterered_predictions is None or count == 0:
        raise ValueError(f"No predictions found with the given parameters")
    
    return list_serial(filterered_predictions)
        

def get_predictions_by_season_week(season: int, week: int) -> list[dict]:
    """Retrieve predictions filtered by season and week"""
    query = {"season": season, "week": week}

    filtered_predictions = predictions.find(query)
    count = predictions.count_documents(query)

    if filtered_predictions is None or count == 0:
        raise ValueError(f"No predictions found for week {week} of the {season} NFL season")
    
    return list_serial(filtered_predictions)

def get_predictions_by_team(team: str) -> list[dict]:
    """Retrieve predictions where a team is playing (home or away)"""
    query = {
        "$or": [
            {"home_team": team},
            {"away_team": team}
        ]
    }

    filtered_predictions = predictions.find(query)
    count = predictions.count_documents(query)

    if filtered_predictions is None or count == 0:
        raise ValueError(f"No predictions found including {team}")
    
    return list_serial(filtered_predictions)

def create_prediction(prediction: CreatePredictionRequest) -> dict:
    """Create a new prediction in the database"""
    prediction_dict = prediction.model_dump()
    result = predictions.insert_one(prediction_dict)

    if result is None:
        raise ValueError("Error creating prediction")
    
    prediction_dict["_id"] = result.inserted_id

    return individual_serial(prediction_dict)

def update_prediction(prediction_id: str, prediction: CreatePredictionRequest) -> dict:
    """Update an existing prediction"""

    prediction_dict = prediction.model_dump()
    result = predictions.find_one_and_update(
        {"_id": ObjectId(prediction_id)},
        {"$set": prediction_dict},
        return_document=True
    )
    if result is None:
        raise ValueError(f"Prediction with id: {prediction_id} not found")
    
    return individual_serial(result)


def delete_prediction(prediction_id: str) -> bool:
    """Delete a prediction by ID"""
    result = predictions.delete_one({"_id": ObjectId(prediction_id)})
    
    if result.deleted_count == 0:
        raise ValueError(f"Prediction with id: {prediction_id} not found")
    
    return result.deleted_count > 0

def delete_all() -> bool:
    result = predictions.delete_many({})

    if result.deleted_count == 0:
        raise ValueError(f"No predictions deleted")
    
    return result.deleted_count > 0
