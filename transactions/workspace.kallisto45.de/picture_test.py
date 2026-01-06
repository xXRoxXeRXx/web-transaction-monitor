from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class WorkspaceKallisto45DePictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "workspace.kallisto45.de_picture_test"
        super().__init__(usecase_name=name)

    def run(self) -> None:
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto('https://workspace.kallisto45.de/login')
        )

        # Step 2: Cookie & Login
        def login_logic():
            # Robust Login (Using the recorded roles with fallback to IDs if possible)
            username = os.getenv('KALLISTO_USER')
            password = os.getenv('KALLISTO_PASS')
            
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
            # Click folder (tr:nth-child(2))
            self.page.locator('tr:nth-child(2) > .files-list__row-name > .files-list__row-icon > .material-design-icon > .material-design-icon__svg > path').click(timeout=10000)
            
            # Click subfolder
            self.page.locator('.material-design-icon.folder-icon > .material-design-icon__svg > path').click(timeout=10000)
            
            # Open specific picture preview (tr:nth-child(3))
            self.page.locator('tr:nth-child(3) > .files-list__row-name > .files-list__row-icon > .files-list__row-icon-preview-container > .files-list__row-icon-preview').click(timeout=10000)

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
    monitor = WorkspaceKallisto45DePictureTest()
    monitor.execute()

