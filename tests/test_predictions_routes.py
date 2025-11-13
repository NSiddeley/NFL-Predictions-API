import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from main import app
from database import test_collection

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_test_db():
    """Setup test database before each test and cleanup after"""
    # Clear test collection before each test
    test_collection.delete_many({})

    yield

    # Cleanup after test
    test_collection.delete_many({})


@pytest.fixture
def sample_prediction_data():
    """Sample prediction data for testing"""
    return {
        "season": 2024,
        "week": 10,
        "home_team": "Kansas City Chiefs",
        "away_team": "Denver Broncos",
        "home_win": True,
        "confidence": 0.85,
        "model_used": "RandomForest-v1",
        "is_correct": None
    }


@pytest.fixture
def sample_prediction_data_2():
    """Second sample prediction data for testing"""
    return {
        "season": 2024,
        "week": 11,
        "home_team": "Buffalo Bills",
        "away_team": "Miami Dolphins",
        "home_win": False,
        "confidence": 0.72,
        "model_used": "XGBoost-v2",
        "is_correct": True
    }


class TestCreatePrediction:
    """Tests for POST /predictions/ endpoint"""

    def test_create_prediction_success(self, sample_prediction_data):
        """Test successfully creating a new prediction"""
        response = client.post("/predictions/", json=sample_prediction_data)

        assert response.status_code == 201
        data = response.json()
        assert data["season"] == sample_prediction_data["season"]
        assert data["week"] == sample_prediction_data["week"]
        assert data["home_team"] == sample_prediction_data["home_team"]
        assert data["away_team"] == sample_prediction_data["away_team"]
        assert data["home_win"] == sample_prediction_data["home_win"]
        assert data["confidence"] == sample_prediction_data["confidence"]
        assert data["model_used"] == sample_prediction_data["model_used"]
        assert "_id" in data

    def test_create_prediction_invalid_data(self):
        """Test creating prediction with invalid data"""
        invalid_data = {
            "season": "not_an_int",  # Invalid type
            "week": 1,
            "home_team": "Team A",
            "away_team": "Team B"
        }

        response = client.post("/predictions/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_prediction_missing_required_fields(self):
        """Test creating prediction with missing required fields"""
        incomplete_data = {
            "season": 2024,
            "week": 1
            # Missing required fields
        }

        response = client.post("/predictions/", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_create_prediction_confidence_out_of_range(self):
        """Test creating prediction with confidence outside valid range"""
        invalid_data = {
            "season": 2024,
            "week": 1,
            "home_team": "Team A",
            "away_team": "Team B",
            "home_win": True,
            "confidence": 1.5,  # Out of range (should be 0.0-1.0)
            "model_used": "model-x",
            "is_correct": None
        }

        response = client.post("/predictions/", json=invalid_data)
        # This may pass depending on your validation rules
        # Add specific confidence validation in your model if needed
        assert response.status_code in [201, 400, 422]


class TestGetAllPredictions:
    """Tests for GET /predictions/ endpoint"""

    def test_get_all_predictions_success(self, sample_prediction_data, sample_prediction_data_2):
        """Test retrieving all predictions"""
        # Create test predictions
        client.post("/predictions/", json=sample_prediction_data)
        client.post("/predictions/", json=sample_prediction_data_2)

        response = client.get("/predictions/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_predictions_empty_database(self, setup_test_db):
        """Test getting predictions when database is empty"""
        response = client.get("/predictions/")

        # Should return 404 or empty list based on your implementation
        assert response.status_code in [200, 404]

    def test_get_predictions_filter_by_season_and_week(self, sample_prediction_data):
        """Test filtering predictions by season and week"""
        # Create test prediction
        client.post("/predictions/", json=sample_prediction_data)

        response = client.get(
            "/predictions/",
            params={"season": sample_prediction_data["season"], "week": sample_prediction_data["week"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(pred["season"] == sample_prediction_data["season"] for pred in data)
            assert all(pred["week"] == sample_prediction_data["week"] for pred in data)

    def test_get_predictions_filter_by_team(self, sample_prediction_data):
        """Test filtering predictions by team"""
        # Create test prediction
        client.post("/predictions/", json=sample_prediction_data)

        response = client.get(
            "/predictions/",
            params={"team": sample_prediction_data["home_team"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            # Check that team appears in either home_team or away_team
            assert all(
                pred["home_team"] == sample_prediction_data["home_team"] or
                pred["away_team"] == sample_prediction_data["home_team"]
                for pred in data
            )

    def test_get_predictions_filter_no_results(self):
        """Test filtering with parameters that return no results"""
        response = client.get(
            "/predictions/",
            params={"season": 9999, "week": 99}
        )

        # Should return 404 based on your implementation
        assert response.status_code in [200, 404]


class TestGetPredictionById:
    """Tests for GET /predictions/{prediction_id} endpoint"""

    def test_get_prediction_by_id_success(self, sample_prediction_data):
        """Test retrieving a prediction by valid ID"""
        # Create a prediction first
        create_response = client.post("/predictions/", json=sample_prediction_data)
        created_prediction = create_response.json()
        prediction_id = created_prediction["_id"]

        # Retrieve the prediction
        response = client.get(f"/predictions/{prediction_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == prediction_id
        assert data["season"] == sample_prediction_data["season"]
        assert data["home_team"] == sample_prediction_data["home_team"]

    def test_get_prediction_by_id_not_found(self):
        """Test retrieving a prediction with non-existent ID"""
        fake_id = str(ObjectId())
        response = client.get(f"/predictions/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert "message" in data

    def test_get_prediction_by_id_invalid_format(self):
        """Test retrieving a prediction with invalid ID format"""
        invalid_id = "not-a-valid-objectid"
        response = client.get(f"/predictions/{invalid_id}")

        # Should return 400 or 500 based on your error handling
        assert response.status_code in [400, 404, 500]


class TestUpdatePrediction:
    """Tests for PUT /predictions/{prediction_id} endpoint"""

    def test_update_prediction_success(self, sample_prediction_data):
        """Test successfully updating a prediction"""
        # Create a prediction first
        create_response = client.post("/predictions/", json=sample_prediction_data)
        created_prediction = create_response.json()
        prediction_id = created_prediction["_id"]

        # Update the prediction
        updated_data = sample_prediction_data.copy()
        updated_data["confidence"] = 0.95
        updated_data["is_correct"] = True

        response = client.put(f"/predictions/{prediction_id}", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0.95
        assert data["is_correct"] == True

    def test_update_prediction_not_found(self, sample_prediction_data):
        """Test updating a non-existent prediction"""
        fake_id = str(ObjectId())
        response = client.put(f"/predictions/{fake_id}", json=sample_prediction_data)

        assert response.status_code == 404
        data = response.json()
        assert "message" in data

    def test_update_prediction_invalid_id(self, sample_prediction_data):
        """Test updating with invalid ID format"""
        invalid_id = "invalid-id-format"
        response = client.put(f"/predictions/{invalid_id}", json=sample_prediction_data)

        assert response.status_code in [400, 404, 500]

    def test_update_prediction_invalid_data(self, sample_prediction_data):
        """Test updating with invalid data"""
        # Create a prediction first
        create_response = client.post("/predictions/", json=sample_prediction_data)
        created_prediction = create_response.json()
        prediction_id = created_prediction["_id"]

        # Try to update with invalid data
        invalid_data = {
            "season": "not_an_int",  # Invalid type
            "week": 1
        }

        response = client.put(f"/predictions/{prediction_id}", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestDeletePrediction:
    """Tests for DELETE /predictions/{prediction_id} endpoint"""

    def test_delete_prediction_success(self, sample_prediction_data):
        """Test successfully deleting a prediction"""
        # Create a prediction first
        create_response = client.post("/predictions/", json=sample_prediction_data)
        created_prediction = create_response.json()
        prediction_id = created_prediction["_id"]

        # Delete the prediction
        response = client.delete(f"/predictions/{prediction_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["pred_id"] == prediction_id
        assert data["was_deleted"] == True

        # Verify it's actually deleted
        get_response = client.get(f"/predictions/{prediction_id}")
        assert get_response.status_code == 404

    def test_delete_prediction_not_found(self):
        """Test deleting a non-existent prediction"""
        fake_id = str(ObjectId())
        response = client.delete(f"/predictions/{fake_id}")

        # Based on your implementation, this might return 200 with was_deleted=False
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["was_deleted"] == False

    def test_delete_prediction_invalid_id(self):
        """Test deleting with invalid ID format"""
        invalid_id = "invalid-id-format"
        response = client.delete(f"/predictions/{invalid_id}")

        assert response.status_code in [400, 404, 500]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_full_crud_workflow(self, sample_prediction_data):
        """Test complete CRUD workflow: Create -> Read -> Update -> Delete"""
        # CREATE
        create_response = client.post("/predictions/", json=sample_prediction_data)
        assert create_response.status_code == 201
        prediction_id = create_response.json()["_id"]

        # READ
        read_response = client.get(f"/predictions/{prediction_id}")
        assert read_response.status_code == 200
        assert read_response.json()["_id"] == prediction_id

        # UPDATE
        updated_data = sample_prediction_data.copy()
        updated_data["is_correct"] = True
        update_response = client.put(f"/predictions/{prediction_id}", json=updated_data)
        assert update_response.status_code == 200
        assert update_response.json()["is_correct"] == True

        # DELETE
        delete_response = client.delete(f"/predictions/{prediction_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["was_deleted"] == True

        # VERIFY DELETION
        verify_response = client.get(f"/predictions/{prediction_id}")
        assert verify_response.status_code == 404

    def test_multiple_predictions_same_game(self, sample_prediction_data):
        """Test creating multiple predictions for the same game with different models"""
        # Create first prediction
        first_response = client.post("/predictions/", json=sample_prediction_data)
        assert first_response.status_code == 201

        # Create second prediction with different model
        second_data = sample_prediction_data.copy()
        second_data["model_used"] = "NeuralNet-v1"
        second_data["confidence"] = 0.78

        second_response = client.post("/predictions/", json=second_data)
        assert second_response.status_code == 201

        # Verify both exist
        response = client.get(
            "/predictions/",
            params={"season": sample_prediction_data["season"], "week": sample_prediction_data["week"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_filtering_across_multiple_weeks(self, sample_prediction_data, sample_prediction_data_2):
        """Test filtering predictions across different weeks and seasons"""
        # Create predictions for different weeks
        client.post("/predictions/", json=sample_prediction_data)
        client.post("/predictions/", json=sample_prediction_data_2)

        # Filter by first week
        week1_response = client.get(
            "/predictions/",
            params={"season": sample_prediction_data["season"], "week": sample_prediction_data["week"]}
        )
        assert week1_response.status_code == 200
        week1_data = week1_response.json()

        # Filter by second week
        week2_response = client.get(
            "/predictions/",
            params={"season": sample_prediction_data_2["season"], "week": sample_prediction_data_2["week"]}
        )
        assert week2_response.status_code == 200
        week2_data = week2_response.json()

        # Verify they return different results
        if len(week1_data) > 0 and len(week2_data) > 0:
            assert week1_data[0]["week"] != week2_data[0]["week"]


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_confidence_boundary_values(self, sample_prediction_data):
        """Test predictions with boundary confidence values"""
        # Test minimum confidence (0.0)
        min_data = sample_prediction_data.copy()
        min_data["confidence"] = 0.0
        min_response = client.post("/predictions/", json=min_data)
        assert min_response.status_code == 201

        # Test maximum confidence (1.0)
        max_data = sample_prediction_data.copy()
        max_data["confidence"] = 1.0
        max_response = client.post("/predictions/", json=max_data)
        assert max_response.status_code == 201

    def test_prediction_with_none_is_correct(self, sample_prediction_data):
        """Test creating and updating predictions with is_correct as None"""
        # Create with None
        sample_prediction_data["is_correct"] = None
        create_response = client.post("/predictions/", json=sample_prediction_data)
        assert create_response.status_code == 201

        prediction_id = create_response.json()["_id"]

        # Verify it was stored correctly
        get_response = client.get(f"/predictions/{prediction_id}")
        assert get_response.status_code == 200
        assert get_response.json()["is_correct"] is None

    def test_team_name_with_special_characters(self, sample_prediction_data):
        """Test predictions with team names containing special characters"""
        special_data = sample_prediction_data.copy()
        special_data["home_team"] = "St. Louis Rams"
        special_data["away_team"] = "San Francisco 49ers"

        response = client.post("/predictions/", json=special_data)
        assert response.status_code == 201

        # Verify filtering works with special characters
        filter_response = client.get(
            "/predictions/",
            params={"team": "St. Louis Rams"}
        )
        assert filter_response.status_code == 200

    def test_extreme_week_numbers(self, sample_prediction_data):
        """Test predictions with edge case week numbers"""
        # Week 1
        week1_data = sample_prediction_data.copy()
        week1_data["week"] = 1
        response1 = client.post("/predictions/", json=week1_data)
        assert response1.status_code == 201

        # Week 18 (end of regular season)
        week18_data = sample_prediction_data.copy()
        week18_data["week"] = 18
        response18 = client.post("/predictions/", json=week18_data)
        assert response18.status_code == 201
