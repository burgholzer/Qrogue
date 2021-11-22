$QROGUE_PATH = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$CONFIG_PATH = Join-Path -Path ${QROGUE_PATH} -ChildPath "installer\qrogue.config"
$GAME_PATH = Join-Path -Path ${QROGUE_PATH} -ChildPath "main.py"

$config = Get-Content ${CONFIG_PATH}

# load powershell profile
#$profile_parent = Split-Path -Path $profile -Parent
#$qrogue_profile = Join-Path -ChildPath QrogueProfile.ps1 -Path ${profile_parent}
#. ${qrogue_profile}

# start game
$PYTHON = ${config} | Select-Object -First 1
& ${PYTHON} ${GAME_PATH}
