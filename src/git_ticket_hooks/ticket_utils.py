import os
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from dotenv import load_dotenv

# --- CONFIGURATIE ---

# Bepaal de root van de Git-repository.
GIT_ROOT = Path(os.getcwd())

# Laad omgevingsvariabelen uit het .env-bestand in de root van de repository.
load_dotenv(dotenv_path=GIT_ROOT / '.env')

# URL naar het .env.example bestand voor documentatie.
ENV_EXAMPLE_URL = "https://github.com/caldaibis/git-ticket-reference-test/blob/main/.env.example"

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
    Retourneert het ID in een canoniek formaat, bijv. "[PROJ-123]" of "[#123]".
    """
    # Patroon 1: Canoniek formaat, bijv. [PROJ-123] of [#123]
    match = re.search(r"\[([A-Z]{2,10}-[0-9]+)\]", content, re.IGNORECASE)
    if match:
        ticket = match.group(1).upper().replace("_", "-")
        canoniek_formaat = f"[{ticket}]"
        debug_log(f"Gevonden canoniek ticket: {canoniek_formaat}")
        return canoniek_formaat

    match = re.search(r"\[#([0-9]+)\]", content)
    if match:
        ticket_num = match.group(1)
        canoniek_formaat = f"[#{ticket_num}]"
        debug_log(f"Gevonden platform ticket: {canoniek_formaat}")
        return canoniek_formaat

    # Patroon 2: Ruw formaat in branch-namen, bijv. PROJ-123- of 123-
    for pattern in get_ticket_regexes():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # Extract the most relevant part of the match
            ticket_part = next((g for g in match.groups() if g and (g.upper().startswith(tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) or g.isdigit())), None)
            if ticket_part:
                # Formatteer naar een canoniek formaat
                if '-' in ticket_part or '_' in ticket_part:
                    canoniek_formaat = f"[{ticket_part.upper().replace('_', '-')}]"
                else:
                    canoniek_formaat = f"[#{ticket_part}]"
                debug_log(f"Gevonden ruw ticket: {ticket_part}, geformatteerd naar {canoniek_formaat}")
                return canoniek_formaat

    debug_log(f"Geen ticket ID gevonden in: '{content[:70]}...'")
    return None


def extract_issue_num(ticket_id: str) -> str:
    """Extraheert het numerieke gedeelte uit een ticket-ID."""
    clean_id = ticket_id.strip("[]#")
    # Werkt voor "PROJ-123" en "123"
    return clean_id.split("-")[-1] if "-" in clean_id else clean_id


# --- VALIDATIEKLASSEN ---
class TicketValidator(ABC):
    @abstractmethod
    def ticket_exists(self, ticket_id: str) -> bool:
        pass

    def warn_and_skip(self, message: str) -> bool:
        """Print een waarschuwing en slaat de validatie over."""
        print(f"\033[93m[Waarschuwing] {message}\033[0m", file=sys.stderr)
        debug_log(f"WARN: {message}")
        return True  # True betekent "validatie geslaagd" omdat we het overslaan

    def api_get(self, url: str, headers: dict) -> bool:
        debug_log(f"API GET: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            debug_log(f"API RESPONSE: {resp.status_code} {resp.text[:200]}")
            return resp.status_code == 200
        except requests.RequestException as e:
            print(f"\033[91mFOUT: API-aanroep mislukt: {e}\033[0m", file=sys.stderr)
            debug_log(f"ERROR: API-aanroep mislukt: {e}")
            return False


class GitLabValidator(TicketValidator):
    def __init__(self):
        self.token = os.getenv("GITLAB_TOKEN")
        self.project_id = os.getenv("GITLAB_PROJECT_ID")

    def ticket_exists(self, ticket_id: str) -> bool:
        if not self.token or not self.project_id:
            return self.warn_and_skip("GitLab validatie overgeslagen: GITLAB_TOKEN of GITLAB_PROJECT_ID ontbreekt in .env")
        url = f"https://gitlab.com/api/v4/projects/{self.project_id}/issues/{extract_issue_num(ticket_id)}"
        return self.api_get(url, {"PRIVATE-TOKEN": self.token})


class GitHubValidator(TicketValidator):
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPO")

    def ticket_exists(self, ticket_id: str) -> bool:
        if not self.token or not self.repo:
            return self.warn_and_skip("GitHub validatie overgeslagen: GITHUB_TOKEN of GITHUB_REPO ontbreekt in .env")
        url = f"https://api.github.com/repos/{self.repo}/issues/{extract_issue_num(ticket_id)}"
        return self.api_get(url, {"Authorization": f"token {self.token}"})


class AzureValidator(TicketValidator):
    def __init__(self):
        self.token = os.getenv("AZURE_TOKEN")
        self.org = os.getenv("AZURE_ORG")
        self.project = os.getenv("AZURE_PROJECT")

    def ticket_exists(self, ticket_id: str) -> bool:
        if not self.token or not self.org or not self.project:
            return self.warn_and_skip("Azure validatie overgeslagen: AZURE_TOKEN, AZURE_ORG of AZURE_PROJECT ontbreekt in .env")
        url = f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workitems/{extract_issue_num(ticket_id)}?api-version=6.0"
        return self.api_get(url, {"Authorization": f"Basic {self.token}"})


class NoopValidator(TicketValidator):
    def ticket_exists(self, ticket_id: str) -> bool:
        return True


def get_validator(platform: str) -> TicketValidator:
    """Factory functie die de juiste validator retourneert op basis van het platform."""
    validators = {
        "gitlab": GitLabValidator,
        "github": GitHubValidator,
        "azure": AzureValidator,
    }
    return validators.get(platform, NoopValidator)()