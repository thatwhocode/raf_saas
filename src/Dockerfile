FROM python:3.12-bookworm
WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
COPY .  .
ENV PYTHONPATH=/app