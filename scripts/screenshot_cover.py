"""Screenshot an HTML cover template to PNG using Playwright."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def screenshot_html(html_path: str, output_path: str, width: int = 1242, height: int = 1660) -> str:
    html_file = Path(html_path).resolve()
    if not html_file.exists():
        print(f"Error: {html_file} not found")
        sys.exit(1)

    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto(f"file://{html_file}")
        page.wait_for_timeout(500)
        page.screenshot(path=str(output), type="png")
        browser.close()

    print(f"Screenshot saved: {output}")
    print(f"  Size: {width}x{height}px")
    return str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Screenshot HTML to PNG")
    parser.add_argument("--html", required=True, help="Path to HTML file")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--width", type=int, default=1242)
    parser.add_argument("--height", type=int, default=1660)
    args = parser.parse_args()
    screenshot_html(args.html, args.output, args.width, args.height)


if __name__ == "__main__":
    main()
