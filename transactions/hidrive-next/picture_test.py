from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class HiDriveNextPictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_next_picture_test"
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

        # Step 3: Browse and open picture
        def browse_logic():
            # Click folder 'pictures'
            self.page.locator('tr:nth-child(3) > .files-list__row-name > .files-list__row-icon > .material-design-icon > .material-design-icon__svg > path').click(timeout=10000)
            
            # Click folder 'norway'
            self.page.locator('.material-design-icon.folder-icon > .material-design-icon__svg > path').click(timeout=10000)
            
            # Open picture using data-cy attribute (language-independent)
            self.page.locator('tr[data-cy-files-list-row-name="abhishek-umrao-qsvNYg6iMGk-unsplash.jpg"] img').click(timeout=10000)
            
            # Wait for image to fully load
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close and Logout
        def logout_logic():
            # Close Preview using class and aria-label (language-independent)
            self.page.locator('button.header-close[aria-label="Close"]').click(timeout=5000)
            
            # Logout using data-qa attributes (language-independent)
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=5000)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-LOGOUT-TARGET"]').click(timeout=5000)

        self.measure_step("04_Close and Logout", logout_logic)

if __name__ == "__main__":
    monitor = HiDriveNextPictureTest()
    monitor.execute()

