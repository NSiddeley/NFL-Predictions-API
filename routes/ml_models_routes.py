from fastapi import APIRouter, Query, status, Request
from fastapi.responses import JSONResponse
from models.ml_model_packages import MLModelPackage, CreateMLModelPackageRequest
from services.model_package_services import (
    get_all_model_packages,
    get_model_package_by_id,
    get_model_by_package_label,
    get_model_package_by_train_date,
    get_model_package_by_params,
    create_model_package,
    update_model_package,
    delete_model_package
)
from typing import Optional, List

models_router = APIRouter()

# CREATE - Add a new ML model package
@models_router.post("/", status_code=status.HTTP_201_CREATED, response_model=MLModelPackage, response_class=JSONResponse)
def add_model_package(request: Request, payload: CreateMLModelPackageRequest):
    """
    Create a new ML model package

    - **package_label**: Model package label
    - **model**: Trained ML model
    - **model_features**: List of features the model will accept
    - **model_scores**: Accuracy scores for the model
    - **dataset**: Dataset the model was trained on
    - **model_target**: Target column for the model
    - **date_trained**: Date the model was trained on (MM-DD-YYYY)
    """
    try:
        new_package = create_model_package(payload)
        return JSONResponse(content=new_package, status_code=201)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
# READ - Get all packages with optional filters
@models_router.get("/", status_code=status.HTTP_200_OK, response_model=List[MLModelPackage], response_class=JSONResponse)
def get_packages(
    request: Request,
    date_trained: Optional[str] = Query(None, description="Filter by date model was trained ('MM-DD-YYYY')"),
    label: Optional[str] = Query(None, description="Filter by model package label")
):
    """
    Retrieve all packages with optional filters

    - **date_trained**: Filter by date model was trained on (MM-DD-YYYY)
    - **label**: Filter by model package label
    """
    try:
        if date_trained or label:
            packages = get_model_package_by_params(date=date_trained,
                                                    label=label)
        else:
            packages = get_all_model_packages()

        return JSONResponse(content=packages, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# READ - Get a single package by ID
@models_router.get("/{package_id}", status_code=status.HTTP_200_OK, response_model=MLModelPackage, response_class=JSONResponse)
def get_package(request: Request, package_id: str):
    """
    Retrieve a specific model package by its ID

    - **package_id**: MongoDB ObjectId of the package
    """
    try:
        package = get_model_package_by_id(package_id)

        return JSONResponse(content=package, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# UPDATE - update an existing model package
@models_router.put("/{package_id}", status_code=status.HTTP_200_OK, response_model=MLModelPackage, response_class=JSONResponse)
def update_package(request: Request, package_id: str, package: CreateMLModelPackageRequest):
    """
    Update an existing model package

    - **package_id**: MongoDB ObjectId of the package to be updated
    - All prediction fields will be updated with the provided values
    """
    try:
        updated_package = update_model_package(package_id, package)

        return JSONResponse(content=updated_package, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
# DELETE - deleate a model package
@models_router.delete("/{package_id}", status_code=status.HTTP_200_OK, response_model=dict, response_class=JSONResponse)
def delete_package(request: Request, package_id: str):
    """
    Delete a package by its ID

    - **package_id**: MongoDB coument ID of the package to be deleted
    """
    try:
        success = delete_model_package(package_id)

        return JSONResponse(content={"package_id": package_id, "was_deleted": success}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)