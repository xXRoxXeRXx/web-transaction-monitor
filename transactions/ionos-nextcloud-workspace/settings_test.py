from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class IonosNextcloudWorkspaceSettingsTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "ionos_nextcloud_workspace_settings_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('IONOS_NEXTCLOUD_WORKSPACE_URL', 'https://workspace.kallisto45.de/login')
        username = os.getenv('IONOS_NEXTCLOUD_WORKSPACE_USER')
        password = os.getenv('IONOS_NEXTCLOUD_WORKSPACE_PASS')
        
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Cookie & Login
        def login_logic():
            # Login using data attributes (language-independent)
            self.page.locator('input[data-login-form-input-user]').fill(username, timeout=10000)
            self.page.locator('input[data-login-form-input-password]').fill(password, timeout=10000)
            self.page.locator('button[data-login-form-submit]').click(timeout=10000)
            
            # Wait for dashboard to load
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open settings menu and navigate to Security
        def navigate_to_settings_and_security():
            # Open settings menu using ID (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=10000)
            
            # Navigate to Settings using ID (language-independent)
            self.page.locator('a#settings').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
            
            # Navigate to Security using data-section-id (language-independent)
            self.page.locator('li[data-section-id="security"] a').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("03_Navigate to Settings & Security", navigate_to_settings_and_security)

        # Step 4: Go back to files
        def go_back_to_files():
            # Use ID (language-independent)
            self.page.locator('a#nextcloud').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 5: Logout
        def logout():
            # Open settings menu using ID (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=10000)
            
            # Logout using ID (language-independent)
            self.page.locator('a#logout').click(timeout=10000)

        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = IonosNextcloudWorkspaceSettingsTest()
    monitor.execute()
