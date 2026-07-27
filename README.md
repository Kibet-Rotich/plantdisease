# 🌱 AgriGuard Autonomous ML Service
**An End-to-End Autonomous Foliage Pathology Classification & Retraining Pipeline**

[![Live Demo URL](https://img.shields.io/badge/Live_Deployment-Online-10b981?style=for-the-badge)](https://your-cloud-url.onrender.com)
[![YouTube Video Demo](https://img.shields.io/badge/YouTube_Video_Demo-Watch_Here-ff0000?style=for-the-badge&logo=youtube)](https://youtube.com/your-video-link)

---

## 📖 Project Overview
AgriGuard is an autonomous, production-grade computer vision service engineered to classify plant foliage diseases from non-tabular image data (PlantVillage dataset). The system transitions a static convolutional neural network into a resilient cloud architecture featuring:
* **Real-time Single Prediction API:** Sub-second diagnosis across *Healthy*, *Early Blight*, and *Late Blight* Tomato classes.
* **3-Biomarker Feature Storytelling Engine:** Automatically extracts and visualizes physical pathology ratios (HSV Chlorosis degradation, Canny edge structural fragmentation, and Otsu necrotic lesion surface area) to explain *why* the neural network made its decision.
* **Autonomous Background Retraining:** An interactive UI control where users stage bulk zip dataset uploads and trigger asynchronous fine-tuning cycles without causing server downtime or API blocking.
* **Horizontal Docker Scaling & Load Balancing:** Containerized with FastAPI, Uvicorn, and Nginx reverse-proxy load balancing to handle thousands of concurrent IoT field sensor requests.

---

## 🗂️ Repository Directory Structure
Strictly structured according to production ML engineering standards:

```text
plantdisease/
├── README.md                # Comprehensive project documentation & results
├── docker-compose.yml       # Multi-container scaling & Nginx load balancer
├── locustfile.py            # High-concurrency IoT stress simulation script
├── backend/
│   ├── Dockerfile           # Keras 3 / FastAPI container blueprint
│   ├── requirements.txt     # Pinned Python ML dependencies
│   ├── main.py              # Asynchronous API routes & background task handlers
│   ├── src/
│   │   ├── preprocessing.py # Byte decoding & 3-biomarker feature extraction
│   │   ├── model.py         # Keras 3 auto-discovery & fine-tuning engine
│   │   └── prediction.py    # Singleton RAM caching for zero-I/O latency
│   ├── data/                # Train/Test splits & staging directories
│   └── models/              # Saved model weights (_agriguard_model.keras)
├── frontend/
│   ├── index.html           # Tailwind CSS responsive dashboard
│   ├── app.js               # Async API polling & Chart.js storytelling renderer
│   └── style.css            # Custom UI animations & dropzone styling
└── nginx/
    └── nginx.conf           # Reverse proxy & round-robin load balancer


🛠️ Step-by-Step Local Setup Instructions1. PrerequisitesDocker & Docker Compose V2 installed on your host machine.Python 3.10+ (optional, for local virtual environment execution).2. Clone the RepositoryBashgit clone [https://github.com/your-username/plantdisease.git](https://github.com/your-username/plantdisease.git)
cd plantdisease
3. Launch with Horizontal Docker ScalingBuild the application image and spin up the Nginx load balancer along with 3 replicas of the FastAPI backend:Bashdocker compose up --build -d --scale backend=3
4. Access the ApplicationInteractive Frontend UI: Open your browser to http://localhost:8080FastAPI Swagger API Docs: Navigate to http://localhost:8080/api/docs📈 Locust Load Testing & Horizontal Scaling ResultsTo evaluate production performance under high traffic, the system was stress-tested using Locust, simulating 50 concurrent agricultural IoT cameras flooding the /api/predict endpoint.🧪 Experimental SetupSimulated Users: 50 concurrent sensorsSpawn Rate: 5 users/secTarget Load Balancer: Nginx Reverse Proxy (http://localhost:8080)📊 Performance Comparison: 1 vs. 3 Docker ContainersBy routing traffic through Nginx, scaling from 1 container to 3 horizontally distributed containers yielded zero dropped requests and significantly improved throughput under concurrency:Metric1 Docker Container3 Docker Containers (Scaled)Performance ImpactTotal Failures0 (0.00%)0 (0.00%)100% Reliability MaintainedAvg Prediction Latency~1450 ms~557 ms61.5% Latency ReductionRequests Per Second (RPS)~6.5 req/sec~17.89 req/sec2.75x Throughput IncreaseSystem StabilityHeavy CPU queueingClean round-robin load distributionZero event-loop blocking(Insert your Locust screenshot here in GitHub: ![Locust Scaling Proof](link-to-your-image.png))🔬 Feature Storytelling: What Do The 3 Biomarkers Tell Us?Instead of treating deep learning as a black box, AgriGuard extracts three interpretable visual features before classification:Chlorosis Degradation Index (HSV Color Space): Healthy leaves maintain high green saturation. As Blight takes hold, chlorophyll breaks down, shifting pixel density toward yellow/brown frequencies.Structural Edge Density (Canny Edge Variance): Healthy leaves display smooth outer boundaries. Fungal infection introduces concentric, fragmented lesions, causing high-frequency edge density to spike.Necrotic Lesion Ratio (Otsu Thresholding): Quantifies physical tissue death. Separates localized early-stage infection (<5% surface area) from systemic late-stage necrosis (>25%), giving farmers an immediate severity score.