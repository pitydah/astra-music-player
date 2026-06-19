#!/usr/bin/python3
"""Remove black background rectangles/paths from sidebar SVGs."""

from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

SRC_DIR = Path("/home/cristian/Descargas/sidebar outpaint")
BACKUP_DIR = SRC_DIR / "backup"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def local_name(tag: str) -> str:
    return tag.split("}")[-1].lower()


def parse_float(value, default=0.0):
    try:
        return float(str(value).replace("px", "").strip())
    except Exception:
        return default


def parse_viewbox(root):
    viewbox = root.attrib.get("viewBox", "")
    if viewbox:
        parts = [parse_float(x) for x in viewbox.replace(",", " ").split()]
        if len(parts) == 4:
            return parts
    w = parse_float(root.attrib.get("width", 24), 24)
    h = parse_float(root.attrib.get("height", 24), 24)
    return [0.0, 0.0, w, h]


def style_value(style: str, key: str) -> str:
    if not style:
        return ""
    m = re.search(rf"{re.escape(key)}\s*:\s*([^;]+)", style, re.I)
    return m.group(1).strip() if m else ""


def get_attr_or_style(elem, key: str) -> str:
    value = elem.attrib.get(key, "")
    if value:
        return value.strip()
    return style_value(elem.attrib.get("style", ""), key)


def is_dark_color(value: str) -> bool:
    if not value:
        return False
    v = value.strip().lower().replace(" ", "")
    if v in {"black", "#000", "#000000", "rgb(0,0,0)", "rgba(0,0,0,1)"}:
        return True
    m = re.match(r"#([0-9a-f]{3})$", v)
    if m:
        h = m.group(1)
        r, g, b = int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16)
        return r < 25 and g < 25 and b < 25
    m = re.match(r"#([0-9a-f]{6})$", v)
    if m:
        h = m.group(1)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return r < 25 and g < 25 and b < 25
    m = re.match(r"rgba?\((\d+),(\d+),(\d+)(?:,([0-9.]+))?\)", v)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) else 1.0
        return r < 25 and g < 25 and b < 25 and a > 0.5
    return False


def is_canvas_rect(elem, vx, vy, vw, vh) -> bool:
    x = parse_float(elem.attrib.get("x", vx), vx)
    y = parse_float(elem.attrib.get("y", vy), vy)
    w = parse_float(elem.attrib.get("width", 0), 0)
    h = parse_float(elem.attrib.get("height", 0), 0)
    return (
        x <= vx + vw * 0.03 and
        y <= vy + vh * 0.03 and
        w >= vw * 0.90 and
        h >= vh * 0.90
    )


def likely_large_black_path(elem, vx, vy, vw, vh) -> bool:
    d = elem.attrib.get("d", "")
    if not d:
        return False
    numbers = [parse_float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
    if len(numbers) < 8:
        return False
    xs = numbers[0::2]
    ys = numbers[1::2]
    if not xs or not ys:
        return False
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y
    return width >= vw * 0.85 and height >= vh * 0.85 and min_x <= vx + vw * 0.08


def clean_svg(svg_path: Path) -> int:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    vx, vy, vw, vh = parse_viewbox(root)
    removed = 0

    def walk(parent):
        nonlocal removed
        for child in list(parent):
            tag = local_name(child.tag)
            fill = get_attr_or_style(child, "fill")

            if is_dark_color(fill):
                if tag == "rect" and is_canvas_rect(child, vx, vy, vw, vh):
                    parent.remove(child)
                    removed += 1
                    continue
                if tag == "path" and likely_large_black_path(child, vx, vy, vw, vh):
                    parent.remove(child)
                    removed += 1
                    continue
            walk(child)

    walk(root)
    if removed:
        tree.write(svg_path, encoding="utf-8", xml_declaration=True)
    return removed


def main():
    if not SRC_DIR.exists():
        raise SystemExit(f"No existe: {SRC_DIR}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    svgs = sorted(p for p in SRC_DIR.glob("*.svg") if p.is_file())

    for svg in svgs:
        backup = BACKUP_DIR / svg.name
        if not backup.exists():
            shutil.copy2(svg, backup)
        try:
            removed = clean_svg(svg)
            total += removed
            print(f"  {svg.name}: fondos eliminados={removed}")
        except Exception as e:
            print(f"  ERROR {svg.name}: {e}")

    print(f"Total fondos eliminados: {total}")


if __name__ == "__main__":
    main()
