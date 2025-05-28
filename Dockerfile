# ---- Base Python image ----
FROM python:3.11-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies ----
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy files into image ----
COPY requirements.txt .
COPY . .

# ---- Install Python dependencies ----
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---- Load environment variables ----
ENV ENV_FILE_PATH=.env

# ---- Expose port ----
EXPOSE 8000

# ---- Run FastAPI app ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]