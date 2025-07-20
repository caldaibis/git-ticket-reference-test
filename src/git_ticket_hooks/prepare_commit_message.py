#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import re

from dotenv import load_dotenv

# --- CONFIGURATIE ---

# Bepaal de root van de Git-repository.
GIT_ROOT = Path(os.getcwd())

# Laad omgevingsvariabelen uit het .env-bestand in de root van de repository.
load_dotenv(dotenv_path=GIT_ROOT / ".env")

# Standaard reguliere expressies voor het herkennen van ticket ID's.
# 1. Traditioneel formaat: PROJ-123
# 2. Platform-specifiek formaat: #123, feature/123-, 123_
DEFAULT_TICKET_REGEXES = [
    r"([A-Z]{2,10}-[0-9]+)",
    r"(^|/|#)([0-9]+)([-_])",
]


def get_ticket_regexes() -> list[str]:
    """Haalt de ticket regexes op uit de .env-instelling, of gebruikt de standaardwaarden."""
    env_regex = os.getenv("TICKET_REGEX")
    if env_regex:
        return [r.strip() for r in env_regex.split(",") if r.strip()]
    return DEFAULT_TICKET_REGEXES


def find_ticket_id(content: str) -> str | None:
    """
    Zoekt naar een ticket-ID in een string (commit message of branch-naam).
    Probeert meerdere patronen in een specifieke volgorde voor de beste match.
    Retourneert het ID in een canoniek formaat, bijv. "[PROJ-123]" of "[#123]".
    """
    for regex in get_ticket_regexes():
        match = re.search(regex, content)
        if match:
            return f"[{match.group(1)}]"

    return None


def get_branch():
    """Get current git branch name."""
    return os.popen("git rev-parse --abbrev-ref HEAD").read().strip()


def main():
    parser = argparse.ArgumentParser(
        description="Add ticket ID from branch to commit message"
    )
    parser.add_argument(
        "commit_file", required=True, help="Path to the commit message file"
    )
    args = parser.parse_args()

    commit_file = Path(args.commit_file)
    branch = get_branch()
    ticket = find_ticket_id(branch)

    if not ticket:
        return

    commit_content = commit_file.read_text().strip()
    if not find_ticket_id(commit_content):
        commit_file.write_text(f"{ticket} {commit_content}")


if __name__ == "__main__":
    main()
