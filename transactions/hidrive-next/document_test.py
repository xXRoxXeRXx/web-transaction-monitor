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
            
            # Fill Username
            self.page.fill("input#username", username, timeout=30000)
            self.page.click("button#button--with-loader", timeout=30000)
            
            # Fill Password
            self.page.fill("input#password", password, timeout=30000)
            self.page.click("button#button--with-loader", timeout=30000)
            
            # Wait for page load and network idle after login
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_timeout(2000)
            
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
