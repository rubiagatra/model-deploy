from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

# --- Model Training ---
# For this demonstration, we'll train a simple model on application startup.
# In a real-world application, you would load a pre-trained model file
# (e.g., using joblib or pickle).
iris = load_iris()
X, y = iris.data, iris.target

# Train a simple logistic regression model
model = LogisticRegression(max_iter=200)
model.fit(X, y)

# Get the target names (e.g., "setosa", "versicolor", "virginica")
target_names = iris.target_names

# --- FastAPI Application ---
app = FastAPI(
    title="Iris Species Predictor API",
    description="A simple API to predict the species of an Iris flower based on its measurements.",
    version="1.0.0",
)

# --- API Data Models ---
# Pydantic model for the input features
class IrisFeatures(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

    class Config:
        # Provide an example for the API documentation
        schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        }

# Pydantic model for the prediction output
class Prediction(BaseModel):
    predicted_species: str
    predicted_class_id: int

# --- API Endpoints ---
@app.get("/")
def read_root():
    """A welcome message for the API root."""
    return {"message": "Welcome to the Iris Prediction API. Navigate to /docs for a full API specification."}

@app.post("/predict", response_model=Prediction)
def predict_species(features: IrisFeatures):
    """
    Predicts the Iris species from input flower measurements.
    
    - **sepal_length**: Length of the sepal (cm)
    - **sepal_width**: Width of the sepal (cm)
    - **petal_length**: Length of the petal (cm)
    - **petal_width**: Width of the petal (cm)
    
    Returns the predicted species name and its corresponding class ID.
    """
    # Convert input data from the request into a numpy array for the model
    input_data = np.array([[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width
    ]])
    
    # Make a prediction using the trained model
    predicted_class_id = model.predict(input_data)[0]
    predicted_species = target_names[predicted_class_id]
    
    return {
        "predicted_species": predicted_species,
        "predicted_class_id": int(predicted_class_id)
    }

