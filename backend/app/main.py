from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import ALLOWED_CONTENT_TYPES, DATASET_DIR, FRONTEND_DIR, MAX_UPLOAD_BYTES, MODEL_PATH
from .predictor import discover_classes, get_model_status, predict_image


app = FastAPI(
    title="AnomlyX ML Backend",
    description="Backend API for image-based metal defect prediction.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "AnomlyX ML Backend",
        "frontend": "/app",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/app", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/styles.css", include_in_schema=False)
def styles() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "styles.css")


@app.get("/script.js", include_in_schema=False)
def script() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "script.js")


@app.get("/health")
def health() -> dict[str, object]:
    model_status = get_model_status(load=True)
    return {
        "status": "ok",
        "dataset_dir": str(DATASET_DIR),
        "dataset_found": DATASET_DIR.exists(),
        "model_path": model_status.path,
        "model_file_found": model_status.file_found,
        "model_ready": model_status.loadable,
        "model_loaded": model_status.loaded,
        "model_error": model_status.error,
        "class_names": model_status.class_names,
    }


@app.get("/classes")
def classes() -> dict[str, object]:
    return {
        "dataset_dir": str(DATASET_DIR),
        "classes": discover_classes(),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict[str, object]:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPG, PNG, or WEBP image.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Uploaded image is too large.")

    prediction = predict_image(file.filename or "uploaded-image", image_bytes)
    return {
        "filename": file.filename,
        "defect": prediction.defect,
        "severity": prediction.severity,
        "confidence": prediction.confidence,
        "model_ready": prediction.model_ready,
        "source": prediction.source,
        "message": prediction.message,
    }


app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
