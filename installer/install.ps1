param( [Parameter(Mandatory=$true)] $EnvPath, [Parameter(Mandatory=$true)] $SavesPath )
 "Path to virtual Environment: " + $EnvPath
 "Path for Game profile (Save files, config, ...): " + $SavesPath

 Write-Host $SavesPath

$PIP = Join-Path -Path $EnvPath -ChildPath "Scripts\pip.exe"
$PYTHON = Join-Path -Path $EnvPath -ChildPath "python.exe"
$QROGUE_PATH = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$QROGUE_PATH = Split-Path -Path $QROGUE_PATH -Parent
$SAVES_PATH = Join-Path -Path $SavesPath -ChildPath "Qrogue"

$CONFIG_PATH = Join-Path -Path $QROGUE_PATH -ChildPath "installer\qrogue.config"
$PYTHON | Out-File -FilePath $CONFIG_PATH
$SAVES_PATH | Out-File -FilePath $CONFIG_PATH -Append

Write-Host "[Qrogue] Installing the required packages in the provided environment..."
$REQUIREMENTS = Join-Path -Path $QROGUE_PATH -ChildPath "installer\requirements_windows.txt"
& $PIP install -r $REQUIREMENTS
Write-Host "[Qrogue] Done installing!"

Write-Host "[Qrogue] Setting up Game profile..."
$LOGS_PATH = Join-Path -Path $SAVES_PATH -ChildPath "logs"
$KEYLOGS_PATH = Join-Path -Path $SAVES_PATH -ChildPath "keylogs"
$SCREEN_PATH = Join-Path -Path $SAVES_PATH -ChildPath "screenprints"
if (-Not (Test-Path $SAVES_PATH)) {
    New-Item -Path $SAVES_PATH -ItemType Directory
}
if (-Not (Test-Path $LOGS_PATH)) {
    New-Item -Path $LOGS_PATH -ItemType Directory
}
if (-Not (Test-Path $KEYLOGS_PATH)) {
    New-Item -Path $KEYLOGS_PATH -ItemType Directory
}
if (-Not (Test-Path $SCREEN_PATH)) {
    New-Item -Path $SCREEN_PATH -ItemType Directory
}

# set up powershell profile for shell customization
$qrogue_profile = Join-Path -Path $SAVES_PATH -ChildPath QrogueProfile.ps1
$output = New-Item -Path $qrogue_profile -ItemType File -Force
Write-Host "[Qrogue] Finished. You can play now by executing play_qrogue.ps1 (best experience in Powershell)!"
