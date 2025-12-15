FROM python:3.13-slim

# Install system dependencies required for WeasyPrint and other tools
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
# Default port for local development, Railway will override this
ENV PORT=8501

WORKDIR /app

# Create virtual environment
RUN uv venv

# Copy requirements file
COPY requirements.txt ./

# Install dependencies using uv
RUN uv pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (informative for Docker, Railway ignores this but uses $PORT)
EXPOSE $PORT

# Healthcheck to verify Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Command to run the application using the PORT environment variable
CMD sh -c "streamlit run main.py --server.port=${PORT} --server.address=0.0.0.0"
