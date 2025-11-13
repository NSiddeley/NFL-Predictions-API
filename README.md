# NFL Predictions API

A RESTful API built with FastAPI for managing and tracking NFL game predictions. This API provides endpoints for storing, retrieving, updating, and analyzing machine learning model predictions for NFL games.

## Overview

The NFL Predictions API serves as the backend for NFL prediction applications, enabling developers to integrate prediction tracking, model performance monitoring, and historical prediction analysis into their web applications.

## Features

- **CRUD Operations**: Create, read, update, and delete NFL game predictions
- **Advanced Filtering**: Query predictions by season, week, or team
- **Model Tracking**: Track which ML model generated each prediction
- **Confidence Scoring**: Store and retrieve confidence levels for each prediction
- **Result Validation**: Track prediction accuracy after games conclude
- **Data Validation**: Robust input validation using Pydantic models
- **MongoDB Integration**: Scalable NoSQL database for storing predictions
- **Auto-Generated Documentation**: Interactive API documentation via Swagger UI
- **RESTful Design**: Standard HTTP methods and status codes
- **Type Safety**: Full type hints and schema validation

## Tech Stack

- **Framework**: FastAPI (Python 3.13+)
- **Database**: MongoDB
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI)
- **Testing**: Pytest with async support

## API Documentation

### Base URL

```
Production: https://your-api-domain.com
Development: http://localhost:8000
```

### Interactive Documentation

Once deployed, access the interactive API documentation:

- **Swagger UI**: `{BASE_URL}/docs`
- **ReDoc**: `{BASE_URL}/redoc`

## Endpoints

### Root Endpoint

#### Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to NFL Predictions API"
}
```

---

### Predictions Endpoints

#### Get All Predictions

Retrieve all predictions with optional filtering.

```http
GET /predictions/
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `season` | integer | No | Filter by NFL season year (e.g., 2024) |
| `week` | integer | No | Filter by week number (1-22) |
| `team` | string | No | Filter by team name (matches home or away) |

**Example Requests:**

```http
# Get all predictions
GET /predictions/

# Get predictions for Week 10 of 2024 season
GET /predictions/?season=2024&week=10

# Get all predictions involving the Chiefs
GET /predictions/?team=Kansas%20City%20Chiefs
```

**Response (200 OK):**
```json
[
  {
    "pred_id": "507f1f77bcf86cd799439011",
    "season": 2024,
    "week": 10,
    "home_team": "Kansas City Chiefs",
    "away_team": "Denver Broncos",
    "home_win": true,
    "confidence": 0.85,
    "model_used": "RandomForest-v1",
    "is_correct": true
  }
]
```

**Error Responses:**
- `404 Not Found` - No predictions match the filter criteria
- `500 Internal Server Error` - Server error

---

#### Get Prediction by ID

Retrieve a specific prediction by its unique identifier.

```http
GET /predictions/{prediction_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prediction_id` | string | Yes | MongoDB ObjectId of the prediction |

**Example Request:**

```http
GET /predictions/507f1f77bcf86cd799439011
```

**Response (200 OK):**
```json
{
  "pred_id": "507f1f77bcf86cd799439011",
  "season": 2024,
  "week": 10,
  "home_team": "Kansas City Chiefs",
  "away_team": "Denver Broncos",
  "home_win": true,
  "confidence": 0.85,
  "model_used": "RandomForest-v1",
  "is_correct": true
}
```

**Error Responses:**
- `404 Not Found` - Prediction not found
- `500 Internal Server Error` - Server error

---

#### Create Prediction

Create a new NFL game prediction.

```http
POST /predictions/
```

**Request Body:**

```json
{
  "season": 2024,
  "week": 10,
  "home_team": "Kansas City Chiefs",
  "away_team": "Denver Broncos",
  "home_win": true,
  "confidence": 0.85,
  "model_used": "RandomForest-v1",
  "is_correct": null
}
```

