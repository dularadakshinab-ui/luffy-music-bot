FROM python:3.11

# Install system dependencies (FFmpeg is required for audio)
RUN apt update && apt install -y ffmpeg libffi-dev libnacl-dev build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Run bot
CMD ["python", "bot.py"]
