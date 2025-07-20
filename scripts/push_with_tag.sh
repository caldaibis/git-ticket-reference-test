#!/usr/bin/env bash
# filepath: /home/caldaibis/repos/git-ticket-reference-test/scripts/push_with_tag.sh
set -euo pipefail

# Read current version from pyproject.toml
current_version=$(grep -E '^version\s*=' pyproject.toml | sed -E 's/version\s*=\s*["'"'"']([^'"'"'"]*)["'"'"']/\1/')

# Increment patch version
IFS='.' read -r major minor patch <<< "$current_version"
new_version="${major}.${minor}.$((patch + 1))"

# Update pyproject.toml with new version
sed -i "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml

# Create and push tag
git add pyproject.toml
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Bump version to $new_version"
git tag -a "$new_version" -m "Release $new_version"
git push origin "$new_version"
git push

echo "Successfully bumped version to $new_version, created tag, and pushed"