# Script to commit each file with its simple description as the commit message

$repoPath = "c:\1deathcounter"
Set-Location $repoPath

# Read FILE_DESCRIPTIONS.md to get descriptions
$descriptions = @{}
$content = Get-Content "FILE_DESCRIPTIONS.md" -Raw

# Parse descriptions from FILE_DESCRIPTIONS.md
if ($content -match '(?s)## Files(.*?)## Folders') {
    $filesSection = $matches[1]
    $filesSection -split "`n" | ForEach-Object {
        if ($_ -match '\*\*(.+?)\*\* - (.+)') {
            $filename = $matches[1].Trim()
            $description = $matches[2].Trim()
            $descriptions[$filename] = $description
        }
    }
}

# Add folder descriptions
if ($content -match '(?s)## Folders(.*)') {
    $foldersSection = $matches[1]
    $foldersSection -split "`n" | ForEach-Object {
        if ($_ -match '\*\*(.+?)\*\* - (.+)') {
            $foldername = $matches[1].Trim()
            $description = $matches[2].Trim()
            $descriptions[$foldername] = $description
        }
    }
}

# Function to get description for a file
function Get-FileDescription {
    param($filePath)
    
    $relativePath = $filePath.Replace("$repoPath\", "").Replace("\", "/")
    $fileName = Split-Path $relativePath -Leaf
    $folderName = Split-Path $relativePath -Parent
    
    # Check for exact match
    if ($descriptions.ContainsKey($relativePath)) {
        return $descriptions[$relativePath]
    }
    
    # Check for folder match
    if ($folderName -and $descriptions.ContainsKey("$folderName/")) {
        $folderDesc = $descriptions["$folderName/"]
        # Generate description based on file type
        $ext = [System.IO.Path]::GetExtension($fileName).ToLower()
        switch ($ext) {
            ".py" { return "$folderDesc - Python script" }
            ".bat" { return "$folderDesc - Batch script" }
            ".json" { return "$folderDesc - Configuration file" }
            ".txt" { return "$folderDesc - Text file" }
            ".cs" { return "$folderDesc - C# script" }
            ".exe" { return "$folderDesc - Executable" }
            ".ps1" { return "$folderDesc - PowerShell script" }
            default { return "$folderDesc - $fileName" }
        }
    }
    
    # Check for root file match
    if ($descriptions.ContainsKey($fileName)) {
        return $descriptions[$fileName]
    }
    
    # Generate generic description
    $ext = [System.IO.Path]::GetExtension($fileName).ToLower()
    $name = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
    switch ($ext) {
        ".py" { return "Python script: $name" }
        ".bat" { return "Batch script: $name" }
        ".json" { return "Configuration file: $name" }
        ".txt" { return "Text file: $name" }
        ".cs" { return "C# script: $name" }
        ".exe" { return "Executable: $name" }
        ".ps1" { return "PowerShell script: $name" }
        ".md" { return "Markdown documentation: $name" }
        default { return $fileName }
    }
}

# Get all tracked files
$allFiles = git ls-files

Write-Host "Creating commits for all files with their descriptions..."
Write-Host "Total files: $($allFiles.Count)"
Write-Host ""

# Commit each file individually
foreach ($file in $allFiles) {
    $filePath = Join-Path $repoPath $file
    if (Test-Path $filePath -PathType Leaf) {
        $description = Get-FileDescription $filePath
        Write-Host "Committing: $file"
        Write-Host "  Message: $description"
        
        # Touch text files to ensure they can be committed
        # Skip binary files (.exe, images, etc.)
        $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
        $binaryExts = @('.exe', '.dll', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.bin')
        
        if ($binaryExts -notcontains $ext) {
            try {
                # Force a change by normalizing line endings or ensuring trailing newline
                $content = Get-Content $filePath -Raw -ErrorAction Stop
                $needsChange = $false
                
                # Check if file needs trailing newline
                if ($content -and -not $content.EndsWith("`n") -and -not $content.EndsWith("`r`n")) {
                    $needsChange = $true
                }
                
                # Always ensure file ends with newline for consistency
                if (-not $needsChange) {
                    # Add a trailing newline if it doesn't exist, or normalize
                    $newContent = $content.TrimEnd("`r", "`n") + "`n"
                    if ($newContent -ne $content) {
                        Set-Content -Path $filePath -Value $newContent -NoNewline
                        $needsChange = $true
                    }
                } else {
                    Add-Content -Path $filePath -Value "`n" -NoNewline
                }
            } catch {
                # File might be binary or have encoding issues, skip touching
            }
        }
        
        # Stage only this file
        git add "$file"
        
        # Commit with the description as message
        git commit -m "$description" --no-verify
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Committed successfully" -ForegroundColor Green
        } else {
            Write-Host "  Skipped (file unchanged)" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

Write-Host "Done! All files have been committed with their descriptions."
Write-Host "Run git push origin main to push all commits."
