#!/usr/bin/env python3
"""Bundle src/ into one self-contained index.html (CSS, images and the
intro animation inlined) so it works wherever a single file is served."""
import base64, gzip, html, json, mimetypes, re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

def data_uri(p: Path) -> str:
    mime = {"svg": "image/svg+xml", "jpg": "image/jpeg", "png": "image/png"}[p.suffix[1:]]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

def inline_assets(text: str) -> str:
    def sub(m):
        p = SRC / m.group(0)
        return data_uri(p) if p.exists() else m.group(0)
    return re.sub(r"assets/[\w.-]+\.(?:svg|jpg|png)", sub, text)

# intro bundle: images are referenced from inside its gzipped JSX modules
intro = (SRC / "intro-standalone.html").read_text()
mm = re.search(r'(<script type="__bundler/manifest">)(.*?)(</script>)', intro, re.S)
manifest = json.loads(mm.group(2))
for entry in manifest.values():
    if entry.get("compressed") and "jsx" in entry["mime"] or entry["mime"] == "application/javascript":
        code = gzip.decompress(base64.b64decode(entry["data"])).decode()
        new = inline_assets(code)
        if new != code:
            entry["data"] = base64.b64encode(gzip.compress(new.encode(), 9)).decode()
intro = intro[:mm.start(2)] + json.dumps(manifest) + intro[mm.end(2):]

page = (SRC / "index.html").read_text()
css = (SRC / "styles.css").read_text()
page = page.replace('<link rel="stylesheet" href="styles.css">', f"<style>\n{css}</style>")
page = inline_assets(page)
page = re.sub(r'src="intro-standalone\.html"', lambda m: 'srcdoc="' + html.escape(intro, quote=True) + '"', page)
(ROOT / "index.html").write_text(page)
print("index.html", round(len(page) / 1e6, 2), "MB")
