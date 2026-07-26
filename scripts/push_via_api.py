#!/usr/bin/env python3
"""
Push local changes to the GitHub profile repo using the GitHub Contents API.
Useful when normal 'git push' is slow, fails with network/SSL errors, or is blocked.

Usage:
  1. Create a Personal Access Token (classic) with 'repo' scope:
     https://github.com/settings/tokens
  2. Export it in your terminal:
     export GITHUB_TOKEN=ghp_xxxxxxxx
  3. Run from the repo root:
     python3 scripts/push_via_api.py

It will push the current local versions of tracked files listed in FILES below.
"""

import os
import sys
import json
import base64
import subprocess

OWNER = "iampraveen6"
REPO = "iampraveen6"
BRANCH = "Main"

# Add paths here that you want to keep in sync with the remote.
# The script only creates/updates files that exist locally.
FILES = [
    "README.md",
    "SETUP.md",
    "scripts/push_via_api.py",
]

TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
if not TOKEN:
    print("ERROR: Set GITHUB_TOKEN or GH_TOKEN env var with a repo-scoped PAT.")
    sys.exit(1)

HEADERS = [
    f"Authorization: token {TOKEN}",
    "Accept: application/vnd.github.v3+json",
]


def curl(method, path, payload=None):
    """Call GitHub Contents API using curl. Returns (returncode, parsed_json_or_text)."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    cmd = ["curl", "-s", "-X", method] + [h for header in HEADERS for h in ("-H", header)]
    kwargs = {"capture_output": True, "text": True}

    if method == "GET":
        url += f"?ref={BRANCH}"
    else:
        cmd += ["-H", "Content-Type: application/json", "-d", "@-"]
        kwargs["input"] = json.dumps(payload)

    cmd.append(url)
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        return result.returncode, result.stderr
    try:
        return result.returncode, json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.returncode, result.stdout


def get_sha(path):
    status, data = curl("GET", path)
    if status == 0 and isinstance(data, dict) and "sha" in data:
        return data["sha"]
    return None


def put_file(repo_path, local_path, message):
    if not os.path.exists(local_path):
        print(f"SKIP {local_path} (not found locally)")
        return False

    with open(local_path, "rb") as f:
        content = f.read()

    sha = get_sha(repo_path)
    payload = {
        "message": message,
        "content": base64.b64encode(content).decode(),
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    status, resp = curl("PUT", repo_path, payload)
    if status == 0 and isinstance(resp, dict) and "content" in resp:
        print(f"OK  {repo_path}")
        return True
    print(f"FAIL {repo_path}: {resp}")
    return False


def main():
    print(f"Pushing to {OWNER}/{REPO}@{BRANCH} via GitHub API...\n")
    pushed = False
    for repo_path in FILES:
        local_path = repo_path
        ok = put_file(repo_path, local_path, f"chore: update {repo_path} via API")
        if ok:
            pushed = True
    print("\nDone." if pushed else "\nNothing pushed.")
    sys.exit(0 if pushed else 1)


if __name__ == "__main__":
    main()
