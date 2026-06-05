# AnomlyX Backend

FastAPI backend for the future ML image diagnosis workflow.

This version gives the frontend a prediction API before the model is trained:

- `GET /health` checks dataset/model configuration.
- `GET /classes` reads defect folders from `Defect_Dataset`.
- `POST /predict` accepts a JPG, PNG, or WEBP image and returns a prediction-shaped response.

Until a trained model is connected, `/predict` uses a small filename stub. For example, uploading `high-crack.jpg` returns `Crack` and `high` with low confidence. This is only for API testing.

The root frontend posts uploaded images to `http://127.0.0.1:8001/predict` and applies the returned `defect` and `severity` to the diagnosis/report UI.

## Setup

Install Python 3.11 or newer, then run:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8001/docs
```

## Test Prediction

Use the Swagger page at `/docs`, or run:

```bash
curl -X POST "http://127.0.0.1:8001/predict" -F "file=@../assets/defects/high-crack.png"
```

## Environment

Copy `.env.example` if you want custom paths:

```text
ANOMLYX_DATASET_DIR=../Defect_Dataset
ANOMLYX_MODEL_PATH=
ANOMLYX_MAX_UPLOAD_MB=10
```

## Model Hook

Connect the real model inside `app/predictor.py` in `predict_image()`.
Keep the returned JSON fields stable:

```json
{
  "defect": "Crack",
  "severity": "high",
  "confidence": 0.94,
  "model_ready": true
}
```
