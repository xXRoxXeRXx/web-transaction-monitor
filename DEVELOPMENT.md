# Development Setup Instructions

## Prerequisites
- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (for running the full stack)

## Local Development

### 1. Install Dependencies

```bash
poetry install
```

### 2. Install Playwright Browsers

```bash
poetry run playwright install chromium
```

### 3. Set Up Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials.

### 4. Run Tests Locally

Run a single test:
```bash
poetry run python transactions/storage.ionos.fr/picture_test.py
```

### 5. Run Unit Tests

```bash
poetry run pytest
```

With coverage report:
```bash
poetry run pytest --cov=. --cov-report=html
```

### 6. Type Checking

```bash
poetry run mypy main.py monitor_base.py runners/
```

### 7. Code Linting

```bash
poetry run ruff check .
```

Fix automatically:
```bash
poetry run ruff check --fix .
```

## Docker Development

### Start the Full Stack

```bash
docker-compose up -d --build
```

### View Logs

```bash
docker-compose logs -f monitor-app
```

### Restart After Code Changes

```bash
docker-compose restart monitor-app
```

### Stop Everything

```bash
docker-compose down
```

## Creating New Tests

See the main README.md for detailed instructions on creating tests.

For Nextcloud-like interfaces, you can extend `NextcloudPictureTestBase`:

```python
from nextcloud_base import NextcloudPictureTestBase

class MyTest(NextcloudPictureTestBase):
    def __init__(self, usecase_name: str = None) -> None:
        super().__init__(
            usecase_name=usecase_name or "my_test",
            base_url='https://my.instance.com/login',
            username_env='MY_USER',
            password_env='MY_PASS',
            # ... configure selectors
        )
```

## Troubleshooting

### Tests fail with timeout errors
- Increase timeout values in the test
- Check if the website is accessible
- Run with `headless=False` to see what's happening

### Metrics not showing in Grafana
- Check Prometheus is scraping: http://localhost:9090/targets
- Verify metrics endpoint: http://localhost:8000/metrics
- Check Grafana data source configuration

### Module import errors
- Ensure you're in the Poetry shell: `poetry shell`
- Or prefix commands with `poetry run`
