#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from .ticket_utils import debug_log, find_ticket_id, DEBUG_LOG_PATH


def get_branch_name() -> str:
    """Haalt de huidige Git branch-naam op."""
    try:
        return os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
    except Exception:
        return ""


def main():
    debug_log("--- prepare_commit_message.py ---")
    if len(sys.argv) < 2:
        sys.exit(0)  # Doe niets als er geen bestandsnaam is

    commit_msg_filepath = Path(sys.argv[1])
    branch_name = get_branch_name()
    debug_log(f"Branch name: {branch_name}")

    ticket_id = find_ticket_id(branch_name)
    if not ticket_id:
        debug_log("No ticket found in branch name. Exiting.")
        print(f"\033[93mGeen ticket ID gevonden in branchnaam. Zie het debug logbestand voor details: {DEBUG_LOG_PATH}\033[0m", file=sys.stderr)
        sys.exit(0)

    with open(commit_msg_filepath, "r+", encoding="utf-8") as f:
        content = f.read().strip()
        debug_log(f"Commit message before: '{content}'")

        # Voeg ticket toe als het bericht leeg is of nog geen ticket bevat
        if not find_ticket_id(content):
            new_content = f"{ticket_id}: {content}"
            f.seek(0, 0)
            f.write(new_content)
            f.truncate()
            debug_log(f"Commit message after: '{new_content}'")
        else:
            debug_log("Ticket already present in commit message.")


if __name__ == "__main__":
    main()
