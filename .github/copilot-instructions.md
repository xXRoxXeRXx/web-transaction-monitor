# Web Transaction Monitor - AI Coding Agent Instructions

## Architecture Overview

This is a **synthetic web monitoring system** that uses Playwright to execute scheduled browser-based transactions and exposes metrics to Prometheus/Grafana. The architecture follows a plugin-based pattern where tests are auto-discovered.

### Core Components

1. **`main.py`** - Orchestrator that discovers tests in `transactions/` recursively, schedules them via APScheduler (sequential execution with ThreadPoolExecutor(1)), and runs Prometheus metrics server on port 8000
2. **`monitor_base.py`** - Abstract base class that all tests inherit from. Manages Playwright lifecycle, wraps test steps with timing/metrics via `measure_step()`, and exports to Prometheus
3. **`runners/python_runner.py`** - Execution engine that uses AST parsing to detect if a file is class-based (MonitorBase subclass) or script-based, then runs appropriately
4. **`transactions/`** - Test repository organized by platform (e.g., `hidrive-legacy/`, `ionos-nextcloud-workspace/`). Tests are auto-discovered and scheduled
5. **Docker stack** - Three containers: `monitor-app` (runs main.py), `prometheus` (scrapes metrics), `grafana` (visualization)

### Critical Design Patterns

**Sequential Execution**: Tests run one-at-a-time via `ThreadPoolExecutor(1)` to prevent resource conflicts. Jobs use staggered start times (1-second offsets) to ensure proper ordering.

**Step Naming Convention**: Steps MUST be prefixed with `01_`, `02_`, etc. to ensure Grafana displays them chronologically (not alphabetically). Example: `self.measure_step("01_Login", login_action)`

**Metrics Labels**: All Prometheus metrics use `usecase` and `step` labels. The `usecase` name is derived from the file path relative to `transactions/` with path separators replaced by underscores (e.g., `hidrive-legacy/picture_test.py` → `hidrive-legacy_picture_test`)

**Headless Mode**: Controlled by `HEADLESS` environment variable. Default is `true` (Docker), set to `false` for local debugging with visible browser.

## Adding New Tests

Tests follow this structure pattern (see `transactions/hidrive-legacy/picture_test.py` as reference):

```python
from monitor_base import MonitorBase
import os

class MyTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "my_test"
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get credentials from environment
        url = os.getenv('MY_PLATFORM_URL')
        username = os.getenv('MY_PLATFORM_USER')
        password = os.getenv('MY_PLATFORM_PASS')
        
        # Each step is wrapped with measure_step for metrics
        self.measure_step("01_Navigate", lambda: self.page.goto(url))
        
        def login():
            self.page.fill("#username", username)
            self.page.click("#login")
            self.page.wait_for_selector(".dashboard")
        self.measure_step("02_Login", login)
```

**Key Requirements**:
- Inherit from `MonitorBase`
- Implement `run()` method with test logic
- Use `self.measure_step()` for ALL user actions to capture metrics
- Prefix steps with numbers (`01_`, `02_`, etc.)
- Read config from environment variables (credentials, URLs)
- Use `self.page` (Playwright Page object) for browser automation

## Local Development Workflows

**Run single test with visible browser**:
```bash
# Set HEADLESS=false in .env first
python run_test.py hidrive-legacy-picture
```

**Run all tests**:
```bash
python run_test.py all
```

**Record new test flow**:
```bash
npx playwright codegen https://your-site.com --target python
# Then wrap the generated code in MonitorBase structure
```

**Local testing with Docker**:
```bash
make docker-up        # Start full stack
make docker-logs      # View monitor logs
make docker-down      # Stop stack
```

**Unit tests** (pytest with mocking):
```bash
make test             # Run with coverage
make test-fast        # Skip coverage for speed
```

**Code quality**:
```bash
make lint             # Ruff linting
make lint-fix         # Auto-fix issues
make type-check       # mypy
make format           # Ruff formatting
```

## Environment Configuration

- `.env` file stores credentials and config (not in git, copy from `.env.example`)
- `HEADLESS=true` - Run browser headlessly (Docker default)
- `SCHEDULE_INTERVAL=300` - Test execution interval in seconds
- `PROMETHEUS_PORT=8000` - Metrics server port
- `DEBUG=false` - If true, enables verbose logging; if false, only shows START/SUCCESS/FAILED

Platform-specific variables follow pattern: `{PLATFORM}_URL`, `{PLATFORM}_USER`, `{PLATFORM}_PASS`

## Prometheus Metrics

Exported metrics (accessible at `http://localhost:8000/metrics`):

- `transaction_duration_seconds{usecase="...", step="..."}` - Step execution time
- `transaction_success{usecase="..."}` - 1.0 = success, 0.0 = failure
- `transaction_last_run_timestamp{usecase="..."}` - Unix timestamp
- `transaction_step_failure_total{usecase="...", step="..."}` - Failure counter per step

## Logging Behavior

The system has two modes controlled by `DEBUG` environment variable:

**Production mode** (`DEBUG=false`):
- Only logs transaction START/SUCCESS/FAILED (always visible)
- Errors always logged with stack traces
- Suppresses step-by-step details

**Debug mode** (`DEBUG=true`):
- Shows all step execution details
- Full Playwright/APScheduler logging
- Use for troubleshooting test failures

## Testing Strategy

Unit tests (see `tests/`) use pytest with mocking:
- Mock Playwright objects to avoid browser startup
- Test `MonitorBase` lifecycle (setup/teardown/execute)
- Verify metrics recording behavior
- Use `pytest-mock` for patching external dependencies

Integration tests run actual browser automation against live sites (credentials required).

## Docker Details

- **Volume mounts**: `transactions/`, `runners/`, `main.py`, `monitor_base.py` are mounted to allow hot-reload without rebuild
- **Healthchecks**: All services have health endpoints checked every 30s
- **Prometheus retention**: 730 days (2 years) for long-term trend analysis
- **Grafana provisioning**: Dashboards and datasources auto-loaded from `grafana/provisioning/`

## Common Pitfalls

1. **Forgetting step prefixes**: Steps without numbers (`01_`, `02_`) appear alphabetically in Grafana, breaking flow visualization
2. **Missing environment variables**: Tests will fail if credentials not in `.env`
3. **Not calling `measure_step()`**: Actions outside `measure_step()` won't be tracked in metrics
4. **Concurrent execution**: If you modify `ThreadPoolExecutor(1)` to allow parallel tests, Playwright instances may conflict
5. **Import issues**: Tests in `transactions/` must import `from monitor_base import MonitorBase` (not `from ../monitor_base`)

## File Naming Conventions

- Test files: `{action}_test.py` (e.g., `picture_test.py`, `settings_test.py`)
- Test classes: `{Platform}{Action}Test` (e.g., `HiDriveLegacyPictureTest`)
- Usecase names: Lowercase with underscores (e.g., `hidrive_legacy_picture_test`)

---

**Quick Start for New Contributors**: Copy an existing test from `transactions/hidrive-legacy/`, modify the selectors and URLs, add credentials to `.env`, then run with `python run_test.py <test-name>`.
