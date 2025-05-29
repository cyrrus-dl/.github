"""Script to update the team member table in the organization's README.md file.

This script fetches organization members from GitHub API, combines their information
with metadata from team_meta.json, and updates the README.md file with a formatted
table of team members.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests
import json


ORG_NAME = "cyrrus-dl"
README_FILE = "profile/README.md"
META_FILE = "team_meta.json"


def fetch_members() -> List[Dict]:
    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch members:", response.text)
        return []

    return response.json()


def load_metadata() -> Dict:
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("team_meta.json not found.")
        return {}


def fetch_user_bio(username: str) -> Optional[str]:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json().get("bio", None)


def get_next_monday_utc() -> datetime:
    now = datetime.now(timezone.utc)
    days_ahead = (7 - now.weekday()) % 7
    next_monday = now + timedelta(days=days_ahead)
    return next_monday.replace(hour=6, minute=0, second=0, microsecond=0)


def generate_table(members: List[Dict], meta: Dict) -> str:

    lines = [
        "| Name        | GitHub        | Specialty Areas                         |",
        "|-------------|---------------|------------------------------------------|"
    ]

    updated = False

    for member in members:
        login = member["login"]
        profile_url = member["html_url"]

        if login not in meta:
            bio = fetch_user_bio(login)
            meta[login] = {
                "name": login,
                "specialty": bio if bio else "Not specified"
            }
            updated = True

        meta_info = meta[login]
        name = meta_info.get("name", login)
        specialty = meta_info.get("specialty", "Not specified")

        lines.append(f"| `{name}` | [@{login}]({profile_url}) | {specialty} |")

    if updated:
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print("team_meta.json updated with new members.")

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    next_update = get_next_monday_utc().strftime("%Y-%m-%d %H:%M UTC")
    lines.append(
        f"\n_Last updated: {now_utc}. Next update scheduled: {next_update} via GitHub Actions._"
    )

    return "\n".join(lines)


def update_readme(table: str) -> None:
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!-- START_TEAM_TABLE -->"
    end = "<!-- END_TEAM_TABLE -->"

    if start not in content or end not in content:
        print("README does not contain team table markers.")
        return

    before = content.split(start)[0] + start
    after = content.split(end)[1]
    new_content = before + "\n" + table + "\n" + end + after

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README.md updated.")


if __name__ == "__main__":
    members = fetch_members()
    meta = load_metadata()
    table = generate_table(members, meta)
    update_readme(table)