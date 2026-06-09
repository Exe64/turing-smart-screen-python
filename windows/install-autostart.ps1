# ============================================================================
#  Installe le demarrage automatique a l'ouverture de session Windows.
#  Cree un raccourci dans le dossier "Demarrage" de l'utilisateur courant
#  qui lance le gestionnaire multi-ecrans sans aucune fenetre.
#
#  Utilisation (clic droit > "Executer avec PowerShell"), ou dans un terminal :
#     powershell -ExecutionPolicy Bypass -File windows\install-autostart.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

# Dossier racine du projet (parent de "windows\")
$projectDir = Split-Path -Parent $PSScriptRoot
$vbs        = Join-Path $PSScriptRoot "run-hidden.vbs"

if (-not (Test-Path $vbs)) {
    Write-Error "Fichier introuvable : $vbs"
    exit 1
}

# Dossier "Demarrage" de l'utilisateur courant
$startup = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startup "TuringSmartScreen.lnk"

# Creation du raccourci -> wscript.exe lance le VBS (donc pythonw, sans console)
$shell    = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($lnkPath)
$shortcut.TargetPath       = Join-Path $env:WINDIR "System32\wscript.exe"
$shortcut.Arguments        = "`"$vbs`""
$shortcut.WorkingDirectory = $projectDir
$shortcut.WindowStyle      = 7   # minimise / sans fenetre
$shortcut.Description       = "Turing Smart Screen - Gestionnaire multi-ecrans"
$shortcut.Save()

Write-Host ""
Write-Host "Demarrage automatique installe." -ForegroundColor Green
Write-Host "  Raccourci : $lnkPath"
Write-Host ""
Write-Host "Le programme se lancera a la prochaine ouverture de session."
Write-Host "Pour le lancer des maintenant sans redemarrer :"
Write-Host "  double-cliquez sur windows\run-hidden.vbs"
Write-Host ""
Write-Host "Pour desinstaller : windows\uninstall-autostart.ps1"
