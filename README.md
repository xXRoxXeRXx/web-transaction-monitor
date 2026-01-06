# Web Application Performance Monitoring

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![GitHub release](https://img.shields.io/github/v/release/xXRoxXeRXx/web-transaction-monitor)](https://github.com/xXRoxXeRXx/web-transaction-monitor/releases)

A high-performance, Docker-based synthetic monitoring solution using **Python**, **Playwright**, **Prometheus**, and **Grafana**.

This tool records step-level execution times for web transactions and visualizes them to detect performance regressions and outages.## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Adding Monitoring Tests](#adding-a-new-monitoring-test)
- [Configuration](#configuration)

## ✨ Features

- **Native Playwright Execution**: Uses pure Python Playwright for maximum stability and speed.
- **Detailed Metrics**: Captures duration for every single step, success/failure status, and timestamps.
- **Chronological Dashboards**: Automatically sorts test steps in the correct order (01, 02, etc.) in Grafana.
- **Zero-Config Discovery**: Simply drop a Python file into the `transactions/` folder, and it's automatically scheduled.
- **Docker-Ready**: Full stack (Monitor, Prometheus, Grafana) orchestrated via Docker Compose.
- **Type-Safe**: Full type hints for better IDE support and error detection.
- **Well-Tested**: Comprehensive unit test coverage with pytest.
- **Extensible**: Base classes for common patterns (e.g., Nextcloud tests).

## Project Structure

- `main.py`: The heart of the system—discovers tests, schedules them, and runs the Prometheus metrics server.
- `monitor_base.py`: The foundation for all tests. It manages the Playwright browser lifecycle and automatically handles metrics reporting.
- `transactions/`: Place your monitoring scripts here (recursive subdirectories are supported):
  - `hidrive-legacy/`: HiDrive Legacy platform tests
  - `hidrive-next/`: HiDrive Next platform tests  
  - `ionos-nextcloud-workspace/`: IONOS Nextcloud Workspace tests
  - `ionos-managed-nextcloud/`: IONOS Managed Nextcloud tests
- `runners/python_runner.py`: Executes your Python monitoring scripts.
- `run_test.py`: Universal test runner for local execution with visible browser.
- `.env`: Environment configuration (not in repository, copy from `.env.example`).

## Quick Start

### 1. Start the Stack
```bash
docker-compose up -d --build
```

### 2. Access the Tools
- **Grafana**: [http://localhost:3000](http://localhost:3000) (Admin / admin)
- **Metrics (Prometheus format)**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## Adding a New Monitoring Test

The best way to create a new test is to record it using the Playwright CLI and then wrap it in our `MonitorBase` class.

### 1. Record the Flow

Run the following command on your local machine to record your interaction:

```bash
npx playwright codegen https://your-website.com --target python
```

### 2. Create the Test File

Create a new file in `transactions/your-platform/test_name.py`:

```python
from monitor_base import MonitorBase
import os

class MyNewTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "my_new_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self):
        # Get configuration from environment
        login_url = os.getenv('MY_PLATFORM_URL', 'https://your-website.com')
        username = os.getenv('MY_PLATFORM_USER')
        password = os.getenv('MY_PLATFORM_PASS')
        
        # Step 1: Initialize
        self.measure_step("01_Go to Start", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Interaction Logic
        def interaction():
            self.page.fill("#username", username)
            self.page.click("#login-button")
            self.page.wait_for_selector(".dashboard")
            
        self.measure_step("02_Login Flow", interaction)

if __name__ == "__main__":
    monitor = MyNewTest()
    monitor.execute()
```

### 3. Add Environment Variables

Add your credentials to `.env` (copy from `.env.example` if needed):

```bash
MY_PLATFORM_URL=https://your-website.com
MY_PLATFORM_USER=your_username
MY_PLATFORM_PASS=your_password
```

### 4. Test Locally

Run your test locally with visible browser:

```bash
python run_test.py your-test-name
```

### 5. Automatic Sorting in Grafana

Always prefix your step names with numbers (e.g., `01_`, `02_`). This ensures that Grafana displays them in the correct chronological order instead of alphabetically.

## Configuration

Environment variables in `docker-compose.yml`:

- `SCHEDULE_INTERVAL`: How often tests should run (in seconds). Default: `300`.
- `PROMETHEUS_PORT`: Port for the metrics server. Default: `8000`.
- `HEADLESS`: Set to `true` (default) for production or `false` for debugging.

Platform credentials are configured in `.env` file (copy from `.env.example`).

##  Metrics

The system exports the following Prometheus metrics:

- `transaction_duration_seconds{step="...",usecase="..."}` - Duration of each test step
- `transaction_success{usecase="..."}` - Success status (1.0 = success, 0.0 = failure)
- `transaction_last_run_timestamp{usecase="..."}` - Timestamp of last execution

Access Grafana dashboards at `http://localhost:3000` (default credentials: admin/admin).

---

**Made with ❤️ for reliable web monitoring**
