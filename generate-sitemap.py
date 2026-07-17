#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成 sitemap.xml — Censilcoating

扫描仓库全部 .html，用 git 最后提交时间作为 lastmod。
由 .github/workflows/sitemap.yml 在每次 push 时自动执行。
不想被收录的页面加进 EXCLUDE 即可。
"""
import os, subprocess, sys
from datetime import datetime, timezone

SITE = "https://censilcoat.com"
EXCLUDE = {"404.html", "thanks.html", "thank-you.html"}
EXCLUDE_DIRS = {".git", ".github", "node_modules"}


def git_lastmod(path):
    try:
        # 排除 stamp-dates.py 的提交，否则 lastmod 会变成"盖日期的时间"
        # 而不是"内容真正改动的时间"，与页面上显示的日期打架。
        out = subprocess.run(["git", "log", "-1", "--format=%cI",
                              "--invert-grep", "--grep=chore: stamp last-updated dates",
                              "--", path],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        if out:
            return out[:10]
    except Exception:
        pass
    try:
        return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def collect():
    pages = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in files:
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(root, f), ".").replace(os.sep, "/")
            if rel in EXCLUDE or f in EXCLUDE:
                continue
            pages.append(rel)
    return sorted(pages)


def build(pages):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        out += ["  <url>", f"    <loc>{SITE}/{p}</loc>",
                f"    <lastmod>{git_lastmod(p)}</lastmod>", "  </url>"]
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def main():
    pages = collect()
    if not pages:
        print("::error::未找到任何 html，中止（避免空 sitemap 覆盖线上）")
        sys.exit(1)
    xml = build(pages)
    old = open("sitemap.xml", encoding="utf-8").read() if os.path.exists("sitemap.xml") else ""
    if old == xml:
        print(f"sitemap.xml 无变化（{len(pages)} 个页面），跳过")
        return
    open("sitemap.xml", "w", encoding="utf-8").write(xml)
    print(f"sitemap.xml 已更新：{len(pages)} 个页面")
    for p in pages:
        print("  " + p)


if __name__ == "__main__":
    main()
