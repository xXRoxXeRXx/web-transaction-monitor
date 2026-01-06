from monitor_base import MonitorBase
import logging
import os

logger = logging.getLogger(__name__)

class StorageIonosFrPictureTest(MonitorBase):
    def __init__(self, usecase_name: str = None) -> None:
        name = usecase_name or "storage.ionos.fr_picture_test"
        super().__init__(usecase_name=name)

    def run(self) -> None:
        # Step 1: Go to start URL
        self.measure_step("01_Go to start URL", lambda: 
            self.page.goto('https://id.ionos.fr/identifier?')
        )

        # Step 2: Cookie & Login
        def login_logic():
            # Robust Cookie Acceptance
            try:
                self.page.click("#selectAll", timeout=2000)
            except Exception:
                pass
            
            # Fill Username
            self.page.fill("input#username", os.getenv('IONOS_USER'), timeout=5000)
            self.page.click("button#button--with-loader", timeout=5000)
            
            # Fill Password
            self.page.fill("input#password", os.getenv('IONOS_PASS'), timeout=10000)
            self.page.click("button#button--with-loader", timeout=5000)
            
            # Fast Wait for post-login element
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

        self.measure_step("03_Browse and open picture", browse_logic)

        # Step 4: Close and Logout
        def logout_logic():
            # Close Preview
            self.page.get_by_role('button', name='Close', exact=True).click(timeout=5000)
            
            # Logout
            self.page.get_by_role('button', name='User Menu').click(timeout=5000)
            self.page.get_by_role('link', name='Abmelden').click(timeout=5000)

        self.measure_step("04_Close and Logout", logout_logic)

if __name__ == "__main__":
    monitor = StorageIonosFrPictureTest()
    monitor.execute()

