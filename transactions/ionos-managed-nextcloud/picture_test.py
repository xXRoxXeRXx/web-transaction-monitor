from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class IonosManagedNextcloudPictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "ionos_managed_nextcloud_picture_test"
        # Read headless setting from environment (default: True for Docker)
        headless = os.getenv('HEADLESS', 'true').lower() in ('true', '1', 'yes')
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        # Get configuration from environment
        login_url = os.getenv('IONOS_MANAGED_NEXTCLOUD_URL', 'https://workspace.kallisto45.de/login')
        username = os.getenv('IONOS_MANAGED_NEXTCLOUD_USER')
        password = os.getenv('IONOS_MANAGED_NEXTCLOUD_PASS')
        
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto(login_url)
        )

        # Step 2: Cookie & Login
        def login_logic():
            # Robust Login (Using the recorded roles with fallback to IDs if possible)
            try:
                self.page.get_by_role('textbox', name='Kontoname oder E-Mail-Adresse').fill(username, timeout=10000)
            except Exception:
                # Fallback to broad locator if role name differs by language
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

        self.measure_step("02_Cookie & Login", login_logic)

        # Step 3: Browse and open picture
        def browse_logic():
            # Click folder 'pictures'
            self.page.locator('tr:nth-child(3) > .files-list__row-name > .files-list__row-icon > .material-design-icon > .material-design-icon__svg > path').click(timeout=10000)
            
            # Click folder 'norway'
            self.page.locator('.material-design-icon.folder-icon > .material-design-icon__svg > path').click(timeout=10000)
            
            # Open picture
            self.page.get_by_role('row', name='Auswahl für die Datei "abhishek-umrao-qsvNYg6iMGk-unsplash.jpg" umschalten').locator('img').click(timeout=10000)
            
            # Wait for image to fully load
            self.page.wait_for_load_state("networkidle", timeout=10000)

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close and Logout
        def logout_logic():
            # Close Preview
            try:
                self.page.get_by_role('button', name='Schließen', exact=True).click(timeout=5000)
            except Exception:
                self.page.locator('button.close, [aria-label="Close"]').click(timeout=5000)
            
            # Logout
            try:
                self.page.get_by_role('button', name='Einstellungen-Menü').click(timeout=5000)
                self.page.get_by_role('link', name='Abmelden').click(timeout=10000)
            except Exception:
                self.page.locator('#settings, .settings-menu').click(timeout=5000)
                self.page.locator('#logout, .logout-link').click(timeout=10000)

        self.measure_step("04_Close and Logout", logout_logic)

if __name__ == "__main__":
    monitor = IonosManagedNextcloudPictureTest()
    monitor.execute()

