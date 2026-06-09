# Démarrage automatique sous Windows

Scripts pour lancer le **gestionnaire multi-écrans** (`multiscreen.py`)
automatiquement à l'ouverture de session Windows, sans fenêtre visible.

> Prérequis : Python 3.9+ installé et accessible dans le `PATH`
> (à l'installation, cochez **« Add Python to PATH »**).

## Installation (3 étapes)

1. **Installer les dépendances** — double-cliquez sur :

   ```
   windows\install-deps.bat
   ```

2. **Tester** que tout fonctionne (avec une fenêtre console pour voir les erreurs) :

   ```
   windows\start.bat
   ```

   L'écran doit s'allumer et afficher le moniteur. Fermez avec `Ctrl + C`.

3. **Activer le démarrage automatique** — voir ci-dessous.

## Démarrage automatique : quelle méthode ?

Le programme a besoin des **droits administrateur** pour lire les capteurs
matériels (températures CPU/GPU via LibreHardwareMonitor) et accéder à l'écran.
Choisissez la méthode selon votre cas :

### A. Avec droits administrateur — Planificateur de tâches *(recommandé)*

Indispensable si le programme ne fonctionne qu'en *« Exécuter en tant
qu'administrateur »*. Crée une tâche planifiée « à l'ouverture de session »
avec autorisations maximales — **aucune invite UAC au logon**.

Clic droit sur `windows\install-autostart-admin.ps1` → **« Exécuter avec
PowerShell »** (une invite UAC apparaît **à l'installation**, c'est normal),
ou dans un terminal :

```powershell
powershell -ExecutionPolicy Bypass -File windows\install-autostart-admin.ps1
```

Le script retire automatiquement l'éventuel raccourci de la méthode B pour
éviter un double lancement. Pour lancer tout de suite sans redémarrer :

```powershell
Start-ScheduledTask -TaskName TuringSmartScreen
```

Désinstaller :

```powershell
powershell -ExecutionPolicy Bypass -File windows\uninstall-autostart-admin.ps1
```

### B. Sans droits administrateur — dossier *Démarrage*

Plus simple, mais **ne s'élève pas en administrateur** : à n'utiliser que si le
programme fonctionne sans droits admin sur votre machine.

```powershell
powershell -ExecutionPolicy Bypass -File windows\install-autostart.ps1
```

Pour le démarrer immédiatement sans redémarrer, double-cliquez sur
`windows\run-hidden.vbs`. Désinstaller :

```powershell
powershell -ExecutionPolicy Bypass -File windows\uninstall-autostart.ps1
```

## Fichiers

| Fichier | Rôle |
|---------|------|
| `install-deps.bat` | Installe les dépendances (`requirements.txt` + `pynput`) |
| `start.bat` | Lance le programme **avec** console (test / débogage) |
| `check-claude.bat` | Diagnostic de l'écran Claude (pourquoi il est vide) |
| `run-hidden.vbs` | Lance le programme **sans** fenêtre (utilisé par l'autostart) |
| `install-autostart-admin.ps1` | **(A)** Tâche planifiée au logon, droits admin |
| `uninstall-autostart-admin.ps1` | Supprime la tâche planifiée |
| `install-autostart.ps1` | **(B)** Raccourci dans le dossier *Démarrage* (sans admin) |
| `uninstall-autostart.ps1` | Supprime ce raccourci |

## Notes

- **Affichage à l'envers** : dans `config.yaml`, ajustez
  `DISPLAY_REVERSE: true/false` selon l'orientation de votre écran.
- **Port COM** : par défaut `config.yaml` utilise `COM_PORT: "AUTO"`. Si l'écran
  n'est pas détecté, renseignez le port manuellement (ex. `COM_PORT: "COM3"`).
- **Usage Claude Code** : sous Windows, le token principal de Claude Code est
  stocké dans le **Gestionnaire d'identifiants Windows** (le fichier
  `%USERPROFILE%\.claude\.credentials.json` ne contient que les tokens MCP des
  plugins). L'écran le lit automatiquement aux deux endroits.
  **Si cet écran reste vide**, lancez `windows\check-claude.bat` : il affiche la
  cause réelle (token introuvable, expiré, erreur API…).
  Méthode la plus fiable (token dédié, supportée par Claude Code) :
  1. `claude setup-token` dans un terminal,
  2. `setx CLAUDE_CODE_OAUTH_TOKEN "sk-ant-oat01-..."` (copiez le token affiché),
  3. fermez/rouvrez le terminal — le moniteur lira ce token automatiquement.
  Le token peut aussi venir de `%USERPROFILE%\.claude\.credentials.json`
  (`claudeAiOauth`), de `CLAUDE_CONFIG_DIR`, ou de `CLAUDE_CREDENTIALS`.
- **Écran par défaut** : c'est le **premier** de la liste `screens:` dans
  `multiscreen.yaml`. Réordonnez la liste pour changer celui affiché au démarrage.
- **Écrans personnalisés** : ajoutez vos écrans et raccourcis clavier dans
  `multiscreen.yaml` (voir les commentaires dans ce fichier).
- Le dossier *Démarrage* est accessible via `Win + R` → `shell:startup`.
