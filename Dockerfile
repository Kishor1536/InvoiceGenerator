FROM python:3.11-slim

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
    libgdk-pixbuf-2.0-0 \
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

# Move virtual env outside of /app to avoid being overwritten by volume mount
ENV VIRTUAL_ENV=/opt/venv
# Update PATH to include venv bin
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Create virtual environment in /opt/venv
RUN uv venv $VIRTUAL_ENV

# Copy requirements file
COPY requirements.txt ./

# Install dependencies into the virtual environment
RUN uv pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose a typical dev port; Railway mainly uses the env var anyway
EXPOSE 8501

# Healthcheck: use $PORT if set, else 8501
HEALTHCHECK CMD curl --fail http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Command using absolute path to ensure streamlit is found
# Uses $PORT if provided (Railway), otherwise defaults to 8501 (Local)
CMD sh -c "streamlit run main.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
