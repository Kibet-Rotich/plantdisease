import numpy as np
from src.model import load_trained_model, CLASS_NAMES
from src.preprocessing import preprocess_image_bytes, extract_biomarkers_from_bytes

# Global memory cache for fast inference
_MODEL_INSTANCE = None

def get_cached_model():
    """Returns the cached model instance or loads it into memory if empty."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = load_trained_model()
    return _MODEL_INSTANCE

def reload_cached_model():
    """Forces an in-memory reload of the model after background retraining completes."""
    global _MODEL_INSTANCE
    _MODEL_INSTANCE = load_trained_model()
    return True

def predict_image_payload(image_bytes: bytes) -> dict:
    """Executes inference and mathematical feature extraction on raw HTTP bytes."""
    model = get_cached_model()
    tensor = preprocess_image_bytes(image_bytes)
    
    probabilities = model.predict(tensor, verbose=0)[0]
    predicted_idx = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_idx])
    
    biomarkers = extract_biomarkers_from_bytes(image_bytes)
    clean_classes = [c.replace("Tomato___", "") for c in CLASS_NAMES]
    
    return {
        "prediction": clean_classes[predicted_idx],
        "confidence": round(confidence, 4),
        "probabilities": {cls: round(float(p), 4) for cls, p in zip(clean_classes, probabilities)},
        "biomarkers": biomarkers
    }