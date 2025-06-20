#!/usr/bin/env python3
import os
import re
import sys

# Het commit message bestand is het eerste argument
commit_msg_filepath = sys.argv[1]

# Haal de branchnaam op via git
branch_name = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()

# Regex voor ticketreferentie: bijv. ABC-123 of PROJECT_456
TICKET_REGEX = r"([A-Z][A-Z0-9]+[-_][0-9]+)"
match = re.search(TICKET_REGEX, branch_name)

if not match:
    sys.exit(0)  # Geen ticket in branchnaam, doe niets

ticket = match.group(1)

# Lees het huidige commit message
with open(commit_msg_filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Voeg ticket toe als die nog niet in het bericht staat
if ticket not in content:
    new_content = f"{ticket}: {content}"
    with open(commit_msg_filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
