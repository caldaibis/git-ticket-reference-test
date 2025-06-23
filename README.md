# Git Ticket Reference Automation

Deze repository automatiseert het toevoegen en valideren van ticketreferenties in Git commit messages voor GitLab, GitHub en Azure DevOps.

## Functionaliteit
- **prepare-commit-msg**: Voegt automatisch een ticketreferentie toe aan het commitbericht, op basis van de branchnaam (bijv. `feature/ABC-123-beschrijving`).
- **commit-msg**: Valideert of het commitbericht een geldige ticketreferentie bevat.

## Integratie in jouw project

Om deze automatische ticket-referenties in jouw repository te gebruiken, volg je deze stappen. Dit hoef je maar één keer per repository te doen.

1. Installeer [pre-commit](https://pre-commit.com/)

Indien je dit nog niet hebt:

```bash
   # Met pipx
   pipx install pre-commit

   # Met uv
   uv tool install pre-commit
   ```

2. Configureer .pre-commit-config.yaml

Maak een .pre-commit-config.yaml-bestand aan in de root van je project (of voeg dit toe aan je bestaande bestand). Voeg de volgende configuratie toe:


```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/caldaibis/git-ticket-reference-test.git
    rev: v1.0.0  # Gebruik de laatste versie-tag
    hooks:
    -   id: prepare-commit-msg-ticket
    -   id: validate-commit-msg-ticket
```

3. Activeer de Hooks

Voer het volgende commando uit in je project-repository. Dit koppelt de hooks aan je lokale Git-configuratie.

```bash
pre-commit install --hook-type prepare-commit-msg --hook-type commit-msg
```

4. (Optioneel) Configureer API-validatie

Voor validatie tegen GitLab, GitHub of Azure DevOps:

   1. Download het `.env.example`-bestand van de automation repository.
   2. Hernoem het naar `.env` en plaats het in de root van jouw project.
   3. Vul de vereiste variabelen in (zie `.env.example` voor details).

Dat is alles! De hooks worden nu automatisch uitgevoerd bij elke `git commit`.

**Let op:**
- Voor Azure DevOps moet de Personal Access Token base64-gecodeerd zijn: `echo -n ":<PAT>" | base64`
- Als de benodigde variabelen ontbreken, wordt alleen gewaarschuwd en niet geblokkeerd.

### Makkelijk updaten

Als je de nieuwste versie van deze hooks wil hebben, kun je in jouw project simpelweg `pre-commit autoupdate` draaien. pre-commit ziet de nieuwe tag en werkt de rev in hun configuratie automatisch bij.

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
