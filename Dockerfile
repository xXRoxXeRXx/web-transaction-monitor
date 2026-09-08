FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install the stable Google Chrome channel used by the production monitor.
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy configuration
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no interaction, no dev deps)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Install Playwright runtime dependencies for the browser channel.
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x /app/cleanup_processes.sh /app/entrypoint.sh

# Expose Prometheus metrics port
EXPOSE 8000

# Run the application with entrypoint script
ENV PYTHONUNBUFFERED=1
CMD ["/app/entrypoint.sh"]
