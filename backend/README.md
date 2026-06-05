# AnomlyX Backend

FastAPI backend for the AnomlyX ML image diagnosis workflow.

The trained model is committed at `../ml/saved_models/defect_classifier.keras`,
so teammates do **not** need to train the model before running the backend.
When the model file is present, `/predict` uses real TensorFlow/Keras inference.
If the model file is missing, the backend falls back to a small filename-based
placeholder so the API can still be tested.

- `GET /health` checks dataset/model configuration.
- `GET /classes` reads defect folders from `Defect_Dataset`.
- `POST /predict` accepts a JPG, PNG, or WEBP image and returns a prediction-shaped response.

The root frontend posts uploaded images to `http://127.0.0.1:8001/predict` and applies the returned `defect` and `severity` to the diagnosis/report UI.

## Setup

Use Python **3.10, 3.11, or 3.12** because TensorFlow may not publish wheels for
newer Python versions yet.

Linux/macOS:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Linux/macOS or Windows PowerShell:

```bash
uvicorn app.main:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8001/docs
```

## Frontend

Run the frontend from the project root in a second terminal.

Linux/macOS:

```bash
cd /path/to/AnomlyX
python3 -m http.server 8000
```

Windows PowerShell:

```powershell
cd C:\path\to\AnomlyX
py -m http.server 8000
```

Open:

```text
http://localhost:8000
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

The backend automatically detects:

```text
../ml/saved_models/defect_classifier.keras
```

Keep the returned JSON fields stable if the prediction implementation changes:

```json
{
  "defect": "Crack",
  "severity": "high",
  "confidence": 0.94,
  "model_ready": true
}
```
