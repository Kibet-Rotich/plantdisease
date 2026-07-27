// Point this to your FastAPI local or cloud instance
const API_BASE_URL = "/api";

// Global DOM references
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const uptimeText = document.getElementById("uptime-text");
const cacheText = document.getElementById("cache-text");
const terminalLogs = document.getElementById("terminal-logs");

// Global Chart.js instance variable
let biomarkerChartInstance = null;

// --- 1. SYSTEM MONITORING & TELEMETRY POLLING ---
async function fetchHealthTelemetry() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error("Server unresponsive");
        
        const data = await response.json();
        
        // Update status UI
        statusText.textContent = "Online";
        statusText.className = "font-semibold text-emerald-400";
        statusDot.className = "w-3 h-3 rounded-full bg-emerald-500 animate-pulse";
        
        // Format uptime (e.g., 120.5s -> 2m 0s)
        const uptimeSecs = Math.floor(data.uptime_seconds);
        const mins = Math.floor(uptimeSecs / 60);
        const secs = uptimeSecs % 60;
        uptimeText.textContent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
        
        // Update cache status
        cacheText.textContent = data.model_in_memory ? "Active (RAM)" : "Cold";
        cacheText.className = data.model_in_memory ? "font-semibold text-emerald-400" : "font-semibold text-amber-400";
        
    } catch (error) {
        statusText.textContent = "Offline";
        statusText.className = "font-semibold text-rose-500";
        statusDot.className = "w-3 h-3 rounded-full bg-rose-500";
        uptimeText.textContent = "--";
        cacheText.textContent = "Disconnected";
        cacheText.className = "font-semibold text-rose-400";
    }
}

// Poll health telemetry every 4 seconds
setInterval(fetchHealthTelemetry, 4000);
fetchHealthTelemetry(); // Initial call on load

// Helper function to write to the live UI log terminal
function logToTerminal(message, type = "info") {
    const time = new Date().toLocaleTimeString();
    const logEntry = document.createElement("div");
    
    if (type === "error") {
        logEntry.innerHTML = `<span class="text-rose-400">[` + time + `] ERROR:</span> ` + message;
    } else if (type === "success") {
        logEntry.innerHTML = `<span class="text-emerald-400">[` + time + `] OK:</span> ` + message;
    } else {
        logEntry.innerHTML = `<span class="text-slate-400">[` + time + `] INFO:</span> ` + message;
    }
    
    terminalLogs.prepend(logEntry);
}

// --- 2. SINGLE INFERENCE & BIOMARKER STORYTELLING ---
const imageInput = document.getElementById("image-input");
const dropzonePredict = document.getElementById("dropzone-predict");
const fileLabel = document.getElementById("file-label");

dropzonePredict.addEventListener("click", () => imageInput.click());
imageInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        fileLabel.textContent = e.target.files[0].name;
        fileLabel.className = "text-sm text-emerald-400 font-medium";
    }
});

document.getElementById("prediction-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = imageInput.files[0];
    if (!file) return;

    const btn = document.getElementById("btn-predict");
    btn.disabled = true;
    btn.innerHTML = `<svg class="animate-spin h-5 w-5 mr-3 text-white inline" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Running Vision Inference...`;
    
    logToTerminal(`Submitting ${file.name} to /predict endpoint...`);

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Prediction request failed");
        }

        const res = await response.json();
        const data = res.data;
        logToTerminal(`Inference successful: Classified as ${data.prediction} (${(data.confidence * 100).toFixed(1)}%)`, "success");

        // Display results panel
        document.getElementById("results-panel").classList.remove("hidden");
        
        // Render Image Preview
        const reader = new FileReader();
        reader.onload = (e) => document.getElementById("preview-image").src = e.target.result;
        reader.readAsDataURL(file);

        // Update Diagnosis Summary
        const badge = document.getElementById("predicted-class-badge");
        badge.textContent = data.prediction;
        
        // Color code class badge
        if (data.prediction.toLowerCase().includes("healthy")) {
            badge.className = "text-xl font-bold px-4 py-1.5 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800";
        } else {
            badge.className = "text-xl font-bold px-4 py-1.5 rounded-lg bg-rose-950 text-rose-300 border border-rose-800";
        }

        const confPct = Math.round(data.confidence * 100);
        document.getElementById("confidence-val").textContent = `${confPct}%`;
        document.getElementById("confidence-bar").style.width = `${confPct}%`;

        // Render Biomarker Storytelling Chart
        renderBiomarkerChart(data.biomarkers);

    } catch (error) {
        logToTerminal(`Inference error: ${error.message}`, "error");
        alert(`Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>Analyze Foliage & Extract Biomarkers</span>`;
    }
});

// --- 3. CHART.JS BIOMARKER STORYTELLING RENDERER ---
function renderBiomarkerChart(biomarkers) {
    const ctx = document.getElementById("biomarkerChart").getContext("2d");
    
    // Destroy existing chart if running consecutive predictions
    if (biomarkerChartInstance) {
        biomarkerChartInstance.destroy();
    }

    const labels = ["Chlorosis Degradation (HSV)", "Structural Edge Density (Canny)", "Necrotic Lesion Ratio (Otsu)"];
    const values = [biomarkers.chlorosis_index, biomarkers.edge_density, biomarkers.lesion_ratio];

    biomarkerChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Biomarker Ratio (0.0 to 1.0)",
                data: values,
                backgroundColor: [
                    "rgba(251, 191, 36, 0.7)",   // Amber for Chlorosis
                    "rgba(129, 140, 248, 0.7)",  // Indigo for Edge Density
                    "rgba(244, 63, 94, 0.7)"     // Rose for Lesion Ratio
                ],
                borderColor: [
                    "#f59e0b",
                    "#6366f1",
                    "#e11d48"
                ],
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1.0,
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: "#cbd5e1", font: { size: 11 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` Score: ${(context.raw * 100).toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// --- 4. BULK DATA UPLOAD & PIPELINE RETRAINING ---
document.getElementById("upload-data-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = document.getElementById("zip-input").files[0];
    if (!file) return;

    logToTerminal(`Uploading ${file.name} to /upload-data staging directory...`);
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload-data`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Bulk upload failed");
        }

        const data = await response.json();
        logToTerminal(`Staging success: ${data.message}`, "success");
        e.target.reset();
    } catch (error) {
        logToTerminal(`Upload error: ${error.message}`, "error");
    }
});

document.getElementById("retrain-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const epochs = document.getElementById("epochs-input").value;
    
    if (!confirm(`Are you sure you want to trigger a model retraining cycle for ${epochs} epochs? This will fine-tune the classification head in the background.`)) {
        return;
    }

    const btn = document.getElementById("btn-retrain");
    btn.disabled = true;
    btn.innerHTML = `<svg class="animate-spin h-5 w-5 mr-3 text-white inline" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Retraining Pipeline Triggered...`;

    logToTerminal(`Sending POST request to /retrain?epochs=${epochs}...`);

    try {
        const response = await fetch(`${API_BASE_URL}/retrain?epochs=${epochs}`, {
            method: "POST"
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Retraining request failed");
        }

        const data = await response.json();
        logToTerminal(`Pipeline triggered: ${data.message}`, "success");
        logToTerminal(`Monitor backend terminal for TensorFlow training epoch logs...`, "info");
        
    } catch (error) {
        logToTerminal(`Retraining trigger error: ${error.message}`, "error");
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = `<span>🚀 Trigger Pipeline Retraining Cycle</span>`;
        }, 3000);
    }
});