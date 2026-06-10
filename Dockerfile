FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY bot.py .
COPY search/ ./search/
COPY json/ ./json/
COPY functions/ ./functions/

# Create log and data directories
RUN mkdir -p log data

CMD ["python", "bot.py"]
