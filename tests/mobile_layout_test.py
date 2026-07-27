from __future__ import annotations

import math
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SCREENSHOTS = ROOT / "tests" / "screenshots"
MOBILE_VIEWPORTS = [(320, 568), (360, 800), (390, 844), (430, 932), (768, 1024)]


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def box(page, selector: str) -> dict:
    rect = page.locator(selector).bounding_box()
    assert_true(rect is not None, f"Missing visible box for {selector}")
    return rect


def dispatch_touch(page, event_type: str, x: int, y: int) -> None:
    page.locator("#deck").evaluate(
        """(el, point) => {
            const event = new Event(point.type, { bubbles: true, cancelable: true });
            const touch = { clientX: point.x, clientY: point.y };
            Object.defineProperty(event, 'touches', { value: point.type === 'touchstart' ? [touch] : [] });
            Object.defineProperty(event, 'changedTouches', { value: [touch] });
            el.dispatchEvent(event);
        }""",
        {"type": event_type, "x": x, "y": y},
    )


def check_mobile(page, width: int, height: int) -> None:
    page.set_viewport_size({"width": width, "height": height})
    page.set_content(HTML, wait_until="load")
    page.wait_for_selector(".slide.active")

    slide_count = page.locator(".slide").count()
    assert_true(slide_count == 15, f"{width}x{height}: expected 15 slides, found {slide_count}")

    root_width = page.evaluate("document.documentElement.scrollWidth")
    assert_true(root_width <= width, f"{width}x{height}: page overflows horizontally ({root_width}px)")

    slide_display = page.locator(".slide.active").evaluate("el => getComputedStyle(el).display")
    assert_true(slide_display == "block", f"{width}x{height}: mobile slide must use natural block flow, got {slide_display}")

    controls = box(page, ".controls")
    assert_true(controls["y"] + controls["height"] <= height + 1, f"{width}x{height}: controls extend below viewport")
    assert_true(controls["height"] >= 64, f"{width}x{height}: controls are too short for touch use")

    for selector in ("#prev", "#next", "#print"):
        rect = box(page, selector)
        assert_true(rect["width"] >= 44 and rect["height"] >= 44, f"{width}x{height}: {selector} is below 44px touch target")

    hero = page.locator(".hero-flow")
    assert_true(hero.count() == 1, f"{width}x{height}: mobile-safe hero flow is missing")
    hero_direction = hero.evaluate("el => getComputedStyle(el).flexDirection")
    assert_true(hero_direction == "column", f"{width}x{height}: hero flow must stack vertically, got {hero_direction}")

    head = box(page, ".slide.active .head")
    content = box(page, ".slide.active .content")
    assert_true(content["y"] >= head["y"] + head["height"] - 1, f"{width}x{height}: slide content overlaps the heading")

    slide = page.locator(".slide.active")
    slide_right = slide.evaluate("el => el.getBoundingClientRect().right")
    hero_right = hero.evaluate("el => el.getBoundingClientRect().right")
    assert_true(hero_right <= slide_right + 1, f"{width}x{height}: hero diagram exceeds slide width")

    if (width, height) == (390, 844):
        # Horizontal swipes navigate, vertical gestures do not, and swipe boundaries do not wrap.
        dispatch_touch(page, "touchstart", 310, 260)
        dispatch_touch(page, "touchend", 120, 270)
        assert_true(page.locator(".slide.active .num").inner_text().strip() == "02", "left swipe did not advance")
        dispatch_touch(page, "touchstart", 210, 550)
        dispatch_touch(page, "touchend", 195, 250)
        assert_true(page.locator(".slide.active .num").inner_text().strip() == "02", "vertical gesture changed slides")
        page.keyboard.press("Home")
        dispatch_touch(page, "touchstart", 90, 260)
        dispatch_touch(page, "touchend", 290, 270)
        assert_true(page.locator(".slide.active .num").inner_text().strip() == "01", "right swipe wrapped before slide 1")
        page.keyboard.press("End")
        dispatch_touch(page, "touchstart", 310, 260)
        dispatch_touch(page, "touchend", 110, 270)
        assert_true(page.locator(".slide.active .num").inner_text().strip() == "15", "left swipe wrapped after slide 15")
        page.keyboard.press("Home")

        active = page.locator(".slide.active")
        active.evaluate("el => el.scrollTop = 500")
        page.locator("#next").click()
        assert_true(page.locator(".slide.active").evaluate("el => el.scrollTop") == 0, "new slide did not reset to the top")
        page.keyboard.press("Home")

    # Every slide must be reachable with the visible Next button. The final click loops to slide one.
    for expected in range(1, 15):
        page.locator("#next").click()
        current = page.locator(".slide.active .num").inner_text().strip()
        assert_true(current == f"{expected + 1:02d}", f"{width}x{height}: expected slide {expected + 1:02d}, got {current}")
        page_width = page.evaluate("document.documentElement.scrollWidth")
        assert_true(page_width <= width, f"{width}x{height}: slide {expected + 1} introduces horizontal overflow")

    page.locator("#next").click()
    assert_true(page.locator(".slide.active .num").inner_text().strip() == "01", f"{width}x{height}: final Next control did not return to slide 1")

    if (width, height) == (390, 844):
        SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        page.wait_for_timeout(350)
        page.screenshot(path=str(SCREENSHOTS / "mobile-slide-01.png"), full_page=False)
        for _ in range(7):
            page.locator("#next").click()
        page.wait_for_timeout(350)
        page.screenshot(path=str(SCREENSHOTS / "mobile-slide-08.png"), full_page=False)


def check_desktop(page) -> None:
    width, height = 1440, 900
    page.set_viewport_size({"width": width, "height": height})
    page.set_content(HTML, wait_until="load")
    page.wait_for_selector(".slide.active")

    deck = box(page, ".deck")
    ratio = deck["width"] / deck["height"]
    assert_true(math.isclose(ratio, 16 / 9, rel_tol=0.015), f"desktop: deck ratio changed to {ratio:.3f}")

    slide_display = page.locator(".slide.active").evaluate("el => getComputedStyle(el).display")
    rows = page.locator(".slide.active").evaluate("el => getComputedStyle(el).gridTemplateRows")
    assert_true(slide_display == "grid", f"desktop: slide display changed to {slide_display}")
    assert_true(rows != "none" and len(rows.split()) >= 3, f"desktop: three-row presentation grid is missing ({rows})")

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    page.wait_for_timeout(350)
    page.screenshot(path=str(SCREENSHOTS / "desktop-slide-01.png"), full_page=False)


def main() -> int:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            for width, height in MOBILE_VIEWPORTS:
                page = browser.new_page()
                check_mobile(page, width, height)
                page.close()
                print(f"PASS mobile {width}x{height}")
            page = browser.new_page()
            check_desktop(page)
            page.close()
            print("PASS desktop 1440x900")
            browser.close()
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
