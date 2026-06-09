# ============================================================================
#  Supprime la tache planifiee creee par install-autostart-admin.ps1.
#  S'eleve tout seul en administrateur (une invite UAC, c'est normal).
#     powershell -ExecutionPolicy Bypass -File windows\uninstall-autostart-admin.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

# --- Auto-elevation ---
$identity  = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -Verb RunAs -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`""
    )
    exit
}

$taskName = "TuringSmartScreen"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Tache planifiee '$taskName' supprimee." -ForegroundColor Green
} else {
    Write-Host "Aucune tache '$taskName' trouvee (rien a supprimer)."
}

Read-Host "Appuyez sur Entree pour fermer"
