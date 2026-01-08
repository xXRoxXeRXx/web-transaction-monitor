from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class IonosManagedNextcloudSettingsTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "ionos_managed_nextcloud_settings_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('IONOS_MANAGED_NEXTCLOUD_URL', 'https://managed-nextcloud.example.com/login')
        username = os.getenv('IONOS_MANAGED_NEXTCLOUD_USER')
        password = os.getenv('IONOS_MANAGED_NEXTCLOUD_PASS')
        
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Cookie & Login
        def login_logic():
            # Login using data attributes (language-independent)
            self.page.locator('input[data-login-form-input-user]').fill(username, timeout=30000)
            self.page.locator('input[data-login-form-input-password]').fill(password, timeout=30000)
            self.page.locator('button[data-login-form-submit]').click(timeout=30000)
            
            # Wait for dashboard to load (increased timeout for networkidle due to background requests)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open settings menu and navigate to Security
        def navigate_to_settings_and_security():
            # Open settings menu using ID (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            
            # Navigate to Personal Settings using ID (language-independent)
            self.page.locator('a#settings').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Navigate to Security - use href to distinguish between user and admin security (language-independent)
            self.page.locator('li[data-section-id="security"] a[href*="/settings/user/security"]').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
        
        self.measure_step("03_Navigate to Settings & Security", navigate_to_settings_and_security)

        # Step 4: Go back to files
        def go_back_to_files():
            # Go back to files using ID (language-independent)
            self.page.locator('a#nextcloud').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 5: Logout
        def logout():
            # Open settings menu and logout using IDs (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            self.page.locator('a#logout').click(timeout=30000)

        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = IonosManagedNextcloudSettingsTest()
    monitor.execute()
