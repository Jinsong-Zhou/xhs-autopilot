"""Xiaohongshu cover image generator using Pillow.

Generates 1242x1660px (3:4 portrait) cover images with Chinese text,
optimized for Xiaohongshu's image requirements.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
import textwrap
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- Constants ---

WIDTH = 1242
HEIGHT = 1660
PADDING = 80
TEXT_AREA_WIDTH = WIDTH - PADDING * 2

# Font discovery: macOS stores PingFang in different locations depending on version
FONT_SEARCH_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/PingFang.ttc",
]

# PingFang.ttc font indices (macOS standard ordering)
# We try several indices and pick the first that reports "PingFang SC"
FONT_INDEX_CANDIDATES = list(range(30))

# Color schemes: (background_colors, text_color, accent_color)
COLOR_SCHEMES: dict[str, dict] = {
    "warm": {
        "gradient": [(255, 154, 120), (255, 99, 132)],
        "solid": (255, 240, 235),
        "text": (60, 20, 10),
        "accent": (255, 99, 132),
        "text_on_gradient": (255, 255, 255),
    },
    "cool": {
        "gradient": [(102, 126, 234), (118, 75, 162)],
        "solid": (235, 238, 255),
        "text": (20, 20, 60),
        "accent": (102, 126, 234),
        "text_on_gradient": (255, 255, 255),
    },
    "green": {
        "gradient": [(67, 206, 162), (24, 164, 140)],
        "solid": (235, 250, 245),
        "text": (10, 50, 40),
        "accent": (24, 164, 140),
        "text_on_gradient": (255, 255, 255),
    },
    "neutral": {
        "gradient": [(90, 90, 90), (50, 50, 50)],
        "solid": (245, 245, 245),
        "text": (30, 30, 30),
        "accent": (90, 90, 90),
        "text_on_gradient": (255, 255, 255),
    },
}


def _find_pingfang_font() -> str:
    """Locate PingFang.ttc on macOS, including AssetsV2 path on macOS 15+."""
    for path in FONT_SEARCH_PATHS:
        if Path(path).exists():
            return path

    # macOS 15+: font stored in AssetsV2 directory, find via fc-list
    try:
        result = subprocess.run(
            ["fc-list", "--format=%{file}\n"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.splitlines():
            if "PingFang.ttc" in line:
                return line.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("Warning: PingFang font not found, falling back to system default")
    return ""


def _load_font(font_path: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load PingFang SC font at the given size.

    Scans TTC indices to find PingFang SC Semibold (bold) or Regular.
    """
    target_style = "Semibold" if bold else "Regular"

    if font_path:
        for idx in FONT_INDEX_CANDIDATES:
            try:
                font = ImageFont.truetype(font_path, size, index=idx)
                name = font.getname()
                # name is (family, style) e.g. ("PingFang SC", "Semibold")
                if "SC" in name[0] and target_style in name[1]:
                    return font
            except (OSError, IndexError):
                break

        # Fallback: just use index 0
        try:
            return ImageFont.truetype(font_path, size, index=0)
        except OSError:
            pass

    return ImageFont.load_default()


