# ============================================================================
#  Demarrage automatique AVEC droits administrateur (Planificateur de taches).
#
#  Le gestionnaire multi-ecrans a besoin des droits admin pour lire les
#  capteurs materiels (LibreHardwareMonitor) et acceder a l'ecran. Le dossier
#  "Demarrage" ne peut pas elever les droits : on passe donc par une tache
#  planifiee "a l'ouverture de session" avec autorisations maximales
#  (aucune invite UAC au logon).
#
#  Ce script s'eleve tout seul (une invite UAC a l'installation, c'est normal).
#  Utilisation : clic droit > "Executer avec PowerShell", ou :
#     powershell -ExecutionPolicy Bypass -File windows\install-autostart-admin.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

# --- Auto-elevation : relance le script en administrateur si besoin ---
$identity  = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Demande des droits administrateur..."
    Start-Process powershell.exe -Verb RunAs -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`""
    )
    exit
}

$taskName   = "TuringSmartScreen"
$projectDir = Split-Path -Parent $PSScriptRoot
$vbs        = Join-Path $PSScriptRoot "run-hidden.vbs"
$wscript    = Join-Path $env:WINDIR "System32\wscript.exe"

if (-not (Test-Path $vbs)) {
    Write-Error "Fichier introuvable : $vbs"
    Read-Host "Appuyez sur Entree pour fermer"
    exit 1
}

# Retirer l'ancien raccourci du dossier "Demarrage" (evite un double lancement)
$startupLnk = Join-Path ([Environment]::GetFolderPath("Startup")) "TuringSmartScreen.lnk"
if (Test-Path $startupLnk) {
    Remove-Item $startupLnk
    Write-Host "Ancien raccourci du dossier Demarrage supprime."
}

# Supprimer une tache existante du meme nom (reinstallation propre)
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# wscript lance run-hidden.vbs -> pythonw multiscreen.py (aucune fenetre)
$action    = New-ScheduledTaskAction -Execute $wscript -Argument "`"$vbs`"" -WorkingDirectory $projectDir
$trigger   = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType Interactive -RunLevel Highest
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
                                          -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description "Turing Smart Screen - Gestionnaire multi-ecrans (admin, au logon)" | Out-Null

Write-Host ""
Write-Host "Tache planifiee '$taskName' creee." -ForegroundColor Green
Write-Host "  -> Se lance a l'ouverture de session, en administrateur, sans invite UAC."
Write-Host ""
Write-Host "Pour la lancer immediatement (sans redemarrer) :"
Write-Host "  Start-ScheduledTask -TaskName $taskName"
Write-Host ""
Write-Host "Pour desinstaller : windows\uninstall-autostart-admin.ps1"
Write-Host ""
Read-Host "Appuyez sur Entree pour fermer"
