from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class HiDriveNextDocumentTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_next_document_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('HIDRIVE_NEXT_URL', 'https://id.ionos.fr/identifier?')
        username = os.getenv('HIDRIVE_NEXT_USER')
        password = os.getenv('HIDRIVE_NEXT_PASS')
        
        if not username or not password:
            raise ValueError("HIDRIVE_NEXT_USER and HIDRIVE_NEXT_PASS must be set in environment")
        
        # Step 1: Go to start URL
        def goto_start():
            self.page.goto(login_url)

        self.measure_step("01_Goto HiDrive Next", goto_start)

        # Step 2: Cookie & Login
        def login_logic():
            # Robust Cookie Acceptance
            try:
                self.page.click("#selectAll", timeout=30000)
            except Exception:
                pass
            
            # Fill Username (initial page)
            username_field = self.page.locator("input#username, input[type='email'][name='identifier']")
            username_field.first.wait_for(state="visible", timeout=30000)
            
            # Get the current URL before clicking
            url_before_click = self.page.url
            logger.info(f"URL before username submit: {url_before_click}")
            
            # Fill and submit username
            self.page.fill("input#username, input[type='email'][name='identifier']", username)
            self.page.click("button#button--with-loader", timeout=30000)
            
            # Wait for page to respond to the click
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(1500)  # Give page time to process
            
            # Check what happened after the click
            url_after_click = self.page.url
            logger.info(f"URL after username submit: {url_after_click}")
            
            # Check if we're still on an IONOS ID page (email input page)
            if "/identifier" in url_after_click or "id.ionos" in url_after_click:
                # We're on IONOS ID page - check if username field is still there
                email_field_visible = self.page.locator("input#username, input[type='email'][name='identifier']").is_visible()
                
                if email_field_visible:
                    # Email field still visible - this means we redirected to IONOS but form wasn't submitted
                    logger.info("Detected IONOS ID redirect - username field still visible, resubmitting")
                    
                    # Fill username again and click
                    self.page.fill("input#username, input[type='email'][name='identifier']", username)
                    self.page.click("button#button--with-loader", timeout=30000)
                    self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                    self.page.wait_for_timeout(1500)
                    
                    logger.info(f"URL after second submit: {self.page.url}")
            
            # Now wait for password field to appear (exclude hidden honeypot field)
            password_field = self.page.locator("input#password:not(.hidden), input[type='password']:not(.hidden):not([name='hiddenPassword'])")
            password_field.first.wait_for(state="visible", timeout=30000)
            
            # Fill password and submit
            logger.info("Password field visible - filling password")
            self.page.fill("input#password:not(.hidden), input[type='password']:not(.hidden):not([name='hiddenPassword'])", password)
            self.page.click("button#button--with-loader", timeout=30000)
            
            # Wait for post-login page to load
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Wait for files list to appear
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Open document
        def open_document():
            # Click on first document with .docx extension using data-cy attribute
            self.page.locator('tr[data-cy-files-list-row][data-cy-files-list-row-name$=".docx"]').first.locator('button[data-cy-files-list-row-name-link]').click(timeout=30000)
            
            # Wait for Collabora iframe to load (name is dynamic: collaboraframe_xxxxx)
            self.page.wait_for_selector('iframe[name^="collaboraframe_"]', timeout=60000)
            
            # Get the iframe and wait for close button
            iframe = self.page.frame_locator('iframe[name^="collaboraframe_"]')
            iframe.locator('#closebutton').wait_for(timeout=30000)
            
            # Wait for document canvas to be rendered (indicates document is loaded)
            iframe.locator('#document-canvas').wait_for(state='visible', timeout=30000)

        self.measure_step("03_Open document", open_document)

        # Step 4: Close document
        def close_document():
            # Click close button in iframe
            iframe = self.page.frame_locator('iframe[name^="collaboraframe_"]')
            iframe.locator('#closebutton').click(timeout=30000)
            
            # Wait for navigation back to file list
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Wait for files list to appear
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("04_Close document", close_document)

        # Step 5: Logout
        def logout_logic():
            # Open user menu
            self.page.locator('ionos-icons[role="button"][aria-label="User Menu"]').click(timeout=30000)
            
            # Click logout using data-qa attribute (language-independent)
            self.page.locator('ionos-user-menu-item[data-qa="IONOS-USER-MENU-LOGOUT-TARGET"]').click(timeout=30000)

        self.measure_step("05_Logout", logout_logic)

if __name__ == "__main__":
    test = HiDriveNextDocumentTest()
    test.execute()
