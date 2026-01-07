from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class HiDriveNextSettingsTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_next_settings_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('HIDRIVE_NEXT_URL', 'https://id.ionos.fr/identifier?')
        username = os.getenv('HIDRIVE_NEXT_USER')
        password = os.getenv('HIDRIVE_NEXT_PASS')
        
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Cookie & Login
        def login_logic():
            # Robust Cookie Acceptance
            try:
                self.page.click("#selectAll", timeout=2000)
            except Exception:
                pass
            
            # Fill Username
            self.page.fill("input#username", username, timeout=10000)
            self.page.click("button#button--with-loader", timeout=10000)
            
            # Fill Password
            self.page.fill("input#password", password, timeout=10000)
            self.page.click("button#button--with-loader", timeout=10000)
            
            # Wait for page load and network idle after login
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_timeout(2000)
            
            # Wait for files list to appear
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open user menu, navigate to settings and apps
        def navigate_to_settings_and_apps():
            # Open user menu using aria-label (language-independent)
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=10000)
            
            # Navigate to Settings using data-qa attribute (language-independent)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-SETTINGS-TARGET"]').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
            
            # Navigate to Apps & Software using icon class (language-independent)
            # Increased timeout as this can be slow in Docker/headless mode
            self.page.locator('a.app-navigation-entry-link:has(.desktop-classic-icon)').click(timeout=20000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("03_Navigate to Settings & Apps", navigate_to_settings_and_apps)

        # Step 5: Go back to files
        def go_back_to_files():
            # Use ID (language-independent)
            self.page.locator('#backButton a.app-navigation-entry-link').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 6: Logout
        def logout():
            # Open user menu
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=10000)
            
            # Click logout using data-qa attribute (language-independent)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-LOGOUT-TARGET"]').click(timeout=10000)
        
        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = HiDriveNextSettingsTest()
    monitor.execute()
