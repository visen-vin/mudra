# Backend stage
FROM python:3.11-slim as backend

WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY tests/ ./tests/

# Frontend stage
FROM node:18-slim as frontend

WORKDIR /app

# Install frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Build frontend
COPY frontend/ .
RUN npm run build

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY --from=backend /app/backend ./backend

# Copy built frontend
COPY --from=frontend /app/dist ./frontend/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/mudra.db

# Create data directory for SQLite
RUN mkdir /app/data

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "backend/main.py"]
