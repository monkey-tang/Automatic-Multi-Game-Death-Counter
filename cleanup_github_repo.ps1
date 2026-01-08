# GitHub Repository Cleanup Script
# This script cleans up the main branch to match the structure in c:\v1.5 DeathCounter

$sourceFolder = "c:\v1.5 DeathCounter"

Write-Host "=== GitHub Repository Cleanup Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a git repository!" -ForegroundColor Red
    Write-Host "Please run this script from your git repository root directory." -ForegroundColor Yellow
    exit 1
}

# Check if source folder exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "ERROR: Source folder not found: $sourceFolder" -ForegroundColor Red
    Write-Host "Please ensure c:\v1.5 DeathCounter exists with the desired structure." -ForegroundColor Yellow
    exit 1
}

# Get current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Current branch: $currentBranch" -ForegroundColor Yellow

if ($currentBranch -ne "main") {
    Write-Host "WARNING: You are not on the 'main' branch!" -ForegroundColor Red
    try {
        $confirm = Read-Host "Continue anyway? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "Aborted." -ForegroundColor Yellow
            exit 0
        }
    } catch {
        # Non-interactive mode - auto-continue
        Write-Host "Non-interactive mode: Continuing on branch $currentBranch..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Remove ALL files/folders except: DeathCounterInstaller.exe, README.md, and folders (All Contents, Debug.Test, Edit)" -ForegroundColor White
Write-Host "  2. Copy folder structure from $sourceFolder if needed" -ForegroundColor White
Write-Host ""

# Check for -AutoConfirm parameter
$autoConfirm = $false
if ($args -contains "-AutoConfirm" -or $args -contains "-y") {
    $autoConfirm = $true
    Write-Host "Auto-confirm mode: Proceeding automatically..." -ForegroundColor Cyan
} else {
    try {
        $confirm = Read-Host "Do you want to proceed with cleanup? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "Aborted." -ForegroundColor Yellow
            exit 0
        }
    } catch {
        # Non-interactive mode - auto-confirm
        Write-Host "Non-interactive mode detected. Proceeding automatically..." -ForegroundColor Cyan
        $autoConfirm = $true
    }
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Green

# Define what to KEEP
$keepFiles = @("DeathCounterInstaller.exe", "README.md", ".gitignore", "cleanup_github_repo.ps1")
$keepFolders = @("All Contents", "Debug.Test", "Edit", ".git")

# Get all current items
$allItems = Get-ChildItem -Force

# List of items to remove (everything except what we want to keep)
$itemsToRemove = @()
foreach ($item in $allItems) {
    $shouldKeep = $false
    
    if ($item.PSIsContainer) {
        # It's a folder
        if ($keepFolders -contains $item.Name) {
            $shouldKeep = $true
        }
    } else {
        # It's a file
        if ($keepFiles -contains $item.Name) {
            $shouldKeep = $true
        }
    }
    
    if (-not $shouldKeep) {
        $itemsToRemove += $item.Name
    }
}

# Remove each item
$removedCount = 0
foreach ($item in $itemsToRemove) {
    if (Test-Path $item) {
        Write-Host "Removing: $item" -ForegroundColor Yellow
        try {
            if (Test-Path $item -PathType Container) {
                # It's a folder
                git rm -r --cached $item 2>$null
                Remove-Item -Path $item -Recurse -Force -ErrorAction Stop
            } else {
                # It's a file
                git rm --cached $item 2>$null
                Remove-Item -Path $item -Force -ErrorAction Stop
            }
            $removedCount++
            Write-Host "  [OK] Removed: $item" -ForegroundColor Green
        } catch {
            Write-Host "  [ERROR] Error removing $item : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  - Not found: $item (skipping)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Copying folder structure from $sourceFolder..." -ForegroundColor Green

# Copy folders from source if they don't exist
$foldersToCopy = @("All Contents", "Debug.Test", "Edit")
foreach ($folder in $foldersToCopy) {
    $sourcePath = Join-Path $sourceFolder $folder
    $destPath = $folder
    
    if (Test-Path $sourcePath) {
        if (-not (Test-Path $destPath)) {
            Write-Host "Copying folder: $folder" -ForegroundColor Yellow
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            Write-Host "  [OK] Copied: $folder" -ForegroundColor Green
        } else {
            Write-Host "  - Folder already exists: $folder (skipping)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [ERROR] Source folder not found: $sourcePath" -ForegroundColor Red
    }
}

# Ensure DeathCounterInstaller.exe exists
$installerSource = Join-Path $sourceFolder "DeathCounterInstaller.exe"
$installerDest = "DeathCounterInstaller.exe"
if (Test-Path $installerSource) {
    if (-not (Test-Path $installerDest) -or (Get-Item $installerSource).LastWriteTime -gt (Get-Item $installerDest).LastWriteTime) {
        Write-Host "Copying: DeathCounterInstaller.exe" -ForegroundColor Yellow
        Copy-Item -Path $installerSource -Destination $installerDest -Force
        Write-Host "  [OK] Copied: DeathCounterInstaller.exe" -ForegroundColor Green
    }
}

# Ensure README.md exists
$readmeSource = Join-Path $sourceFolder "README.md"
$readmeDest = "README.md"
if (Test-Path $readmeSource) {
    if (-not (Test-Path $readmeDest) -or (Get-Item $readmeSource).LastWriteTime -gt (Get-Item $readmeDest).LastWriteTime) {
        Write-Host "Copying: README.md" -ForegroundColor Yellow
        Copy-Item -Path $readmeSource -Destination $readmeDest -Force
        Write-Host "  [OK] Copied: README.md" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Cleanup complete! Removed $removedCount item(s)." -ForegroundColor Green
Write-Host ""

# Show current structure
Write-Host "Final repository structure:" -ForegroundColor Cyan
Write-Host ""

# Top level files (should be DeathCounterInstaller.exe)
Write-Host "TOP LEVEL FILES (should be at top):" -ForegroundColor Yellow
$topFiles = Get-ChildItem -File | Where-Object { $_.Name -ne ".gitignore" -and $_.Name -ne "cleanup_github_repo.ps1" } | Sort-Object Name
foreach ($file in $topFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor White
}

# Folders (middle)
Write-Host ""
Write-Host "FOLDERS (middle):" -ForegroundColor Yellow
$folders = Get-ChildItem -Directory | Where-Object { $_.Name -ne ".git" } | Sort-Object Name
foreach ($folder in $folders) {
    Write-Host "  - $($folder.Name)/" -ForegroundColor White
}

# README should be at bottom
Write-Host ""
Write-Host "BOTTOM (should be README.md):" -ForegroundColor Yellow
if (Test-Path "README.md") {
    Write-Host "  [OK] README.md" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] README.md not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the changes: git status" -ForegroundColor White
Write-Host "2. Stage all changes: git add -A" -ForegroundColor White
Write-Host "3. Commit: git commit -m 'Clean up main branch structure to match v1.5 folder'" -ForegroundColor White
Write-Host "4. Push: git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "Note: The cleanup script (cleanup_github_repo.ps1) will remain in the repo." -ForegroundColor Gray
Write-Host "You can remove it manually after cleanup if desired." -ForegroundColor Gray
Write-Host ""
