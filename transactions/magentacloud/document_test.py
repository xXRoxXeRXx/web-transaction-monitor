from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class MagentaCloudDocumentTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "magentacloud_document_test"
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

            try:
                self.page.get_by_role("button", name="Login").click(timeout=30000)
            except Exception:
                pass

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

        # Step 3: Browse and open document
        def browse_logic():
            # Navigate to documents folder
            documents_button = self.page.locator('tr[data-cy-files-list-row-name="documents"] button[data-cy-files-list-row-name-link]')
            documents_button.wait_for(state="visible", timeout=30000)
            documents_button.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Open first document (assuming it's a PDF or text file)
            first_document = self.page.locator('tr[data-cy-files-list-row]:not([data-cy-files-list-row-name*="."]) button[data-cy-files-list-row-name-link]').first
            first_document.wait_for(state="visible", timeout=30000)
            first_document.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("03_Browse and open document", browse_logic)

        # Step 4: Close document viewer
        def close_viewer():
            # Try to close via Escape key
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)
            
            # If viewer has a close button, try that as well
            try:
                close_button = self.page.locator('button[aria-label*="Close"], button[aria-label*="Schließen"]').first
                if close_button.is_visible():
                    close_button.click()
                    self.page.wait_for_timeout(500)
            except Exception:
                pass

        self.measure_step("04_Close document viewer", close_viewer)

        # Step 5: Logout
        def logout():
            user_menu = self.page.locator('#user-menu button.header-menu__trigger')
            user_menu.wait_for(state="visible", timeout=30000)
            user_menu.click()
            self.page.wait_for_timeout(500)
            
            logout_link = self.page.locator('a#logout')
            logout_link.wait_for(state="visible", timeout=30000)
            logout_link.click()

        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = MagentaCloudDocumentTest()
    monitor.execute()