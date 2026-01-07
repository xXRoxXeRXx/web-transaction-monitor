from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class HiDriveLegacySettingsTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_legacy_settings_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('HIDRIVE_LEGACY_URL', 'https://hidrive.ionos.com/#login')
        username = os.getenv('HIDRIVE_LEGACY_USER')
        password = os.getenv('HIDRIVE_LEGACY_PASS')
        
        if not username or not password:
            raise ValueError("HIDRIVE_LEGACY_USER and HIDRIVE_LEGACY_PASS must be set in environment")
        
        # Step 1: Go to start URL
        def goto_start():
            self.page.goto(login_url)
        
        self.measure_step("01_Go to start URL", goto_start)

        # Step 2: Cookie & Login
        def login_logic():
            # Accept cookies
            try:
                self.page.locator('[data-qa="privacy_consent_approve_all"]').click(timeout=5000)
            except Exception:
                logger.info("[hidrive-legacy_settings_test] Cookie banner not found")
            
            # Fill username
            self.page.fill('input[name="username"]', username)
            
            # Fill password
            self.page.fill('input[name="password"]', password)
            
            # Click login
            self.page.click('[data-qa="login_submit"]')
            
            # Wait for login to complete
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_selector('.file-item-icon', timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Navigate to Settings
        def navigate_to_settings():
            # Click on Settings link using the correct selector
            self.page.locator('li.sj-navigation-item[data-name="settings.account"] a').click(timeout=5000)
            self.page.wait_for_load_state("networkidle", timeout=15000)

        self.measure_step("03_Navigate to Settings", navigate_to_settings)

        # Step 4: Navigate to Private section
        def navigate_to_private():
            # Click on Personal/Private link using the correct selector
            self.page.locator('li.sj-navigation-item[data-name="my.files"] a').click(timeout=5000)
            self.page.wait_for_load_state("networkidle", timeout=15000)

        self.measure_step("04_Navigate to Private", navigate_to_private)

        # Step 5: Logout
        def logout_logic():
            # Logout
            self.page.locator('a[href="#logout"]').click()
            self.page.wait_for_load_state("networkidle", timeout=15000)

        self.measure_step("05_Logout", logout_logic)

if __name__ == "__main__":
    monitor = HiDriveLegacySettingsTest()
    monitor.execute()
