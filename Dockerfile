FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (including pre-built React frontend in frontend/dist)
COPY . .

# Environment config
ENV PORT=8000
EXPOSE 8000

# Start unified FastAPI server serving React SPA & REST API
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
