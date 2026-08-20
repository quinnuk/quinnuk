"""
Regenerates the auto-managed repo list in README.md between the markers:

  <!-- REPO-LIST:START -->
  ...table gets replaced here...
  <!-- REPO-LIST:END -->

Pulls every public, non-fork repo for GH_USERNAME via the GitHub API,
sorted by most recently pushed, and writes a markdown table with
name / description / primary language / star count.
"""

import os
import sys
import urllib.request
import json

USERNAME = os.environ.get("GH_USERNAME", "quinnuk")
TOKEN = os.environ.get("GH_TOKEN")
README_PATH = "README.md"
START_MARKER = "<!-- REPO-LIST:START -->"
END_MARKER = "<!-- REPO-LIST:END -->"


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    # Skip forks and the profile repo itself (named the same as the username)
    return [
        r for r in data
        if not r.get("fork") and r.get("name", "").lower() != USERNAME.lower()
    ]


def build_table(repos):
    if not repos:
        return "_No public repositories found._"
    lines = ["| Project | What it does | Language | ⭐ |", "|---|---|---|---|"]
    for r in repos:
        name = r["name"]
        html_url = r["html_url"]
        desc = (r.get("description") or "").replace("|", "\\|").strip()
        lang = r.get("language") or "-"
        stars = r.get("stargazers_count", 0)
        lines.append(f"| [**{name}**]({html_url}) | {desc} | {lang} | {stars} |")
    return "\n".join(lines)


def main():
    repos = fetch_repos()
    table = build_table(repos)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print(
            f"Markers {START_MARKER!r} / {END_MARKER!r} not found in {README_PATH}. "
            "Add them to README.md first.",
            file=sys.stderr,
        )
        sys.exit(1)

    before = content.split(START_MARKER)[0]
    after = content.split(END_MARKER)[1]
    new_content = f"{before}{START_MARKER}\n{table}\n{END_MARKER}{after}"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    main()