def _draw_gradient(img: Image.Image, color_top: tuple, color_bottom: tuple) -> None:
    """Draw a vertical linear gradient on the image."""
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels, handling CJK characters."""
    lines: list[str] = []
    current_line = ""

    for char in text:
        test_line = current_line + char
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line

    if current_line:
        lines.append(current_line)

    return lines


def _draw_centered_text(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int,
    color: tuple,
    max_width: int = TEXT_AREA_WIDTH,
) -> int:
    """Draw centered, auto-wrapped text. Returns the Y position after text."""
    lines = _wrap_text(text, font, max_width)
    line_height = font.getbbox("测")[3] - font.getbbox("测")[1]
    spacing = int(line_height * 0.4)

    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += line_height + spacing

    return y


def _draw_left_text(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    color: tuple,
    max_width: int,
) -> int:
    """Draw left-aligned, auto-wrapped text. Returns the Y position after text."""
    lines = _wrap_text(text, font, max_width)
    line_height = font.getbbox("测")[3] - font.getbbox("测")[1]
    spacing = int(line_height * 0.4)

    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += line_height + spacing

    return y


# --- Template renderers ---


def render_gradient(
    title: str,
    subtitle: str | None,
    scheme: dict,
    font_path: str,
) -> Image.Image:
    """Gradient background with centered large title."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    _draw_gradient(img, scheme["gradient"][0], scheme["gradient"][1])
    draw = ImageDraw.Draw(img)

    title_font = _load_font(font_path, 96, bold=True)
    text_color = scheme["text_on_gradient"]

    # Vertically center the title block
    title_lines = _wrap_text(title, title_font, TEXT_AREA_WIDTH)
    line_h = title_font.getbbox("测")[3] - title_font.getbbox("测")[1]
    total_height = len(title_lines) * (line_h + int(line_h * 0.4))

    if subtitle:
        sub_font = _load_font(font_path, 48, bold=False)
        total_height += 80 + (sub_font.getbbox("测")[3] - sub_font.getbbox("测")[1])
    else:
        sub_font = None

    start_y = (HEIGHT - total_height) // 2
    y = _draw_centered_text(draw, title, title_font, start_y, text_color)

    if subtitle and sub_font:
        y += 40
        sub_color = (*text_color[:3],) if len(text_color) == 3 else text_color
        _draw_centered_text(draw, subtitle, sub_font, y, sub_color)

    # Decorative line
    line_y = start_y - 60
    line_width = 200
    draw.line(
        [(WIDTH // 2 - line_width // 2, line_y), (WIDTH // 2 + line_width // 2, line_y)],
        fill=(*text_color[:3],),
        width=3,
    )

    return img


def render_minimal(
    title: str,
    subtitle: str | None,
    scheme: dict,
    font_path: str,
) -> Image.Image:
    """Clean solid background with elegant typography."""
    img = Image.new("RGB", (WIDTH, HEIGHT), scheme["solid"])
    draw = ImageDraw.Draw(img)

    title_font = _load_font(font_path, 88, bold=True)
    text_color = scheme["text"]

    # Title at upper third
    start_y = HEIGHT // 3
    y = _draw_centered_text(draw, title, title_font, start_y, text_color)

    if subtitle:
        sub_font = _load_font(font_path, 44, bold=False)
        y += 50
        _draw_centered_text(draw, subtitle, sub_font, y, scheme["accent"])

    # Accent bar at bottom
    bar_height = 8
    draw.rectangle(
        [(PADDING, HEIGHT - 120), (WIDTH - PADDING, HEIGHT - 120 + bar_height)],
        fill=scheme["accent"],
    )

    return img


def render_list(
    title: str,
    subtitle: str | None,
    scheme: dict,
    font_path: str,
    items: list[str] | None = None,
) -> Image.Image:
    """List/checklist style with title + bullet points."""
    img = Image.new("RGB", (WIDTH, HEIGHT), scheme["solid"])
    draw = ImageDraw.Draw(img)

    # Top accent block
    draw.rectangle([(0, 0), (WIDTH, 200)], fill=scheme["accent"])

    title_font = _load_font(font_path, 72, bold=True)
    item_font = _load_font(font_path, 52, bold=False)
    num_font = _load_font(font_path, 56, bold=True)

    # Title on accent block
    y = 60
    _draw_centered_text(draw, title, title_font, y, scheme["text_on_gradient"])

    # List items
    if not items:
        items = _extract_list_items(subtitle or title)

    y = 280
    item_x = PADDING + 80
    item_max_width = TEXT_AREA_WIDTH - 100

    for i, item in enumerate(items[:6], 1):
        # Number circle
        circle_x = PADDING + 20
        circle_r = 28
        draw.ellipse(
            [
                (circle_x - circle_r, y - 4),
                (circle_x + circle_r, y + circle_r * 2 - 4),
            ],
            fill=scheme["accent"],
        )
        num_bbox = num_font.getbbox(str(i))
        num_w = num_bbox[2] - num_bbox[0]
        draw.text(
            (circle_x - num_w // 2, y - 2),
            str(i),
            font=num_font,
            fill=(255, 255, 255),
        )

        # Item text
        y = _draw_left_text(draw, item, item_font, item_x, y, scheme["text"], item_max_width)
        y += 30

    return img


def render_bold(
    title: str,
    subtitle: str | None,
    scheme: dict,
    font_path: str,
) -> Image.Image:
    """Bold poster style with oversized text."""
    img = Image.new("RGB", (WIDTH, HEIGHT), scheme["solid"])
    draw = ImageDraw.Draw(img)

    # Large background accent shape
    draw.rectangle(
        [(0, HEIGHT // 4), (WIDTH, HEIGHT * 3 // 4)],
        fill=scheme["accent"],
    )

    title_font = _load_font(font_path, 128, bold=True)
    text_on_accent = scheme["text_on_gradient"]

    # Title centered on accent block
    title_lines = _wrap_text(title, title_font, TEXT_AREA_WIDTH - 40)
    line_h = title_font.getbbox("测")[3] - title_font.getbbox("测")[1]
    total_h = len(title_lines) * (line_h + int(line_h * 0.4))
    start_y = (HEIGHT - total_h) // 2

    _draw_centered_text(draw, title, title_font, start_y, text_on_accent, TEXT_AREA_WIDTH - 40)

    if subtitle:
        sub_font = _load_font(font_path, 48, bold=False)
        sub_y = HEIGHT * 3 // 4 + 60
        _draw_centered_text(draw, subtitle, sub_font, sub_y, scheme["text"])

    return img


def _extract_list_items(text: str) -> list[str]:
    """Extract list items from subtitle text (split by | or newline or comma)."""
    for sep in ["|", "\n", "，", ","]:
        if sep in text:
            return [item.strip() for item in text.split(sep) if item.strip()]
    # If no separator found, wrap as single item
    return [text]


TEMPLATES = {
    "gradient": render_gradient,
    "minimal": render_minimal,
    "list": render_list,
    "bold": render_bold,
}


def generate_cover(
    title: str,
    subtitle: str | None = None,
    template: str = "gradient",
    color: str = "warm",
    output: str | None = None,
    items: list[str] | None = None,
) -> str:
    """Generate a cover image and return the output path."""
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Choose from: {', '.join(TEMPLATES)}")
    if color not in COLOR_SCHEMES:
        raise ValueError(f"Unknown color: {color}. Choose from: {', '.join(COLOR_SCHEMES)}")

    scheme = COLOR_SCHEMES[color]
    font_path = _find_pingfang_font()

    if template == "list":
        img = render_list(title, subtitle, scheme, font_path, items=items)
    else:
        renderer = TEMPLATES[template]
        img = renderer(title, subtitle, scheme, font_path)

    if not output:
        timestamp = datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "workspace" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        output = str(output_dir / "cover.png")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG", optimize=True)

    # Verify file size (Xiaohongshu limit: 5MB)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    if size_mb > 5:
        # Re-save as JPEG if PNG too large
        jpeg_path = output_path.with_suffix(".jpg")
        img.save(str(jpeg_path), "JPEG", quality=90, optimize=True)
        output_path.unlink()
        output = str(jpeg_path)
        print(f"PNG exceeded 5MB, saved as JPEG: {output}")

    print(f"Cover generated: {output}")
    print(f"  Size: {WIDTH}x{HEIGHT}px")
    print(f"  Template: {template}")
    print(f"  Color: {color}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Xiaohongshu cover images")
    parser.add_argument("--title", required=True, help="Main title text")
    parser.add_argument("--subtitle", default=None, help="Subtitle or list items (separated by |)")
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default="gradient",
        help="Template style (default: gradient)",
    )
    parser.add_argument(
        "--color",
        choices=list(COLOR_SCHEMES.keys()),
        default="warm",
        help="Color scheme (default: warm)",
    )
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument(
        "--items",
        nargs="*",
        default=None,
        help="List items for 'list' template (space-separated)",
    )

    args = parser.parse_args()
    generate_cover(
        title=args.title,
        subtitle=args.subtitle,
        template=args.template,
        color=args.color,
        output=args.output,
        items=args.items,
    )


if __name__ == "__main__":
    main()
