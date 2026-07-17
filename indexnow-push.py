#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把本次提交真正改动的页面推送给 IndexNow（Bing / ChatGPT 搜索 / Copilot / Yandex 等共用）。

要点：
  * 只推本次 push 改动的 URL，不做全量推送。IndexNow 明确要求只提交
    "新增或有实质更新" 的 URL；每次全量刷会被判为滥用。
  * 跳过 stamp-dates 机器人提交（那只是盖日期，不是内容变化）。
  * 密钥文件必须能公开访问，内容等于文件名，否则 Bing 拒收。
"""
import os, sys, json, subprocess, urllib.request, urllib.error

SITE   = "https://censilcoat.com"
HOST   = "censilcoat.com"
KEY    = os.environ.get("INDEXNOW_KEY", "").strip()
ENDPOINT = "https://api.indexnow.org/indexnow"
STAMP_MSG = "chore: stamp last-updated dates"
EXCLUDE = {"404.html", "thanks.html", "thank-you.html"}

def changed_urls():
    """本次 push 里改动的 .html。取 before..after 差异；首次推送则取最后一条非机器人提交。"""
    before = os.environ.get("GITHUB_EVENT_BEFORE", "")
    after  = os.environ.get("GITHUB_SHA", "HEAD")
    rng = f"{before}..{after}" if before and not before.startswith("0000") else f"{after}~1..{after}"
    try:
        out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", rng],
                             capture_output=True, text=True, timeout=30)
        files = [f for f in out.stdout.split("\n") if f.endswith(".html")]
    except Exception as e:
        print(f"git diff failed: {e}", file=sys.stderr)
        return []
    urls = []
    for f in files:
        base = os.path.basename(f)
        if base in EXCLUDE or f in EXCLUDE:
            continue
        urls.append(f"{SITE}/{f}")
    return sorted(set(urls))

def is_stamp_commit():
    try:
        msg = subprocess.run(["git", "log", "-1", "--format=%s"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return msg == STAMP_MSG
    except Exception:
        return False

def verify_key():
    """推送前先自证密钥文件可访问 —— Bing 拒收时不会告诉你原因，这里先查。"""
    url = f"{SITE}/{KEY}.txt"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            body = r.read().decode().strip()
        if body != KEY:
            print(f"ERROR: key file content mismatch at {url}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"ERROR: key file not reachable at {url}: {e}", file=sys.stderr)
        return False

def push(urls):
    payload = {"host": HOST, "key": KEY,
               "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls}
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow accepted: HTTP {r.status}")
            return True
    except urllib.error.HTTPError as e:
        # 200/202 = 收到；400 格式错；403 密钥无效；422 URL 与 host 不符；429 太频繁
        body = e.read().decode(errors="ignore")[:300]
        print(f"IndexNow HTTP {e.code}: {body}", file=sys.stderr)
        return e.code in (200, 202)
    except Exception as e:
        print(f"IndexNow request failed: {e}", file=sys.stderr)
        return False

def main():
    if not KEY:
        print("ERROR: INDEXNOW_KEY not set", file=sys.stderr); sys.exit(1)
    if is_stamp_commit():
        print("Skip: date-stamp commit, not a content change"); return
    urls = changed_urls()
    if not urls:
        print("No changed html to submit"); return
    print(f"{len(urls)} changed URL(s):")
    for u in urls: print("  ", u)
    if not verify_key():
        sys.exit(1)
    sys.exit(0 if push(urls) else 1)

if __name__ == "__main__":
    main()
