from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class MagentaCloudSettingsTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "magentacloud_settings_test"
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        login_url = os.getenv('MAGENTACLOUD_URL', 'https://magentacloud.example.com/login')
        username = os.getenv('MAGENTACLOUD_USER')
        password = os.getenv('MAGENTACLOUD_PASS')

        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: self.page.goto(login_url))

        # Step 2: Cookie & Login
        def login_logic():
            # Recorded MagentaCloud login flow
            try:
                self.page.get_by_role("button", name="Alle akzeptieren").click(timeout=30000)
            except Exception:
                pass

            self.page.get_by_role("textbox", name="Benutzername").click(timeout=30000)
            self.page.get_by_role("textbox", name="Benutzername").fill(username, timeout=30000)
            self.page.get_by_role("button", name="Weiter").click(timeout=30000)

            self.page.get_by_role("textbox", name="Passwort").click(timeout=30000)
            self.page.get_by_role("textbox", name="Passwort").fill(password, timeout=30000)
            self.page.get_by_role("textbox", name="Passwort").press("Enter", timeout=30000)

            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Check for OIDC error and retry if needed
            try:
                error_box = self.page.locator('.guest-box:has-text("Zugriff verboten")')
                if error_box.is_visible(timeout=2000):
                    logger.warning("OIDC error detected, clicking 'Zurück zu MagentaCLOUD' to retry")
                    self.page.locator('a.button.primary[href="/"]').click(timeout=10000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
            
            self.page.wait_for_selector('.files-list', timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open settings menu and navigate to Security
        def navigate_to_settings_and_security():
            # Open user menu
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            self.page.wait_for_timeout(500)
            
            # Click on Settings link (the <a> inside the <li id="settings">)
            self.page.locator('li#settings a').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Navigate to Security using data-section-id (language-independent)
            self.page.locator('li[data-section-id="sessions"] a').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
        
        self.measure_step("03_Navigate to Settings & Security", navigate_to_settings_and_security)

        # Step 4: Go back to files
        def go_back_to_files():
            # Click on "Dateien" link in app menu
            self.page.locator('a[href="/apps/files/"]').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_selector('.files-list', timeout=30000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 5: Logout
        def logout():
            # Open settings menu using ID (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            
            # Logout using ID (language-independent)
            self.page.locator('a#logout').click(timeout=30000)

        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = MagentaCloudSettingsTest()
    monitor.execute()