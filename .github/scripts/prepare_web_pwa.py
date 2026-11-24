import json
import re
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "mobile" / "web"
LOGO = ROOT / "mobile" / "assets" / "brand" / "logo_full.png"

if not LOGO.is_file():
    raise SystemExit(f"Missing official logo: {LOGO}")

WEB.mkdir(parents=True, exist_ok=True)
(WEB / "icons").mkdir(parents=True, exist_ok=True)

source = Image.open(LOGO).convert("RGBA")

def make_icon(size: int, filename: str, safe_ratio: float):
    canvas = Image.new("RGBA", (size, size), "#101827")
    max_size = int(size * safe_ratio)
    logo = ImageOps.contain(source, (max_size, max_size), Image.Resampling.LANCZOS)
    x = (size - logo.width) // 2
    y = (size - logo.height) // 2
    canvas.alpha_composite(logo, (x, y))
    canvas.convert("RGB").save(WEB / "icons" / filename, format="PNG", optimize=True)

make_icon(192, "Icon-192.png", 0.88)
make_icon(512, "Icon-512.png", 0.88)
make_icon(192, "Icon-maskable-192.png", 0.70)
make_icon(512, "Icon-maskable-512.png", 0.70)

manifest = {
    "name": "لیگ نخبگان مالیاتی",
    "short_name": "لیگ نخبگان",
    "description": "رقابت کن، رتبه بگیر، نخبه شو!",
    "start_url": "/app/",
    "scope": "/app/",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#101827",
    "theme_color": "#101827",
    "prefer_related_applications": False,
    "icons": [
        {"src": "icons/Icon-192.png", "sizes": "192x192",
         "type": "image/png"},
        {"src": "icons/Icon-512.png", "sizes": "512x512",
         "type": "image/png"},
        {"src": "icons/Icon-maskable-192.png", "sizes": "192x192",
         "type": "image/png", "purpose": "maskable"},
        {"src": "icons/Icon-maskable-512.png", "sizes": "512x512",
         "type": "image/png", "purpose": "maskable"}
    ]
}
(WEB / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

index = WEB / "index.html"
if not index.is_file():
    raise SystemExit("Flutter web index.html was not generated")

html = index.read_text(encoding="utf-8")

if "<head>" not in html:
    raise SystemExit("Could not find HTML head element")

html, title_count = re.subn(
    r"<title>.*?</title>",
    "<title>لیگ نخبگان مالیاتی</title>",
    html,
    count=1,
    flags=re.DOTALL
)
if title_count != 1:
    raise SystemExit("Could not safely update HTML title")

html = re.sub(
    r'\s*<meta\s+name=["\']theme-color["\'][^>]*>',
    "",
    html,
    flags=re.IGNORECASE
)
html = re.sub(
    r'\s*<meta\s+name=["\']apple-mobile-web-app-title["\'][^>]*>',
    "",
    html,
    flags=re.IGNORECASE
)

tags = """
  <meta name="theme-color" content="#101827">
  <meta name="description" content="رقابت کن، رتبه بگیر، نخبه شو!">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="لیگ نخبگان مالیاتی">
"""
html = html.replace("<head>", "<head>\n" + tags, 1)

if 'href="manifest.json"' not in html:
    raise SystemExit("Manifest link missing from Flutter index.html")

index.write_text(html, encoding="utf-8")

print("SUCCESS: RAQTIVA PWA branding generated.")
print("Manifest scope/start_url: /app/")
print("Official logo:", LOGO)
print("Icons: 192, 512 and maskable variants")
