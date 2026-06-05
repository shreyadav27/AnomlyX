# AnomlyX

AnomlyX is a frontend prototype for industrial metal defect diagnosis. It helps an inspector upload an inspection image for backend prediction or manually select a defect type and severity level, then generates visual signs, likely root causes, engineering remedies, prevention checks, and a printable inspection report.

The project has a static frontend built with HTML, CSS, and JavaScript plus a FastAPI backend for image prediction. Until a trained model is connected, the backend returns a filename-based placeholder prediction so the frontend/backend workflow can be tested end to end.

## Features

- Image upload wired to the FastAPI `POST /predict` endpoint.
- Manual defect diagnosis by defect type and severity.
- Severity levels for `Low`, `Medium`, and `High`.
- Defect reference image thumbnails for severity comparison.
- Root cause, remedy, and prevention checklist output.
- Defect library with search and quick-load actions.
- Printable diagnostic report page.
- Browser-based save action using `localStorage`.
- ML API with health, dataset class discovery, and image prediction endpoints.

## Supported Defect List

The current manual knowledge base includes:

| Defect | Process Area | Description |
| --- | --- | --- |
| Porosity | Casting / Welding | Gas pockets or cavities trapped inside or on the surface of metal. |
| Crack | Structural | Linear fracture caused by stress, cooling rate, fatigue, or poor fusion. |
| Slag Inclusion | Welding | Non-metallic trapped material inside a weld bead or casting. |
| Misrun | Casting | Incomplete casting caused by molten metal failing to fill the mold cavity. |
| Corrosion | Service / Surface | Chemical or electrochemical degradation such as rust, pitting, or section loss. |
| Shrinkage | Casting | Void or depression caused by metal contraction during solidification. |

Each defect has three severity entries: low, medium, and high. Every severity entry includes visual signs, root cause notes, recommended remedies, and prevention checklist items.

## Project Structure

```text
AnomlyX/
├── index.html          # Main application markup
├── styles.css          # Application styling and responsive layout
├── script.js           # Defect data, UI rendering, navigation, reports
├── assets/defects/     # Normalized defect reference images
├── backend/            # FastAPI backend for future ML prediction
├── Defect_Dataset/     # Training dataset folders grouped by defect/severity
├── frontend.md         # UI prompt/design notes
├── plan.md             # Development roadmap notes
└── README.md
```

## How to Run

Because this is a static prototype, no build step is required. Start the backend first if you want image prediction.

1. Start the backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

2. Serve the frontend from the project root:

```bash
python3 -m http.server 8000
```

3. Visit:

```text
http://localhost:8000
```

You can also open `index.html` directly in a browser for manual diagnosis. The backend allows local static origins and direct-file development.

## Backend API

Install Python 3.11 or newer, then run:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Open the API docs:

```text
http://127.0.0.1:8001/docs
```

Available endpoints:

- `GET /health` checks API, dataset, and model configuration.
- `GET /classes` reads defect folders from `Defect_Dataset`.
- `POST /predict` accepts a JPG, PNG, or WEBP image.

## Basic Usage

1. Go to the `Diagnose` page.
2. Upload an inspection image to call the backend prediction API.
3. Or select a defect type and choose `Low`, `Medium`, or `High` severity manually.
4. Add optional inspector, batch, material, location, and notes.
5. Click `Generate Diagnosis` or `Update Result`.
6. Use `Print Report` to open the report page and print/export from the browser.
7. Use the `Defect Library` to browse supported defects and load one into the diagnosis workflow.

## Known Defects and Limitations

- The extra `manual-porosity-enhanced.png` asset is not currently used by the app workflow.
- The backend prediction endpoint currently uses a filename-based placeholder until real inference code is connected.
- The app uses static frontend data. Defects, remedies, and image paths are hard-coded in `script.js`.
- Saved results only store the latest report in browser `localStorage`; there is no report history database.
- Print/export currently relies on the browser print dialog instead of a dedicated PDF export library.
- The diagnostic guidance is educational/prototype content and should be validated by qualified manufacturing or quality-control experts before real production use.

## Future Improvements

- Move defect data into a JSON file or backend service.
- Keep new image assets named with the same pattern: `assets/defects/<severity>-<defect>.png`.
- Add more defect categories such as blowhole, undercut, lack of fusion, pitting corrosion, cold shut, and surface roughness.
- Add report history, exportable PDFs, and persistent inspection records.
- Replace the backend placeholder predictor with TensorFlow, PyTorch, ONNX, or Teachable Machine inference.
- Add image upload and frontend ML integration using the backend prediction endpoint.
- Validate root causes and remedies against welding/casting inspection standards.

## Tech Stack

- HTML5
- CSS3
- Vanilla JavaScript
- Python
- FastAPI
- Google Fonts and Material Symbols

## Status

AnomlyX is in the manual prototype plus backend scaffold phase. The current focus is collecting enough labeled images, then replacing the placeholder predictor with a trained model.
