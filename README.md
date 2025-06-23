# Git Ticket Reference Automation

Deze repository automatiseert het toevoegen en valideren van ticketreferenties in Git commit messages voor GitLab, GitHub en Azure DevOps.

## Functionaliteit
- **prepare-commit-msg**: Voegt automatisch een ticketreferentie toe aan het commitbericht, op basis van de branchnaam (bijv. `feature/ABC-123-beschrijving`).
- **commit-msg**: Valideert of het commitbericht een geldige ticketreferentie bevat.

## Installatie
1. Installeer [pre-commit](https://pre-commit.com/):
   ```bash
   # Met pipx
   pipx install pre-commit

   # Met uv
   uv tool install pre-commit
   ```
2. Installeer de hooks:
   ```bash
   pre-commit install --hook-type prepare-commit-msg --hook-type commit-msg
   ```

## Configuratie
- De configuratie staat in `.pre-commit-config.yaml`.
- De scripts staan in de map `scripts/`.

## Optionele uitbreiding
- API-validatie van tickets is mogelijk door de scripts uit te breiden en tokens via omgevingsvariabelen aan te bieden. 

## API-validatie van tickets

Wil je dat commit messages alleen geaccepteerd worden als het ticket-ID daadwerkelijk bestaat op GitLab, GitHub of Azure DevOps? Zet dan de juiste variabelen in een `.env`-bestand. Zie `.env.example` voor een voorbeeld.

1. Kopieer het voorbeeldbestand:
   ```sh
   cp .env.example .env
   ```
2. Vul de juiste waarden in voor jouw platform en project.
3. De benodigde variabelen worden automatisch geladen uit `.env` door de hook scripts (via python-dotenv).
4. Zet de variabele `TICKET_PLATFORM` op `gitlab`, `github` of `azure`.

**Let op:**
- Voor Azure DevOps moet de Personal Access Token base64-gecodeerd zijn: `echo -n ":<PAT>" | base64`
- Als de benodigde variabelen ontbreken, wordt alleen gewaarschuwd en niet geblokkeerd.

## Debugging & Logging

Wil je precies zien wat de hooks doen? Zet dan de debug-modus aan:

1. Zet in je `.env` of shell:
   ```sh
   DEBUG_TICKET_HOOK=1
   ```
2. Doe een commit. De hooks loggen nu alle relevante stappen naar:
   ```
   .git/ticket_hook_debug.log
   ```
3. Bekijk dit bestand voor uitgebreide debug-informatie over branch, commit message, matches, API-calls, etc.

Zet de variabele uit (`DEBUG_TICKET_HOOK=0` of verwijder uit `.env`) om logging uit te schakelen. 
