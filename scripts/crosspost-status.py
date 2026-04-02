#!/usr/bin/env python3
"""Cross-post status checker for blog articles."""

import os
import re
import glob

BLOG_BASE = "https://ktaka.blog.ccmp.jp"

def find_articles():
    """Find all 2026+ blog articles."""
    articles = []
    for path in sorted(glob.glob("content/2026/*/index.md")):
        name = path.split("/")[2]
        lang = "EN" if name.endswith("En") else "JP"
        articles.append({"name": name, "lang": lang, "path": path})
    return articles

def extract_canonical(filepath):
    """Extract canonical_url from frontmatter."""
    with open(filepath) as f:
        for line in f:
            m = re.match(r'canonical_url:\s*"?([^"\s]+)"?', line)
            if m:
                return m.group(1)
    return None

def extract_crosspost_url(filepath):
    """Extract blog URL from crosspost notice."""
    with open(filepath) as f:
        for line in f:
            m = re.search(r'ktaka\.blog\.ccmp\.jp/((?:en/)?2026/\w+)', line)
            if m:
                return f"{BLOG_BASE}/{m.group(1)}"
    return None

def check_published_zenn(filepath):
    """Check Zenn published status."""
    with open(filepath) as f:
        for line in f:
            if line.startswith("published:"):
                return "true" in line
    return False

def check_published_devto(filepath):
    """Check dev.to published status."""
    with open(filepath) as f:
        for line in f:
            if line.startswith("published:"):
                return "true" in line
    return False

def check_published_qiita(filepath):
    """Check Qiita published status (id is set after publish)."""
    with open(filepath) as f:
        for line in f:
            if line.startswith("id:"):
                val = line.split(":", 1)[1].strip()
                return val != "null" and val != ""
    return False

def build_crosspost_map():
    """Build mapping from blog path to crosspost files."""
    mapping = {}

    # Zenn new: articles/
    for f in glob.glob("articles/*.md"):
        url = extract_canonical(f)
        if url:
            mapping.setdefault(url, {})["zenn"] = (f, check_published_zenn(f), False)

    # Zenn legacy: docs/*-zenn/*.md
    for f in glob.glob("docs/*-zenn/*.md"):
        url = extract_crosspost_url(f)
        if url:
            mapping.setdefault(url, {})["zenn"] = (f, True, True)

    # dev.to new: devto/
    for f in glob.glob("devto/*.md"):
        url = extract_canonical(f)
        if url:
            # Map EN canonical to JP article name
            mapping.setdefault(url, {})["devto"] = (f, check_published_devto(f), False)

    # dev.to legacy: docs/*-devto/*.md
    for f in glob.glob("docs/*-devto/*.md"):
        url = extract_canonical(f)
        if url:
            mapping.setdefault(url, {})["devto"] = (f, True, True)

    # Qiita: qiita/public/
    for f in glob.glob("qiita/public/*.md"):
        url = extract_crosspost_url(f)
        if url:
            mapping.setdefault(url, {})["qiita"] = (f, check_published_qiita(f), False)

    return mapping

def status_str(info):
    if info is None:
        return "❌"
    _, published, legacy = info
    suffix = " (docs/)" if legacy else ""
    if published:
        return f"✅ published{suffix}"
    else:
        return "📝 draft"

def main():
    import sys
    args = [a.lower() for a in sys.argv[1:]]
    missing_only = "--missing" in args
    platform = next((a for a in args if a != "--missing"), None)

    articles = find_articles()
    crosspost = build_crosspost_map()

    all_cols = {"zenn": 3, "devto": 4, "dev.to": 4, "qiita": 5}
    all_headers = ["記事", "言語", "Blog", "Zenn", "dev.to", "Qiita"]

    if platform and platform in all_cols:
        col_idx = all_cols[platform]
        headers = ["記事", "言語", "Blog", all_headers[col_idx]]
    else:
        headers = all_headers
        platform = None

    rows = []

    for art in articles:
        name = art["name"]
        lang = art["lang"]
        if lang == "EN":
            base_name = name[:-2]
            canonical = f"{BLOG_BASE}/en/2026/{base_name}"
        else:
            canonical = f"{BLOG_BASE}/2026/{name}"

        info = crosspost.get(canonical, {})

        if lang == "JP":
            zenn = status_str(info.get("zenn"))
            devto = "-"
            qiita = status_str(info.get("qiita"))
        else:
            zenn = "-"
            devto = status_str(info.get("devto"))
            qiita = "-"

        all_values = [name, lang, "✅", zenn, devto, qiita]

        if platform:
            col_idx = all_cols[platform]
            row = [name, lang, "✅", all_values[col_idx]]
            if all_values[col_idx] == "-":
                continue
            if missing_only and all_values[col_idx] != "❌":
                continue
            rows.append(row)
        else:
            if missing_only:
                has_missing = any(v == "❌" for v in all_values[3:])
                if not has_missing:
                    continue
            rows.append(all_values)

    # Calculate column widths (accounting for wide chars: emoji, CJK)
    import unicodedata
    def display_width(s):
        w = 0
        for c in s:
            if unicodedata.east_asian_width(c) in ('F', 'W'):
                w += 2
            else:
                w += 1
        return w

    all_rows = [headers] + rows
    widths = [max(display_width(r[i]) for r in all_rows) for i in range(len(headers))]

    def pad(s, w):
        return s + " " * (w - display_width(s))

    def fmt_row(row):
        return "| " + " | ".join(pad(v, w) for v, w in zip(row, widths)) + " |"

    print(fmt_row(headers))
    print("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    for row in rows:
        print(fmt_row(row))

if __name__ == "__main__":
    main()
