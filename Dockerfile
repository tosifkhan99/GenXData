# Multi-stage Docker build for Data Generator
# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./
COPY frontend/yarn.lock* ./

# Install all dependencies (including devDependencies needed for build)
RUN yarn install --frozen-lockfile

# Copy frontend source
COPY frontend/ ./

# Build the frontend
RUN yarn build

# Stage 2: Build the Python backend
FROM python:3.12-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual env, install deps globally
RUN poetry config virtualenvs.create false

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (production only, including API group)
RUN poetry install --only=main,api --no-dev

# Copy backend source code
COPY . .
RUN rm -rf frontend/

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/dist ./static

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ping || exit 1

# Start the FastAPI server
CMD ["poetry", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 