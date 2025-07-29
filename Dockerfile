# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies required for Manim
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    pkg-config \
    # Cairo and Pango dependencies
    libcairo2-dev \
    libpango1.0-dev \
    libgirepository1.0-dev \
    # FFmpeg for video processing
    ffmpeg \
    # LaTeX for mathematical rendering
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-latex-recommended \
    texlive-science \
    tipa \
    # Additional graphics libraries
    libglib2.0-dev \
    libgtk-3-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    # Git for potential dependency installation
    git \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directory for Manim output
RUN mkdir -p /app/media

# Set proper permissions
RUN chmod +x /app

# Expose the port
EXPOSE 5000

# Health check (using Python's requests instead of curl)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=10)" || exit 1

# Run the application
CMD ["python", "app.py"]
