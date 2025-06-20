#!/usr/bin/env python3
import os
import re
import sys
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv

# Laad .env automatisch
load_dotenv()

# Debug logging setup
DEBUG = os.getenv("DEBUG_TICKET_HOOK") == "1"
DEBUG_LOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", ".git", "ticket_hook_debug.log"
)


def debug_log(msg):
    if DEBUG:
        with open(DEBUG_LOG_PATH, "a") as log:
            log.write(msg + "\n")


# Ticket regex configuratie
DEFAULT_TICKET_REGEXES = [
    r"[A-Z][A-Z0-9]+[-_][0-9]+",  # Standaard: PROJECT_123 of PROJECT-123
    r"[A-Z]+-[0-9]+",  # JIRA: PROJ-123
]

EXAMPLE_BRANCH = "feature/PROJ-123-omschrijving"
EXAMPLE_COMMIT = "PROJ-123: beschrijving van de wijziging"

# Platform ticket-URL templates
TICKET_URLS = {
    "gitlab": lambda ticket: f"https://gitlab.com/{os.getenv('GITLAB_NAMESPACE', '<namespace>')}/{os.getenv('GITLAB_PROJECT', '<project>')}/-/issues/{TicketValidator.extract_issue_num(ticket)}",
    "github": lambda ticket: f"https://github.com/{os.getenv('GITHUB_REPO', '<org>/<repo>')}/issues/{TicketValidator.extract_issue_num(ticket)}",
    "azure": lambda ticket: f"https://dev.azure.com/{os.getenv('AZURE_ORG', '<org>')}/{os.getenv('AZURE_PROJECT', '<project>')}/_workitems/edit/{TicketValidator.extract_issue_num(ticket)}",
}


def get_ticket_regexes():
    env_regex = os.getenv("TICKET_REGEX")
    if env_regex:
        return [r.strip() for r in env_regex.split(",") if r.strip()]
    return DEFAULT_TICKET_REGEXES


TICKET_REGEXES = get_ticket_regexes()


class TicketValidator(ABC):
    @abstractmethod
    def ticket_exists(self, ticket_id: str) -> bool:
        pass

    @staticmethod
    def extract_issue_num(ticket_id: str) -> str:
        return (
            ticket_id.split("-")[-1] if "-" in ticket_id else ticket_id.split("_")[-1]
        )

    def warn_and_skip(self, message: str) -> bool:
        print(f"\033[93m[Waarschuwing] {message}\033[0m", file=sys.stderr)
        debug_log(f"WARN: {message}")
        return True  # Sla validatie over als niet geconfigureerd

    def api_get(self, url: str, headers: dict) -> bool:
        debug_log(f"API GET: {url} HEADERS: {headers}")
        try:
            resp = requests.get(url, headers=headers)
            debug_log(f"API RESPONSE: {resp.status_code} {resp.text[:200]}")
            return resp.status_code == 200
        except Exception as e:
            print(f"\033[91mFOUT: API-aanroep mislukt: {e}\033[0m", file=sys.stderr)
            debug_log(f"ERROR: API-aanroep mislukt: {e}")
            return False


class GitLabValidator(TicketValidator):
    def __init__(self):
        self.token = os.getenv("GITLAB_TOKEN")
        self.project_id = os.getenv("GITLAB_PROJECT_ID")

    def ticket_exists(self, ticket_id: str) -> bool:
        if not self.token or not self.project_id:
            return self.warn_and_skip(
                "GitLab API-validatie overgeslagen: GITLAB_TOKEN of GITLAB_PROJECT_ID ontbreekt."
            )
        issue_num = self.extract_issue_num(ticket_id)
        url = f"https://gitlab.com/api/v4/projects/{self.project_id}/issues/{issue_num}"
        headers = {"PRIVATE-TOKEN": self.token}
        return self.api_get(url, headers)


