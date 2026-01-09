from abc import ABC, abstractmethod
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
    def __init__(self, usecase_name: str, headless: bool = True) -> None:
        self.usecase_name = usecase_name
        self.headless = headless
        self.playwright: Optional[object] = None
        self.browser: Optional[Browser] = None
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
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        # Use default system locale for language-independent testing
        self.page = self.browser.new_page()

    def teardown(self) -> None:
        """Cleans up Playwright"""
        if self.page: self.page.close()
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()

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
        except Exception:
            duration = time.time() - start_time
            # Take screenshot and save HTML before logging error
            self._take_screenshot(step_name, "step_failure")
            self._save_page_html(step_name, "step_failure")
            # Always log errors, regardless of DEBUG mode
            logger.error(f"[{self.usecase_name}] Step '{step_name}' FAILED after {duration:.2f}s", exc_info=True)
            STEP_FAILURE.labels(usecase=self.usecase_name, step=step_name).inc()
            raise

    def execute(self) -> None:
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

    @abstractmethod
    def run(self) -> None:
        """Implement the actual test steps here using self.page"""
        pass
