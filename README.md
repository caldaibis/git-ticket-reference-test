# Git Ticket Reference Automation

Deze repository automatiseert het toevoegen en valideren van ticketreferenties in Git commit messages voor GitLab, GitHub en Azure DevOps.

## Functionaliteit
- **prepare-commit-msg**: Voegt automatisch een ticketreferentie toe aan het commitbericht, op basis van de branchnaam (bijv. `feature/ABC-123-beschrijving`).
- **commit-msg**: Valideert of het commitbericht een geldige ticketreferentie bevat.

## Installatie
1. Installeer [pre-commit](https://pre-commit.com/):
   ```sh
   pip install pre-commit
   ```
2. Installeer de hooks:
   ```sh
   pre-commit install --hook-type prepare-commit-msg --hook-type commit-msg
   ```

## Configuratie
- De configuratie staat in `.pre-commit-config.yaml`.
- De scripts staan in de map `scripts/`.

## Optionele uitbreiding
- API-validatie van tickets is mogelijk door de scripts uit te breiden en tokens via omgevingsvariabelen aan te bieden. 