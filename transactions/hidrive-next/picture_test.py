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
                self.page.click("#selectAll", timeout=30000)
            except Exception:
                pass
            
            # Fill Username
            username_field = self.page.locator("input#username")
            username_field.wait_for(state="visible", timeout=30000)
            self.page.fill("input#username", username)
            
            # Click submit and wait for navigation
            self.page.click("button#button--with-loader", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Check which page we landed on after username submit
            current_url = self.page.url
            
            # Try to detect if password field is already visible (normal flow)
            password_field = self.page.locator("input#password")
            try:
                password_field.wait_for(state="visible", timeout=3000)
                # Normal flow: password field appeared on same page
                logger.info("Normal login flow - password field visible")
                self.page.fill("input#password", password)
                self.page.click("button#button--with-loader", timeout=30000)
            except Exception:
                # Password field not visible - check if redirected to IONOS ID
                if "id.ionos.fr" in current_url or "id.ionos.de" in current_url or "id.ionos.com" in current_url:
                    logger.info("Detected redirect to IONOS ID login page")
                    
                    # Username is pre-filled, just click continue button
                    self.page.click("button#button--with-loader", timeout=30000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    
                    # Fill password on IONOS ID page
                    password_field_ionos = self.page.locator("input#password")
                    password_field_ionos.wait_for(state="visible", timeout=30000)
                    self.page.fill("input#password", password)
                    self.page.click("button#button--with-loader", timeout=30000)
                else:
                    # Unknown state - re-raise the exception
                    raise
            
            # Wait for post-login page to load
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Fast Wait for post-login element
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Browse and open picture
        def browse_logic():
            # Click folder 'pictures'
            self.page.locator('tr:nth-child(3) > .files-list__row-name > .files-list__row-icon > .material-design-icon > .material-design-icon__svg > path').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Click folder 'norway'
            self.page.locator('.material-design-icon.folder-icon > .material-design-icon__svg > path').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Open picture - click on the row name to avoid canvas overlay issues
            self.page.locator('tr[data-cy-files-list-row-name="abhishek-umrao-qsvNYg6iMGk-unsplash.jpg"] .files-list__row-name-text').click(timeout=30000)
            
            # Wait for image to fully load
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Verify image viewer is open and image is loaded
            self.page.wait_for_selector('.viewer__file-wrapper img.loaded', timeout=30000)

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close and Logout
        def logout_logic():
            # Close Preview using class and aria-label (language-independent)
            self.page.locator('button.header-close[aria-label="Close"]').click(timeout=30000)
            
            # Logout using data-qa attributes (language-independent)
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=30000)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-LOGOUT-TARGET"]').click(timeout=30000)

        self.measure_step("04_Close and Logout", logout_logic)

if __name__ == "__main__":
    monitor = HiDriveNextPictureTest()
    monitor.execute()

