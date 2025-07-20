# Automatisering van Git Ticket Referenties

Deze repository biedt een `pre-commit` hook om automatisch ticketreferenties toe te voegen aan je Git commit-berichten op basis van je branch-naam.

## 🚀 Quick Start

1. Installeer `pre-commit`

Indien je dit nog niet hebt: `pip install pre-commit` of `pipx install pre-commit` of `uv tool install pre-commit`

2. Creëer en Configureer `.pre-commit-config.yaml`

Voeg de volgende regels toe aan je `.pre-commit-config.yaml` bestand:

```yaml
# .pre-commit-config.yaml

repos:
-   repo: https://github.com/caldaibis/git-ticket-reference-test.git
    rev: v1.21.0  # Mogelijk is dit niet de nieuwste versie tag! Zie hieronder om automatisch up te daten naar de nieuwste.
    hooks:
    -   id: prepare-commit-msg-ticket
```

2. Activeer de Hook

```bash
pre-commit install --hook-type prepare-commit-msg
```

3. Updaten naar de nieuwste versie

Om de hook bij te werken naar de laatste versie, voer je het volgende commando uit:

```bash
pre-commit autoupdate
```

Dit commando controleert de Git-repository's in je `.pre-commit-config.yaml` en werkt de `rev` automatisch bij naar de nieuwste tag.

## Hoe het Werkt

Na installatie zal bij elke git commit de ticket-ID uit je branch-naam gelezen worden en automatisch vooraan je commit-bericht plaatsen.
