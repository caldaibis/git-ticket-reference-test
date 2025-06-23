#!/bin/bash

# ==============================================================================
#  Setup Script voor Automatische Git Ticket Referenties
#  Dit script configureert de pre-commit hooks in een doelrepository.
# ==============================================================================

# --- Configuratie (pas deze URL aan naar jouw repo) ---
REPO_URL="https://github.com/caldaibis/git-ticket-reference-test.git"
# --- Einde Configuratie ---

# Kleurcodes voor output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Setup voor Automatische Ticket Referenties ---${NC}"

# 1. Controleer of pre-commit geïnstalleerd is
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}FOUT: 'pre-commit' is niet geïnstalleerd.${NC}"
    echo "Installeer het eerst via: pip install pre-commit of pipx install pre-commit of uv tool install pre-commit"
    echo "Zie ook: https://pre-commit.com/#install"
    exit 1
fi

# 2. Haal de laatste versie-tag op van de remote repo
echo "Zoeken naar de laatste versie van de hooks..."
LATEST_TAG=$(git ls-remote --tags --sort="v:refname" "$REPO_URL" | tail -n1 | sed 's/.*\///')

if [ -z "$LATEST_TAG" ]; then
    echo -e "${YELLOW}FOUT: Kon geen versie-tag vinden in de remote repository.${NC}"
    echo "Zorg ervoor dat de repo '${REPO_URL}' minstens één versie-tag heeft (bv. v1.0.0)."
    exit 1
fi
echo "Gevonden versie: ${GREEN}$LATEST_TAG${NC}"

# 3. Configureer .pre-commit-config.yaml (maakt aan of voegt toe)
CONFIG_FILE=".pre-commit-config.yaml"
HOOK_CONFIG=$(cat <<EOF
# Configuratie voor automatische ticket referenties
  - repo: $REPO_URL
    rev: $LATEST_TAG
    hooks:
    -   id: prepare-commit-msg-ticket
    -   id: validate-commit-msg-ticket
EOF
)

if ! grep -q "$REPO_URL" "$CONFIG_FILE" 2>/dev/null; then
    echo "Toevoegen van hook-configuratie aan ${CONFIG_FILE}..."
    echo -e "\n$HOOK_CONFIG" >> "$CONFIG_FILE"
else
    echo "Hook-configuratie bestaat al in ${CONFIG_FILE}. Overslaan."
fi

# 4. Maak .env bestand aan van voorbeeld, indien het nog niet bestaat
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Downloaden van configuratievoorbeeld naar ${ENV_FILE}..."
    ENV_EXAMPLE_URL="https://raw.githubusercontent.com/$(echo $REPO_URL | sed 's/https:\/\///' | sed 's/.git//')/main/.env.example"
    curl -s -o "$ENV_FILE" "$ENV_EXAMPLE_URL"
    echo -e "${YELLOW}BELANGRIJK: Pas het aangemaakte '${ENV_FILE}' bestand aan met jouw tokens en instellingen!${NC}"
else
    echo "Bestand '${ENV_FILE}' bestaat al. Overslaan."
fi

# 5. Voeg .env toe aan .gitignore, indien nog niet aanwezig
GITIGNORE_FILE=".gitignore"
if ! grep -q "^\.env$" "$GITIGNORE_FILE" 2>/dev/null; then
    echo "Toevoegen van .env aan ${GITIGNORE_FILE}..."
    echo -e "\n# Lokale omgevingsvariabelen voor Git hooks\n.env" >> "$GITIGNORE_FILE"
fi

# 6. Installeer de Git hooks
echo "Installeren van de Git hooks..."
pre-commit install --hook-type prepare-commit-msg --hook-type commit-msg

echo -e "\n${GREEN}✔ Setup voltooid!${NC}"
echo "De hooks zijn nu actief in deze repository."