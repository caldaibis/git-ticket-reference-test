#!/usr/bin/env python3
import re
import sys

commit_msg_filepath = sys.argv[1]

TICKET_REGEX = r"([A-Z][A-Z0-9]+[-_][0-9]+)"

with open(commit_msg_filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(TICKET_REGEX, content)

if not match:
    print(
        "\033[91mFOUT: Commit message mist een geldige ticketreferentie (bijv. ABC-123 of PROJECT_456).\033[0m",
        file=sys.stderr,
    )
    sys.exit(1)

# Optioneel: hier kan API-validatie van het ticketnummer worden toegevoegd
# Bijvoorbeeld: check_ticket_exists(match.group(1))

sys.exit(0)
