import requests
import json

ORG_NAME = "cyrrus-dl"
README_FILE = "profile/README.md"
META_FILE = "team_meta.json"

def fetch_members():
    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch members:", response.text)
        return []
    return response.json()

def load_metadata():
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("team_meta.json not found.")
        return {}

def fetch_user_bio(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json().get("bio", None)

def generate_table(members, meta):
    lines = [
        "| Name        | GitHub        | Specialty Areas                         |",
        "|-------------|---------------|------------------------------------------|"
    ]

    if not members:
        lines.append(
            "\n*To appear in this list, go to your "
            "[organization membership settings](https://github.com/orgs/Cyrrus-Delta-Labs/people), "
            "locate your name, and set your membership to **public**.*"
        )
        return "\n".join(lines)

    for member in members:
        login = member["login"]
        profile_url = member["html_url"]

        meta_info = meta.get(login, {})
        name = meta_info.get("name", login)

        # We update specialty in meta.json instead of taking it from the bio
        specialty = meta_info.get("specialty")

        if not specialty:
            bio = fetch_user_bio(login)
            specialty = bio if bio else "*Not specified*"

        lines.append(f"| `{name}` | [@{login}]({profile_url}) | {specialty} |")

    return "\n".join(lines)

def update_readme(table):
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