FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libbz2-dev \
    zlib1g-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip setuptools

RUN pip install -r requirements.txt

COPY . /app


CMD ["python", "main.py"]