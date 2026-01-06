from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class HiDriveLegacyPictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_legacy_picture_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('HIDRIVE_LEGACY_URL', 'https://hidrive.ionos.com/#login')
        username = os.getenv('HIDRIVE_LEGACY_USER')
        password = os.getenv('HIDRIVE_LEGACY_PASS')
        
        if not username or not password:
            raise ValueError("HIDRIVE_LEGACY_USER and HIDRIVE_LEGACY_PASS must be set in environment")
        
        # Step 1: Go to start URL
        def goto_start():
            self.page.goto(login_url)
        
        self.measure_step("01_Go to start URL", goto_start)

        # Step 2: Cookie & Login
        def login_logic():
            # Accept cookies
            try:
                self.page.locator('[data-qa="privacy_consent_approve_all"]').click(timeout=5000)
            except Exception:
                logger.info("[hidrive-legacy_picture_test] Cookie banner not found")
            
            # Fill username
            self.page.fill('input[name="username"]', username)
            
            # Fill password
            self.page.fill('input[name="password"]', password)
            
            # Click login
            self.page.click('[data-qa="login_submit"]')
            
            # Wait for file list
            self.page.wait_for_selector('.file-item-icon', timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Browse and open picture
        def browse_logic():
            # First folder
            self.page.locator('.file-item-icon > svg > path').click()
            
            # Second folder
            self.page.locator('.file-item-icon > svg > path').click()
            
            # Open picture (3rd item)
            self.page.locator('tile-item:nth-child(3) > .itemcontent > .file-item-icon > .thumbnail').click()
            
            # Wait for image to load (wait for viewer to be ready)
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close and Logout
        def logout_logic():
            # Close preview
            self.page.locator('.filesviewer-overlay-close').click()
            
            # Logout
            self.page.locator('a[href="#logout"]').click()
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("04_Close and Logout", logout_logic)

if __name__ == "__main__":
    monitor = HiDriveLegacyPictureTest()
    monitor.execute()
