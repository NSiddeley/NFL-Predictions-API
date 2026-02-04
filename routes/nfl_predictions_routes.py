from fastapi import APIRouter, Query, status, Request
from fastapi.responses import JSONResponse
from models.predictions import Prediction, CreatePredictionRequest
from services.nfl_predictions_services import (
    get_all_predictions,
    get_prediction_by_id,
    get_predictions_by_params,
    get_predictions_by_season_week,
    get_predictions_by_team,
    create_prediction,
    update_prediction,
    delete_prediction,
    delete_all
)
from typing import Optional, List

nfl_predictions_router = APIRouter()

# CREATE - Add a new prediction
@nfl_predictions_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Prediction, response_class=JSONResponse)
def add_prediction(request: Request, payload: CreatePredictionRequest):
    """
    Create a new NFL game prediction

    - **season**: NFL season year
    - **week**: Week number (1-18 for regular season)
    - **home_team**: Home team name
    - **away_team**: Away team name
    - **home_win**: Predicted winner (True if home team wins)
    - **confidence**: Confidence level (0.0 to 1.0)
    - **model_used**: Name of the prediction model
    - **is_correct**: Whether prediction was correct (None if game not concluded)
    """
    try:
        new_prediction = create_prediction(payload)
        return JSONResponse(content=new_prediction, status_code=201)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# READ - Get all predictions with optional filters
@nfl_predictions_router.get("/", status_code=status.HTTP_200_OK, response_model=List[Prediction], response_class=JSONResponse)
def get_predictions(
    request: Request,
    season: Optional[int] = Query(None, description="Filter by season"),
    week: Optional[int] = Query(None, description="Filter by week"),
    team: Optional[str] = Query(None, description="Filter by team (home or away)")
):
    """
    Retrieve all predictions with optional filters

    - **season**: Filter by specific season
    - **week**: Filter by specific week
    - **team**: Filter by team name
    """
    try:
        if season or week or team:
            predictions = get_predictions_by_params(season=season,
                                                    week=week,
                                                    team=team)
        else:
            predictions = get_all_predictions()

        return JSONResponse(content=predictions, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# READ - Get a single prediction by ID
@nfl_predictions_router.get("/{prediction_id}", status_code=status.HTTP_200_OK, response_model=Prediction, response_class=JSONResponse)
def get_prediction(request: Request, prediction_id: str):
    """
    Retrieve a specific prediction by its ID

    - **prediction_id**: MongoDB ObjectId of the prediction
    """
    try:
        prediction = get_prediction_by_id(prediction_id)
        
        return JSONResponse(content=prediction, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# UPDATE - Update an existing prediction
@nfl_predictions_router.put("/{prediction_id}", status_code=status.HTTP_200_OK, response_model=Prediction, response_class=JSONResponse)
def update_prediction_route(request: Request, prediction_id: str, prediction: CreatePredictionRequest):
    """
    Update an existing prediction

    - **prediction_id**: MongoDB ObjectId of the prediction to update
    - All prediction fields will be updated with the provided values
    """
    try:
        updated_prediction = update_prediction(prediction_id, prediction)

        return JSONResponse(content=updated_prediction, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
@nfl_predictions_router.delete("/deleteall", status_code=status.HTTP_200_OK, response_class=JSONResponse)
def delete_all_route(request: Request):
    """
    Delete all documents in the predictions collection
    FOR TESTING ONLY
    """
    try:
        success = delete_all()

        return JSONResponse(content={"was_deleted": success}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# DELETE - Delete a prediction
@nfl_predictions_router.delete("/{prediction_id}", status_code=status.HTTP_200_OK, response_model=dict, response_class=JSONResponse)
def delete_prediction_route(request: Request, prediction_id: str):
    """
    Delete a prediction by its ID

    - **prediction_id**: MongoDB ObjectId of the prediction to delete
    """
    try:
        success = delete_prediction(prediction_id)

        return JSONResponse(content={"pred_id": prediction_id, "was_deleted": success}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
