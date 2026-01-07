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
            # Robust Login (Using the recorded roles with fallback to IDs if possible)
            try:
                self.page.get_by_role('textbox', name='Kontoname oder E-Mail-Adresse').fill(username, timeout=10000)
            except Exception:
                # Fallback to broad locator if role name differs by language
                self.page.locator('input[name="user"], #user').fill(username, timeout=5000)
                
            try:
                self.page.get_by_role('textbox', name='Passwort').fill(password, timeout=10000)
            except Exception:
                self.page.locator('input[name="password"], #password').fill(password, timeout=5000)
                
            try:
                self.page.get_by_role('button', name='Anmelden').click(timeout=10000)
            except Exception:
                self.page.locator('button[type="submit"], #submit').click(timeout=5000)
            
            # Wait for dashboard
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open settings menu and navigate to Security
        def navigate_to_settings_and_security():
            # Open settings menu
            try:
                self.page.get_by_role('button', name='Einstellungen-Menü').click(timeout=10000)
            except Exception:
                self.page.locator('button#settings, .settings-menu').click(timeout=5000)
            
            # Navigate to Personal Settings using the specific ID
            try:
                self.page.locator('a#settings[href*="/settings/user"]').click(timeout=10000)
            except Exception:
                # Fallback to text-based selector
                self.page.get_by_role('link', name='Persönliche Einstellungen').click(timeout=5000)
            
            # Navigate to Security
            try:
                self.page.get_by_role('link', name='Sicherheit').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("Sicherheit"), a:has-text("Security"), a[href*="security"]').first.click(timeout=5000)
            
            # Wait for security page to load
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("03_Navigate to Settings & Security", navigate_to_settings_and_security)

        # Step 4: Go back to files
        def go_back_to_files():
            try:
                self.page.get_by_role('link', name='Dateien aufrufen').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("Dateien aufrufen"), a:has-text("Access files"), a[href*="files"]').click(timeout=5000)
            
            # Wait for files page to load
            self.page.wait_for_load_state("networkidle", timeout=15000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 5: Logout
        def logout():
            # Open settings menu
            try:
                self.page.get_by_role('button', name='Einstellungen-Menü').click(timeout=10000)
            except Exception:
                self.page.locator('button#settings, .settings-menu').click(timeout=5000)
            
            # Logout
            try:
                self.page.get_by_role('link', name='Abmelden').click(timeout=10000)
            except Exception:
                self.page.locator('a:has-text("Abmelden"), a:has-text("Logout"), #logout').click(timeout=5000)

        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = IonosManagedNextcloudSettingsTest()
    monitor.execute()
