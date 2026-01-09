from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class HiDriveNextSettingsTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_next_settings_test"
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
            
            # Fill Username (initial page - HiDrive login)
            username_field = self.page.locator("input#username")
            username_field.wait_for(state="visible", timeout=30000)
            self.page.fill("input#username", username)
            self.page.wait_for_timeout(1000)  # Wait 1 second after filling
            
            # Click submit button
            self.page.click("button#button--with-loader", timeout=30000)
            
            # Wait for page to navigate
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Check current URL after first submit
            current_url = self.page.url
            logger.info(f"URL after first submit: {current_url}")
            
            # Check if we got redirected to IONOS ID page with email field
            if "id.ionos" in current_url and "/identifier" in current_url:
                # We're on IONOS redirect page - check if email field is visible
                email_field_ionos = self.page.locator("input[type='email'][name='identifier']")
                
                if email_field_ionos.is_visible():
                    logger.info("Detected IONOS ID redirect - email field visible, filling and submitting")
                    
                    # Fill email and submit on IONOS page
                    self.page.fill("input[type='email'][name='identifier']", username)
                    self.page.wait_for_timeout(1000)  # Wait 1 second after filling
                    self.page.click("button#button--with-loader", timeout=30000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    
                    logger.info(f"URL after IONOS submit: {self.page.url}")
            
            # Check again if we're still on email page (sometimes happens)
            # Wait a bit and check if email field is still visible
            self.page.wait_for_timeout(2000)
            email_field_check = self.page.locator("input[type='email'][name='identifier']")
            
            if email_field_check.is_visible():
                logger.warning("Still on email page after first attempt - retrying email submit")
                self.page.fill("input[type='email'][name='identifier']", username)
                self.page.wait_for_timeout(1000)
                self.page.click("button#button--with-loader", timeout=30000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                logger.info(f"URL after retry email submit: {self.page.url}")
            
            # Now wait for password field to appear (use exact selector from HTML)
            password_field = self.page.locator("input[type='password'][name='password']")
            password_field.wait_for(state="visible", timeout=30000)
            
            # Fill password and submit
            logger.info("Password field visible - filling password")
            self.page.fill("input[type='password'][name='password']", password)
            self.page.wait_for_timeout(1000)  # Wait 1 second after filling
            self.page.click("button#button--with-loader", timeout=30000)
            
            # Wait for post-login page to load
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Check if we're still on login page (login failed)
            current_url_after_password = self.page.url
            logger.info(f"URL after password submit: {current_url_after_password}")
            
            # If we're still on IONOS login page, try login again
            if "id.ionos" in current_url_after_password and "/identifier" in current_url_after_password:
                logger.warning("Still on login page after password submit - retrying login")
                
                # Fill email again
                email_field_retry = self.page.locator("input[type='email'][name='identifier']")
                if email_field_retry.is_visible():
                    self.page.fill("input[type='email'][name='identifier']", username)
                    self.page.wait_for_timeout(1000)
                    self.page.click("button#button--with-loader", timeout=30000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    logger.info(f"URL after retry email submit: {self.page.url}")
                
                # Fill password again
                password_field_retry = self.page.locator("input[type='password'][name='password']")
                password_field_retry.wait_for(state="visible", timeout=30000)
                self.page.fill("input[type='password'][name='password']", password)
                self.page.wait_for_timeout(1000)
                self.page.click("button#button--with-loader", timeout=30000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                logger.info(f"URL after retry password submit: {self.page.url}")
            
            # Wait for files list to appear
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open user menu, navigate to settings and apps
        def navigate_to_settings_and_apps():
            # Open user menu using aria-label (language-independent)
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=30000)
            
            # Navigate to Settings using data-qa attribute (language-independent)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-SETTINGS-TARGET"]').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Navigate to Apps & Software using icon class (language-independent)
            # Increased timeout as this can be slow in Docker/headless mode
            self.page.locator('a.app-navigation-entry-link:has(.desktop-classic-icon)').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
        
        self.measure_step("03_Navigate to Settings & Apps", navigate_to_settings_and_apps)

        # Step 5: Go back to files
        def go_back_to_files():
            # Use ID (language-independent)
            self.page.locator('#backButton a.app-navigation-entry-link').click(timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
        
        self.measure_step("04_Go back to files", go_back_to_files)

        # Step 6: Logout
        def logout():
            # Open user menu
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=30000)
            
            # Click logout using data-qa attribute (language-independent)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-LOGOUT-TARGET"]').click(timeout=30000)
        
        self.measure_step("05_Logout", logout)

if __name__ == "__main__":
    monitor = HiDriveNextSettingsTest()
    monitor.execute()
