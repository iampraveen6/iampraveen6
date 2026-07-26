#!/usr/bin/env python3
"""
Auto-update the '🆕 Latest:' callout in README.md to the most recently pushed public repo.
Designed to run from GitHub Actions on a schedule or manually.
"""

import json
import os
import re
import subprocess
import sys

OWNER = "iampraveen6"
README_CANDIDATES = ["README.md", "README.MD"]


def get_latest_repo():
    """Return the latest public repo (excluding the profile repo itself)."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    url = f"https://api.github.com/users/{OWNER}/repos?sort=pushed&direction=desc&per_page=15"
    cmd = ["curl", "-s", "-L", "-H", "Accept: application/vnd.github.v3+json"]
    if token:
        cmd += ["-H", f"Authorization: token {token}"]
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("curl error:", result.stderr, file=sys.stderr)
        sys.exit(1)
    try:
        repos = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("Failed to parse API response:", e, file=sys.stderr)
        sys.exit(1)

    if not isinstance(repos, list):
        print("Unexpected API response:", repos, file=sys.stderr)
        sys.exit(1)

    for r in repos:
        name = r.get("name", "").lower()
        if name != OWNER.lower():
            return r
    return None


def sanitize_description(desc):
    """Clean and truncate description for the callout."""
    if not desc:
        return "New repository"
    desc = " ".join(desc.split()).replace("|", "\\|")
    if len(desc) > 90:
        desc = desc[:87].rstrip() + "..."
    return desc


def update_readme(repo):
    name = repo["name"]
    url = f"https://github.com/{OWNER}/{name}"
    desc = sanitize_description(repo.get("description"))
    new_line = f"> 🆕 **Latest:** [{name}]({url}) — {desc}."

    readme_path = None
    for cand in README_CANDIDATES:
        if os.path.exists(cand):
            readme_path = cand
            break
    if not readme_path:
        print("No README.md or README.MD found", file=sys.stderr)
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"^> 🆕 \*\*Latest:\*\* .*$", re.MULTILINE)
    new_content, subs = pattern.subn(new_line, content)
    if subs == 0:
        print("Latest callout marker not found", file=sys.stderr)
        sys.exit(1)

    if new_content == content:
        print(f"Latest badge already points to {name}. No changes.")
        return False

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {readme_path}: latest is now {name}")
    return True


def main():
    repo = get_latest_repo()
    if not repo:
        print("No public repos found", file=sys.stderr)
        sys.exit(1)
    changed = update_readme(repo)
    sys.exit(0 if changed else 0)


if __name__ == "__main__":
    main()
