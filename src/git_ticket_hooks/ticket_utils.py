import os
import re
from pathlib import Path

from dotenv import load_dotenv

# --- CONFIGURATIE ---

# Bepaal de root van de Git-repository.
GIT_ROOT = Path(os.getcwd())

# Laad omgevingsvariabelen uit het .env-bestand in de root van de repository.
load_dotenv(dotenv_path=GIT_ROOT / ".env")

# Pad naar het debug-logbestand.
DEBUG_LOG_PATH = GIT_ROOT / ".git" / "ticket_hook_debug.log"

# Standaard reguliere expressies voor het herkennen van ticket ID's.
# 1. Traditioneel formaat: PROJ-123
# 2. Platform-specifiek formaat: #123, feature/123-, 123_
DEFAULT_TICKET_REGEXES = [
    r"([A-Z]{2,10}-[0-9]+)",
    r"(^|/|#)([0-9]+)([-_])",
]

# Voorbeelden voor gebruikers.
EXAMPLE_BRANCH = "feature/PROJ-123-nieuwe-functionaliteit of feature/123-iets-anders"
EXAMPLE_COMMIT = "[PROJ-123]: beschrijving of [#123]: beschrijving"


# --- HULPFUNCTIES ---


def debug_log(msg: str):
    """Schrijft een debug-bericht naar het logbestand."""
    with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as log:
        log.write(msg + "\n")


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
    # Patroon 1: Prioriteit voor canonieke formaten, typisch in commit-berichten.
    # Deze zijn expliciet en moeten voorrang krijgen.
    # Voorbeeld: [PROJ-123]
    match = re.search(r"\[([A-Z]{2,10}-[0-9]+)\]", content, re.IGNORECASE)
    if match:
        ticket = match.group(1).upper().replace("_", "-")
        canoniek_formaat = f"[{ticket}]"
        debug_log(f"Gevonden canoniek ticket (traditioneel): {canoniek_formaat}")
        return canoniek_formaat

    # Voorbeeld: [#123]
    match = re.search(r"\[#([0-9]+)\]", content)
    if match:
        ticket_num = match.group(1)
        canoniek_formaat = f"[#{ticket_num}]"
        debug_log(f"Gevonden canoniek ticket (platform): {canoniek_formaat}")
        return canoniek_formaat

    # Patroon 2: Zoek naar ruwe formaten, typisch in branch-namen.
    # Deze zijn minder expliciet en dienen als fallback.

    # Zoek eerst naar het traditionele formaat (bv. PROJ-123), dit is specifieker.
    match = re.search(r"([A-Z]{2,10}-[0-9]+)", content, re.IGNORECASE)
    if match:
        ticket = match.group(1).upper().replace("_", "-")
        canoniek_formaat = f"[{ticket}]"
        debug_log(
            f"Gevonden ruw ticket (traditioneel): {ticket}, geformatteerd naar {canoniek_formaat}"
        )
        return canoniek_formaat

    # Zoek als laatste naar platform-specifieke nummers (bv. /123-).
    match = re.search(r"(?:^|/|#)([0-9]+)(?:[-_])", content)
    if match:
        ticket_num = match.group(1)
        canoniek_formaat = f"[#{ticket_num}]"
        debug_log(
            f"Gevonden ruw ticket (platform): {ticket_num}, geformatteerd naar {canoniek_formaat}"
        )
        return canoniek_formaat

    debug_log(f"Geen ticket ID gevonden in: '{content[:70]}...'")
    return None


def extract_issue_num(ticket_id: str) -> str:
    """Extraheert het numerieke gedeelte uit een ticket-ID."""
    clean_id = ticket_id.strip("[]#")
    # Werkt voor "PROJ-123" en "123"
    return clean_id.split("-")[-1] if "-" in clean_id else clean_id
