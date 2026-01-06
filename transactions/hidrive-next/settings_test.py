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
            self.page.fill("input#username", username, timeout=5000)
            self.page.click("button#button--with-loader", timeout=5000)
            
            # Fill Password
            self.page.fill("input#password", password, timeout=10000)
            self.page.click("button#button--with-loader", timeout=5000)
            
            # Fast Wait for post-login element
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open user menu, navigate to settings and apps
        def navigate_to_settings_and_apps():
            # Open user menu
            try:
                self.page.get_by_role('button', name='User Menu').click(timeout=10000)
            except Exception:
                self.page.locator('button[aria-label="User Menu"], .user-menu-button').click(timeout=5000)
            
            # Navigate to Settings
            try:
                self.page.get_by_role('link', name='Einstellungen').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("Einstellungen"), a[href*="settings"]').click(timeout=5000)
            
            # Navigate to Apps & Software
            try:
                self.page.get_by_role('link', name='App & Software').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("App & Software"), a:has-text("Apps")').click(timeout=5000)
            
            # Wait for apps page to load
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("03_Navigate to Settings & Apps", navigate_to_settings_and_apps)

        # Step 5: Go back to files
        def go_back_to_files():
            try:
                self.page.get_by_role('link', name='Zurück zu Dateien').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("Zurück zu Dateien"), a:has-text("Back to Files"), a[href*="files"]').click(timeout=5000)
            
            # Wait for files page to load
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 6: Logout
        def logout():
            try:
                self.page.get_by_role('button', name='User Menu').click(timeout=10000)
            except Exception:
                self.page.locator('button[aria-label="User Menu"], .user-menu-button').click(timeout=5000)
            
            try:
                self.page.get_by_role('link', name='Abmelden').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("Abmelden"), a:has-text("Logout"), #logout').click(timeout=5000)
        
        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = HiDriveNextSettingsTest()
    monitor.execute()
