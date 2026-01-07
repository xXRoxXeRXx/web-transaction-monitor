from monitor_base import MonitorBase
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class HiDriveLegacyDocumentTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "hidrive_legacy_document_test"
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
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        document_name = f"Test_{timestamp}.docx"
        
        # Step 1: Go to start URL
        def goto_start():
            self.page.goto(login_url)
        
        self.measure_step("01_Go to start URL", goto_start)

        # Step 2: Cookie & Login
        def login_logic():
            # Accept cookies using data-qa (language-independent)
            try:
                self.page.locator('[data-qa="privacy_consent_approve_all"]').click(timeout=5000)
            except Exception:
                logger.info("[hidrive-legacy_document_test] Cookie banner not found")
            
            # Fill username
            self.page.fill('input[name="username"]', username)
            
            # Fill password
            self.page.fill('input[name="password"]', password)
            
            # Click login using data-qa
            self.page.click('[data-qa="login_submit"]')
            
            # Wait for login to complete
            self.page.wait_for_load_state("networkidle", timeout=15000)
            self.page.wait_for_selector('.file-item-icon', timeout=30000)

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Create and edit document
        def create_document_logic():
            # Click "mehr" button using data-qa (language-independent)
            self.page.locator('[data-qa="menubar_more"]').click(timeout=10000)
            
            # Click "Neues Dokument" menu item (div in menu, not button)
            self.page.locator('div.sj-menuitem[data-qa="menubar_new_document"]').click(timeout=10000)
            
            # Enter document name (without .docx extension, will be added automatically)
            filename_without_ext = document_name.replace('.docx', '')
            self.page.fill('input[name="file-name"]', filename_without_ext, timeout=10000)
            
            # Click "Erstellen" button using data-qa (language-independent)
            self.page.locator('[data-qa="file_create_ok"]').click(timeout=10000)
            
            # Wait for Collabora iframe to load (can be slow)
            self.page.wait_for_selector('iframe[name="collabora-online-viewer"]', timeout=60000)
            
            # Get iframe and type text
            iframe = self.page.frame_locator('iframe[name="collabora-online-viewer"]')
            iframe.locator('#clipboard-area').fill('Dies ist ein Test!', timeout=10000)
            
            # Wait for document canvas to confirm content is rendered
            iframe.locator('#document-canvas').wait_for(state='visible', timeout=10000)

        self.measure_step("03_Create and edit document", create_document_logic)

        # Step 4: Close document
        def close_document():
            # Close the editor
            self.page.locator('.office-editor-close').click(timeout=10000)
            
            # Wait for document list to appear and network to be idle
            self.page.wait_for_selector('tile-item', timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)

        self.measure_step("04_Close document", close_document)

        # Step 5: Delete document
        def delete_document():
            # Find the document and scroll it into view
            document_tile = self.page.locator('tile-item').filter(has_text=document_name)
            document_tile.scroll_into_view_if_needed(timeout=10000)
            
            # Right-click on the item to open context menu
            document_tile.locator('.itemcontent').click(button='right', timeout=10000, force=True)
            
            # Click "Löschen" in context menu using data-qa
            self.page.locator('[data-qa="contextmenu_delete"]').click(timeout=10000)
            
            # Confirm deletion using class (language-independent)
            self.page.locator('button.confirm-overlay-ok').click(timeout=10000)
            
            # Wait for deletion to complete
            self.page.wait_for_timeout(1000)

        self.measure_step("05_Delete document", delete_document)

        # Step 6: Logout
        def logout_logic():
            # Click logout link
            self.page.locator('a[href="#logout"]').click(timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("06_Logout", logout_logic)

if __name__ == "__main__":
    monitor = HiDriveLegacyDocumentTest()
    monitor.execute()
