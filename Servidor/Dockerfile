# ==============================================================================
# Smart Classroom AI - Production Dockerfile
# Usa imagen base de Python (evita conflictos de versiones)
# ==============================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Smart Classroom Team"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_CPP_MIN_LOG_LEVEL=3

# Install system dependencies for OpenCV and TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Copy and install requirements
COPY requirements.docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download DeepFace models during build (NOT at runtime)
# This makes the image larger but eliminates cold start delays
RUN python -c "from deepface import DeepFace; \
    DeepFace.build_model('Facenet512'); \
    DeepFace.build_model('retinaface'); \
    print('Models downloaded successfully')"

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
