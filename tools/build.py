"""Build the public site (index.html) from src/site.html.

    python tools/build.py                      # public build -> index.html
    python tools/build.py --research-preview   # local only -> research-preview.html (git-ignored)

The public build reads ONLY data/heritage/ (sources, village profiles, approved entries).
It never reads research/. Every approved entry is re-checked against the rules; if any
fails, the build stops so unapproved material cannot slip into the public site.
"""
import argparse, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import heritage_rules as R  # noqa: E402

BEGIN, END = "/*HERITAGE:BEGIN*/", "/*HERITAGE:END*/"
WRAP_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""
WRAP_TAIL = "\n</body>\n</html>\n"


class BuildError(Exception):
    pass


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_entries(folder):
    out = []
    for p in sorted(glob.glob(os.path.join(folder, "**", "*.json"), recursive=True)):
        data = load_json(p, [])
        for e in data if isinstance(data, list) else [data]:
            e["_file"] = os.path.relpath(p, ROOT)
            out.append(e)
    return out


def heritage_payload(root=ROOT, research=False):
    data = os.path.join(root, "data", "heritage")
    sources = load_json(os.path.join(data, "sources.json"), [])
    villages = load_json(os.path.join(data, "villages.json"), [])
    approved = load_entries(os.path.join(data, "approved"))
    entries = []
    for e in approved:
        if not R.is_public(e, sources):
            raise BuildError("%s (%s) is in data/heritage/approved but is not publishable: %s"
                             % (e.get("id"), e.get("_file"), "; ".join(R.problems(e, sources))))
        entries.append(R.public_view(e))
    payload = {"sources": sources, "villages": villages, "entries": entries, "mode": "public"}
    if research:
        rdir = os.path.join(root, "research")
        drafts = [dict(R.public_view({**e, "publication": {**(e.get("publication") or {}), "scope": "full-text"}}),
                       researchStatus=(e.get("research") or {}).get("status"),
                       publicationStatus=(e.get("publication") or {}).get("status"),
                       problems=R.problems(e, sources))
                  for e in load_entries(rdir)]
        payload.update(mode="research-preview", drafts=drafts)
    return payload


def build(root=ROOT, research=False, out=None):
    with open(os.path.join(root, "src", "site.html"), encoding="utf-8") as f:
        src = f.read()
    if src.count(BEGIN) != 1 or src.count(END) != 1:
        raise BuildError("src/site.html must contain exactly one heritage data block")
    payload = json.dumps(heritage_payload(root, research), ensure_ascii=False, separators=(",", ":"))
    a, b = src.index(BEGIN) + len(BEGIN), src.index(END)
    html = WRAP_HEAD + src[:a] + payload + src[b:] + WRAP_TAIL
    if research:
        html = html.replace("<body>\n", "<body>\n<div style=\"position:fixed;z-index:999;left:0;right:0;bottom:0;background:#7A4E6B;color:#fff;font:600 13px system-ui;padding:8px 12px;text-align:center\">RESEARCH PREVIEW · contains unpublished material · do not share or commit</div>\n", 1)
    out = out or os.path.join(root, "research-preview.html" if research else "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--research-preview", action="store_true")
    args = ap.parse_args()
    try:
        print("Built", os.path.relpath(build(research=args.research_preview), ROOT))
    except BuildError as e:
        print("BUILD STOPPED:", e, file=sys.stderr)
        sys.exit(1)
