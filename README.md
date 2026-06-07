# AnomlyX

AnomlyX is a frontend prototype for industrial metal defect diagnosis. It helps an inspector upload an inspection image for backend prediction or manually select a defect type and severity level, then generates visual signs, likely root causes, engineering remedies, prevention checks, and a printable inspection report.

The project has a static frontend built with HTML, CSS, and JavaScript plus a FastAPI backend for image prediction. A MobileNetV2 transfer-learning model has been trained for defect-type classification; when the trained Keras model is present at `ml/saved_models/defect_classifier.keras`, the backend uses real ML inference and falls back to a filename-based placeholder only when the model is unavailable.

## Features

- Image upload wired to the FastAPI `POST /predict` endpoint.
- Trained MobileNetV2 defect classifier with real backend inference support.
- Manual defect diagnosis by defect type and severity.
- Severity levels for `Low`, `Medium`, and `High`.
- Defect reference image thumbnails for severity comparison.
- Root cause, remedy, and prevention checklist output.
- Defect library with search and quick-load actions.
- Printable diagnostic report page.
- Browser-based save action using `localStorage`.
- ML API with health, dataset class discovery, and image prediction endpoints.

## Supported Defect List

The current manual knowledge base and trained ML classifier include:

| Defect | Process Area | Description |
| --- | --- | --- |
| Porosity | Casting / Welding | Gas pockets or cavities trapped inside or on the surface of metal. |
| Crack | Structural | Linear fracture caused by stress, cooling rate, fatigue, or poor fusion. |
| Slag Inclusion | Welding | Non-metallic trapped material inside a weld bead or casting. |
| Misrun | Casting | Incomplete casting caused by molten metal failing to fill the mold cavity. |
| Corrosion | Service / Surface | Chemical or electrochemical degradation such as rust, pitting, or section loss. |
| Shrinkage | Casting | Void or depression caused by metal contraction during solidification. |

Each defect has three severity entries: low, medium, and high. Every severity entry includes visual signs, root cause notes, recommended remedies, and prevention checklist items.

## ML Training Status

The AnomlyX defect classifier has been trained locally using MobileNetV2 transfer learning.

| Item | Value |
| --- | --- |
| Model | MobileNetV2 + custom dense classification head |
| Input size | 224 x 224 RGB |
| Classes | Corrosion, Crack, Misrun, Porosity, Shrinkage, Slag_Inclusion |
| Total images | 935 |
| Training split | 748 images |
| Validation split | 187 images |
| Best validation accuracy | 83.42% |
| Saved model path | `ml/saved_models/defect_classifier.keras` |
| Training curve | `ml/results/training_history.png` |

Dataset distribution:

| Class | Images |
| --- | ---: |
| Corrosion | 71 |
| Crack | 52 |
| Misrun | 260 |
| Porosity | 261 |
| Shrinkage | 260 |
| Slag_Inclusion | 31 |

The trained model predicts defect type. Severity is still derived from filename hints or confidence heuristics in the backend response.

## Project Structure

```text
AnomlyX/
├── frontend/           # Static frontend application
│   ├── index.html      # Main application markup
│   ├── styles.css      # Application styling and responsive layout
│   ├── script.js       # Defect data, UI rendering, navigation, reports
│   └── assets/defects/ # Normalized defect reference images
├── backend/            # FastAPI backend for future ML prediction
├── Defect_Dataset/     # Training dataset folders grouped by defect/severity
├── frontend.md         # UI prompt/design notes
├── plan.md             # Development roadmap notes
└── README.md
```

## Team Runbook

The trained model is committed at `ml/saved_models/defect_classifier.keras`, so
teammates do **not** need to train the model before running the app. After
pulling the repo, start the backend and frontend in two separate terminals.

Use Python **3.10, 3.11, or 3.12** for the backend because TensorFlow may not
publish wheels for newer Python versions yet.

### Linux/macOS

Terminal 1 - backend:

```bash
git pull
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Terminal 2 - frontend:

```bash
cd /path/to/AnomlyX/frontend
python3 -m http.server 8000
```

Open:

```text
http://localhost:8000
```

Backend API docs:

```text
http://127.0.0.1:8002/docs
```

### Windows PowerShell

Terminal 1 - backend:

```powershell
git pull
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Terminal 2 - frontend:

```powershell
cd C:\path\to\AnomlyX\frontend
py -m http.server 8000
```

Open:

```text
http://localhost:8000
```

Backend API docs:

```text
http://127.0.0.1:8002/docs
```

The backend automatically looks for:

```text
ml/saved_models/defect_classifier.keras
```

If the file exists, `/predict` uses the trained model. If it is missing, the
backend falls back to the filename-based placeholder prediction.

## How to Run

Because this is a static prototype, no build step is required. Start the backend first if you want image prediction.

1. Start the backend on Linux/macOS:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

On Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

2. Serve the frontend from the `frontend` folder:

```bash
cd frontend
python3 -m http.server 8000
```

On Windows PowerShell:

```powershell
cd frontend
py -m http.server 8000
```

3. Visit:

```text
http://localhost:8000
```

You can also open `frontend/index.html` directly in a browser for manual diagnosis. The backend allows local static origins and direct-file development.

## Backend API

Install Python 3.10, 3.11, or 3.12, then run:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

On Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Open the API docs:

```text
http://127.0.0.1:8002/docs
```

Available endpoints:

- `GET /health` checks API, dataset, and model configuration.
- `GET /classes` reads defect folders from `Defect_Dataset`.
- `POST /predict` accepts a JPG, PNG, or WEBP image and uses the trained model when available.

## Basic Usage

1. Go to the `Diagnose` page.
2. Upload an inspection image to call the backend prediction API.
3. Or select a defect type and choose `Low`, `Medium`, or `High` severity manually.
4. Add optional inspector, batch, material, location, and notes.
5. Click `Generate Diagnosis`.
6. Use `Print Report` to open the report page and print/export from the browser.
7. Use the `Defect Library` to browse supported defects and load one into the diagnosis workflow.

## Known Defects and Limitations

- The extra `manual-porosity-enhanced.png` asset is not currently used by the app workflow.
- The backend falls back to a filename-based placeholder if the trained model file is not present.
- The app uses static frontend data. Defects, remedies, and image paths are hard-coded in `frontend/script.js`.
- Saved results only store the latest report in browser `localStorage`; there is no report history database.
- Print/export currently relies on the browser print dialog instead of a dedicated PDF export library.
- The diagnostic guidance is educational/prototype content and should be validated by qualified manufacturing or quality-control experts before real production use.

## Future Improvements

- Move defect data into a JSON file or backend service.
- Keep new image assets named with the same pattern: `frontend/assets/defects/<severity>-<defect>.png`.
- Add more defect categories such as blowhole, undercut, lack of fusion, pitting corrosion, cold shut, and surface roughness.
- Add report history, exportable PDFs, and persistent inspection records.
- Improve the trained model with more balanced images and severity-aware labels.
- Add image upload result confidence visualization in the frontend.
- Validate root causes and remedies against welding/casting inspection standards.

## Tech Stack

- HTML5
- CSS3
- Vanilla JavaScript
- Python
- FastAPI
- Google Fonts and Material Symbols

## Status

AnomlyX now has a trained defect-type classifier connected through the backend inference path. The current focus is improving dataset balance, adding severity classification, and validating model outputs against quality-control expertise.
