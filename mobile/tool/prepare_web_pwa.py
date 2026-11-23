#!/usr/bin/env python3
"""Apply RAQTIVA branding to Flutter's generated web shell and install icons."""
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
web = root / "web"
build = web / "build"
# Flutter build output is mobile/build/web; source web shell is mobile/web.
source_logo = root / "assets" / "brand" / "logo_full.png"
if not source_logo.is_file():
    raise SystemExit(f"Brand logo not found: {source_logo}")

index = web / "index.html"
html = index.read_text(encoding="utf-8")
html = html.replace('content="A new Flutter project."', 'content="لیگ نخبگان مالیاتی؛ رقابت کن، رتبه بگیر، نخبه شو!"')
html = html.replace('content="tax_league"', 'content="لیگ نخبگان مالیاتی"')
html = html.replace('<title>tax_league</title>', '<title>لیگ نخبگان مالیاتی</title>')
html = html.replace('content="black"', 'content="black-translucent"')
if 'name="theme-color"' not in html:
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n  <meta name="theme-color" content="#101827">')
if 'viewport-fit=cover' not in html:
    html = html.replace('content="width=device-width, initial-scale=1.0"', 'content="width=device-width, initial-scale=1.0, viewport-fit=cover"')
index.write_text(html, encoding="utf-8")

manifest_path = web / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({
    "name": "لیگ نخبگان مالیاتی",
    "short_name": "لیگ نخبگان",
    "description": "رقابت کن، رتبه بگیر، نخبه شو!",
    "background_color": "#101827",
    "theme_color": "#101827",
    "orientation": "portrait-primary",
    "display": "standalone",
})
manifest["icons"] = [
    {"src": "icons/Icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icons/Icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icons/Icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
    {"src": "icons/Icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
]
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

icons = web / "icons"
icons.mkdir(parents=True, exist_ok=True)
logo = Image.open(source_logo).convert("RGBA")
for size, filename in [(192, "Icon-192.png"), (512, "Icon-512.png"), (192, "Icon-maskable-192.png"), (512, "Icon-maskable-512.png")]:
    canvas = Image.new("RGBA", (size, size), "#101827")
    fitted = logo.copy()
    fitted.thumbnail((int(size * 0.78), int(size * 0.78)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
    canvas.convert("RGB").save(icons / filename, format="PNG", optimize=True)

favicon = Image.new("RGBA", (64, 64), "#101827")
small = logo.copy()
small.thumbnail((52, 52), Image.Resampling.LANCZOS)
favicon.alpha_composite(small, ((64-small.width)//2, (64-small.height)//2))
favicon.save(web / "favicon.png", format="PNG", optimize=True)
print("RAQTIVA PWA branding prepared.")
