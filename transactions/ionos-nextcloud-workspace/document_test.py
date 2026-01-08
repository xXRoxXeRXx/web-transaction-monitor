from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class IonosNextcloudWorkspaceDocumentTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "ionos_nextcloud_workspace_document_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('IONOS_NEXTCLOUD_WORKSPACE_URL', 'https://workspace.kallisto45.de/login')
        username = os.getenv('IONOS_NEXTCLOUD_WORKSPACE_USER')
        password = os.getenv('IONOS_NEXTCLOUD_WORKSPACE_PASS')
        
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Login
        def login_logic():
            # Login using data attributes (language-independent)
            self.page.locator('input[data-login-form-input-user]').fill(username, timeout=10000)
            self.page.locator('input[data-login-form-input-password]').fill(password, timeout=10000)
            self.page.locator('button[data-login-form-submit]').click(timeout=10000)
            
            # Wait for dashboard to load
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Login", login_logic)

        # Step 3: Create and edit document
        def create_document_logic():
            # Click "Neu" button using class (language-independent)
            self.page.locator('button.action-item__menutoggle:has(.plus-icon)').click(timeout=10000)
            
            # Click "Neues Dokument" using data-cy (language-independent)
            self.page.locator('[data-cy-upload-picker-menu-entry="template-new-richdocuments-1"]').click(timeout=10000)
            
            # Click "Erstellen" using data-cy (language-independent)
            self.page.locator('button[data-cy-files-new-node-dialog-submit]').click(timeout=10000)
            
            # Wait for Collabora iframe to load (can be slow in Docker/headless)
            self.page.wait_for_selector('iframe[name^="collaboraframe"]', timeout=60000)
            
            # Get the iframe (use dynamic name detection)
            iframe_locator = self.page.frame_locator('iframe[name^="collaboraframe"]')
            
            # Click in document area and type text
            iframe_locator.locator('.leaflet-layer').click(timeout=10000)
            iframe_locator.locator('#clipboard-area').fill('Dies ist ein Test!', timeout=10000)
            
            # Wait for document canvas to confirm content is rendered
            iframe_locator.locator('#document-canvas').wait_for(state='visible', timeout=10000)

        self.measure_step("03_Create and edit document", create_document_logic)

        # Step 4: Close document
        def close_document_logic():
            # Close document in Collabora using ID (language-independent)
            iframe_locator = self.page.frame_locator('iframe[name^="collaboraframe"]')
            iframe_locator.locator('button#closebutton').click(timeout=10000)
            
            # Wait for return to file list
            self.page.wait_for_selector('.files-list', timeout=10000)

        self.measure_step("04_Close document", close_document_logic)

        # Step 5: Delete document
        def delete_document_logic():
            # Click actions menu for the document (language-independent)
            self.page.locator('tr[data-cy-files-list-row]:has-text("Neues") button.action-item__menutoggle').first.click(timeout=10000)
            
            # Click delete using data-cy (language-independent)
            self.page.locator('[data-cy-files-list-row-action="delete"]').click(timeout=10000)
            
            # Wait for deletion to complete
            self.page.wait_for_timeout(1000)

        self.measure_step("05_Delete document", delete_document_logic)

        # Step 6: Logout
        def logout_logic():
            # Open settings menu and logout using IDs (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=5000)
            self.page.locator('a#logout').click(timeout=10000)

        self.measure_step("06_Logout", logout_logic)


if __name__ == "__main__":
    monitor = IonosNextcloudWorkspaceDocumentTest()
    monitor.execute()
