import cv2
import numpy as np

def preprocess_image_bytes(image_bytes: bytes, target_size: tuple = (224, 224)) -> np.ndarray:
    """Decodes raw HTTP byte stream and formats it into a 4D tensor for inference."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image file format.")
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, target_size)
    return np.expand_dims(img_resized, axis=0)

def extract_biomarkers_from_bytes(image_bytes: bytes) -> dict:
    """Extracts Chlorosis (HSV), Edge Density (Canny), and Lesion Ratio (Otsu) metrics."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 1. Chlorosis Index (HSV color space green degradation)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue_channel = img_hsv[:, :, 0]
    green_ratio = float(np.sum((hue_channel >= 35) & (hue_channel <= 85)) / hue_channel.size)
    
    # 2. Structural Lesion Boundaries (Canny Edge Density)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edge_density = float(np.sum(edges > 0) / edges.size)
    
    # 3. Necrotic Lesion Ratio (Otsu thresholding)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    lesion_ratio = float(np.sum(thresh > 0) / thresh.size)
    
    return {
        "chlorosis_index": round(1.0 - green_ratio, 4),
        "edge_density": round(edge_density, 4),
        "lesion_ratio": round(lesion_ratio, 4)
    }