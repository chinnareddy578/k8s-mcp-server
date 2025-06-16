# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Rust (required for uv)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv and move it to /usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/

# Create a virtual environment and install dependencies
RUN uv venv /app/venv && \
    . /app/venv/bin/activate && \
    uv pip install -e .

# Create directories for kubeconfig and minikube
RUN mkdir -p /root/.kube && \
    mkdir -p /root/.minikube

# Expose the port the app runs on (for HTTP mode)
EXPOSE 8080

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app/src

# Use the virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

# Set default environment variables
ENV MCP_MODE=stdio
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV KUBECONFIG=/root/.kube/config

# Command to run the application
ENTRYPOINT ["python", "-u", "src/main.py"] 