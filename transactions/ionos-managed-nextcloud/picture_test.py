from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class IonosManagedNextcloudPictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "ionos_managed_nextcloud_picture_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('IONOS_MANAGED_NEXTCLOUD_URL', 'https://workspace.kallisto45.de/login')
        username = os.getenv('IONOS_MANAGED_NEXTCLOUD_USER')
        password = os.getenv('IONOS_MANAGED_NEXTCLOUD_PASS')
        
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
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Browse and open picture
        def browse_logic():
            # Click folder 'pictures'
            self.page.locator('tr:nth-child(3) > .files-list__row-name > .files-list__row-icon > .material-design-icon > .material-design-icon__svg > path').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Click folder 'norway'
            self.page.locator('.material-design-icon.folder-icon > .material-design-icon__svg > path').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Open picture - click on the row name to avoid canvas overlay issues
            self.page.locator('tr[data-cy-files-list-row-name="abhishek-umrao-qsvNYg6iMGk-unsplash.jpg"] .files-list__row-name-text').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Verify image viewer is open and image is loaded
            self.page.wait_for_selector('.viewer__file-wrapper img.loaded', timeout=10000)

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close and Logout
        def logout_logic():
            # Close Preview using class selector (language-independent)
            self.page.locator('button.header-close').click(timeout=5000)
            
            # Logout using IDs (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=5000)
            self.page.locator('a#logout').click(timeout=10000)

        self.measure_step("04_Close and Logout", logout_logic)

if __name__ == "__main__":
    monitor = IonosManagedNextcloudPictureTest()
    monitor.execute()