**Response (201 Created):**
```json
{
  "pred_id": "507f1f77bcf86cd799439011",
  "season": 2024,
  "week": 10,
  "home_team": "Kansas City Chiefs",
  "away_team": "Denver Broncos",
  "home_win": true,
  "confidence": 0.85,
  "model_used": "RandomForest-v1",
  "is_correct": null
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data (validation error)
- `500 Internal Server Error` - Server error

---

#### Update Prediction

Update an existing prediction.

```http
PUT /predictions/{prediction_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prediction_id` | string | Yes | MongoDB ObjectId of the prediction |

**Request Body:**

```json
{
  "season": 2024,
  "week": 10,
  "home_team": "Kansas City Chiefs",
  "away_team": "Denver Broncos",
  "home_win": true,
  "confidence": 0.85,
  "model_used": "RandomForest-v1",
  "is_correct": true
}
```

**Response (200 OK):**
```json
{
  "pred_id": "507f1f77bcf86cd799439011",
  "season": 2024,
  "week": 10,
  "home_team": "Kansas City Chiefs",
  "away_team": "Denver Broncos",
  "home_win": true,
  "confidence": 0.85,
  "model_used": "RandomForest-v1",
  "is_correct": true
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Prediction not found
- `500 Internal Server Error` - Server error

---

#### Delete Prediction

Delete a specific prediction.

```http
DELETE /predictions/{prediction_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prediction_id` | string | Yes | MongoDB ObjectId of the prediction |

**Response (200 OK):**
```json
{
  "pred_id": "507f1f77bcf86cd799439011",
  "was_deleted": true
}
```

**Error Responses:**
- `404 Not Found` - Prediction not found
- `500 Internal Server Error` - Server error

---

## Data Models

### Prediction Schema

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `pred_id` | string | Yes* | Unique prediction identifier | Auto-generated (MongoDB ObjectId) |
| `season` | integer | Yes | NFL season year | 1920-2050 |
| `week` | integer | Yes | Week number | 1-22 (1-18 regular season, 19-22 playoffs) |
| `home_team` | string | Yes | Home team name | 1-100 characters |
| `away_team` | string | Yes | Away team name | 1-100 characters, must differ from home_team |
| `home_win` | boolean | Yes | Predicted winner | `true` if home team wins, `false` if away team wins |
| `confidence` | float | Yes | Prediction confidence | 0.0-1.0 (0 = no confidence, 1 = complete confidence) |
| `model_used` | string | Yes | ML model identifier | 1-100 characters |
| `is_correct` | boolean | No | Prediction accuracy | `null` before game, `true`/`false` after game concludes |

*`pred_id` is auto-generated on creation and returned in responses

### Validation Rules

The API enforces the following validation rules:

1. **Team Validation**
   - Home and away teams must be different
   - Team names must be 1-100 characters

2. **Season Validation**
   - Must be between 1920 (NFL founding) and 2050

3. **Week Validation**
   - Regular season: weeks 1-18
   - Playoffs: weeks 19-22

4. **Confidence Validation**
   - Must be a decimal value between 0.0 and 1.0
   - Represents probability (e.g., 0.85 = 85% confidence)

5. **Model Name**
   - Must be non-empty string (1-100 characters)
   - Used to track which ML model generated the prediction

## Integration Examples

### JavaScript/TypeScript (Fetch API)

```javascript
// Get predictions for Week 10, 2024 season
async function getPredictions() {
  const response = await fetch(
    'https://your-api-domain.com/predictions/?season=2024&week=10'
  );
  const predictions = await response.json();
  return predictions;
}

// Create a new prediction
async function createPrediction(predictionData) {
  const response = await fetch('https://your-api-domain.com/predictions/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(predictionData),
  });
  const newPrediction = await response.json();
  return newPrediction;
}

// Update prediction after game concludes
async function updatePredictionResult(predictionId, isCorrect) {
  const prediction = await fetch(`https://your-api-domain.com/predictions/${predictionId}`);
  const data = await prediction.json();

  data.is_correct = isCorrect;

  const response = await fetch(
    `https://your-api-domain.com/predictions/${predictionId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }
  );
  return await response.json();
}
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function PredictionsList() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPredictions() {
      try {
        const response = await fetch(
          'https://your-api-domain.com/predictions/?season=2024&week=10'
        );
        const data = await response.json();
        setPredictions(data);
      } catch (error) {
        console.error('Error fetching predictions:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchPredictions();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {predictions.map((pred) => (
        <div key={pred.pred_id}>
          <h3>{pred.home_team} vs {pred.away_team}</h3>
          <p>Prediction: {pred.home_win ? pred.home_team : pred.away_team}</p>
          <p>Confidence: {(pred.confidence * 100).toFixed(0)}%</p>
          <p>Model: {pred.model_used}</p>
          {pred.is_correct !== null && (
            <p>Result: {pred.is_correct ? '✅ Correct' : '❌ Incorrect'}</p>
          )}
        </div>
      ))}
    </div>
  );
}
```

### Python Example

```python
import requests

BASE_URL = "https://your-api-domain.com"

# Get all predictions for a team
def get_team_predictions(team_name):
    response = requests.get(
        f"{BASE_URL}/predictions/",
        params={"team": team_name}
    )
    return response.json()

# Create a new prediction
def create_prediction(prediction_data):
    response = requests.post(
        f"{BASE_URL}/predictions/",
        json=prediction_data
    )
    return response.json()

# Example usage
new_prediction = {
    "season": 2024,
    "week": 10,
    "home_team": "Kansas City Chiefs",
    "away_team": "Denver Broncos",
    "home_win": True,
    "confidence": 0.85,
    "model_used": "RandomForest-v1",
    "is_correct": None
}

result = create_prediction(new_prediction)
print(f"Created prediction with ID: {result['pred_id']}")
```

## Use Cases

### 1. Prediction Dashboard
Display all predictions for the current week with confidence scores and model information.

```javascript
GET /predictions/?season=2024&week=10
```

### 2. Team Analysis
Show historical prediction performance for a specific team.

```javascript
GET /predictions/?team=BAL
```

### 3. Model Performance Tracking
Filter predictions by model to analyze accuracy over time.

```javascript
GET /predictions/
// Filter client-side by model_used and calculate accuracy percentage
```

### 4. Live Updates
Update predictions with actual results as games conclude.

```javascript
PUT /predictions/{prediction_id}
// Set is_correct: true/false based on game outcome
```

### 5. Weekly Comparison
Compare predictions across different models for the same week.

```javascript
GET /predictions/?season=2024&week=10
// Group by game and compare model predictions
```

## HTTP Status Codes

The API uses standard HTTP status codes:

| Code | Description |
|------|-------------|
| `200` | Success (GET, PUT, DELETE) |
| `201` | Created (POST) |
| `400` | Bad Request - Invalid input data |
| `404` | Not Found - Resource doesn't exist |
| `500` | Internal Server Error |

## Error Response Format

All error responses follow this format:

```json
{
  "message": "Error description"
}
```

**Examples:**

```json
// Validation error
{
  "message": "Home team and away team must be different"
}

// Not found error
{
  "message": "Prediction with id: 507f1f77bcf86cd799439011 not found"
}

// No results error
{
  "message": "No predictions found for week 10 of the 2024 NFL season"
}
```

## Data Integrity

- **Idempotency**: PUT and DELETE operations are idempotent
- **Atomic Operations**: All database operations are atomic
- **Validation**: All inputs are validated server-side regardless of client validation
- **Type Safety**: Pydantic models ensure type consistency

## License

This project is licensed under the MIT License.

---

**API Version**: 1.0.0
**Last Updated**: 2024
**Built with FastAPI**
