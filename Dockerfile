# Multi-stage Dockerfile for Railway deployment
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . .

# Install Python dependencies for backend
WORKDIR /app/backend
RUN uv sync --locked --quiet

# Install Node.js dependencies for frontend
WORKDIR /app/frontend
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

RUN npm ci
RUN npm run build

# Set final working directory
WORKDIR /app

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Default command (will be overridden by Railway)
CMD ["python", "start.py"]
