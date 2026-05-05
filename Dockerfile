FROM python:3.11

RUN apt update && apt install -y ffmpeg libffi-dev libnacl-dev build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
