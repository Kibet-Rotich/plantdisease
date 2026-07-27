FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Nginx and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all repository code
COPY . .

# Apply cloud Nginx configuration
COPY nginx/cloud_nginx.conf /etc/nginx/nginx.conf

# Grant read/write permissions so bulk upload & retraining endpoints can save to disk
RUN mkdir -p /app/backend/data/train /app/backend/models && \
    chmod -R 777 /app/backend/data /app/backend/models

# Expose Render web port
EXPOSE 8080

# Create a startup script: uvicorn in background, nginx in foreground
RUN echo '#!/bin/bash\n\
cd /app/backend && uvicorn main:app --host 127.0.0.1 --port 8000 &\n\
nginx -g "daemon off;"' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]