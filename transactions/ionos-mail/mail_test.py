import os

from monitor_base import MonitorBase


class IonosMailTest(MonitorBase):
    def __init__(self, usecase_name: str | None = None) -> None:
        name = usecase_name or "ionos_mail_mail_test"
        headless = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
        super().__init__(usecase_name=name, headless=headless)

    def run(self) -> None:
        login_url = os.getenv("IONOS_MAIL_URL", "https://id.ionos.de/")
        username = os.getenv("IONOS_MAIL_USER")
        password = os.getenv("IONOS_MAIL_PASS")

        self.measure_step("01_Go to login", lambda: self.page.goto(login_url))

        def login():
            cookie_accept = self.page.get_by_test_id("confirm-all")
            if cookie_accept.is_visible(timeout=2_000):
                cookie_accept.click(timeout=10_000)

            self.page.locator("#username").fill(username, timeout=30_000)
            self.page.locator('button[type="submit"]').click(timeout=30_000)

            password_field = self.page.locator('input[type="password"]:visible')
            password_field.wait_for(state="visible", timeout=30_000)
            password_field.fill(password)
            self.page.locator('button[type="submit"]:visible').click(timeout=30_000)

        self.measure_step("02_Login", login)

        def confirm_mail_opened():
            self.page.get_by_role("heading", name="Posteingang").wait_for(
                state="visible", timeout=30_000
            )

        self.measure_step("03_Open Mail", confirm_mail_opened)

        def open_first_email():
            first_email = self.page.locator('li[role="option"].list-item').first
            first_email.click(timeout=30_000)
            self.page.locator(
                'li[role="option"].list-item[aria-selected="true"]'
            ).wait_for(state="visible", timeout=30_000)

        self.measure_step("04_Open first email", open_first_email)

        def logout():
            self.page.locator('button[aria-label="Abmelden"]').click(timeout=30_000)
            self.page.wait_for_load_state("networkidle", timeout=30_000)
            self.page.locator("#username").wait_for(state="visible", timeout=30_000)

        self.measure_step("05_Logout", logout)


if __name__ == "__main__":
    IonosMailTest().execute()