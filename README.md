# Web Application Performance Monitoring

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A high-performance, Docker-based synthetic monitoring solution using **Python**, **Playwright**, **Prometheus**, and **Grafana**.

This tool records step-level execution times for web transactions and visualizes them to detect performance regressions and outages.## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Adding Monitoring Tests](#adding-a-new-monitoring-test)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

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
- `transactions/`: Place your monitoring scripts here (recursive subdirectories are supported).
- `runners/python_runner.py`: Executes your Python monitoring scripts.

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
Create a new file in `transactions/your.domain/test_name.py`:

```python
from monitor_base import MonitorBase

class MyNewTest(MonitorBase):
    def run(self):
        # Step 1: Initialize
        self.measure_step("01_Go to Start", lambda: 
            self.page.goto('https://your-website.com')
        )

        # Step 2: Interaction Logic
        def interaction():
            self.page.fill("#username", "my-user")
            self.page.click("#login-button")
            self.page.wait_for_selector(".dashboard")
            
        self.measure_step("02_Login Flow", interaction)
```

### 3. Automatic Sorting in Grafana
Always prefix your step names with numbers (e.g., `01_`, `02_`). This ensures that Grafana displays them in the correct chronological order instead of alphabetically.

## Configuration

Environment variables in `docker-compose.yml`:

- `SCHEDULE_INTERVAL`: How often tests should run (in seconds). Default: `300`.
- `PROMETHEUS_PORT`: Port for the metrics server. Default: `8000`.
- `HEADLESS`: Set to `true` (default) for production or `false` for debugging.

For detailed development setup, testing, and troubleshooting, see [DEVELOPMENT.md](DEVELOPMENT.md).

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation
- [Prometheus](https://prometheus.io/) - Metrics collection
- [Grafana](https://grafana.com/) - Visualization
- [APScheduler](https://apscheduler.readthedocs.io/) - Job scheduling

## 📊 Screenshots

### Grafana Dashboard
![Grafana Dashboard](docs/images/dashboard-preview.png)
*Real-time monitoring of transaction steps and success rates*

### Metrics Export
```
transaction_duration_seconds{step="01_Login",usecase="example_test"} 2.45
transaction_success{usecase="example_test"} 1.0
```

## 🔗 Links

- [Documentation](DEVELOPMENT.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

---

**Made with ❤️ for reliable web monitoring**
