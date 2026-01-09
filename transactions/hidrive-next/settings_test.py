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
                    
                    # On IONOS ID page, we MUST fill the username field
                    # Even if it appears hidden or pre-filled, we need to ensure it has a value
                    username_field_ionos = self.page.locator("input#username, input[type='email']")
                    username_field_ionos.first.wait_for(state="attached", timeout=5000)
                    
                    # Force fill the username
                    logger.info("Filling username on IONOS ID page")
                    self.page.fill("input#username", username)
                    
                    # Click continue button and wait for navigation
                    logger.info(f"Current URL before continue: {self.page.url}")
                    self.page.click("button#button--with-loader", timeout=30000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    logger.info(f"Current URL after continue: {self.page.url}")
                    
                    # Wait a bit more for page to stabilize
                    self.page.wait_for_timeout(2000)
                    
                    # Fill password on IONOS ID page
                    password_field_ionos = self.page.locator("input#password")
                    password_field_ionos.wait_for(state="visible", timeout=30000)
                    self.page.fill("input#password", password)
                    self.page.click("button#button--with-loader", timeout=30000)
                else:
                    # Unknown state - re-raise the exception
                    raise
            
            # Wait for page load and network idle after login
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_timeout(2000)
            
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
