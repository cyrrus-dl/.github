# GitHub Organization Team Table Updater

This project automatically updates a team member table in your organization's README.md file using GitHub's API. It fetches organization members, their information, and maintains a metadata file for additional member details.

## Features

- Automatically fetches organization members from GitHub API
- Maintains member metadata in a JSON file
- Updates member information including:
  - Name
  - GitHub profile link
  - Specialty areas (from bio or metadata)
- Automatically updates the README.md file with a formatted table
- Schedules weekly updates via GitHub Actions

## Prerequisites

- Python 3.6+
- GitHub organization with public access
- GitHub API access (no token required for public organizations)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/github-team-table-updater.git
cd github-team-table-updater
```

2. Install required dependencies:
```bash
pip install requests
```

## Configuration

1. Update the constants in `update_readme_team.py`:
```python
ORG_NAME = "your-organization-name"
README_FILE = "profile/README.md"
META_FILE = "team_meta.json"
```

2. Add the following markers to your README.md file:
```markdown
<!-- START_TEAM_TABLE -->
<!-- END_TEAM_TABLE -->
```

3. Create a `team_meta.json` file with member metadata (optional):
```json
{
  "username": {
    "name": "Full Name",
    "specialty": "Specialty Area"
  }
}
```

## Usage

Run the script manually:
```bash
python update_readme_team.py
```

### GitHub Actions Setup

To automate updates, create a GitHub Actions workflow file (`.github/workflows/update-team-table.yml`):

```yaml
name: Update Team Table

on:
  schedule:
    - cron: '0 6 * * 1'  # Runs at 6:00 UTC every Monday
  workflow_dispatch:  # Allows manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests
      - name: Run update script
        run: python update_readme_team.py
      - name: Commit and push if changed
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update team table" && git push)
```

## How It Works

1. The script fetches organization members from GitHub API
2. For each member:
   - Checks if metadata exists in `team_meta.json`
   - If not, fetches their bio from GitHub
   - Updates metadata if new information is found
3. Generates a markdown table with member information
4. Updates the README.md file between the specified markers

## Contributing

Feel free to submit issues and enhancement requests!