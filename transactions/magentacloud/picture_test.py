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
            # Accept cookies (language-independent)
            try:
                self.page.locator('button[data-action="accept-all"], button:has-text("Alle akzeptieren"), button:has-text("Accept all")').first.click(timeout=30000)
            except Exception:
                pass

            # Username field (language-independent - uses input type and name/id)
            username_field = self.page.locator('input[type="text"][name*="user" i], input[type="text"][name*="username" i], input[type="email"]').first
            username_field.wait_for(state="visible", timeout=30000)
            username_field.click()
            username_field.fill(username)
            
            # Submit button (scale-button custom element)
            self.page.locator('scale-button[type="submit"], scale-button[name="pw_submit"]').first.click(timeout=30000)

            # Password field (language-independent)
            password_field = self.page.locator('input[type="password"]').first
            password_field.wait_for(state="visible", timeout=30000)
            password_field.click()
            password_field.fill(password)
            
            # Submit password (scale-button)
            self.page.locator('scale-button[type="submit"], scale-button[name="pw_submit"]').first.click(timeout=30000)

            # Wait for navigation after password submit
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
            
            # Check if redirected to 2FA setup page and skip it
            current_url = self.page.url
            if "account.idm.telekom.com/account-manager/auth-methods/setup" in current_url:
                logger.warning("2FA setup page detected, clicking 'Später' to skip")
                try:
                    # Click "Später" button (scale-button with variant="secondary")
                    later_button = self.page.locator('scale-button[variant="secondary"]:has-text("Später"), scale-button:has-text("Später")')
                    later_button.first.click(timeout=10000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                except Exception as e:
                    logger.error(f"Could not click 'Später' button: {e}")
                    raise
            
            # Wait for files list with multiple possible selectors
            try:
                self.page.wait_for_selector('.files-list', timeout=30000)
            except Exception as e:
                # Try alternative selector or log current URL for debugging
                logger.error(f"Files list not found. Current URL: {self.page.url}")
                # Try waiting for the file list wrapper
                self.page.wait_for_selector('[data-cy-files-list]', timeout=10000)

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
