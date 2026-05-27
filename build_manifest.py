from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
import json
from datetime import datetime

src = Path(__file__).parent / "Ceramika Rybaki"

def exif_to_ms(s):
    if not s:
        return None
    try:
        dt = datetime.strptime(str(s), "%Y:%m:%d %H:%M:%S")
        return int(dt.timestamp() * 1000)
    except Exception:
        return None

items = []
missing = 0
for f in sorted(src.glob("*.jpeg")):
    taken_ms = None
    try:
        img = Image.open(f)
        exif = img.getexif()
        dt = None
        for k, v in exif.items():
            tag = TAGS.get(k, k)
            if tag == "DateTimeOriginal":
                dt = v
                break
        if not dt:
            for k, v in exif.items():
                tag = TAGS.get(k, k)
                if tag in ("DateTime", "DateTimeDigitized"):
                    dt = v
                    break
        taken_ms = exif_to_ms(dt)
    except Exception:
        pass
    if not taken_ms:
        missing += 1
    items.append({"file": f.name, "takenMs": taken_ms})

manifest = {"folder": "Ceramika Rybaki", "items": items}
(src / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

js_lines = ["window.GALLERY_MANIFEST = ["]
for it in items:
    ms = "null" if it["takenMs"] is None else str(it["takenMs"])
    js_lines.append(f"  {{ file: '{it['file']}', takenMs: {ms} }},")
js_lines.append("];")
(src / "manifest.js").write_text("\n".join(js_lines) + "\n", encoding="utf-8")

print(f"items={len(items)} missing_dates={missing}")
