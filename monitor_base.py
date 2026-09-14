from abc import ABC, abstractmethod
import subprocess
import time
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from playwright.sync_api import sync_playwright, Page, Browser
from prometheus_client import Gauge, Counter

# Configure logging based on DEBUG environment variable
logger = logging.getLogger(__name__)
debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

# Note: The actual log level is set in main.py/run_test.py
# This just provides the debug_mode flag for conditional logging

# METRICS DEFINITION
TRANS_DURATION = Gauge(
    'transaction_duration_seconds', 
    'Duration of a specific step in the transaction', 
    ['usecase', 'step']
)
TRANS_SUCCESS = Gauge(
    'transaction_success', 
    '1 if the last transaction run was successful, 0 otherwise', 
    ['usecase']
)
TRANS_LAST_RUN = Gauge(
    'transaction_last_run_timestamp', 
    'Timestamp of the last run attempt', 
    ['usecase']
)
STEP_FAILURE = Counter(
    "transaction_step_failure_total",
    "Total number of failures per step",
    ["usecase", "step"]
)

class MonitorBase(ABC):
    def _save_error_stack(self, step_name: str, error_type: str, exc: Exception) -> str:
        """
        Saves the error stack trace to a text file with timestamp and step name.
        Returns the path to the saved error file.
        """
        import traceback
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_step_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in step_name)
        filename = f"{self.usecase_name}_{safe_step_name}_{error_type}_{timestamp}_error.txt"
        filepath = self.screenshots_dir / filename
        stack = traceback.format_exc()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(stack)
            logger.info(f"[{self.usecase_name}] Error stack saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"[{self.usecase_name}] Failed to save error stack: {e}")
            return ""
    def __init__(self, usecase_name: str, headless: bool = True) -> None:
        self.usecase_name = usecase_name
        self.headless = headless
        self.playwright: Optional[object] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[object] = None
        self.external_browser = False
        self.page: Optional[Page] = None
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    def _take_screenshot(self, step_name: str, error_type: str = "error") -> str:
        """
        Takes a screenshot and saves it with timestamp and step name.
        Returns the path to the saved screenshot.
        """
        if not self.page:
            logger.warning(f"Cannot take screenshot: page is not initialized")
            return ""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Sanitize step name for filename
            safe_step_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in step_name)
            filename = f"{self.usecase_name}_{safe_step_name}_{error_type}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            self.page.screenshot(path=str(filepath), full_page=True)
            logger.info(f"[{self.usecase_name}] Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"[{self.usecase_name}] Failed to take screenshot: {e}")
            return ""

    def _save_page_html(self, step_name: str, error_type: str = "error") -> str:
        """
        Saves the current page HTML content with timestamp and step name.
        Returns the path to the saved HTML file.
        """
        if not self.page:
            logger.warning(f"Cannot save HTML: page is not initialized")
            return ""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Sanitize step name for filename
            safe_step_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in step_name)
            filename = f"{self.usecase_name}_{safe_step_name}_{error_type}_{timestamp}.html"
            filepath = self.screenshots_dir / filename
            
            # Get the full HTML content
            html_content = self.page.content()
            
            # Also add metadata at the top
            metadata = f"""<!--
URL: {self.page.url}
Title: {self.page.title()}
Timestamp: {timestamp}
Use Case: {self.usecase_name}
Step: {step_name}
Error Type: {error_type}
-->

"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(metadata + html_content)
            
            logger.info(f"[{self.usecase_name}] HTML saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"[{self.usecase_name}] Failed to take screenshot: {e}")
            return ""

    def setup(self) -> None:
        """Initializes Playwright"""
        self.playwright = sync_playwright().start()
        launch_options = {"headless": self.headless}
        browser_channel = os.getenv("PLAYWRIGHT_CHANNEL")
        if browser_channel:
            launch_options["channel"] = browser_channel
        if os.getenv("PLAYWRIGHT_NO_SANDBOX", "false").lower() in ("true", "1", "yes"):
            launch_options["args"] = ["--no-sandbox", "--disable-dev-shm-usage"]

        cdp_url = os.getenv("PLAYWRIGHT_CDP_URL")
        if cdp_url:
            self.browser = self.playwright.chromium.connect_over_cdp(cdp_url)
            self.context = self.browser.contexts[0]
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.external_browser = True
            return

        user_data_dir = os.getenv("PLAYWRIGHT_USER_DATA_DIR")
        if user_data_dir:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir,
                **launch_options,
            )
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            return

        self.browser = self.playwright.chromium.launch(**launch_options)
        storage_state_path = os.getenv("PLAYWRIGHT_STORAGE_STATE")
        if storage_state_path and Path(storage_state_path).is_file():
            self.context = self.browser.new_context(storage_state=storage_state_path)
            self.page = self.context.new_page()
        else:
            if storage_state_path:
                logger.warning(
                    f"[{self.usecase_name}] Storage state not found: {storage_state_path}; "
                    "starting without restored authentication"
                )
            self.page = self.browser.new_page()

    def _force_kill_orphaned_browser_processes(self) -> None:
        """Terminate stale Chromium/Chrome processes to recover from a hung browser session."""
        try:
            if os.name == "nt":
                subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'chrome|chromium|msedge' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
                    ],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                )
            else:
                subprocess.run(
                    [
                        "bash",
                        "-lc",
                        "ps -eo pid,etimes,comm --no-headers 2>/dev/null | awk 'BEGIN{IGNORECASE=1} $2 ~ /chrome|chromium|msedge/ && $3 > 120 { print $1 }' | xargs -r kill -9 || true",
                    ],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                )
        except Exception as e:
            logger.warning(f"[{self.usecase_name}] Failed to force-kill orphaned browser processes: {e}")

    def _close_with_timeout(self, close_callable: Callable[[], None], resource_name: str, timeout_seconds: float = 10.0) -> None:
        """Call a Playwright close method in-band and force a process cleanup only if it raises an error.

        Using another thread for Playwright sync objects is unsafe and triggers the greenlet
        "Cannot switch to a different thread" error seen in production.
        """
        if close_callable is None:
            return

        start = time.monotonic()
        try:
            close_callable()
        except Exception as e:
            elapsed = time.monotonic() - start
            logger.warning(f"[{self.usecase_name}] Failed to close {resource_name} after {elapsed:.2f}s: {e}")
            self._force_kill_orphaned_browser_processes()
            return

        elapsed = time.monotonic() - start
        if elapsed > timeout_seconds:
            logger.warning(f"[{self.usecase_name}] {resource_name} close exceeded timeout ({elapsed:.2f}s > {timeout_seconds}s); forcing cleanup")
            self._force_kill_orphaned_browser_processes()

    def teardown(self) -> None:
        """Cleans up Playwright on the same thread it was created on.

        Playwright sync objects are not safe to close from another thread. Cross-thread
        shutdown is exactly what caused the "Cannot switch to a different thread" and
        subsequent "Sync API inside asyncio loop" failures.
        """
        try:
            if self.page and not self.external_browser:
                self._close_with_timeout(self.page.close, "page")
        except Exception:
            pass

        try:
            if self.context and not self.external_browser:
                self._close_with_timeout(self.context.close, "context")
        except Exception:
            pass

        try:
            if self.browser:
                self._close_with_timeout(self.browser.close, "browser")
        except Exception:
            pass

        try:
            if self.playwright:
                self._close_with_timeout(self.playwright.stop, "playwright")
        except Exception:
            pass

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    def measure_step(self, step_name: str, action: Callable[[], None]) -> None:
        """
        Executes 'action' (callable), measures time, and records metrics.
        Takes screenshot on error. Raises exception on failure to stop the flow.
        """
        if debug_mode:
            logger.info(f"[{self.usecase_name}] Starting step: {step_name}")
        start_time = time.time()
        try:
            action()
            duration = time.time() - start_time
            TRANS_DURATION.labels(usecase=self.usecase_name, step=step_name).set(duration)
            if debug_mode:
                logger.info(f"[{self.usecase_name}] Step '{step_name}' success ({duration:.2f}s)")
        except Exception as exc:
            duration = time.time() - start_time
            # Take screenshot, save HTML, and error stack before logging error
            self._take_screenshot(step_name, "step_failure")
            self._save_page_html(step_name, "step_failure")
            self._save_error_stack(step_name, "step_failure", exc)
            TRANS_DURATION.labels(usecase=self.usecase_name, step=step_name).set(duration)
            # Always log errors, regardless of DEBUG mode
            logger.error(f"[{self.usecase_name}] Step '{step_name}' FAILED after {duration:.2f}s", exc_info=True)
            STEP_FAILURE.labels(usecase=self.usecase_name, step=step_name).inc()
            raise

    def execute(self) -> bool:
        """
        Full execution wrapper: Setup -> Run -> Teardown -> Record Success/Fail
        Note: Screenshots are taken by measure_step() on step failures.
        """
        # Always log start of transaction
        logger.info(f"[{self.usecase_name}] Transaction START")
        TRANS_LAST_RUN.labels(usecase=self.usecase_name).set_to_current_time()
        success = False
        try:
            self.setup()
            self.run()
            success = True
            # Always log successful completion
            logger.info(f"[{self.usecase_name}] Transaction SUCCESS")
        except Exception:
            # Always log failures (screenshot already taken in measure_step)
            logger.error(f"[{self.usecase_name}] Transaction FAILED", exc_info=True)
        finally:
            self.teardown()
            TRANS_SUCCESS.labels(usecase=self.usecase_name).set(1 if success else 0)
        return success

    @abstractmethod
    def run(self) -> None:
        """Implement the actual test steps here using self.page"""
        pass
