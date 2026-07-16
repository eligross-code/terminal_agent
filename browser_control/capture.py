# browser_control/capture.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional

from playwright.sync_api import sync_playwright, Page


@dataclass
class ElementRef:
    ref: str
    role: str
    name: str
    tag: str
    selector: str
    bounds: list[float]
    value: Optional[str] = None
    disabled: bool = False
    checked: Optional[bool] = None


JS_CAPTURE_ELEMENTS = """
() => {
  const AGENT_ATTR = "data-local-agent-ref";

  function isVisible(el) {
    const r = el.getBoundingClientRect();
    const s = window.getComputedStyle(el);

    if (!s) return false;
    if (s.display === "none") return false;
    if (s.visibility === "hidden") return false;
    if (Number(s.opacity) === 0) return false;
    if (r.width <= 0 || r.height <= 0) return false;

    if (r.bottom < 0 || r.right < 0) return false;
    if (r.top > window.innerHeight || r.left > window.innerWidth) return false;

    return true;
  }

  function roleFor(el) {
    const explicit = el.getAttribute("role");
    if (explicit) return explicit;

    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute("type") || "").toLowerCase();

    if (tag === "a") return "link";
    if (tag === "button") return "button";
    if (tag === "textarea") return "textbox";
    if (tag === "select") return "dropdown";

    if (tag === "input") {
      if (type === "checkbox") return "checkbox";
      if (type === "radio") return "radio";
      if (type === "submit" || type === "button") return "button";
      if (type === "search") return "searchbox";
      return "textbox";
    }

    if (el.isContentEditable) return "textbox";

    return tag;
  }

  function nameFor(el) {
    const aria = el.getAttribute("aria-label");
    if (aria) return aria.trim();

    const labelledBy = el.getAttribute("aria-labelledby");
    if (labelledBy) {
      const labelEl = document.getElementById(labelledBy);
      if (labelEl && labelEl.innerText) return labelEl.innerText.trim();
    }

    if (el.labels && el.labels.length) {
      return Array.from(el.labels).map(l => l.innerText.trim()).join(" ").trim();
    }

    const placeholder = el.getAttribute("placeholder");
    if (placeholder) return placeholder.trim();

    const title = el.getAttribute("title");
    if (title) return title.trim();

    const alt = el.getAttribute("alt");
    if (alt) return alt.trim();

    const imgAlt = el.querySelector?.("img[alt]")?.getAttribute("alt");
    if (imgAlt) return imgAlt.trim();

    const text = el.innerText || el.textContent || "";
    if (text.trim()) return text.trim().replace(/\\s+/g, " ").slice(0, 120);

    if ("value" in el && el.value) return String(el.value).slice(0, 120);

    const href = el.getAttribute("href");
    if (href) return href.slice(0, 120);

    return "";
  }

  document.querySelectorAll("[" + AGENT_ATTR + "]").forEach(el => {
    el.removeAttribute(AGENT_ATTR);
  });

  const candidates = Array.from(document.querySelectorAll([
    "a[href]",
    "button",
    "input:not([type='hidden'])",
    "textarea",
    "select",
    "summary",
    "[role]",
    "[onclick]",
    "[contenteditable='true']",
    "[tabindex]:not([tabindex='-1'])"
  ].join(",")));

  const out = [];

  for (const el of candidates) {
    if (!isVisible(el)) continue;

    const ref = "e" + String(out.length + 1);
    el.setAttribute(AGENT_ATTR, ref);

    const r = el.getBoundingClientRect();

    out.push({
      ref,
      role: roleFor(el),
      name: nameFor(el),
      tag: el.tagName.toLowerCase(),
      selector: "[" + AGENT_ATTR + "='" + ref + "']",
      bounds: [r.x, r.y, r.width, r.height],
      value: "value" in el ? String(el.value).slice(0, 200) : null,
      disabled: !!el.disabled || el.getAttribute("aria-disabled") === "true",
      checked:
        typeof el.checked === "boolean"
          ? !!el.checked
          : el.getAttribute("aria-checked") === "true"
            ? true
            : el.getAttribute("aria-checked") === "false"
              ? false
              : null
    });
  }

  return out;
}
"""


class Observations:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page: Optional[Page] = None
        self.refs: Dict[str, ElementRef] = {}

    def start(self) -> "Observations":
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=self.headless)
        self.page = self.browser.new_page()
        return self

    def close(self) -> None:
        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self.page = None
        self.refs = {}

    def observe_browser_and_tabs(self) -> dict:
        page = self._page()

        return {
            "active_tab_id": "main",
            "tabs": [
                {
                    "tab_id": "main",
                    "url": page.url,
                    "title": page.title(),
                }
            ],
        }

    def goto(self, url: str) -> dict:
        page = self._page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        return self.return_page_state()

    def return_page_state(self, tab_id: str = "main") -> dict:
        page = self._page()

        raw_elements = page.evaluate(JS_CAPTURE_ELEMENTS)

        elements = [
            ElementRef(
                ref=item["ref"],
                role=item["role"],
                name=item.get("name") or "",
                tag=item["tag"],
                selector=item["selector"],
                bounds=item["bounds"],
                value=item.get("value"),
                disabled=item.get("disabled", False),
                checked=item.get("checked"),
            )
            for item in raw_elements
        ]

        self.refs = {el.ref: el for el in elements}

        return {
            "tab_id": "main",
            "url": page.url,
            "title": page.title(),
            "elements": [asdict(el) for el in elements],
        }

    def get_ref(self, ref: str) -> ElementRef:
        if ref not in self.refs:
            raise KeyError(f"Unknown ref: {ref}. Call browser_observe first.")
        return self.refs[ref]

    def screenshot(self, path: str = "browser.png") -> str:
        page = self._page()
        page.screenshot(path=path, full_page=False)
        return path

    def _page(self) -> Page:
        if self.page is None:
            raise RuntimeError("Browser is not started")
        return self.page