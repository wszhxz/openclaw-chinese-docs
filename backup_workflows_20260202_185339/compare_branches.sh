#!/bin/bash

# Script to compare original-en and main branches to identify files needing translation
# This implements the change detection part of our sync workflow

set -e

echo "Comparing original-en and main branches to identify changes..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Change to the repository directory
cd /tmp/openclaw-docs-check

# Store current branch to restore later
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Switch to main branch
git checkout main

# Get the list of files that differ between the two branches
echo "Checking for differences between original-en and main branches..."
# Look for all markdown files in the docs directory and subdirectories
DIFF_OUTPUT=$(git diff --name-only original-en -- "docs/**/*.md" "docs/*.md")

if [ -z "$DIFF_OUTPUT" ]; then
    echo "No differences found - all files are up to date."
    echo "TRANSLATION_STATUS=up-to-date" > /tmp/translation_status.txt
else
    echo "Found changed/new files:"
    echo "$DIFF_OUTPUT"
    
    # Write the list of files to translate to a temporary file
    echo "$DIFF_OUTPUT" > /tmp/files_to_translate.txt
    
    # Count the number of files that need translation
    COUNT=$(echo "$DIFF_OUTPUT" | grep -c '^' || echo 0)
    # Remove any trailing whitespace
    COUNT=$(echo "$COUNT" | tr -d ' ')
    echo "NUMBER_OF_FILES=$COUNT" > /tmp/translation_status.txt
    echo "FILES_TO_TRANSLATE=/tmp/files_to_translate.txt" >> /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    
    echo "$COUNT files need translation or updating."
fi

# Restore the original branch
git checkout "$CURRENT_BRANCH"

echo "Comparison completed."