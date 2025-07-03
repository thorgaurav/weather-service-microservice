# Dockerfile

# 1. Base image
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy dependencies
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
