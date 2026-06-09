# ============================================================================
#  Supprime le demarrage automatique installe par install-autostart.ps1.
#     powershell -ExecutionPolicy Bypass -File windows\uninstall-autostart.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

$startup = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startup "TuringSmartScreen.lnk"

if (Test-Path $lnkPath) {
    Remove-Item $lnkPath
    Write-Host "Demarrage automatique supprime : $lnkPath" -ForegroundColor Green
} else {
    Write-Host "Aucun demarrage automatique trouve (rien a supprimer)."
}
