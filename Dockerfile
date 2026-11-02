FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/TimoMuenger/LB-324

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--timeout", "600", "main:app"]
