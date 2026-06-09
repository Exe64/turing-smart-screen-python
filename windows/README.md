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

3. **Activer le démarrage automatique** — clic droit sur
   `windows\install-autostart.ps1` → **« Exécuter avec PowerShell »**,
   ou dans un terminal :

   ```powershell
   powershell -ExecutionPolicy Bypass -File windows\install-autostart.ps1
   ```

   Le programme se lancera désormais à chaque ouverture de session.
   Pour le démarrer immédiatement sans redémarrer, double-cliquez sur
   `windows\run-hidden.vbs`.

## Désinstaller le démarrage automatique

```powershell
powershell -ExecutionPolicy Bypass -File windows\uninstall-autostart.ps1
```

## Fichiers

| Fichier | Rôle |
|---------|------|
| `install-deps.bat` | Installe les dépendances (`requirements.txt` + `pynput`) |
| `start.bat` | Lance le programme **avec** console (test / débogage) |
| `run-hidden.vbs` | Lance le programme **sans** fenêtre (utilisé par l'autostart) |
| `install-autostart.ps1` | Crée le raccourci dans le dossier *Démarrage* |
| `uninstall-autostart.ps1` | Supprime ce raccourci |

## Notes

- **Port COM** : par défaut `config.yaml` utilise `COM_PORT: "AUTO"`. Si l'écran
  n'est pas détecté, renseignez le port manuellement (ex. `COM_PORT: "COM3"`).
- **Usage Claude Code** : l'écran « Claude Code Usage » lit vos identifiants dans
  `%USERPROFILE%\.claude\.credentials.json`. Si vos credentials sont ailleurs,
  définissez la variable d'environnement `CLAUDE_CREDENTIALS`.
- **Écrans personnalisés** : ajoutez vos écrans et raccourcis clavier dans
  `multiscreen.yaml` (voir les commentaires dans ce fichier).
- Le dossier *Démarrage* est accessible via `Win + R` → `shell:startup`.
