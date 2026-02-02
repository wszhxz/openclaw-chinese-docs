#!/bin/bash

# Master orchestration script for OpenClaw Chinese Docs project
# Implements the complete three-stage workflow: Sync -> Translate -> Build

set -e

echo "==========================================="
echo "OpenClaw Chinese Docs - Master Workflow"
echo "Implementing the three-stage process:"
echo "1. Sync (Dual-branch management)"
echo "2. Translate (Distributed by directory)"
echo "3. Build (Full site rebuild)"
echo "==========================================="

START_TIME=$(date)

echo "Stage 1: Sync - Updating from upstream repository"
echo "------------------------------------------------"
/tmp/sync_dual_branch.sh

echo ""
echo "Stage 2: Detect Changes - Identifying files for translation"
echo "----------------------------------------------------------"
/tmp/compare_branches.sh

echo ""
echo "Stage 3: Monitor Structure - Checking for directory changes"
echo "----------------------------------------------------------"
/tmp/monitor_structure.sh

echo ""
echo "Stage 4: Distributed Translation - Processing by directory"
echo "----------------------------------------------------------"
TRANSLATION_STATUS="up-to-date"
source /tmp/translation_status.txt

if [ "$TRANSLATION_STATUS" = "needed" ]; then
    echo "Translation required for $(grep NUMBER_OF_FILES /tmp/translation_status.txt | cut -d'=' -f2) files"
    /tmp/distributed_translation.sh
else
    echo "No translation needed at this time"
fi

echo ""
echo "Stage 5: Build Preparation - Preparing for site build"
echo "-----------------------------------------------------"
# In a real scenario, this would trigger the actual build process
# For now, we'll just simulate it
echo "Simulating build preparation..."

# Read directory structure changes without sourcing the file
if [ -f /tmp/dir_structure_change.txt ]; then
    NEW_DIRS_DETECTED=$(grep NEW_DIRS_DETECTED /tmp/dir_structure_change.txt | cut -d'=' -f2)
    REMOVED_DIRS_DETECTED=$(grep REMOVED_DIRS_DETECTED /tmp/dir_structure_change.txt | cut -d'=' -f2)
    
    if [ "$NEW_DIRS_DETECTED" = "1" ]; then
        NEW_DIRS=$(sed -n '/^NEW_DIRS=$/,/^REMOVED_DIRS_DETECTED=/p' /tmp/dir_structure_change.txt | head -n -1 | sed '1d' | sed '/^$/d')
        echo "WARNING: New directories detected - translation workflows may need adjustment"
        echo "New directories:"
        echo "$NEW_DIRS"
    fi
    if [ "$REMOVED_DIRS_DETECTED" = "1" ]; then
        REMOVED_DIRS=$(sed -n '/^REMOVED_DIRS=$/,/^$/p' /tmp/dir_structure_change.txt | head -n -1 | sed '1d' | sed '/^$/d')
        echo "INFO: Directories removed:"
        echo "$REMOVED_DIRS"
    fi
fi

echo ""
echo "==========================================="
echo "Master Workflow Completed"
echo "Started: $START_TIME"
echo "Ended: $(date)"
echo ""
echo "Workflow Summary:"
echo "- Sync: Complete (dual-branch management)"
echo "- Change Detection: Complete"
echo "- Structure Monitoring: Complete"
echo "- Translation: $(if [ "$TRANSLATION_STATUS" = "needed" ]; then echo "Processed"; else echo "Not required"; fi)"
echo "- Build: Ready for execution"
echo ""
echo "Next Steps:"
if [ "$TRANSLATION_STATUS" = "needed" ]; then
    echo "- Translation work completed for $(grep NUMBER_OF_FILES /tmp/translation_status.txt | cut -d'=' -f2) files"
    echo "- Ready for build process"
fi
if [ -f /tmp/dir_structure_change.txt ]; then
    if [ "$NEW_DIRS_DETECTED" = "1" ]; then
        echo "- Directory structure changes detected - consider adjusting translation workflows"
    fi
fi
echo "- Push changes to trigger GitHub Pages build"
echo "==========================================="