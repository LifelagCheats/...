# Save this file as SetupAndRun.ps1 and run it with administrative privileges

# CONFIGURATION VARIABLES
$repoUrl  = "https://https://github.com/LifelagCheats/..."  # change this to your repo URL
$repoName = "..."                                      # expected folder name after cloning
$mainScript = "script.pyw"                                   # the script to execute inside the repo

# Function to check if a command exists
function Command-Exists {
    param([string]$cmd)
    $ErrorActionPreference = 'SilentlyContinue'
    $exists = Get-Command $cmd -ErrorAction SilentlyContinue
    $ErrorActionPreference = 'Continue'
    return $exists -ne $null
}

Write-Host "Starting setup..."

# 1. Install Git if not already installed
if (-not (Command-Exists "git")) {
    Write-Host "Installing Git..."
    winget install --id Git.Git -e --silent `
        --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "Git is already installed."
}

# 2. Install Python if not already installed
if (-not (Command-Exists "python")) {
    Write-Host "Installing Python..."
    winget install --id Python.Python.3 -e --silent `
        --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "Python is already installed."
}

# 3. Clone the repository
Write-Host "Cloning repository..."
if (Test-Path $repoName) {
    Write-Host "Repository folder '$repoName' already exists. Removing it..."
    Remove-Item -Recurse -Force $repoName
}
git clone $repoUrl

# 4. Change directory into the repo folder
Set-Location $repoName

# 5. Upgrade pip and install all requirements from requirements.txt
Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt file found."
}

# 6. Execute the main script
Write-Host "Executing the main script: $mainScript"
pythonw.exe $mainScript

Write-Host "Setup complete."
