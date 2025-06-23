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
        sys.exit(0)  # Geen actie vereist als er geen bestandsnaam is.

    commit_msg_filepath = Path(sys.argv[1])
    branch_name = get_branch_name()
    debug_log(f"Branch-naam: {branch_name}")

    ticket_id = find_ticket_id(branch_name)
    if not ticket_id:
        debug_log("Geen ticket ID gevonden in branch-naam. Script wordt afgesloten.")
        print(f"\033[93mInfo: Geen ticket ID gevonden in branch-naam. Zie {DEBUG_LOG_PATH} voor details.\033[0m", file=sys.stderr)
        sys.exit(0)

    with open(commit_msg_filepath, "r+", encoding="utf-8") as f:
        content = f.read().strip()
        debug_log(f"Oorspronkelijk commit-bericht: '{content}'")

        # Voeg ticket toe als het bericht nog geen ticket-ID bevat.
        if not find_ticket_id(content):
            new_content = f"{ticket_id}: {content}"
            f.seek(0, 0)
            f.write(new_content)
            f.truncate()
            debug_log(f"Aangepast commit-bericht: '{new_content}'")
        else:
            debug_log("Commit-bericht bevat al een ticket-ID.")


if __name__ == "__main__":
    main()
