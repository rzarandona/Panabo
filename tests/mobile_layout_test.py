from __future__ import annotations

import math
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
STYLES = (ROOT / "styles.css").read_text(encoding="utf-8")
SLIDES = (ROOT / "slides.html").read_text(encoding="utf-8")
APP = (ROOT / "app.js").read_text(encoding="utf-8")
body = APP[APP.index(" const slides="):].rsplit("})();", 1)[0]
HTML = INDEX.replace('<link rel="stylesheet" href="styles.css">', f"<style>{STYLES}</style>")
HTML = HTML.replace('<script src="app.js" defer></script>', "")
HTML = HTML.replace('<div class="loading">Loading presentation…</div>', SLIDES)
HTML = HTML.replace("</body>", f"<script>(()=>{{{body}}})();</script></body>")
VIEWPORTS = [(320, 568), (360, 800), (390, 844), (430, 932), (768, 1024)]


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


def box(page, selector):
    rect = page.locator(selector).bounding_box()
    assert_true(rect is not None, f"Missing {selector}")
    return rect


def dispatch_touch(page, event_type, x, y):
    page.locator("#deck").evaluate(
        """(el, point) => {
          const event = new Event(point.type, {bubbles:true,cancelable:true});
          const touch = {clientX:point.x,clientY:point.y};
          Object.defineProperty(event,'touches',{value:point.type==='touchstart'?[touch]:[]});
          Object.defineProperty(event,'changedTouches',{value:[touch]});
          el.dispatchEvent(event);
        }""",
        {"type": event_type, "x": x, "y": y},
    )


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path="/usr/bin/chromium",
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    for width, height in VIEWPORTS:
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(HTML, wait_until="load")
        page.wait_for_selector(".slide.active")
        assert_true(page.locator(".slide").count() == 15, f"{width}x{height}: slide count")
        assert_true(page.evaluate("document.documentElement.scrollWidth") <= width, f"{width}x{height}: horizontal overflow")
        assert_true(page.locator(".slide.active").evaluate("el=>getComputedStyle(el).display") == "block", f"{width}x{height}: mobile flow")
        controls = box(page, ".controls")
        assert_true(controls["y"] + controls["height"] <= height + 1, f"{width}x{height}: controls outside viewport")
        for selector in ("#prev", "#next", "#print"):
            rect = box(page, selector)
            assert_true(rect["width"] >= 44 and rect["height"] >= 44, f"{width}x{height}: touch target {selector}")
        tags = box(page, ".slide.active .tags")
        disclaimer = box(page, ".slide.active .disclaimer")
        panel = box(page, ".slide.active .panel")
        assert_true(tags["y"] + tags["height"] <= disclaimer["y"], f"{width}x{height}: tags overlap disclaimer")
        assert_true(disclaimer["y"] + disclaimer["height"] <= panel["y"], f"{width}x{height}: disclaimer overlaps panel")
        hero = box(page, ".mini-journey")
        slide = box(page, ".slide.active")
        assert_true(hero["x"] + hero["width"] <= slide["x"] + slide["width"] + 1, f"{width}x{height}: hero overflow")
        if (width, height) == (390, 844):
            dispatch_touch(page, "touchstart", 310, 260)
            dispatch_touch(page, "touchend", 120, 270)
            assert_true(page.locator(".slide.active .num").inner_text().strip() == "02", "left swipe")
            page.keyboard.press("Home")
            dispatch_touch(page, "touchstart", 90, 260)
            dispatch_touch(page, "touchend", 290, 270)
            assert_true(page.locator(".slide.active .num").inner_text().strip() == "01", "first boundary")
            page.keyboard.press("End")
            dispatch_touch(page, "touchstart", 310, 260)
            dispatch_touch(page, "touchend", 110, 270)
            assert_true(page.locator(".slide.active .num").inner_text().strip() == "15", "last boundary")
            page.keyboard.press("Home")
        for expected in range(2, 16):
            page.locator("#next").click()
            assert_true(page.locator(".slide.active .num").inner_text().strip() == f"{expected:02d}", f"{width}x{height}: slide {expected}")
        page.locator("#next").click()
        assert_true(page.locator(".slide.active .num").inner_text().strip() == "01", f"{width}x{height}: button loop")
        print(f"PASS mobile {width}x{height}")
        page.close()

    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.set_content(HTML, wait_until="load")
    page.wait_for_selector(".slide.active")
    deck = box(page, ".deck")
    assert_true(math.isclose(deck["width"] / deck["height"], 16 / 9, rel_tol=0.015), "desktop ratio")
    assert_true(page.locator(".slide.active").evaluate("el=>getComputedStyle(el).display") == "grid", "desktop grid")
    print("PASS desktop 1440x900")
    browser.close()
