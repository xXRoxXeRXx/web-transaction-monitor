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
            self.page.wait_for_selector('.files-list', timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

                # Step 3: Browse and open picture
        def browse_logic():
            # Click folder 'pictures' - click on the text/name directly
            self.page.locator('tr[data-cy-files-list-row-name="pictures"] .files-list__row-name-text').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Click folder 'Norway' - click on the text/name directly
            self.page.locator('tr[data-cy-files-list-row-name="Norway"] .files-list__row-name-text').click(timeout=30000)
            self.page.locator('tr[data-cy-files-list-row-name="Norway"] .files-list__row-name-text').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Open picture - click on the text/name directly
            self.page.locator('tr[data-cy-files-list-row-name="abhishek-umrao-qsvNYg6iMGk-unsplash.jpg"] .files-list__row-name-text').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Verify image viewer is open and image is loaded
            self.page.wait_for_selector('.viewer__file-wrapper img.loaded', timeout=30000)

        self.measure_step("03_Browse and open picture", browse_logic)

    

        # Step 4: Logout
        def logout():
            # Close Preview using class selector (language-independent)
            self.page.locator('button.header-close').click(timeout=30000)
            
            # Logout using IDs (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            self.page.locator('a#logout').click(timeout=30000)

        self.measure_step("04_Logout", logout)

if __name__ == "__main__":
    monitor = MagentaCloudPictureTest()
    monitor.execute()
