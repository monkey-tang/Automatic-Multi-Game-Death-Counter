#!/bin/sh
# Git message filter script to update commit messages with detailed descriptions

commit_hash="$GIT_COMMIT"
commit_msg=$(cat)

# Get list of files changed in this commit
files=$(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null)

if [ -z "$files" ]; then
    echo "$commit_msg"
    exit 0
fi

# Get the first file changed (most commits are single-file)
first_file=$(echo "$files" | head -n1)

# Map file to description
case "$first_file" in
    "DeathCounterInstaller.exe")
        echo "Latest installer executable (v1.5). This is the main file users should download. Uses Git LFS for large file storage. Includes Python version compatibility checking and automatic Japanese language pack download for Sekiro support."
        ;;
    "README.md")
        echo "This documentation file. Contains installation instructions, feature descriptions, repository structure, and troubleshooting information."
        ;;
    ".gitattributes")
        echo "Git LFS configuration file. It tells Git which large files (e.g., *.exe) should be tracked by Git Large File Storage instead of directly in the Git repository. This prevents repository bloat and allows for easier management of large binaries."
        ;;
    ".gitignore")
        echo "Git ignore rules. This file specifies intentionally untracked files that Git should ignore (e.g., temporary files, build artifacts, local configurations). It helps keep the repository clean and focused on source code."
        ;;
    "cleanup_github_repo.ps1")
        echo "Utility PowerShell script used to organize the repository structure, remove old files, and copy the desired folder layout from a local reference folder. Helps maintain consistency between local development and GitHub repository."
        ;;
    "create_release.ps1")
        echo "PowerShell script for creating GitHub releases. Can be used to automate the process of creating a new release with the installer executable as a downloadable asset."
        ;;
    "FILE_DESCRIPTIONS.md")
        echo "File containing detailed descriptions for all files and folders, matching the README structure."
        ;;
    "commit_with_descriptions.ps1")
        echo "PowerShell script to commit files with their descriptions."
        ;;
    "All Contents/multi_game_death_counter.py")
        echo "Main daemon script that performs screen capture, OCR detection, and death counting"
        ;;
    "All Contents/death_counter_gui.py")
        echo "GUI application for controlling the daemon and viewing death statistics"
        ;;
    "All Contents/games_config.json")
        echo "Configuration file defining game-specific settings (capture regions, keywords, process names)"
        ;;
    "All Contents/switch_game_manual.py")
        echo "Script for manually switching between games"
        ;;
    "All Contents/change_monitor_id.py")
        echo "Utility for changing monitor detection settings"
        ;;
    "All Contents/capture_debug_once.py")
        echo "Debug utility for capturing a single screen region for testing"
        ;;
    "All Contents/reset_death_counter.py")
        echo "Script to reset death counts to zero"
        ;;
    "All Contents/test_daemon_start.py")
        echo "Test script to diagnose daemon startup issues"
        ;;
    "All Contents/deathcounteraction.cs")
        echo "Streamer.bot action file for integration"
        ;;
    "All Contents/START_DEATH_COUNTER.bat")
        echo "Batch file for starting the daemon"
        ;;
    "All Contents/STOP_DEATH_COUNTER.bat")
        echo "Batch file for stopping the daemon"
        ;;
    "All Contents/RESET_DEATH_COUNTER.bat")
        echo "Batch file for resetting death counts"
        ;;
    "All Contents/CAPTURE_DEBUG.bat")
        echo "Batch file for running debug capture"
        ;;
    "All Contents/CHANGE_MONITOR_ID.bat")
        echo "Batch file for changing monitor settings"
        ;;
    "All Contents/install_dependencies.bat")
        echo "Batch file for installing Python dependencies"
        ;;
    "All Contents/total_deaths.txt")
        echo "Text file storing total death counts"
        ;;
    "All Contents/daemon.ready")
        echo "Flag file indicating daemon is ready"
        ;;
    "All Contents/daemon_startup_error.txt")
        echo "Text file containing daemon startup errors"
        ;;
    "Debug.Test/capture_debug_once.py")
        echo "Debug utility for capturing a single screen region for testing"
        ;;
    "Debug.Test/test_daemon_start.py")
        echo "Test script to diagnose daemon startup issues"
        ;;
    "Debug.Test/CAPTURE_DEBUG.bat")
        echo "Batch file for running debug capture"
        ;;
    "Edit/build_single_file.py")
        echo "Build script that packages all application files into a single installer script. This script embeds all necessary files (Python scripts, configs, batch files) into DeathCounter_Installer_Standalone.py."
        ;;
    "Edit/DeathCounter_Installer_Standalone.py")
        echo "The standalone installer script generated by build_single_file.py. This is the Python script version of the installer before it's compiled into an .exe using PyInstaller."
        ;;
    "Edit/multi_game_death_counter.py")
        echo "Source copy of main daemon script (for reference during build process)"
        ;;
    "Edit/death_counter_gui.py")
        echo "Source copy of GUI application (for reference during build process)"
        ;;
    "Edit/games_config.json")
        echo "Source copy of configuration file (for reference during build process)"
        ;;
    "Edit/switch_game_manual.py")
        echo "Source copy of game switching script (for reference during build process)"
        ;;
    "Edit/change_monitor_id.py")
        echo "Source copy of monitor utility (for reference during build process)"
        ;;
    "Edit/capture_debug_once.py")
        echo "Source copy of debug utility (for reference during build process)"
        ;;
    "Edit/reset_death_counter.py")
        echo "Source copy of reset script (for reference during build process)"
        ;;
    "Edit/test_daemon_start.py")
        echo "Source copy of test script (for reference during build process)"
        ;;
    "Edit/deathcounteraction.cs")
        echo "Source copy of Streamer.bot action file (for reference during build process)"
        ;;
    "Edit/START_DEATH_COUNTER.bat")
        echo "Source copy of start batch file (for reference during build process)"
        ;;
    "Edit/STOP_DEATH_COUNTER.bat")
        echo "Source copy of stop batch file (for reference during build process)"
        ;;
    "Edit/RESET_DEATH_COUNTER.bat")
        echo "Source copy of reset batch file (for reference during build process)"
        ;;
    "Edit/CAPTURE_DEBUG.bat")
        echo "Source copy of debug batch file (for reference during build process)"
        ;;
    "Edit/CHANGE_MONITOR_ID.bat")
        echo "Source copy of monitor batch file (for reference during build process)"
        ;;
    "Edit/install_dependencies.bat")
        echo "Source copy of install batch file (for reference during build process)"
        ;;
    *)
        # For other files, try to match pattern
        if echo "$first_file" | grep -q "^All Contents/"; then
            filename=$(basename "$first_file")
            ext="${filename##*.}"
            name="${filename%.*}"
            case "$ext" in
                py) echo "Python script in All Contents folder: $name" ;;
                bat) echo "Batch file in All Contents folder: $name" ;;
                json) echo "Configuration file in All Contents folder: $name" ;;
                txt) echo "Text file in All Contents folder: $name" ;;
                cs) echo "C# file in All Contents folder: $name" ;;
                *) echo "File in All Contents folder: $filename" ;;
            esac
        elif echo "$first_file" | grep -q "^Debug.Test/"; then
            filename=$(basename "$first_file")
            ext="${filename##*.}"
            name="${filename%.*}"
            case "$ext" in
                py) echo "Debug and testing utility: $name" ;;
                bat) echo "Debug and testing batch file: $name" ;;
                *) echo "Debug and testing file: $filename" ;;
            esac
        elif echo "$first_file" | grep -q "^Edit/"; then
            filename=$(basename "$first_file")
            ext="${filename##*.}"
            name="${filename%.*}"
            case "$ext" in
                py) echo "Development script: $name" ;;
                bat) echo "Development batch file: $name" ;;
                json) echo "Development configuration file: $name" ;;
                cs) echo "Development C# file: $name" ;;
                *) echo "Development file: $filename" ;;
            esac
        else
            # Keep original message for unrecognized files
            echo "$commit_msg"
        fi
        ;;
esac
