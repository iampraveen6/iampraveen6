# Setup & Usage Guide for `iampraveen6/iampraveen6`

This repository hosts the GitHub profile README for [Praveen Kittur](https://github.com/iampraveen6). The file that renders on your public profile is `README.md` (lowercase). If you are cloning this to a new laptop or working on another machine, follow the steps below.

---

## 1. Clone the repository

### Using `git`
```bash
git clone https://github.com/iampraveen6/iampraveen6.git
cd iampraveen6
```

If your network blocks SSH, `https` is the reliable option. If you previously changed the remote to SSH and it fails, switch back with:
```bash
git remote set-url origin https://github.com/iampraveen6/iampraveen6.git
```

### Using GitHub CLI (`gh`)
```bash
gh repo clone iampraveen6/iampraveen6
cd iampraveen6
```

---

## 2. Which file to edit

The profile README that GitHub displays is **`README.md`** (lowercase).

- `README.MD` (uppercase) is no longer used and has been removed from the remote.
- Do not create `README.MD` again — it can cause confusion.

Make all profile edits in `README.md`.

---

## 3. Push changes

### Option A: Normal `git push` (try first)
```bash
git add README.md
git commit -m "update profile"
git push origin Main
```

If this fails with `non-fast-forward` or network errors, see the troubleshooting section below.

### Option B: Use the API helper script (when `git push` is slow/flaky)
If `git push` hangs, fails with `Connection reset`, or returns SSL errors, use `scripts/push_via_api.py`.

1. Create a Personal Access Token (classic) with `repo` scope at:
   https://github.com/settings/tokens
2. Export the token in your terminal:
   ```bash
   export GITHUB_TOKEN=ghp_xxxxxxxx
   ```
3. Run the helper:
   ```bash
   python3 scripts/push_via_api.py
   ```

This script updates `README.md` and any new/changed files via HTTPS using the GitHub Contents API. It is more reliable on restricted networks.

---

## 4. Verify on GitHub

After pushing, hard refresh your profile to see changes:
```
https://github.com/iampraveen6
```

Raw content is sometimes cached for a few seconds by `raw.githubusercontent.com`. If the rendered page does not match your latest commit, wait 10–20 seconds and refresh again.

---

## 5. Important notes about the current profile

- **No auto-update workflow**: The `Update Recent Repositories` workflow and `scripts/update_repos.py` have been removed. The `Recent Repositories` section is hidden, so new public repos do **not** appear automatically. To showcase a new repo, add it to the `## 🚀 Featured Projects` table in `README.md`.
- **GitHub Statistics cards**: The `github-readme-stats` card was removed because the third-party service frequently returns 503 errors. The working streak stats and contribution graph remain.
- **Profile repo rule**: This repo must be named `iampraveen6/iampraveen6` (matching your GitHub username) for the README to render on your profile.

---

## 6. Troubleshooting

| Problem | Solution |
|---|---|
| `git push` rejected with `non-fast-forward` | Run `git pull --rebase origin Main` first, then push. If conflicts appear, resolve them or use `scripts/push_via_api.py`. |
| `Connection closed by ... port 22` | SSH is blocked on your network. Switch to HTTPS: `git remote set-url origin https://github.com/iampraveen6/iampraveen6.git` |
| SSL/certificate errors in Python helper | The helper uses `curl` instead of Python's `urllib` to avoid cert issues. Make sure `curl` is installed. |
| Broken image in Statistics | The stats card may be down again. Edit `README.md` and remove or replace the `<img>` URL that does not load. |

---

## 7. Quick reference — files in this repo

| File / Folder | Purpose |
|---|---|
| `README.md` | Profile content displayed on https://github.com/iampraveen6 |
| `SETUP.md` | This file — setup and usage instructions |
| `scripts/push_via_api.py` | Helper to push changes when `git` is unreliable |
| `.github/workflows/` | Empty after the auto-update workflow was removed |
