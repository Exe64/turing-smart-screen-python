#!/usr/bin/env python3
"""
Diagnostic de l'ecran "Claude Code Usage".

Le moniteur masque les erreurs de recuperation des donnees Claude (elles sont
juste loguees en warning, et l'ecran affiche 0 / vide). Ce script reproduit
l'appel et affiche TOUT : ou sont lus les identifiants, validite du token, et
la reponse brute de l'API. A lancer depuis le dossier du projet :

    python windows\\check-claude.py

Sous Windows, le token principal de Claude Code n'est PAS dans
.credentials.json (qui ne contient que les tokens MCP des plugins) mais dans
le Gestionnaire d'identifiants Windows : ce script cherche aux deux endroits.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def _resolve_credentials_path() -> Path:
    explicit = os.environ.get("CLAUDE_CREDENTIALS")
    if explicit:
        return Path(explicit)
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        return Path(config_dir) / ".credentials.json"
    return Path.home() / ".claude" / ".credentials.json"


CREDENTIALS_PATH = _resolve_credentials_path()
USAGE_API_URL = "https://api.anthropic.com/api/oauth/usage"


def find_oauth(obj):
    """Cherche recursivement un bloc claudeAiOauth.accessToken."""
    if isinstance(obj, dict):
        oauth = obj.get("claudeAiOauth")
        if isinstance(oauth, dict) and oauth.get("accessToken"):
            return oauth
        for value in obj.values():
            found = find_oauth(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_oauth(value)
            if found:
                return found
    return None


def search_windows_credential_manager():
    """Enumere le Gestionnaire d'identifiants Windows et cherche le token Claude."""
    try:
        import win32cred  # pywin32
    except ImportError:
        print("    [X] pywin32 non installe -> lancez windows\\install-deps.bat")
        return None
    try:
        entries = win32cred.CredEnumerate(None, 0)
    except Exception as e:
        print(f"    [X] Enumeration impossible : {e}")
        return None

    claude_entries = [c for c in entries if "claude" in (c.get("TargetName") or "").lower()]
    print(f"    {len(entries)} identifiant(s) au total, {len(claude_entries)} contenant 'claude'.")
    print("    Liste complete des noms (TargetName) pour reperage :")
    for c in entries:
        print(f"      - {c.get('TargetName')}")

    for c in claude_entries:
        blob = c.get("CredentialBlob")
        text = None
        if isinstance(blob, bytes):
            for encoding in ("utf-16-le", "utf-8"):
                try:
                    text = blob.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
        elif isinstance(blob, str):
            text = blob
        if not text:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue
        oauth = find_oauth(data)
        if oauth:
            print(f"    [OK] Token Claude trouve dans : {c.get('TargetName')}")
            return oauth
    return None


def main() -> int:
    print("=" * 60)
    print(" Diagnostic ecran Claude Code Usage")
    print("=" * 60)
    print("Variables d'environnement :")
    for var in ("CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CREDENTIALS", "CLAUDE_CONFIG_DIR", "ANTHROPIC_API_KEY"):
        val = os.environ.get(var)
        shown = "(non definie)" if not val else f"definie (longueur {len(val)})"
        print(f"  {var} : {shown}")
    print(f"\nFichier d'identifiants : {CREDENTIALS_PATH}")
    print(f"  le fichier existe ?  : {CREDENTIALS_PATH.exists()}")

    oauth = None

    # 0) Token longue duree fourni par CLAUDE_CODE_OAUTH_TOKEN (`claude setup-token`)
    env_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if env_token:
        print("\n[OK] Token fourni par CLAUDE_CODE_OAUTH_TOKEN.")
        oauth = {"accessToken": env_token}

    # 1) Dans le fichier .credentials.json
    if oauth is None and CREDENTIALS_PATH.exists():
        try:
            creds = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
            oauth = find_oauth(creds)
            if oauth:
                print("\n[OK] Token Claude trouve dans le fichier .credentials.json.")
            else:
                print("\n[i] Pas de 'claudeAiOauth' dans le fichier")
                print("    (normal sous Windows : il ne contient que les tokens MCP des plugins).")
        except Exception as e:
            print(f"\n[X] Fichier illisible (JSON invalide) : {e}")

    # 2) Dans le Gestionnaire d'identifiants Windows
    if not oauth and sys.platform == "win32":
        print("\nRecherche dans le Gestionnaire d'identifiants Windows...")
        oauth = search_windows_credential_manager()

    if not oauth:
        print("\n[X] Aucun token Claude trouve.")
        print("    Solution recommandee (token dedie, supporte) :")
        print("      1) dans un terminal : claude setup-token")
        print("      2) copiez le token affiche (sk-ant-oat01-...)")
        print('      3) setx CLAUDE_CODE_OAUTH_TOKEN "sk-ant-oat01-..."')
        print("      4) FERMEZ et rouvrez le terminal, puis relancez ce diagnostic.")
        return 1

    token = oauth["accessToken"]
    print(f"     accessToken trouve (longueur {len(token)}).")
    exp = oauth.get("expiresAt")
    if exp:
        # expiresAt est en millisecondes
        exp_dt = datetime.fromtimestamp(exp / 1000)
        now = datetime.now()
        etat = "EXPIRE" if exp_dt < now else "valide"
        print(f"     expiration : {exp_dt}  ({etat})")
        if exp_dt < now:
            print("     -> Token EXPIRE : lancez `claude` sur ce PC pour le rafraichir.")

    # 3) Appel API
    try:
        import requests
    except ImportError:
        print("\n[X] Module 'requests' manquant. Lancez windows\\install-deps.bat")
        return 1

    print(f"\nAppel : GET {USAGE_API_URL}")
    try:
        resp = requests.get(
            USAGE_API_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        print(f"  Reponse HTTP : {resp.status_code}")
        body = resp.text
        print("  Corps :")
        print("  " + (body[:2000] if body else "(vide)"))
        resp.raise_for_status()
        print("\n[OK] L'API renvoie des donnees. L'ecran Claude devrait s'afficher.")
        return 0
    except Exception as e:
        print(f"\n[X] Echec de l'appel API : {e}")
        print("    - HTTP 401 -> token invalide/expire : relancez `claude`.")
        print("    - timeout / erreur reseau -> connexion / proxy / pare-feu.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
