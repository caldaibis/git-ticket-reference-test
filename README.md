# Automatisering van Git Ticket Referenties

Deze repository biedt een set van `pre-commit` hooks om automatisch ticketreferenties (GitLab, GitHub, Azure DevOps) toe te voegen en te valideren in je Git commit-berichten.

## Installatie & Gebruik

1. Installeer `pre-commit`

Indien je dit nog niet hebt: `pip install pre-commit` of `pipx install pre-commit` of `uv tool install pre-commit`

2. Kies de methode die het beste bij je past: de snelle 'one-liner' of de handmatige installatie.

### 🚀 Quick Start (Aanbevolen voor macOS/Linux)

Voor de allersnelste installatie in een nieuw of bestaand project, voer je het volgende commando uit in de root van je repository:

```bash
curl -sSL https://raw.githubusercontent.com/caldaibis/git-ticket-reference-test/main/init.sh | bash
```

Dit script doet het volgende voor je:

   - Controleert of `pre-commit` geïnstalleerd is.
   - Voegt de laatste versie van de hooks toe aan `.pre-commit-config.yaml`.
   - Maakt een `.env` bestand aan op basis van het voorbeeld.
   - Voegt `.env` toe aan je .gitignore.
   - Activeert de hooks in Git.

Je enige taak hierna is het invullen van het `.env` bestand.

### ✋ Handmatige Installatie

Voor volledige controle of voor Windows-gebruikers die geen `bash` gebruiken.

1. Configureer `.pre-commit-config.yaml`

Voeg de volgende regels toe aan je `.pre-commit-config.yaml` bestand:

```yaml
# .pre-commit-config.yaml

repos:
-   repo: https://github.com/caldaibis/git-ticket-reference-test.git
    rev: v1.15.0  # Gebruik de laatste versie-tag (of doe `pre-commit autoupdate` in je CLI)
    hooks:
    -   id: prepare-commit-msg-ticket
    -   id: validate-commit-msg-ticket
```

2. Activeer de Hooks

```bash
pre-commit install --hook-type prepare-commit-msg --hook-type commit-msg
```

3. Configureer API-validatie

Maak handmatig een `.env` bestand aan (zie `.env.example` in deze repo voor een voorbeeld) en voeg `.env` toe aan je `.gitignore`.

## Updaten naar de nieuwste versie

Om de hooks bij te werken naar de laatste versie, voer je het volgende commando uit:

```bash
pre-commit autoupdate
```

Dit commando controleert de Git-repository's in je `.pre-commit-config.yaml` en werkt de `rev` automatisch bij naar de nieuwste tag.

## Hoe het Werkt

Na installatie zal bij elke git commit:

   - `prepare-commit-message`: de ticket-ID uit je branch-naam lezen en automatisch vooraan je commit-bericht plaatsen.
   - `commit-message`: valideren of je commit-bericht een geldige ticket-ID bevat en (indien geconfigureerd) of dit ticket daadwerkelijk bestaat op je gekozen platform.
