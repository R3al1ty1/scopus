FROM ubuntu:20.04

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb \
    && rm ./google-chrome-stable_current_amd64.deb

FROM python:3.12

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