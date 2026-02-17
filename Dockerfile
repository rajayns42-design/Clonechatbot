# Python ka image use karein
FROM python:3.10-slim

# Working directory set karein
WORKDIR /app

# System dependencies install karein
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements copy aur install karein
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Baaki saara code copy karein
COPY . .

# Bot start karne ki command (Folder path ke saath)
CMD ["python3", "-m", "smartchatbot"]
