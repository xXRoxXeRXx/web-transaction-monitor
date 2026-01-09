from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class MagentaCloudDocumentTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "magentacloud_document_test"
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
            
            # Wait for files list with multiple possible selectors
            try:
                self.page.wait_for_selector('.files-list', timeout=30000)
            except Exception as e:
                # Try alternative selector or log current URL for debugging
                logger.error(f"Files list not found. Current URL: {self.page.url}")
                # Try waiting for the file list wrapper
                self.page.wait_for_selector('[data-cy-files-list]', timeout=10000)

        self.measure_step("02_Cookie & Login", login_logic)

       # Step 3: Create and edit document
        def create_document_logic():
            # Click "Neu" button using class (language-independent) - increased timeout
            self.page.locator('button.action-item__menutoggle:has(.plus-icon)').click(timeout=30000)
            
            # Click "Neues Dokument" using data-cy (language-independent)
            self.page.locator('[data-cy-upload-picker-menu-entry="template-new-richdocuments-1"]').click(timeout=30000)
            
            # Click "Erstellen" using data-cy (language-independent)
            self.page.locator('button[data-cy-files-new-node-dialog-submit]').click(timeout=30000)
            
            # Wait for Collabora iframe to load (can be slow in Docker/headless)
            self.page.wait_for_selector('iframe[name^="collaboraframe"]', timeout=60000)
            
            # Get the iframe (use dynamic name detection)
            iframe_locator = self.page.frame_locator('iframe[name^="collaboraframe"]')
            
            # Click in document area and type text
            iframe_locator.locator('.leaflet-layer').click(timeout=30000)
            iframe_locator.locator('#clipboard-area').fill('Dies ist ein Test!', timeout=30000)
            
            # Wait for document canvas to confirm content is rendered
            iframe_locator.locator('#document-canvas').wait_for(state='visible', timeout=30000)

        self.measure_step("03_Create and edit document", create_document_logic)

        # Step 4: Close document
        def close_document_logic():
            # Close document in Collabora using ID (language-independent)
            iframe_locator = self.page.frame_locator('iframe[name^="collaboraframe"]')
            iframe_locator.locator('button#closebutton').click(timeout=30000)
            
            # Wait for return to file list
            self.page.wait_for_selector('.files-list', timeout=30000)

        self.measure_step("04_Close document", close_document_logic)

        # Step 5: Delete document
        def delete_document_logic():
            # Click actions menu for the document (language-independent)
            self.page.locator('tr[data-cy-files-list-row]:has-text("Neues") button.action-item__menutoggle').first.click(timeout=30000)
            
            # Click delete using data-cy (language-independent)
            self.page.locator('[data-cy-files-list-row-action="delete"]').click(timeout=30000)
            
            # Wait for deletion to complete
            self.page.wait_for_timeout(1000)

        self.measure_step("05_Delete document", delete_document_logic)

        # Step 6: Logout
        def logout_logic():
            # Open settings menu and logout using IDs (language-independent)
            self.page.locator('#user-menu button.header-menu__trigger').click(timeout=30000)
            self.page.locator('a#logout').click(timeout=30000)

        self.measure_step("06_Logout", logout_logic)


if __name__ == "__main__":
    monitor = MagentaCloudDocumentTest()
    monitor.execute()