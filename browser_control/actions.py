# browser_control/actions.py

from __future__ import annotations

from browser_control.capture import Observations


class Actions:
    def __init__(self, observations: Observations):
        self.obs = observations

    @property
    def page(self):
        return self.obs._page()

    def observe(self) -> dict:
        return self.obs.return_page_state()

    def goto(self, url: str) -> dict:
        return self.obs.goto(url)

    def click(self, ref: str) -> dict:
        el = self.obs.get_ref(ref)

        if el.disabled:
            raise RuntimeError(f"Element {ref} is disabled")

        locator = self.page.locator(el.selector).first
        locator.scroll_into_view_if_needed()
        locator.click(timeout=5000)

        self.page.wait_for_timeout(500)
        return self.obs.return_page_state()

    def input_text(self, ref: str, text: str, clear_first: bool = True) -> dict:
        el = self.obs.get_ref(ref)

        if el.disabled:
            raise RuntimeError(f"Element {ref} is disabled")

        locator = self.page.locator(el.selector).first
        locator.scroll_into_view_if_needed()
        locator.click(timeout=5000)

        # Try proper fill first.
        try:
            locator.fill(text, timeout=2000)
        except Exception:
            # Fallback: type into whatever got focused.
            if clear_first:
                self.page.keyboard.press("Meta+A")
                self.page.keyboard.press("Backspace")
            self.page.keyboard.type(text, delay=30)

        self.page.wait_for_timeout(300)
        return self.obs.return_page_state()

    def type_text(self, text: str) -> dict:
        self.page.keyboard.type(text, delay=30)
        self.page.wait_for_timeout(300)
        return self.obs.return_page_state()

    def press(self, key: str) -> dict:
        self.page.keyboard.press(key)
        self.page.wait_for_timeout(500)
        return self.obs.return_page_state()

    def scroll(self, amount: int = 600) -> dict:
        self.page.mouse.wheel(0, amount)
        self.page.wait_for_timeout(300)
        return self.obs.return_page_state()

    def screenshot(self, path: str = "browser.png") -> dict:
        return {
            "path": self.obs.screenshot(path)
        }