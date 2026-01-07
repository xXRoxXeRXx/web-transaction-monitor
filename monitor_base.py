from abc import ABC, abstractmethod
import time
import logging
import os
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
        Raises exception on failure to stop the flow.
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
            logger.exception(f"[{self.usecase_name}] Step '{step_name}' FAILED")
            STEP_FAILURE.labels(usecase=self.usecase_name, step=step_name).inc()
            raise

    def execute(self) -> None:
        """
        Full execution wrapper: Setup -> Run -> Teardown -> Record Success/Fail
        """
        TRANS_LAST_RUN.labels(usecase=self.usecase_name).set_to_current_time()
        success = False
        try:
            self.setup()
            self.run()
            success = True
        except Exception:
            logger.exception(f"[{self.usecase_name}] Transaction FAILED") 
        finally:
            self.teardown()
            TRANS_SUCCESS.labels(usecase=self.usecase_name).set(1 if success else 0)

    @abstractmethod
    def run(self) -> None:
        """Implement the actual test steps here using self.page"""
        pass