class GitHubValidator(TicketValidator):
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPO")

    def ticket_exists(self, ticket_id: str) -> bool:
        if not self.token or not self.repo:
            return self.warn_and_skip(
                "GitHub API-validatie overgeslagen: GITHUB_TOKEN of GITHUB_REPO ontbreekt."
            )
        issue_num = self.extract_issue_num(ticket_id)
        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_num}"
        headers = {"Authorization": f"token {self.token}"}
        return self.api_get(url, headers)


class AzureValidator(TicketValidator):
    def __init__(self):
        self.token = os.getenv("AZURE_TOKEN")
        self.org = os.getenv("AZURE_ORG")
        self.project = os.getenv("AZURE_PROJECT")

    def ticket_exists(self, ticket_id: str) -> bool:
        if not self.token or not self.org or not self.project:
            return self.warn_and_skip(
                "Azure API-validatie overgeslagen: AZURE_TOKEN, AZURE_ORG of AZURE_PROJECT ontbreekt."
            )
        work_item_id = self.extract_issue_num(ticket_id)
        url = f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
        headers = {"Authorization": f"Basic {self.token}"}
        return self.api_get(url, headers)


class NoopValidator(TicketValidator):
    def ticket_exists(self, ticket_id: str) -> bool:
        return True


def get_validator(platform: str) -> TicketValidator:
    if platform == "gitlab":
        return GitLabValidator()
    elif platform == "github":
        return GitHubValidator()
    elif platform == "azure":
        return AzureValidator()
    else:
        return NoopValidator()


def find_ticket_id(content: str):
    for regex in TICKET_REGEXES:
        match = re.search(regex, content)
        if match:
            debug_log(f"Matched ticket: {match.group(0)} with regex: {regex}")
            return match.group(0)
    debug_log("No ticket matched.")
    return None


def ticket_url(platform: str, ticket_id: str) -> str:
    if platform in TICKET_URLS and ticket_id:
        try:
            return TICKET_URLS[platform](ticket_id)
        except Exception as e:
            debug_log(f"Ticket URL generation failed: {e}")
            return None
    return None


def main():
    debug_log(f"ARGV: {sys.argv}")
    if len(sys.argv) < 2:
        print(
            "\033[91mFOUT: commit message bestand niet opgegeven.\033[0m",
            file=sys.stderr,
        )
        debug_log("FOUT: commit message bestand niet opgegeven.")
        sys.exit(1)

    commit_msg_filepath = sys.argv[1]
    with open(commit_msg_filepath, "r", encoding="utf-8") as f:
        content = f.read()
    debug_log(f"Commit message content: {content}")

    ticket_id = find_ticket_id(content)
    platform = os.getenv("TICKET_PLATFORM", "none").lower()
    debug_log(f"Platform: {platform}, Ticket ID: {ticket_id}")

    if not ticket_id:
        print(
            "\033[91mFOUT: Commit message mist een geldige ticketreferentie.\033[0m",
            file=sys.stderr,
        )
        print(f"\033[93mVoorbeeld branchnaam: {EXAMPLE_BRANCH}\033[0m", file=sys.stderr)
        print(
            f"\033[93mVoorbeeld commit message: {EXAMPLE_COMMIT}\033[0m",
            file=sys.stderr,
        )
        debug_log("FOUT: Geen geldige ticketreferentie gevonden.")
        sys.exit(1)

    validator = get_validator(platform)
    if not validator.ticket_exists(ticket_id):
        print(
            f"\033[91mFOUT: Ticket {ticket_id} bestaat niet op {platform}.",
            file=sys.stderr,
        )
        url = ticket_url(platform, ticket_id)
        if url:
            print(
                f"\033[93mBekijk of het ticket bestaat: {url}\033[0m", file=sys.stderr
            )
        debug_log(f"FOUT: Ticket {ticket_id} bestaat niet op {platform}.")
        sys.exit(1)
    debug_log("Ticket validatie geslaagd.")
    sys.exit(0)


if __name__ == "__main__":
    main()
