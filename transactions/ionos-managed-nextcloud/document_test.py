from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class IonosManagedNextcloudDocumentTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "ionos_managed_nextcloud_document_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('IONOS_MANAGED_NEXTCLOUD_URL', 'https://managed-nextcloud.example.com/login')
        username = os.getenv('IONOS_MANAGED_NEXTCLOUD_USER')
        password = os.getenv('IONOS_MANAGED_NEXTCLOUD_PASS')
        
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Login
        def login_logic():
            # Robust Login with fallback locators
            try:
                self.page.get_by_role('textbox', name='Kontoname oder E-Mail-Adresse').fill(username, timeout=10000)
            except Exception:
                self.page.locator('input[name="user"], #user').fill(username, timeout=5000)
                
            try:
                self.page.get_by_role('textbox', name='Passwort').fill(password, timeout=10000)
            except Exception:
                self.page.locator('input[name="password"], #password').fill(password, timeout=5000)
                
            try:
                self.page.get_by_role('button', name='Anmelden').click(timeout=10000)
            except Exception:
                self.page.locator('button[type="submit"], #submit').click(timeout=5000)
            
            # Wait for dashboard
            self.page.wait_for_selector(".files-list", timeout=30000)

        self.measure_step("02_Login", login_logic)

        # Step 3: Create and edit document
        def create_document_logic():
            # Click "Neu" button
            try:
                self.page.get_by_role('button', name='Neu').click(timeout=10000)
            except Exception:
                self.page.locator('button:has-text("Neu"), .button-vue:has-text("New")').click(timeout=5000)
            
            # Click "Neues Dokument"
            try:
                self.page.get_by_role('menuitem', name='Neues Dokument').click(timeout=10000)
            except Exception:
                self.page.locator('[role="menuitem"]:has-text("Dokument"), [role="menuitem"]:has-text("Document")').click(timeout=5000)
            
            # Click "Erstellen"
            try:
                self.page.get_by_role('button', name='Erstellen').click(timeout=10000)
            except Exception:
                self.page.locator('button:has-text("Erstellen"), button:has-text("Create")').click(timeout=5000)
            
            # Wait for Collabora iframe to load
            self.page.wait_for_selector('iframe[name^="collaboraframe"]', timeout=30000)
            
            # Get the iframe (use dynamic name detection)
            iframe_locator = self.page.frame_locator('iframe[name^="collaboraframe"]')
            
            # Click in document area and type text
            iframe_locator.locator('.leaflet-layer').click(timeout=10000)
            iframe_locator.locator('#clipboard-area').fill('Dies ist ein Test!', timeout=10000)
            
            # Wait a moment for content to be saved
            self.page.wait_for_timeout(2000)

        self.measure_step("03_Create and edit document", create_document_logic)

        # Step 4: Close document
        def close_document_logic():
            # Close document in Collabora using the specific close button div
            iframe_locator = self.page.frame_locator('iframe[name^="collaboraframe"]')
            try:
                # Click on the close button div (it's a div, not a button)
                iframe_locator.locator('#closebuttonwrapper').click(timeout=10000)
            except Exception:
                # Fallback to closebutton div
                iframe_locator.locator('#closebutton').click(timeout=5000)
            
            # Wait for return to file list
            self.page.wait_for_selector('.files-list', timeout=10000)

        self.measure_step("04_Close document", close_document_logic)

        # Step 5: Delete document
        def delete_document_logic():
            # Click actions menu for the new document
            try:
                self.page.get_by_role('row', name='Auswahl für die Datei "Neues').get_by_label('Aktionen').click(timeout=10000)
            except Exception:
                # Fallback: find first file with "Neues" or "New" in name
                self.page.locator('[data-cy-files-list-row]:has-text("Neues"), [data-cy-files-list-row]:has-text("New")').locator('button[aria-label*="Aktionen"], button[aria-label*="Actions"]').first.click(timeout=5000)
            
            # Click delete
            try:
                self.page.get_by_role('menuitem', name='Datei löschen').click(timeout=10000)
            except Exception:
                self.page.locator('[role="menuitem"]:has-text("löschen"), [role="menuitem"]:has-text("Delete")').click(timeout=5000)
            
            # Wait for deletion to complete
            self.page.wait_for_timeout(1000)

        self.measure_step("05_Delete document", delete_document_logic)

        # Step 6: Logout
        def logout_logic():
            try:
                self.page.get_by_role('button', name='Einstellungen-Menü').click(timeout=5000)
                self.page.get_by_role('link', name='Abmelden').click(timeout=10000)
            except Exception:
                self.page.locator('#settings, .settings-menu').click(timeout=5000)
                self.page.locator('#logout, .logout-link').click(timeout=10000)

        self.measure_step("06_Logout", logout_logic)


if __name__ == "__main__":
    monitor = IonosManagedNextcloudDocumentTest()
    monitor.execute()
