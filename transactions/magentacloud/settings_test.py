from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class MagentaCloudPictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "magentacloud_picture_test"
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

        # Step 3: Browse and open picture
        def browse_logic():
            # Navigate to pictures folder
            pictures_button = self.page.locator('tr[data-cy-files-list-row-name="pictures"] button[data-cy-files-list-row-name-link]')
            pictures_button.wait_for(state="visible", timeout=30000)
            pictures_button.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Navigate to Norway folder
            norway_button = self.page.locator('tr[data-cy-files-list-row-name="Norway"] button[data-cy-files-list-row-name-link]')
            norway_button.wait_for(state="visible", timeout=30000)
            norway_button.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Open image
            image_button = self.page.locator('tr[data-cy-files-list-row-name="abhishek-umrao-qsvNYg6iMGk-unsplash.jpg"] button[data-cy-files-list-row-name-link]')
            image_button.wait_for(state="visible", timeout=30000)
            image_button.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close picture viewer
        def close_viewer():
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)

        self.measure_step("04_Close picture viewer", close_viewer)

        # Step 5: Logout
        def logout():
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            self.page.locator('a#logout').click(timeout=30000)

        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = MagentaCloudPictureTest()
    monitor.execute()