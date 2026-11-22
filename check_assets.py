import re
import sys
from pathlib import Path

files = [Path("index.html"), Path("pousadas/index.html"), Path("pousadas/robo/index.html")]

missing = []
checked = 0
for f in files:
    content = f.read_text(encoding="utf-8")
    # find src/href/srcset attributes
    for m in re.finditer(r'(?:src|href|srcset)\s*=\s*"([^"]+)"', content):
        url = m.group(1)
        # skip absolute URLs, anchors, mailto, tel, data:, blobs
        if url.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:", "blob:")):
            continue
        # skip protocol-relative
        if url.startswith("//"):
            continue
        # skip fragment-only
        if url.strip() == "":
            continue
        # srcset: take each candidate
        if m.group(0).startswith("srcset"):
            candidates = [c.strip().split(" ")[0] for c in url.split(",") if c.strip()]
        else:
            candidates = [url]
        for c in candidates:
            # strip query strings
            c = c.split("?")[0]
            # strip fragment
            c = c.split("#")[0]
            if not c:
                continue
            # skip if points to directory (trailing / or no extension)
            if c.endswith("/"):
                continue
            # relative to the file's dir
            base = f.parent if f.name.endswith(".html") else Path(".")
            target = (base / c).resolve()
            checked += 1
            if not target.exists():
                missing.append(str(c))

print(f"Checked {checked} relative assets across {len(files)} file(s)")
if missing:
    print("MISSING:")
    for m in missing:
        print(" -", m)
    sys.exit(1)
else:
    print("All relative assets found.")
