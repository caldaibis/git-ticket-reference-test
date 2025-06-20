#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

# Laad .env automatisch
load_dotenv()

# Debug logging setup
DEBUG = os.getenv("DEBUG_TICKET_HOOK") == "1"
DEBUG_LOG_PATH = Path(__file__).parent.parent / ".git" / "ticket_hook_debug.log"


def debug_log(msg):
    if DEBUG:
        with open(DEBUG_LOG_PATH, "a") as log:
            log.write(msg + "\n")


# Platform ticket-URL templates
TICKET_URLS = {
    "gitlab": lambda ticket: f"https://gitlab.com/{os.getenv('GITLAB_NAMESPACE', '<namespace>')}/{os.getenv('GITLAB_PROJECT', '<project>')}/-/issues/{extract_issue_num(ticket)}",
    "github": lambda ticket: f"https://github.com/{os.getenv('GITHUB_REPO', '<org>/<repo>')}/issues/{extract_issue_num(ticket)}",
    "azure": lambda ticket: f"https://dev.azure.com/{os.getenv('AZURE_ORG', '<org>')}/{os.getenv('AZURE_PROJECT', '<project>')}/_workitems/edit/{extract_issue_num(ticket)}",
}


def extract_issue_num(ticket_id: str) -> str:
    return ticket_id.split("-")[-1] if "-" in ticket_id else ticket_id.split("_")[-1]


def ticket_url(platform: str, ticket_id: str) -> str:
    if platform in TICKET_URLS and ticket_id:
        try:
            return TICKET_URLS[platform](ticket_id)
        except Exception as e:
            debug_log(f"Ticket URL generation failed: {e}")
            return None
    return None


# Het commit message bestand is het eerste argument
commit_msg_filepath = Path(sys.argv[1])

debug_log(f"prepare_commit_msg.py called with: {sys.argv}")

# Haal de branchnaam op via git
branch_name = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
debug_log(f"Branch name: {branch_name}")

# Regex voor ticketreferentie: bijv. ABC-123 of PROJECT_456
TICKET_REGEX = r"([A-Z][A-Z0-9]+[-_][0-9]+)"
match = re.search(TICKET_REGEX, branch_name)

debug_log(f"Ticket match: {match.group(1) if match else None}")

if not match:
    debug_log("No ticket found in branch name. Exiting.")
    sys.exit(0)  # Geen ticket in branchnaam, doe niets

ticket = match.group(1)

# Bepaal platform voor linkvervanging
platform = os.getenv("TICKET_PLATFORM", "none").lower()
url = ticket_url(platform, ticket)

# Lees het huidige commit message
with open(commit_msg_filepath, "r", encoding="utf-8") as f:
    content = f.read()
debug_log(f"Commit message before: {content}")

# Voeg ticket toe als die nog niet in het bericht staat
if ticket not in content:
    if url:
        ticket_md = f"[{ticket}]({url})"
        new_content = f"{ticket_md}: {content}"
        debug_log(f"Ticket link: {ticket_md}")
    else:
        new_content = f"{ticket}: {content}"
    with open(commit_msg_filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    debug_log(f"Commit message after: {new_content}")
else:
    debug_log("Ticket already present in commit message.")
