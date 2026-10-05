FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend backend
COPY scripts scripts
COPY database database
RUN useradd --create-home pravaha
USER pravaha
ENV API_HOST=0.0.0.0
CMD ["python", "scripts/run_backend.py"]
