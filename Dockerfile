# ---- Base Python image ----
FROM python:3.11-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies ----
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy requirements and install dependencies first (leverage caching) ----
COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---- Copy application files ----
COPY . .

# ---- Set environment variables (Optional) ----
# Consider using a .env file or docker secrets instead in production
ENV ENV_FILE_PATH=.env

# ---- Expose port ----
EXPOSE 8000

# ---- Run FastAPI app ----
CMD ["uvicorn", "fastAPI:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]