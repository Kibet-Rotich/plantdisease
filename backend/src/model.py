import os
import keras
import tensorflow as tf
from pathlib import Path

# --- UNIVERSAL KERAS 3 COMPATIBILITY PATCH ---
# Built-in Keras 3 layers bypass custom_objects. We monkey-patch the built-in
# class directly in RAM to strip out modern Colab kwargs before instantiation.
@classmethod
def _universal_from_config(cls, config):
    config.pop('quantization_config', None)
    return cls(**config)

keras.layers.Layer.from_config = _universal_from_config
keras.layers.Dense.from_config = _universal_from_config
tf.keras.layers.Layer.from_config = _universal_from_config
tf.keras.layers.Dense.from_config = _universal_from_config
# ---------------------------------------------

MODELS_DIR = Path("models")
TRAIN_DIR = Path("data/train")
CLASS_NAMES = ["Tomato___healthy", "Tomato___Early_blight", "Tomato___Late_blight"]

def find_model_file() -> Path:
    """Dynamically finds the trained model file in the models directory."""
    if MODELS_DIR.exists():
        for ext in ["*.keras", "*.h5"]:
            files = list(MODELS_DIR.glob(ext))
            if files:
                return files[0]
    raise FileNotFoundError(f"No .keras or .h5 model file found in {MODELS_DIR.resolve()}")

def load_trained_model() -> tf.keras.Model:
    """Loads the pre-trained model artifact with full backward compatibility."""
    model_path = find_model_file()
    print(f"[{os.getpid()}] Loading model weights from: {model_path}")
    
    return tf.keras.models.load_model(
        str(model_path),
        compile=False
    )

def execute_retraining_pipeline(epochs: int = 3) -> bool:
    """Retrains the model using bulk datasets uploaded to data/train/."""
    print(f"[{os.getpid()}] Starting background retraining cycle for {epochs} epochs...")
    
    if not TRAIN_DIR.exists() or not any(TRAIN_DIR.iterdir()):
        print("Retraining aborted: No training data found in staging directory.")
        return False

    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=(224, 224),
        batch_size=32,
        label_mode="categorical"
    ).cache().prefetch(buffer_size=tf.data.AUTOTUNE)

    model = load_trained_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(train_ds, epochs=epochs, verbose=1)
    
    model_path = find_model_file()
    model.save(str(model_path))
    print("Retraining complete. Model weights updated on disk.")
    return True