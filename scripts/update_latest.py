#!/usr/bin/env python3
"""
Auto-update the '🆕 Latest:' callout and the Featured Projects 'New/✨' marker
in README.md to the most recently pushed public repo.
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
        cutoff = desc.rfind(" ", 0, 90)
        if cutoff == -1:
            cutoff = 90
        desc = desc[:cutoff].rstrip() + "..."
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


def update_featured_table(repo):
    """Move the latest repo to the top of the Featured Projects table and mark it with ✨ / New."""
    name = repo["name"]
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

    lines = content.split("\n")
    try:
        header_idx = lines.index("| Project | What it demonstrates | Link |")
    except ValueError:
        print("Featured Projects table header not found", file=sys.stderr)
        return False

    sep_idx = header_idx + 1
    end_idx = sep_idx + 1
    while end_idx < len(lines) and lines[end_idx].startswith("|"):
        end_idx += 1

    header = lines[header_idx:sep_idx + 1]
    rows = lines[sep_idx + 1:end_idx]
    after = lines[end_idx:]

    parsed = []
    for r in rows:
        parts = [p.strip() for p in r.split("|")]
        if len(parts) < 5:
            parsed.append((r, None))
        else:
            parsed.append((r, parts[1:4]))

    target_idx = None
    for i, (raw, cols) in enumerate(parsed):
        if cols is None:
            continue
        proj = cols[0]
        desc = cols[1]
        if proj.endswith(" ✨"):
            proj = proj[:-2].rstrip()
        desc = re.sub(r"^\*\*New(\*\* —| —\*\*)\s*", "", desc)
        cols[0] = proj
        cols[1] = desc
        if proj.startswith(f"[{name}]"):
            target_idx = i

    if target_idx is None:
        print(f"Latest repo {name} not found in Featured Projects table", file=sys.stderr)
        return False

    cols = parsed[target_idx][1]
    new_proj = cols[0] + " ✨"
    new_desc = "**New —** " + cols[1]
    if cols[0] == new_proj and target_idx == 0:
        return False

    cols[0] = new_proj
    cols[1] = new_desc
    item = parsed.pop(target_idx)
    parsed.insert(0, item)

    new_rows = []
    for raw, cols in parsed:
        if cols is None:
            new_rows.append(raw)
        else:
            new_rows.append("| " + " | ".join(cols) + " |")

    new_content = "\n".join(lines[:header_idx] + header + new_rows + after)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {readme_path}: moved {name} to top of Featured Projects table")
    return True


def main():
    repo = get_latest_repo()
    if not repo:
        print("No public repos found", file=sys.stderr)
        sys.exit(1)
    changed1 = update_readme(repo)
    changed2 = update_featured_table(repo)
    sys.exit(0 if changed1 or changed2 else 1)


if __name__ == "__main__":
    main()
