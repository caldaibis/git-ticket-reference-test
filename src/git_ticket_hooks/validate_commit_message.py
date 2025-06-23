#!/usr/bin/env python3
import os
import sys

from .ticket_utils import (
    debug_log,
    find_ticket_id,
    get_validator,
    EXAMPLE_BRANCH,
    EXAMPLE_COMMIT,
    ENV_EXAMPLE_URL,
    DEBUG_LOG_PATH,
)


def print_error(message: str, show_examples: bool = False):
    """Print een rode foutmelding naar de console en verwijs naar het logbestand."""
    print(f"\033[91mFOUT: {message}\033[0m", file=sys.stderr)
    print(f"\033[93mZie het debug-logbestand voor details: {DEBUG_LOG_PATH}\033[0m", file=sys.stderr)
    if show_examples:
        print(
            f"\033[93m> Voorbeeld branch-naam: {EXAMPLE_BRANCH}\033[0m", file=sys.stderr
        )
        print(
            f"\033[93m> Voorbeeld commit message: {EXAMPLE_COMMIT}\033[0m",
            file=sys.stderr,
        )


def main():
    debug_log("--- validate_commit_message.py ---")
    if len(sys.argv) < 2:
        sys.exit(1)

    commit_msg_filepath = sys.argv[1]
    with open(commit_msg_filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    debug_log(f"Commit message content: '{content}'")

    ticket_id = find_ticket_id(content)
    if not ticket_id:
        print_error(
            "Commit message mist een geldige ticketreferentie.", show_examples=True
        )
        debug_log("Validation FAILED: No ticket ID found.")
        sys.exit(1)

    # --- FEEDBACK LOGIC ---
    platform = os.getenv("TICKET_PLATFORM", "").lower()
    if not platform:
        print(
            "\033[93m[Waarschuwing] Ticket-validatie is overgeslagen omdat 'TICKET_PLATFORM' niet is ingesteld.\033[0m",
            file=sys.stderr,
        )
        print(
            "\033[93mHoewel niet verplicht, wordt dit aanbevolen om de juistheid van ticketreferenties te garanderen.\033[0m",
            file=sys.stderr,
        )
        print(
            f"\033[93mRaadpleeg de documentatie of het .env.example voor configuratie: {ENV_EXAMPLE_URL}\033[0m",
            file=sys.stderr,
        )
        debug_log("Validation SKIPPED: TICKET_PLATFORM not set.")
        sys.exit(0)  # Stop succesvol, want validatie is niet verplicht

    debug_log(f"Platform: {platform}, Ticket ID: {ticket_id}")
    validator = get_validator(platform)
    if not validator.ticket_exists(ticket_id):
        print_error(
            f"Ticket {ticket_id} bestaat niet of kon niet worden geverifieerd op {platform}."
        )
        debug_log(f"Validation FAILED: Ticket {ticket_id} not found on {platform}.")
        sys.exit(1)

    debug_log("Validation SUCCEEDED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
