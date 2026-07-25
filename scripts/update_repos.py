#!/usr/bin/env python3
"""
Auto-updates the "Recent Repositories" table in the GitHub profile README
by fetching the latest public repos for the GitHub user.

Intended to be run from GitHub Actions (scheduled + manual dispatch).
Run manually from the Actions tab for immediate update after creating a new repo.
"""

import json
import subprocess
import re
import sys
from datetime import datetime, timezone

OWNER = "iampraveen6"
LIMIT = 15  # how many recent public repos to show


def fetch_repos():
    """Use gh CLI to list public repos with needed fields."""
    cmd = [
        "gh", "repo", "list", OWNER,
        "--visibility", "public",
        "--limit", str(LIMIT),
        "--json", "name,description,stargazerCount,pushedAt",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("gh CLI error:", result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("Failed to parse gh output:", e, file=sys.stderr)
        sys.exit(1)


def format_date(iso_str):
    """Convert ISO pushedAt to YYYY-MM-DD (UTC)."""
    if not iso_str:
        return ""
    # GitHub returns e.g. 2026-07-25T09:12:34Z
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d")


def sanitize_description(desc):
    """Escape pipes for markdown table, collapse whitespace, truncate."""
    if not desc:
        return ""
    # Replace newlines and pipes
    desc = " ".join(desc.split()).replace("|", "\\|")
    if len(desc) > 75:
        desc = desc[:72].rstrip() + "..."
    return desc


def build_table_rows(repos):
    """Return list of markdown table row strings, sorted by pushedAt desc."""
    # Exclude the profile repo itself
    repos = [r for r in repos if r.get("name", "").lower() != OWNER.lower()]

    # Ensure newest first
    repos = sorted(
        repos,
        key=lambda r: r.get("pushedAt") or "",
        reverse=True
    )

    rows = []
    for r in repos:
        name = r["name"]
        url = f"https://github.com/{OWNER}/{name}"
        desc = sanitize_description(r.get("description")) or "—"
        stars = r.get("stargazerCount", 0)
        pushed = format_date(r.get("pushedAt"))
        rows.append(f"| [{name}]({url}) | {desc} | {stars} | {pushed} |")
    return rows


def update_readme(rows):
    # Prefer standard README.md for GitHub profile rendering
    candidates = ["README.md", "README.MD"]
    readme_path = None
    for cand in candidates:
        try:
            with open(cand, "r", encoding="utf-8") as f:
                content = f.read()
            readme_path = cand
            break
        except FileNotFoundError:
            continue

    if not readme_path:
        print("Neither README.md nor README.MD found", file=sys.stderr)
        sys.exit(1)

    start_marker = "<!-- START AUTO-REPOS -->"
    end_marker = "<!-- END AUTO-REPOS -->"

    if start_marker not in content or end_marker not in content:
        print(f"Auto-update markers not found in {readme_path}", file=sys.stderr)
        sys.exit(1)

    header = "| Repository | Description | ⭐ | Last Push |\n|------------|-------------|---|-----------|"
    body = "\n".join(rows) if rows else "| _No public repos found_ | | | |"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    timestamp = f"_Last updated: {now} UTC_"

    replacement = f"{start_marker}\n{header}\n{body}\n\n{timestamp}\n{end_marker}"

    pattern = re.compile(
        rf"({re.escape(start_marker)})(.*?)({re.escape(end_marker)})",
        re.DOTALL
    )

    new_content, subs = pattern.subn(replacement, content)
    if subs == 0:
        print("Failed to replace auto-repos section", file=sys.stderr)
        sys.exit(1)

    if new_content == content:
        print(f"No changes to {readme_path}")
        return False

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"{readme_path} updated with latest repositories.")
    return True


def main():
    repos = fetch_repos()
    rows = build_table_rows(repos)
    changed = update_readme(rows)
    # Exit code 0 even if no change (so workflow can decide on commit)
    sys.exit(0)


if __name__ == "__main__":
    main()
