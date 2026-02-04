from database import ml_models
from models.ml_model_packages import MLModelPackage, CreateMLModelPackageRequest
from bson import ObjectId
from typing import Optional

def individual_serial(model_package) -> dict:
    """Convert a MongoDB document to a dictionary and return it"""
    return {
        "package_id": str(model_package["_id"]),
        "package_label": model_package["package_label"],
        "model": model_package["model"],
        "model_features": model_package["model_features"],
        "model_scores": model_package["model_scores"],
        "dataset": model_package["dataset"],
        "model_target": model_package["model_target"],
        "date_trained": model_package["date_trained"]
    }

def list_serial(model_package_list) -> list[dict]:
    """Serialize a list of model package MongoDB documents"""
    return [individual_serial(pred) for pred in model_package_list]

def get_all_model_packages() -> list[dict]:
    """Retrieve all model packages from the database"""
    all_packages = ml_models.find({})
    count = ml_models.count_documents({})

    if all_packages is None or count == 0:
        raise ValueError(f"No model packages found")

def get_model_package_by_id(package_id: str) -> dict:
    """Retrieve a single model package by ID"""
    model_package = ml_models.find_one({"_id": ObjectId(package_id)})

    if model_package is None:
        raise ValueError(f"Prediction with id: {package_id} not found") 
    
    return individual_serial(model_package)

def get_model_package_by_params(date: Optional[str]=None, label: Optional[str]=None):
    """Retrieve model packages based on the given parameters"""
    query = {}

    if date:
        query["date_trained"] = date
    if label:
        query["package_label"] = label

    filtered_packages = ml_models.find(query)
    count = ml_models.count_documents(query)

    if filtered_packages is None or count == 0:
        raise ValueError(f"No model package found with the given parameters")

    return list_serial(filtered_packages)

def get_model_package_by_train_date(date: str) -> list[dict]:
    """Retrieve all model packages trained on a certain date"""
    filtered_packages = ml_models.find({"date_trained": date})
    count = ml_models.count_documents({"date_trained": date})

    if filtered_packages is None or count == 0:
        raise ValueError(f"No model packages found that were trained on {date}. \
                         Make sure date is formatted correctly ('MM-DD-YYYY')") 
    
    return list_serial(filtered_packages)

def get_model_by_package_label(label: str) -> dict:
    """Retrieve a model package by its label"""
    model_package = ml_models.find_one({"package_label": label})

    if model_package is None:
        raise ValueError(f"Model package with label {label} not found")
    
    return individual_serial(model_package)

def create_model_package(model_package: CreateMLModelPackageRequest) -> dict:
    """Create a new model package in the database"""
    package_dict = model_package.model_dump()
    result = ml_models.insert_one(package_dict)

    if result is None:
        raise ValueError("Error creating package")
    
    package_dict["_id"] = result.inserted_id

    return individual_serial(package_dict)

def update_model_package(package_id: str, model_package: CreateMLModelPackageRequest) -> dict:
    """Update an existing model package"""

    package_dict = model_package.model_dump()
    result = ml_models.find_one_and_update(
        {"_id": ObjectId(package_id)},
        {"$set": package_dict},
        return_document=True
    )
    if result is None:
        raise ValueError(f"Model package with id: {package_id} not found")
    
    return individual_serial(result)

def delete_model_package(package_id: str) -> bool:
    """Delete a model package by ID"""
    result = ml_models.delete_one({"_id": ObjectId(package_id)})

    if result.deleted_count == 0:
        raise ValueError(f"package with ID: {package_id} not found")

    return result.deleted_count > 0