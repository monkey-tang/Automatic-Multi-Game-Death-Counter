# Script to create GitHub Release v1.5 with DeathCounterInstaller.exe as asset
# Requires GitHub Personal Access Token with 'repo' scope

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [string]$RepoOwner = "monkey-tang",
    [string]$RepoName = "Automatic-Multi-Game-Death-Counter",
    [string]$Tag = "v1.5",
    [string]$ReleaseName = "v1.5 - Multi-Game Death Counter",
    [string]$ExeFile = "DeathCounterInstaller.exe"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Creating GitHub Release v1.5 ===" -ForegroundColor Cyan
Write-Host ""

# Check if exe file exists
if (-not (Test-Path $ExeFile)) {
    Write-Host "ERROR: $ExeFile not found!" -ForegroundColor Red
    exit 1
}

$exeInfo = Get-Item $ExeFile
Write-Host "Found: $($exeInfo.Name) ($([math]::Round($exeInfo.Length / 1MB, 2)) MB)" -ForegroundColor Green
Write-Host ""

# GitHub API endpoints
$baseUrl = "https://api.github.com"
$releasesUrl = "$baseUrl/repos/$RepoOwner/$RepoName/releases"

# Headers
$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
}

# Release notes
$releaseNotes = @"
## Death Counter v1.5

### Features
- **Windowed Mode Support**: Automatically detects and supports fullscreen, windowed, and borderless window modes
- **Multi-Monitor Support**: Handles games spanning across multiple displays
- **Automatic Japanese Pack Download**: Auto-downloads Japanese language packs for Sekiro support
- **Multi-Resolution Support**: Works on any screen resolution (720p, 1080p, 1440p, 4K, ultrawide)

### Supported Games
- Elden Ring
- Dark Souls Remastered
- Dark Souls II
- Dark Souls III
- Sekiro: Shadows Die Twice

### Installation
1. Download **DeathCounterInstaller.exe** from the assets below
2. Run the installer (double-click)
3. Follow the on-screen instructions

**Note**: This installer includes all necessary files and will guide you through the setup process.
"@

# Create release payload
$releaseData = @{
    tag_name = $Tag
    name = $ReleaseName
    body = $releaseNotes
    draft = $false
    prerelease = $false
} | ConvertTo-Json

Write-Host "Creating release..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri $releasesUrl -Method Post -Headers $headers -Body $releaseData -ContentType "application/json"
    $releaseId = $response.id
    Write-Host "✓ Release created! ID: $releaseId" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "Release already exists. Updating..." -ForegroundColor Yellow
        # Get existing release
        $existingRelease = Invoke-RestMethod -Uri "$releasesUrl/tags/$Tag" -Method Get -Headers $headers
        $releaseId = $existingRelease.id
        
        # Update release
        $updateData = @{
            name = $ReleaseName
            body = $releaseNotes
        } | ConvertTo-Json
        Invoke-RestMethod -Uri "$releasesUrl/$releaseId" -Method Patch -Headers $headers -Body $updateData -ContentType "application/json"
        Write-Host "✓ Release updated!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create release" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Uploading $ExeFile..." -ForegroundColor Yellow

# Upload asset
$uploadUrl = "$releasesUrl/$releaseId/assets?name=$ExeFile"
$fileContent = [System.IO.File]::ReadAllBytes((Resolve-Path $ExeFile))

try {
    # GitHub API requires multipart/form-data for file uploads
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"name`"$LF",
        $ExeFile,
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$ExeFile`"",
        "Content-Type: application/octet-stream$LF",
        [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileContent),
        "--$boundary--"
    )
    
    $body = $bodyLines -join $LF
    $bodyBytes = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($body)
    
    $uploadHeaders = @{
        "Authorization" = "token $GitHubToken"
        "Accept" = "application/vnd.github.v3+json"
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }
    
    $uploadResponse = Invoke-RestMethod -Uri $uploadUrl -Method Post -Headers $uploadHeaders -Body $bodyBytes
    Write-Host "✓ File uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Release URL: $($uploadResponse.browser_download_url -replace '/releases/assets/.*', '/releases/tag/' + $Tag)" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Failed to upload file" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to upload the file manually through GitHub's web interface:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/$RepoOwner/$RepoName/releases/tag/$Tag" -ForegroundColor White
    Write-Host "2. Click 'Edit' on the release" -ForegroundColor White
    Write-Host "3. Drag and drop $ExeFile into the 'Attach binaries' section" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Release created successfully!" -ForegroundColor Green
Write-Host "View at: https://github.com/$RepoOwner/$RepoName/releases/tag/$Tag" -ForegroundColor Cyan
