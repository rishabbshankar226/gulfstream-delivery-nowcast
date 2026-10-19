"""Full-page screenshots of the served dashboard with Playwright: python tools/shoot.py <url> <out.png> <width> <light|dark> [height]"""
import sys

from playwright.sync_api import sync_playwright

url, out, width, scheme = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
height = int(sys.argv[5]) if len(sys.argv) > 5 else 0
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": width, "height": height or 900}, device_scale_factor=1)
    page.emulate_media(color_scheme=scheme, reduced_motion="reduce")
    page.goto(url)
    page.wait_for_selector("html.ready")
    page.wait_for_timeout(400)
    page.screenshot(path=out, full_page=not height)
    b.close()
print(out)
