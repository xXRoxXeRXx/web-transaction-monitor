FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy configuration
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no interaction, no dev deps)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Install Playwright browsers (Chromium only for now to save space/time, can add others)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Expose Prometheus metrics port
EXPOSE 8000

# Run the application
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
