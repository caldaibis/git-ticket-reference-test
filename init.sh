#!/bin/bash

# ==============================================================================
#  Setup Script voor Automatische Git Ticket Referenties
#  Dit script configureert de pre-commit hooks in een doelrepository.
# ==============================================================================

# --- Configuratie ---
REPO_URL="https://github.com/caldaibis/git-ticket-reference-test.git"
ENV_EXAMPLE_RAW_URL="https://raw.githubusercontent.com/caldaibis/git-ticket-reference-test/main/.env.example"
# --- Einde Configuratie ---

# Kleurcodes voor output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Setup voor Automatische Ticket Referenties ---${NC}"

# 1. Controleer of pre-commit geïnstalleerd is
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}FOUT: 'pre-commit' is niet geïnstalleerd.${NC}"
    echo "Installeer het eerst via: pip install pre-commit"
    exit 1
fi

# 2. Haal de laatste versie-tag op van de remote repo
echo "Zoeken naar de laatste versie van de hooks..."
LATEST_TAG=$(git ls-remote --tags --sort="v:refname" "$REPO_URL" | tail -n1 | sed 's/.*\///')

if [ -z "$LATEST_TAG" ]; then
    echo -e "${YELLOW}FOUT: Kon geen versie-tag vinden in de remote repository.${NC}"
    exit 1
fi
echo "Gevonden versie: ${GREEN}$LATEST_TAG${NC}"

# 3. Configureer .pre-commit-config.yaml
CONFIG_FILE=".pre-commit-config.yaml"
HOOK_BLOCK=$(cat <<EOF
-   repo: $REPO_URL
    rev: $LATEST_TAG
    hooks:
    -   id: prepare-commit-msg-ticket
    -   id: validate-commit-msg-ticket
EOF
)

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Bestand ${CONFIG_FILE} niet gevonden. Aanmaken..."
    echo "# pre-commit configuratie" > "$CONFIG_FILE"
    echo "repos:" >> "$CONFIG_FILE"
    echo "$HOOK_BLOCK" >> "$CONFIG_FILE"
else
    if ! grep -q "$REPO_URL" "$CONFIG_FILE"; then
        echo "Toevoegen van hook-configuratie aan bestaande ${CONFIG_FILE}..."
        echo "" >> "$CONFIG_FILE"
        echo "$HOOK_BLOCK" >> "$CONFIG_FILE"
    else
        echo "Hook-configuratie voor ${REPO_URL} bestaat al. Overslaan."
    fi
fi

# 4. Maak .env bestand aan van voorbeeld, indien het nog niet bestaat
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Downloaden van configuratievoorbeeld naar ${ENV_FILE}..."
    curl -s -o "$ENV_FILE" "$ENV_EXAMPLE_RAW_URL"
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

# --- SUCCESMELDING ---
echo -e "\n${GREEN}✔ Setup voltooid! De hooks zijn nu actief.${NC}"
echo "-------------------------------------------------------------------"
echo -e "${YELLOW}** ACTIE VEREIST: Configureer API-validatie **${NC}"
echo "Om te controleren of tickets echt bestaan, moet je het aangemaakte"
echo -e "'.env' bestand invullen met de juiste waarden voor jouw platform."
echo "Zonder deze configuratie wordt het bestaan van tickets NIET gevalideerd."
echo "-------------------------------------------------------------------"