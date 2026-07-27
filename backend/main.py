import time
import io
import zipfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from src.prediction import predict_image_payload, reload_cached_model, get_cached_model
from src.model import execute_retraining_pipeline

app = FastAPI(
    title="AgriGuard Autonomous ML Service",
    description="High-throughput API for foliage pathology classification and background retraining.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER_START_TIME = time.time()

@app.on_event("startup")
def preload_model():
    """Pre-warm the neural network in RAM during server boot."""
    try:
        get_cached_model()
        print("Model preloaded successfully into memory.")
    except Exception as e:
        print(f"Warning during boot model load: {e}")

@app.get("/health", tags=["Telemetry"])
def get_system_health():
    """Synchronous endpoint ran in threadpool to avoid event-loop blocking."""
    uptime_seconds = round(time.time() - SERVER_START_TIME, 2)
    return {
        "status": "online",
        "uptime_seconds": uptime_seconds,
        "model_in_memory": get_cached_model() is not None
    }

@app.post("/predict", tags=["Inference"])
def predict_pathology(file: UploadFile = File(...)):
    """Synchronous endpoint ran in threadpool for concurrent ML inference."""
    if not file.content_type or not file.content_type.startswith("image/"):
        # Fallback check for file extension if content_type header is missing
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        contents = file.file.read()
        results = predict_image_payload(contents)
        return {"filename": file.filename, "status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.post("/upload-data", tags=["Data Ingestion"])
def upload_bulk_training_data(file: UploadFile = File(...)):
    """Accepts a .zip archive of structured class folders."""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Bulk upload requires a valid .zip archive.")
    
    try:
        contents = file.file.read()
        zip_buffer = io.BytesIO(contents)
        
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            extract_dir = Path("data/train")
            extract_dir.mkdir(parents=True, exist_ok=True)
            zip_ref.extractall(extract_dir)
            file_count = len(zip_ref.namelist())
            
        return {"status": "success", "message": f"Extracted {file_count} files into staging directory."}
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid zip archive.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

def background_retrain_task(epochs: int):
    success = execute_retraining_pipeline(epochs=epochs)
    if success:
        reload_cached_model()
        print("In-memory cache updated with newly retrained weights.")

@app.post("/retrain", status_code=status.HTTP_202_ACCEPTED, tags=["Pipeline Control"])
def trigger_model_retraining(background_tasks: BackgroundTasks, epochs: Optional[int] = 3):
    background_tasks.add_task(background_retrain_task, epochs=epochs)
    return {
        "status": "accepted",
        "message": f"Retraining task queued in the background for {epochs} epochs."
    }