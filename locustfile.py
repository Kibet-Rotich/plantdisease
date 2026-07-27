import os
from pathlib import Path
from locust import HttpUser, task, between

TEST_IMG_DIR = Path("backend/data/test")

def find_test_image():
    """Locates any test image directly in data/test or in its subdirectories."""
    if TEST_IMG_DIR.exists():
        for ext in ["*.jpg", "*.JPG", "*.jpeg", "*.png", "*.webp"]:
            # Check recursive and direct directory files
            images = list(TEST_IMG_DIR.rglob(ext))
            if images:
                return images[0]
    return None

class AgriGuardSensorSimulator(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.sample_image = find_test_image()
        if not self.sample_image:
            print("[LOCUST ERROR] Could not find test image in backend/data/test/")

    @task(5)
    def simulate_realtime_prediction_flood(self):
        """Simulates IoT field cameras sending images for real-time pathology inference."""
        if not hasattr(self, 'sample_image') or not self.sample_image:
            return

        with open(self.sample_image, "rb") as f:
            image_data = f.read()

        files = {"file": (self.sample_image.name, image_data, "image/jpeg")}
        
        # Hit the Nginx load balancer on port 8080 proxying to /api/predict
        with self.client.post("/api/predict", files=files, catch_response=True) as response:
            if response.status_code == 200 and "success" in response.text:
                response.success()
            else:
                response.failure(f"Prediction failed with status code: {response.status_code}")

    @task(1)
    def simulate_telemetry_ping(self):
        """Simulates frontend dashboards polling system health and uptime."""
        self.client.get("/api/health")